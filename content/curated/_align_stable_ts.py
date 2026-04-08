"""
Use stable-ts to get sub-word-accurate timestamps via forced alignment.
Output: JSON file in the same shape openai-whisper produces (segments + words).

Usage: python _align_stable_ts.py <audio.mp4> <out.json> [model]
"""
import sys
import json
from pathlib import Path
import stable_whisper

audio = sys.argv[1]
out   = Path(sys.argv[2])
model_name = sys.argv[3] if len(sys.argv) > 3 else "small.en"

print(f"loading model {model_name}...")
model = stable_whisper.load_model(model_name)

print(f"transcribing {audio} (this also runs forced alignment)...")
result = model.transcribe(
    audio,
    word_timestamps=True,
    regroup=False,           # keep raw word boundaries
    suppress_silence=True,   # snap word edges to actual speech
    vad=True,                # voice-activity detection for tighter edges
)

# Re-align using stable_ts's dedicated alignment pass for tightest timing
print("running explicit forced alignment pass...")
aligned = model.align(
    audio,
    text=result,             # supply prior transcription
    language="en",
    original_split=True,
)

# Convert stable-ts WhisperResult to whisper-style dict
data = aligned.to_dict()
out.write_text(json.dumps(data, indent=2), encoding="utf-8")
print(f"wrote {out}  ({len(data.get('segments', []))} segments)")
