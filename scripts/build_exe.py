"""Build a standalone Mod Studio folder that runs without Python installed."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

from build_release import ROOT, VERSION, sha256

NAME = "eFootball_Mod_Studio"
DLL_PATH = "native/dxgi.dll"
WORK = ROOT / ".workspace" / "pyinstaller"
OUTPUT = ROOT / "dist" / NAME
ROOT_FILES = (
    "CHANGELOG.md",
    "Disinstalla_Mod_Studio.bat",
    "Installa_Mod_Studio_in_eFootball.bat",
    "LICENSE",
    "README.md",
    "Riavvia_eFootball_con_Mod_Studio.bat",
    "sider.ini",
)


def main() -> int:
    built_dll = ROOT / "rust_sider" / "target" / "release" / "dxgi.dll"
    if not built_dll.is_file():
        raise FileNotFoundError("Build rust_sider before packaging the executable")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--windowed",
            "--name",
            NAME,
            "--paths",
            str(ROOT),
            "--collect-data",
            "qtawesome",
            "--collect-all",
            "cricodecs",
            "--distpath",
            str(ROOT / "dist"),
            "--workpath",
            str(WORK / "build"),
            "--specpath",
            str(WORK),
            str(ROOT / "scripts" / "mod_studio_entry.py"),
        ],
        check=True,
    )

    for filename in ROOT_FILES:
        shutil.copy2(ROOT / filename, OUTPUT / filename)
    # Never place dxgi.dll beside the executable: Windows would load it into Mod Studio itself.
    (OUTPUT / "native").mkdir(exist_ok=True)
    shutil.copy2(built_dll, OUTPUT / DLL_PATH)
    shutil.copytree(ROOT / "bin", OUTPUT / "bin", dirs_exist_ok=True)
    (OUTPUT / "scripts").mkdir(exist_ok=True)
    shutil.copy2(ROOT / "scripts" / "resolve_game_dir.bat", OUTPUT / "scripts")

    manifest = {
        "name": "eFootball Mod Studio",
        "version": VERSION,
        "native_core": {"file": DLL_PATH, "sha256": sha256(OUTPUT / DLL_PATH)},
    }
    (OUTPUT / "release-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Created {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
