"""Cut shots from many films together in descending order of length."""
import os
import subprocess
import tempfile

from .shots import detect_shots


def collect_shots(paths, threshold=0.3, min_shot=0.25):
    shots = []
    for p in paths:
        shots.extend(detect_shots(p, threshold, min_shot))
    return sorted(shots, key=lambda s: s.duration, reverse=True)


def has_audio(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
         "stream=index", "-of", "csv=p=0", path],
        check=True, capture_output=True, text=True).stdout
    return bool(out.strip())


def render(shots, output, width=1280, height=720, fps=24):
    """Re-encode each shot to a common format, then concatenate."""
    vf = (f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
          f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},format=yuv420p")
    with tempfile.TemporaryDirectory() as tmp:
        parts = []
        for i, s in enumerate(shots):
            part = os.path.join(tmp, f"{i:06d}.mp4")
            # Sources without audio get silence so every part has the same streams.
            audio = "0:a:0" if has_audio(s.source) else "1:a"
            subprocess.run(
                ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                 "-ss", f"{s.start:.3f}", "-i", s.source,
                 "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                 "-map", "0:v:0", "-map", audio, "-t", f"{s.duration:.3f}",
                 "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                 "-c:a", "aac", "-ar", "48000", "-ac", "2", part],
                check=True)
            parts.append(part)
        listfile = os.path.join(tmp, "list.txt")
        with open(listfile, "w") as f:
            f.writelines(f"file '{p}'\n" for p in parts)
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
             "-safe", "0", "-i", listfile, "-c", "copy", output], check=True)
