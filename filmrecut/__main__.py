import argparse

from .recut import collect_shots, render
from .shots import detect_shots, shots_to_json


def main():
    ap = argparse.ArgumentParser(prog="filmrecut")
    ap.add_argument("--threshold", type=float, default=0.3,
                    help="scene-change score (0-1) that counts as a cut")
    ap.add_argument("--min-shot", type=float, default=0.25,
                    help="ignore cuts closer together than this (seconds)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("shots", help="print detected shots as JSON")
    d.add_argument("video")
    r = sub.add_parser("recut", help="cut shots from films together, longest first")
    r.add_argument("videos", nargs="+")
    r.add_argument("-o", "--output", required=True)
    r.add_argument("--size", default="1280x720")
    r.add_argument("--fps", type=float, default=24)
    r.add_argument("--ascending", action="store_true")
    a = ap.parse_args()

    if a.cmd == "shots":
        print(shots_to_json(detect_shots(a.video, a.threshold, a.min_shot)))
    else:
        shots = collect_shots(a.videos, a.threshold, a.min_shot)
        if a.ascending:
            shots.reverse()
        w, h = map(int, a.size.split("x"))
        render(shots, a.output, w, h, a.fps)
        print(f"wrote {len(shots)} shots to {a.output}")


if __name__ == "__main__":
    main()
