import os
import zipfile
from pathlib import Path
import shutil

def build_addon():
    # Konfiguracja ścieżek
    project_root = Path(__file__).parent.parent
    addon_src = project_root / "blender_addon"
    output_dir = project_root / "outputs"
    zip_name = "blender_ai_mcp.zip"
    zip_path = output_dir / zip_name

    # Upewnij się, że katalog outputs istnieje
    output_dir.mkdir(exist_ok=True)

    # Usuń stary plik ZIP jeśli istnieje
    if zip_path.exists():
        os.remove(zip_path)
        print(f"Removed old build: {zip_path}")

    print(f"Building addon from: {addon_src}")
    
    # Lista plików/katalogów do zignorowania
    ignore_patterns = {
        "__pycache__",
        ".DS_Store",
        "*.pyc"
    }

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(addon_src):
            # Filtrowanie katalogów (modyfikacja dirs in-place)
            dirs[:] = [d for d in dirs if d not in ignore_patterns]
            
            for file in files:
                if file in ignore_patterns:
                    continue
                if file.endswith(".pyc"):
                    continue
                    
                file_path = Path(root) / file
                # Relatywna ścieżka wewnątrz ZIPa (np. blender_ai_mcp/__init__.py)
                # Ważne: Struktura w ZIP musi zaczynać się od nazwy folderu addona, aby Blender poprawnie go rozpakował
                archive_name = f"blender_ai_mcp/{file_path.relative_to(addon_src)}"
                
                zipf.write(file_path, archive_name)
                print(f"  Added: {archive_name}")

    print(f"\n✅ Build successful: {zip_path}")
    print(f"Size: {zip_path.stat().st_size / 1024:.2f} KB")

if __name__ == "__main__":
    build_addon()
