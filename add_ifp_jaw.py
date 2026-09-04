"""Add a moving GTA San Andreas Jaw track to ANP3 animations."""

from __future__ import annotations

import argparse
import math
import os
import shutil
import struct
from dataclasses import dataclass
from pathlib import Path

KEY_SIZES = {1: 20, 2: 20, 3: 10, 4: 16}


@dataclass
class Track:
    name: str
    start: int
    end: int
    key_type: int
    key_count: int
    hierarchy_id: int


@dataclass
class Animation:
    name: str
    start: int
    end: int
    tracks: list[Track]


def read_name(data: bytes, offset: int) -> str:
    raw = data[offset : offset + 24]
    if len(raw) != 24 or b"\0" not in raw:
        raise ValueError(f"invalid name at {offset:#x}")
    return raw.split(b"\0", 1)[0].decode("ascii")


def parse_ifp(data: bytes) -> list[Animation]:
    if data[:4] != b"ANP3":
        raise ValueError("only ANP3 IFP files are supported")
    if struct.unpack_from("<I", data, 4)[0] != len(data) - 8:
        raise ValueError("invalid ANP3 package size")

    position = 36
    animations = []
    for _ in range(struct.unpack_from("<I", data, 32)[0]):
        animation_start = position
        animation_name = read_name(data, position)
        track_count, frame_data_size = struct.unpack_from("<II", data, position + 24)
        position += 36
        tracks = []
        for _ in range(track_count):
            track_start = position
            track_name = read_name(data, position)
            key_type, key_count, hierarchy_id = struct.unpack_from(
                "<III", data, position + 24
            )
            if key_type not in KEY_SIZES:
                raise ValueError(
                    f"unsupported key type {key_type} in {animation_name}/{track_name}"
                )
            position += 36 + key_count * KEY_SIZES[key_type]
            if position > len(data):
                raise ValueError(f"truncated track {animation_name}/{track_name}")
            tracks.append(
                Track(
                    track_name,
                    track_start,
                    position,
                    key_type,
                    key_count,
                    hierarchy_id,
                )
            )

        actual_frame_size = sum(track.end - track.start - 36 for track in tracks)
        if actual_frame_size != frame_data_size:
            raise ValueError(f"frame data size mismatch in {animation_name}")
        animations.append(Animation(animation_name, animation_start, position, tracks))

    if position != len(data):
        raise ValueError(f"unexpected trailing data at {position:#x}")
    return animations


def key_time(data: bytes, track: Track, index: int) -> int:
    key_size = KEY_SIZES[track.key_type]
    return struct.unpack_from("<H", data, track.start + 36 + index * key_size + 8)[0]


def animation_end(data: bytes, animation: Animation) -> int:
    return max(
        key_time(data, track, track.key_count - 1)
        for track in animation.tracks
        if track.key_count
    )


def jaw_track(data: bytes, donor: Track, target_end: int) -> bytes:
    if donor.key_type != 3 or donor.hierarchy_id != 8:
        raise ValueError("the donor Jaw must have key type 3 and hierarchy ID 8")
    if target_end < 1:
        raise ValueError("the target animation is too short for moving Jaw keys")

    frames = [
        data[donor.start + 36 + index * 10 : donor.start + 46 + index * 10]
        for index in range(donor.key_count)
    ]
    times = [struct.unpack_from("<H", frame, 8)[0] for frame in frames]
    cycle_end = times[-1]
    if cycle_end < 1:
        raise ValueError("the donor Jaw has zero duration")

    output = []
    if target_end < cycle_end:
        # Compress the complete open/close motion instead of copying a static
        # prefix from the donor into short facial animations.
        key_count = min(target_end + 1, donor.key_count)
        for index in range(key_count):
            output_time = round(target_end * index / (key_count - 1))
            source_time = round(cycle_end * index / (key_count - 1))
            source_index = min(
                range(len(times)), key=lambda item: abs(times[item] - source_time)
            )
            frame = bytearray(frames[source_index])
            struct.pack_into("<H", frame, 8, output_time)
            output.append(bytes(frame))
    else:
        for cycle_start in range(0, target_end + 1, cycle_end):
            for frame, source_time in zip(frames, times):
                output_time = cycle_start + source_time
                if output_time > target_end:
                    break
                if output and output_time == struct.unpack_from("<H", output[-1], 8)[0]:
                    continue
                updated = bytearray(frame)
                struct.pack_into("<H", updated, 8, output_time)
                output.append(bytes(updated))
        if struct.unpack_from("<H", output[-1], 8)[0] != target_end:
            source_time = target_end % cycle_end
            source_index = min(
                range(len(times)), key=lambda item: abs(times[item] - source_time)
            )
            frame = bytearray(frames[source_index])
            struct.pack_into("<H", frame, 8, target_end)
            output.append(bytes(frame))

    header = bytearray(data[donor.start : donor.start + 36])
    struct.pack_into("<I", header, 28, len(output))
    return bytes(header) + b"".join(output)


def quaternion_angle(first: tuple[int, ...], current: tuple[int, ...]) -> float:
    first_length = math.sqrt(sum(value * value for value in first))
    current_length = math.sqrt(sum(value * value for value in current))
    dot = abs(
        sum(left * right for left, right in zip(first, current))
        / (first_length * current_length)
    )
    return math.degrees(2 * math.acos(max(-1.0, min(1.0, dot))))


def apply_jaw(
    input_data: bytes,
    donor_data: bytes,
    animation_names: set[str],
    donor_animation_name: str,
) -> tuple[bytes, list[tuple[str, int, int, float]]]:
    donor_animation = next(
        (
            animation
            for animation in parse_ifp(donor_data)
            if animation.name.lower() == donor_animation_name.lower()
        ),
        None,
    )
    if donor_animation is None:
        raise ValueError(f"donor animation not found: {donor_animation_name}")
    donor = next(
        (
            track
            for track in donor_animation.tracks
            if track.name.strip().lower() == "jaw"
            and track.key_type == 3
            and track.hierarchy_id == 8
        ),
        None,
    )
    if donor is None:
        raise ValueError(f"moving Jaw not found in {donor_animation_name}")

    animations = parse_ifp(input_data)
    selected = [
        animation
        for animation in animations
        if animation.name.lower() in animation_names
    ]
    found = {animation.name.lower() for animation in selected}
    if found != animation_names:
        raise ValueError(f"animations not found: {', '.join(sorted(animation_names - found))}")

    output = bytearray(input_data)
    expected = {}
    for animation in reversed(selected):
        target_end = animation_end(input_data, animation)
        jaw = jaw_track(donor_data, donor, target_end)
        body_tracks = [
            input_data[track.start : track.end]
            for track in animation.tracks
            if track.name.strip().lower() != "jaw"
        ]
        replacement = b"".join(body_tracks) + jaw
        output[animation.start + 36 : animation.end] = replacement
        struct.pack_into("<I", output, animation.start + 24, len(body_tracks) + 1)
        struct.pack_into(
            "<I",
            output,
            animation.start + 28,
            sum(len(track) - 36 for track in body_tracks) + len(jaw) - 36,
        )
        expected[animation.name.lower()] = target_end

    struct.pack_into("<I", output, 4, len(output) - 8)
    updated = bytes(output)
    report = []
    for animation in parse_ifp(updated):
        if animation.name.lower() not in animation_names:
            continue
        jaws = [
            track for track in animation.tracks if track.name.strip().lower() == "jaw"
        ]
        if len(jaws) != 1:
            raise ValueError(f"Jaw verification failed in {animation.name}")
        jaw = jaws[0]
        times = [key_time(updated, jaw, index) for index in range(jaw.key_count)]
        quaternions = [
            struct.unpack_from("<hhhh", updated, jaw.start + 36 + index * 10)
            for index in range(jaw.key_count)
        ]
        amplitude = max(
            quaternion_angle(quaternions[0], quaternion)
            for quaternion in quaternions
        )
        if (
            jaw.key_type != 3
            or jaw.hierarchy_id != 8
            or animation.tracks[-1] is not jaw
            or times != sorted(times)
            or times[-1] != expected[animation.name.lower()]
            or amplitude < 0.5
        ):
            raise ValueError(f"moving Jaw verification failed in {animation.name}")
        report.append((animation.name, jaw.key_count, times[-1], amplitude))
    return updated, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("donor_ifp", type=Path, help="IFP containing IDLE_chat/Jaw")
    parser.add_argument("input_ifp", type=Path, help="IFP to modify")
    parser.add_argument("output_ifp", type=Path, help="new IFP path")
    parser.add_argument("animations", nargs="+", help="exact animation names")
    parser.add_argument("--donor-animation", default="IDLE_chat")
    parser.add_argument("--in-place", action="store_true")
    args = parser.parse_args()

    if args.output_ifp.resolve() == args.input_ifp.resolve() and not args.in_place:
        parser.error("use --in-place to overwrite input_ifp")
    input_data = args.input_ifp.read_bytes()
    updated, report = apply_jaw(
        input_data,
        args.donor_ifp.read_bytes(),
        {name.lower() for name in args.animations},
        args.donor_animation,
    )

    if args.in_place:
        backup = args.input_ifp.with_suffix(args.input_ifp.suffix + ".bak")
        if not backup.exists():
            shutil.copy2(args.input_ifp, backup)
    temporary = args.output_ifp.with_suffix(args.output_ifp.suffix + ".tmp")
    temporary.write_bytes(updated)
    os.replace(temporary, args.output_ifp)
    for name, keys, end_time, amplitude in report:
        print(
            f"{name}: Jaw keys={keys}, end={end_time}, amplitude={amplitude:.2f} degrees"
        )


if __name__ == "__main__":
    main()
