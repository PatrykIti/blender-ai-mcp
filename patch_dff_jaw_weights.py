"""Перенос весов Jaw из оригинальных GTA SA DFF в HD-модели."""

from __future__ import annotations

import argparse
import math
import shutil
import struct
from dataclasses import dataclass
from pathlib import Path

CHUNK_STRUCT = 0x01
CHUNK_EXTENSION = 0x03
CHUNK_CLUMP = 0x10
CHUNK_FRAME_LIST = 0x0E
CHUNK_GEOMETRY = 0x0F
CHUNK_GEOMETRY_LIST = 0x1A
PLUGIN_HANIM = 0x11E
PLUGIN_SKIN = 0x116


@dataclass
class Chunk:
    header: int
    content: int
    end: int
    chunk_type: int


@dataclass
class SkinData:
    data: bytes
    ancestors: list[Chunk]
    skin: Chunk
    vertex_count: int
    positions: list[tuple[float, float, float]]
    num_bones: int
    used_bones: list[int]
    max_weights: int
    indices: list[list[int]]
    weights: list[list[float]]
    jaw_index: int
    head_index: int


def chunks(data: bytes, start: int, end: int):
    offset = start
    while offset + 12 <= end:
        chunk_type, size, _version = struct.unpack_from("<III", data, offset)
        chunk_end = offset + 12 + size
        if chunk_end > end:
            break
        yield Chunk(offset, offset + 12, chunk_end, chunk_type)
        offset = chunk_end


def child(data: bytes, parent: Chunk, chunk_type: int) -> Chunk:
    return next(item for item in chunks(data, parent.content, parent.end) if item.chunk_type == chunk_type)


def hierarchy_indices(data: bytes, frame_list: Chunk) -> tuple[int, int]:
    hierarchy: list[tuple[int, int, int]] = []
    frame_children = list(chunks(data, frame_list.content, frame_list.end))
    for extension in (item for item in frame_children[1:] if item.chunk_type == CHUNK_EXTENSION):
        for plugin in chunks(data, extension.content, extension.end):
            if plugin.chunk_type != PLUGIN_HANIM or plugin.end - plugin.content < 12:
                continue
            _version, _node_id, count = struct.unpack_from("<iii", data, plugin.content)
            if count and plugin.end - plugin.content >= 20 + count * 12:
                hierarchy = [
                    struct.unpack_from("<iii", data, plugin.content + 20 + index * 12)
                    for index in range(count)
                ]
    jaw_index = next(index for node_id, index, _flags in hierarchy if node_id == 8)
    head_index = next(index for node_id, index, _flags in hierarchy if node_id == 5)
    return jaw_index, head_index


def parse_skin(data: bytes) -> SkinData:
    top = next(chunks(data, 0, len(data)))
    if top.chunk_type != CHUNK_CLUMP:
        raise ValueError("DFF не содержит Clump")
    frame_list = child(data, top, CHUNK_FRAME_LIST)
    geometry_list = child(data, top, CHUNK_GEOMETRY_LIST)
    geometry = child(data, geometry_list, CHUNK_GEOMETRY)
    geometry_struct = child(data, geometry, CHUNK_STRUCT)
    extension = child(data, geometry, CHUNK_EXTENSION)
    skin = child(data, extension, PLUGIN_SKIN)

    fmt, triangle_count, vertex_count, _morph_count = struct.unpack_from(
        "<Iiii", data, geometry_struct.content
    )
    position_offset = geometry_struct.content + 16
    if fmt & 0x08:  # prelit
        position_offset += vertex_count * 4
    texture_sets = (fmt >> 16) & 0xFF
    if not texture_sets:
        texture_sets = 2 if fmt & 0x80 else (1 if fmt & 0x04 else 0)
    position_offset += vertex_count * 8 * texture_sets
    position_offset += triangle_count * 8
    position_offset += 24  # morph target header
    positions = [
        struct.unpack_from("<3f", data, position_offset + index * 12)
        for index in range(vertex_count)
    ]

    num_bones, num_used, max_weights, _padding = struct.unpack_from(
        "<BBBB", data, skin.content
    )
    used_start = skin.content + 4
    used_bones = list(data[used_start : used_start + num_used])
    indices_start = used_start + num_used
    raw_indices = data[indices_start : indices_start + vertex_count * 4]
    indices = [list(raw_indices[index * 4 : index * 4 + 4]) for index in range(vertex_count)]
    weights_start = indices_start + vertex_count * 4
    flat_weights = struct.unpack_from(
        "<" + "f" * (vertex_count * 4), data, weights_start
    )
    weights = [list(flat_weights[index * 4 : index * 4 + 4]) for index in range(vertex_count)]
    jaw_index, head_index = hierarchy_indices(data, frame_list)
    return SkinData(
        data=data,
        ancestors=[top, geometry_list, geometry, extension],
        skin=skin,
        vertex_count=vertex_count,
        positions=positions,
        num_bones=num_bones,
        used_bones=used_bones,
        max_weights=max_weights,
        indices=indices,
        weights=weights,
        jaw_index=jaw_index,
        head_index=head_index,
    )


def influence(skin: SkinData, vertex: int, bone: int) -> float:
    return sum(
        skin.weights[vertex][slot]
        for slot in range(4)
        if skin.indices[vertex][slot] == bone
    )


def aligned_positions(donor: SkinData, target: SkinData):
    """Совмещает оригинальную и HD-модель при разных системах осей/масштабе."""
    donor_finite = [point for point in donor.positions if all(math.isfinite(value) for value in point)]
    target_finite = [point for point in target.positions if all(math.isfinite(value) for value in point)]
    donor_ranges = [
        max(point[axis] for point in donor_finite) - min(point[axis] for point in donor_finite)
        for axis in range(3)
    ]
    target_ranges = [
        max(point[axis] for point in target_finite) - min(point[axis] for point in target_finite)
        for axis in range(3)
    ]
    donor_vertical = max(range(3), key=lambda axis: donor_ranges[axis])
    target_vertical = max(range(3), key=lambda axis: target_ranges[axis])

    # В GTA SA встречаются модели с вертикальной осью X и Z; Y остаётся глубиной.
    donor_lateral = next(axis for axis in range(3) if axis not in {donor_vertical, 1})
    target_lateral = next(axis for axis in range(3) if axis not in {target_vertical, 1})
    mapping = {target_vertical: donor_vertical, 1: 1, target_lateral: donor_lateral}

    mapped = [tuple(point[mapping[axis]] for axis in range(3)) for point in donor.positions]
    result = []
    mapped_finite = [point for point in mapped if all(math.isfinite(value) for value in point)]
    donor_bounds = [
        (min(point[axis] for point in mapped_finite), max(point[axis] for point in mapped_finite))
        for axis in range(3)
    ]
    target_bounds = [
        (min(point[axis] for point in target_finite), max(point[axis] for point in target_finite))
        for axis in range(3)
    ]
    for point in mapped:
        transformed = []
        for axis in range(3):
            source_min, source_max = donor_bounds[axis]
            target_min, target_max = target_bounds[axis]
            scale = (target_max - target_min) / max(source_max - source_min, 1e-8)
            transformed.append(target_min + (point[axis] - source_min) * scale)
        result.append(tuple(transformed))
    return result


def build_reference(skin: SkinData, cell_size: float, positions=None):
    grid: dict[tuple[int, int, int], list[tuple[tuple[float, float, float], float]]] = {}
    positions = positions or skin.positions
    for vertex, position in enumerate(positions):
        if not all(math.isfinite(value) for value in position):
            continue
        jaw = influence(skin, vertex, skin.jaw_index)
        head = influence(skin, vertex, skin.head_index)
        if jaw + head <= 1e-5:
            continue
        ratio = jaw / (jaw + head)
        cell = tuple(math.floor(value / cell_size) for value in position)
        grid.setdefault(cell, []).append((position, ratio))
    return grid


def reference_ratio(grid, position, radius: float) -> float:
    if not all(math.isfinite(value) for value in position):
        return 0.0
    cell_size = radius
    base = tuple(math.floor(value / cell_size) for value in position)
    nearest: list[tuple[float, float]] = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for reference, ratio in grid.get(
                    (base[0] + dx, base[1] + dy, base[2] + dz), []
                ):
                    distance_squared = sum(
                        (position[axis] - reference[axis]) ** 2 for axis in range(3)
                    )
                    if distance_squared <= radius * radius:
                        nearest.append((distance_squared, ratio))
    if not nearest:
        return 0.0
    nearest.sort(key=lambda item: item[0])
    nearest = nearest[:4]
    if nearest[0][0] < 1e-12:
        return nearest[0][1]
    weighted_sum = 0.0
    weight_sum = 0.0
    for distance_squared, ratio in nearest:
        weight = 1.0 / max(distance_squared, 1e-12)
        weighted_sum += ratio * weight
        weight_sum += weight
    return weighted_sum / weight_sum


def add_jaw_influence(skin: SkinData, vertex: int, ratio: float) -> bool:
    head_slots = [slot for slot in range(4) if skin.indices[vertex][slot] == skin.head_index]
    if not head_slots:
        return False
    head_slot = head_slots[0]
    head_weight = skin.weights[vertex][head_slot]
    jaw_weight = head_weight * ratio
    if jaw_weight <= 1e-4:
        return False

    empty_slot = next(
        (slot for slot in range(4) if skin.weights[vertex][slot] <= 1e-6), None
    )
    if empty_slot is None:
        candidates = [slot for slot in range(4) if slot != head_slot]
        empty_slot = min(candidates, key=lambda slot: skin.weights[vertex][slot])
        skin.weights[vertex][head_slot] += skin.weights[vertex][empty_slot]

    skin.weights[vertex][head_slot] -= jaw_weight
    skin.indices[vertex][empty_slot] = skin.jaw_index
    skin.weights[vertex][empty_slot] = jaw_weight
    return True


def patched_bytes(target: SkinData, donor: SkinData, radius: float) -> tuple[bytes, int]:
    jaw_already_declared = target.jaw_index in target.used_bones
    if not any(influence(donor, vertex, donor.jaw_index) > 1e-5 for vertex in range(donor.vertex_count)):
        raise ValueError("у оригинальной модели нет весов Jaw")

    donor_positions = aligned_positions(donor, target)
    grid = build_reference(donor, radius, donor_positions)
    changed = 0
    for vertex, position in enumerate(target.positions):
        if influence(target, vertex, target.head_index) <= 1e-5:
            continue
        ratio = reference_ratio(grid, position, radius)
        if ratio > 1e-4 and add_jaw_influence(target, vertex, ratio):
            changed += 1
    if not changed:
        raise ValueError("не найдено подходящих вершин лица")

    original = target.data
    old_used_count = len(target.used_bones)
    new_used = sorted(set(target.used_bones + [target.jaw_index]))
    old_indices_start = target.skin.content + 4 + old_used_count
    old_weights_start = old_indices_start + target.vertex_count * 4
    old_tail_start = old_weights_start + target.vertex_count * 16

    flat_indices = bytes(value for row in target.indices for value in row)
    flat_weights = [value for row in target.weights for value in row]
    payload = bytearray()
    payload.extend(struct.pack("<BBBB", target.num_bones, len(new_used), target.max_weights, 0))
    payload.extend(bytes(new_used))
    payload.extend(flat_indices)
    payload.extend(struct.pack("<" + "f" * len(flat_weights), *flat_weights))
    payload.extend(original[old_tail_start : target.skin.end])

    result = bytearray(original[: target.skin.content])
    result.extend(payload)
    result.extend(original[target.skin.end :])
    delta = len(payload) - (target.skin.end - target.skin.content)
    expected_delta = 0 if jaw_already_declared else 1
    if delta != expected_delta:
        raise AssertionError(f"неожиданное изменение размера: {delta}")

    if delta:
        for ancestor in [target.skin, *target.ancestors]:
            size_offset = ancestor.header + 4
            old_size = struct.unpack_from("<I", result, size_offset)[0]
            struct.pack_into("<I", result, size_offset, old_size + delta)
    return bytes(result), changed


def read_img_entries(img_path: Path):
    handle = img_path.open("rb")
    if handle.read(4) != b"VER2":
        raise ValueError("поддерживается только IMG VER2")
    count = struct.unpack("<I", handle.read(4))[0]
    entries = {}
    for _ in range(count):
        entry = handle.read(32)
        offset = struct.unpack_from("<I", entry)[0] * 2048
        name = entry[8:32].split(b"\0", 1)[0].decode("ascii", "ignore").lower()
        entries[name] = offset
    return handle, entries


def read_img_file(handle, entries, name: str) -> bytes:
    offset = entries[name.lower()]
    handle.seek(offset)
    _chunk_type, size, _version = struct.unpack("<III", handle.read(12))
    handle.seek(offset)
    return handle.read(size + 12)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target_dir", type=Path)
    parser.add_argument("gta3_img", type=Path)
    parser.add_argument("--radius", type=float, default=0.04)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    handle, entries = read_img_entries(args.gta3_img)
    results = []
    for path in sorted(args.target_dir.glob("*.dff")):
        try:
            target = parse_skin(path.read_bytes())
        except (StopIteration, ValueError):
            continue
        existing = sum(
            1
            for vertex in range(target.vertex_count)
            if influence(target, vertex, target.jaw_index) > 1e-5
        )
        if existing:
            continue
        donor_name = path.name.lower()
        if donor_name not in entries:
            results.append((path.name, "пропущен: нет оригинала", 0))
            continue
        try:
            donor = parse_skin(read_img_file(handle, entries, donor_name))
            output, changed = patched_bytes(target, donor, args.radius)
            validation = parse_skin(output)
            verified = sum(
                1
                for vertex in range(validation.vertex_count)
                if influence(validation, vertex, validation.jaw_index) > 1e-5
            )
            if verified != changed or validation.jaw_index not in validation.used_bones:
                raise AssertionError("проверка результата не пройдена")
            if args.apply:
                backup = path.with_suffix(path.suffix + ".before-jaw-fix.bak")
                if backup.exists():
                    raise FileExistsError(f"резервная копия уже существует: {backup}")
                shutil.copy2(path, backup)
                path.write_bytes(output)
            results.append((path.name, "исправлен" if args.apply else "готов", changed))
        except (StopIteration, ValueError) as error:
            results.append((path.name, f"пропущен: {error}", 0))

    for name, status, count in results:
        print(f"{name}: {status}; вершин Jaw={count}")


if __name__ == "__main__":
    main()
