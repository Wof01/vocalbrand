"""Optional FFmpeg bootstrap helper.

This keeps deployment resilient: if FFmpeg isn't present and AUTO_FFMPEG=1
we attempt a lightweight download of a static build (Windows only for now).
Designed to be SAFE: will not overwrite existing binaries; silent failures.

Usage:
    from utils.ffmpeg_auto import attempt_auto_ffmpeg
    attempt_auto_ffmpeg()

Environment flags:
    AUTO_FFMPEG=1  -> enable auto download
    FFMPEG_DIR     -> preferred target directory (default: ./ffmpeg)

This is a minimal scaffold; it avoids heavy dependencies.
"""
from __future__ import annotations
import os, sys, zipfile, tempfile, urllib.request
from pathlib import Path

FFMPEG_RELEASE_URL = (
    "https://github.com/GyanD/codexffmpeg/releases/download/8.0/ffmpeg-8.0-essentials_build.zip"
)


def _already_present() -> bool:
    # Simple presence check in PATH or common dirs
    import shutil  # local import
    candidates = [
        os.getenv("FFMPEG_BINARY"),
        shutil.which("ffmpeg"),
        str(Path(os.getcwd()) / "ffmpeg" / "bin" / "ffmpeg.exe"),  # Windows
        str(Path(os.getcwd()) / "ffmpeg" / "bin" / "ffmpeg"),      # Linux
    ]
    return any(p and os.path.exists(p) for p in candidates)


def attempt_auto_ffmpeg() -> None:
    if os.getenv("AUTO_FFMPEG") != "1":
        return
    try:
        import shutil  # local import to keep top small
        if _already_present():
            return
        target_root = Path(os.getenv("FFMPEG_DIR") or (Path(os.getcwd()) / "ffmpeg"))
        bin_dir = target_root / "bin"
        if (bin_dir / "ffmpeg.exe").exists():
            return
        target_root.mkdir(parents=True, exist_ok=True)

        # Download to temp
        with tempfile.TemporaryDirectory() as td:
            zip_path = Path(td) / "ffmpeg.zip"
            urllib.request.urlretrieve(FFMPEG_RELEASE_URL, zip_path)  # nosec - controlled URL
            with zipfile.ZipFile(zip_path, "r") as zf:
                # Extract only bin/*ffmpeg* ffprobe etc.
                for member in zf.namelist():
                    lower = member.lower()
                    if "bin/ffmpeg" in lower or "bin/ffprobe" in lower:
                        zf.extract(member, td)
                # Move discovered bin files
                for exe in ("ffmpeg.exe", "ffprobe.exe"):
                    found = list(Path(td).rglob(exe))
                    if found:
                        bin_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(found[0], bin_dir / exe)
        # Set env vars for current process (helps pydub resolution)
        os.environ.setdefault("FFMPEG_BINARY", str(bin_dir / "ffmpeg.exe"))
        os.environ.setdefault("FFPROBE_BINARY", str(bin_dir / "ffprobe.exe"))
    except Exception:
        # Silent fail: rely on manual installation; no hard crash
        return
