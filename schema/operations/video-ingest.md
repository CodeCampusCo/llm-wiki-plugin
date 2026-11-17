# Video Ingest Playbook

This is a detailed, copy-paste-ready playbook for the LLM agent to follow when ingesting a video or audio source into the wiki. `schema/schema.md` has the high-level contract; this file has the actual commands.

**Scope:** videos from URLs (YouTube, Vimeo, Facebook, Twitter, etc.) and local video/audio files. Produces: a transcript, keyframes, metadata, and a wiki source page.

---

## Prerequisites (check once per session)

```bash
which yt-dlp ffmpeg whisper
# expected: three paths; if any are missing, stop and tell the user
```

If any tool is missing, output:

```
Video ingest requires yt-dlp, ffmpeg, and whisper (or whisper.cpp).
Install on macOS:     brew install yt-dlp ffmpeg whisper-cpp
Install on Ubuntu:    sudo apt install ffmpeg && pipx install yt-dlp
(whisper.cpp: build from source — see https://github.com/ggerganov/whisper.cpp)
```

---

## Variables to set at the start of each ingest

Before running any commands, define and confirm with the user:

```bash
# The source URL (or local path)
URL="https://www.youtube.com/watch?v=..."

# A short kebab-case slug for this video — used in filenames and the wiki page
# Format: YYYY-MM-DD-short-slug  (e.g. 2026-04-11-karpathy-llm-wiki)
SLUG="YYYY-MM-DD-short-slug"

# Where derived artifacts go (inside Tier 2 raw/)
DERIVED="raw/derived/$SLUG"

# Whether to keep the raw video file
# - "archive": keep in archive/videos/ (user opted in)
# - "none":    delete raw video after processing (default, saves space)
KEEP_RAW="none"

# Language hint for Whisper (th, en, ja, ...)
LANG="th"

# Keyframe extraction interval in seconds (default 30)
KEYFRAME_EVERY=30
```

Confirm these with the user before running anything:

> I'll ingest `$URL` as slug `$SLUG`, keeping the raw video: `$KEEP_RAW`, language: `$LANG`, keyframes every `$KEYFRAME_EVERY` seconds. OK?

---

## Step 1 — Create the derived directory

```bash
mkdir -p "$DERIVED/keyframes"
```

---

## Step 2 — Download video + metadata

Download the video at the lowest quality that still gives you usable keyframes (480p is plenty for keyframes — we're not keeping the video long-term in most cases):

```bash
cd "$DERIVED"

yt-dlp \
  -f "bestvideo[height<=480]+bestaudio/best[height<=480]" \
  --write-info-json \
  --write-auto-subs \
  --write-subs \
  --sub-langs "$LANG,en" \
  --convert-subs srt \
  -o "video.%(ext)s" \
  "$URL"
```

Flags explained:

- `-f "bestvideo[height<=480]+bestaudio"` — cap at 480p to save bandwidth and disk.
- `--write-info-json` — saves `video.info.json` with title, author, duration, published date, etc.
- `--write-auto-subs --write-subs` — pull both manual captions (if available, usually higher quality) and auto-generated ones as fallback.
- `--sub-langs "$LANG,en"` — prefer the user's language, then English.
- `--convert-subs srt` — SRT is easier to parse than VTT.

After this step you should have in `$DERIVED/`:

```
video.mp4                 # (or .webm, .mkv)
video.info.json           # metadata
video.{lang}.srt          # captions (if available)
```

---

## Step 3 — Produce the transcript

### Case A: Clean manual captions exist

Check if `video.{lang}.srt` exists and looks clean (not auto-generated):

```bash
ls "$DERIVED"/video.*.srt 2>/dev/null
```

If there's a non-auto SRT, convert it to the wiki's transcript format:

```bash
# Run as a short Python snippet. Shell vars are passed via env so the
# heredoc stays single-quoted (safest — no accidental $-expansion inside Python).
DERIVED="$DERIVED" python3 - <<'PY'
import os, re, pathlib, json

derived = pathlib.Path(os.environ["DERIVED"])
srt = next(derived.glob("video.*.srt"))
lines = srt.read_text().splitlines()

out = ["# Transcript", "", f"Source: {srt.name}", ""]
i = 0
while i < len(lines):
    if re.match(r"\d+$", lines[i]):
        timecode = lines[i+1]
        start = timecode.split(" --> ")[0].split(",")[0]  # HH:MM:SS
        # Collect text lines until blank
        text_lines = []
        i += 2
        while i < len(lines) and lines[i].strip():
            text_lines.append(lines[i])
            i += 1
        text = " ".join(text_lines)
        mm_ss = ":".join(start.split(":")[-2:]) if start.startswith("00:") else start
        out.append(f"**[{mm_ss}]** {text}")
        out.append("")
    i += 1

(derived / "transcript.md").write_text("\n".join(out))
print(f"Wrote {derived/'transcript.md'}")
PY
```

Record `transcript_source: youtube-manual` in metadata.

### Case B: Only auto-captions or no captions → use Whisper

If captions are missing or auto-generated (the file ends in `.{lang}.auto.srt` or doesn't exist), extract audio and run Whisper:

```bash
# Extract audio as 16kHz mono WAV (what whisper.cpp expects)
ffmpeg -i "$DERIVED/video.mp4" \
  -ar 16000 -ac 1 -c:a pcm_s16le \
  "$DERIVED/audio.wav" -y

# Run whisper.cpp (replace with your installation)
whisper "$DERIVED/audio.wav" \
  --language "$LANG" \
  --output_format srt \
  --output_dir "$DERIVED"

# Rename to a predictable name
mv "$DERIVED/audio.srt" "$DERIVED/transcript.srt"

# Delete the large audio file — we don't need it after transcription
rm "$DERIVED/audio.wav"
```

Then convert `transcript.srt` to `transcript.md` using the same Python snippet as Case A, and record `transcript_source: whisper` in metadata.

**For OpenAI API whisper** (if whisper.cpp isn't available):

```bash
# Requires OPENAI_API_KEY
curl https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F model="whisper-1" \
  -F response_format="srt" \
  -F language="$LANG" \
  -F file="@$DERIVED/audio.wav" \
  > "$DERIVED/transcript.srt"
```

---

## Step 4 — Extract keyframes

### Option A: Fixed interval (default)

```bash
ffmpeg -i "$DERIVED/video.mp4" \
  -vf "fps=1/$KEYFRAME_EVERY" \
  -q:v 4 \
  "$DERIVED/keyframes/frame-%04d.jpg" -y
```

This drops one JPEG every `$KEYFRAME_EVERY` seconds, numbered sequentially. For a 10-minute video at 30-second interval you get 20 frames.

Rename frames to include their timestamp:

```bash
DERIVED="$DERIVED" KEYFRAME_EVERY="$KEYFRAME_EVERY" python3 - <<'PY'
import os, pathlib
derived = pathlib.Path(os.environ["DERIVED"]) / "keyframes"
every = int(os.environ["KEYFRAME_EVERY"])
for f in sorted(derived.glob("frame-*.jpg")):
    idx = int(f.stem.split("-")[1]) - 1
    secs = idx * every
    hh = secs // 3600
    mm = (secs % 3600) // 60
    ss = secs % 60
    new_name = f"{hh:02d}-{mm:02d}-{ss:02d}.jpg"
    f.rename(derived / new_name)
PY
```

You should end up with files like `00-00-00.jpg`, `00-00-30.jpg`, `00-01-00.jpg`, ...

### Option B: Scene detection (smarter, optional)

If `scenedetect` is available and the video has distinct scene changes (tutorials, interviews with cutaways, slide decks):

```bash
scenedetect -i "$DERIVED/video.mp4" \
  detect-content \
  save-images -o "$DERIVED/keyframes" \
    --filename '$SCENE_NUMBER-$TIMECODE' \
    --num-images 1
```

---

## Step 5 — Write metadata.json

Extract the important fields from `video.info.json` and write a clean `metadata.json`:

```bash
DERIVED="$DERIVED" LANG="$LANG" KEEP_RAW="$KEEP_RAW" python3 - <<'PY'
import os, json, pathlib, datetime
derived = pathlib.Path(os.environ["DERIVED"])
info = json.loads((derived / "video.info.json").read_text())

meta = {
    "url": info.get("webpage_url"),
    "title": info.get("title"),
    "author": info.get("uploader") or info.get("channel"),
    "author_url": info.get("channel_url") or info.get("uploader_url"),
    "published_date": info.get("upload_date"),  # YYYYMMDD
    "duration_seconds": info.get("duration"),
    "language": os.environ["LANG"],
    "transcript_source": "TO_FILL",  # set to whisper | youtube-auto | youtube-manual
    "ingest_date": datetime.date.today().isoformat(),
    "has_raw_archive": os.environ["KEEP_RAW"] == "archive",
}
(derived / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
print(json.dumps(meta, indent=2, ensure_ascii=False))
PY
```

---

## Step 6 — Move or delete the raw video

Based on `$KEEP_RAW`:

```bash
if [ "$KEEP_RAW" = "archive" ]; then
  # Confirm archive tier is mounted before moving
  if [ -d "archive/videos" ]; then
    mv "$DERIVED/video.mp4" "archive/videos/$SLUG.mp4"
    echo "Raw video moved to archive/videos/$SLUG.mp4"
  else
    echo "WARNING: archive/videos/ not found on this machine."
    echo "Leaving raw video at $DERIVED/video.mp4"
    echo "Please move manually when the archive drive is mounted."
  fi
elif [ "$KEEP_RAW" = "none" ]; then
  rm "$DERIVED/video.mp4" "$DERIVED/video.info.json"
  rm -f "$DERIVED"/video.*.srt
  echo "Raw video deleted. Derived artifacts kept in $DERIVED"
fi
```

---

## Step 7 — Read the transcript and view keyframes

This is where you (the LLM) actually start reading. Before this point you were just a shell orchestrator.

1. Read `$DERIVED/transcript.md` in full. For videos longer than 20 minutes, read in chunks.
2. View 3–5 keyframes. Prioritize: the first frame (usually a title card), frames near chapter markers, and frames the transcript explicitly references (e.g. "as shown in this diagram").
3. If the transcript has obviously garbled sections (nonsense words, repeated phrases, untranslated foreign names), flag them — auto-captions and Whisper both make mistakes.

---

## Step 8 — Discuss with the user, then write the wiki page

Follow the standard Ingest protocol from `schema/schema.md`:

1. Summarize the video to the user and ask for angle/emphasis.
2. Propose which wiki pages to create or update.
3. Create `wiki/sources/$SLUG.md` using the **video source skeleton** in `schema/schema.md`.
4. Embed 3–8 keyframes with timestamp captions. Use relative paths:
   ```markdown
   ![Slide: LLM Wiki architecture | 01:30](../../raw/derived/2026-04-11-example/keyframes/00-01-30.jpg)
   ```
5. Quote transcript lines with `mm:ss` timestamps:
   ```markdown
   > "The wiki is compiled once and then kept current, not re-derived on every query." — 03:42
   ```
6. Update `wiki/index.md` and append to `wiki/log.md`.
7. Create/update concept and entity pages as needed.

---

## Final state check

After a successful video ingest, the directory should look like:

```
raw/derived/2026-04-11-example/
├── transcript.md                # the LLM-readable transcript
├── metadata.json                # url, author, duration, etc.
└── keyframes/
    ├── 00-00-00.jpg
    ├── 00-00-30.jpg
    ├── 00-01-00.jpg
    └── ...

wiki/sources/2026-04-11-example.md   # the wiki page
wiki/log.md                          # appended ingest entry
wiki/index.md                        # updated with new page
```

And depending on `$KEEP_RAW`:

```
archive/videos/2026-04-11-example.mp4   # (if KEEP_RAW=archive)
```

---

## Troubleshooting

**`yt-dlp` says the video is unavailable or blocked.**
Try `--cookies-from-browser chrome` (or `firefox`) to use your browser's session. If it's a private Facebook or LinkedIn post, the user will need to download it manually and provide the file as a local path instead of a URL.

**Whisper produces garbage output.**
Check `$LANG` was set correctly. For Thai, use `th`. For mixed Thai-English content, try `en` first and fall back to `th` if proper nouns get mangled.

**ffmpeg extracts keyframes that are all black or blurry.**
The video might start with a black title card. Either wait longer before the first frame (`-ss 5 -i video.mp4` to skip the first 5 seconds) or switch to scene detection.

**Disk fills up.**
The raw video is usually the biggest file. Make sure step 6 runs. If you're batch-ingesting, set `KEEP_RAW=none` by default.

**The transcript is huge (> 50 KB).**
That's fine for reading, but don't quote more than ~1 KB into a wiki page. Link to the transcript file instead: `See [transcript](../../raw/derived/{slug}/transcript.md) for full context.`
