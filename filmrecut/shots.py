"""Shot boundary detection using ffmpeg's scene-change score."""
import json
import re
import subprocess
from dataclasses import dataclass, asdict


@dataclass
class Shot:
    source: str
    start: float
    end: float

    @property
    def duration(self):
        return self.end - self.start


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path],
        check=True, capture_output=True, text=True).stdout
    return float(json.loads(out)["format"]["duration"])


def detect_cuts(path, threshold=0.3):
    """Return timestamps (seconds) where ffmpeg's scene score exceeds threshold."""
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an",
         "-vf", f"select='gt(scene,{threshold})',showinfo",
         "-f", "null", "-"],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-2000:])
    return [float(m) for m in re.findall(r"pts_time:([\d.]+)", proc.stderr)]


def detect_shots(path, threshold=0.3, min_shot=0.25):
    """Split a video into shots. Cuts closer than min_shot seconds are merged."""
    duration = probe_duration(path)
    bounds = [0.0]
    for t in detect_cuts(path, threshold):
        if t - bounds[-1] >= min_shot and duration - t >= min_shot:
            bounds.append(t)
    bounds.append(duration)
    return [Shot(path, a, b) for a, b in zip(bounds, bounds[1:])]


def shots_to_json(shots):
    return json.dumps([asdict(s) | {"duration": s.duration} for s in shots], indent=2)
