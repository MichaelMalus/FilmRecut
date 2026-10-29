# FilmRecut

Detect the shots in films, then cut every shot from a set of films together in
descending order of length. Needs only Python 3.9+ and `ffmpeg`/`ffprobe` on PATH.

```sh
# 1. Shot boundaries for one video (JSON: source, start, end, duration)
python3 -m filmrecut shots film.mp4

# 2. Recut several films, longest shot first
python3 -m filmrecut recut a.mp4 b.mkv c.mov -o recut.mp4
```

Options: `--threshold` (scene-change score 0–1 that counts as a cut, default 0.3),
`--min-shot` (merge cuts closer than this many seconds, default 0.25),
`--size 1280x720`, `--fps 24`, `--ascending`.

Shot detection uses ffmpeg's `scene` score, which catches hard cuts well but
misses dissolves/fades and cuts between frames of similar brightness. Every shot
is re-encoded to a common size, frame rate and pixel format before concatenation
(sources without audio get silence), so mixed sources join cleanly.
