#!/usr/bin/env python3
"""
news_video_generator.py

One-command English news video generator.

Input:
    - a complete English news article, either as a string or a .txt file.

Output:
    - output/news_video.mp4

Pipeline:
    1. Ollama/Qwen turns the article into a broadcast-style script + scene prompts.
    2. Kokoro-82M creates the complete English news-reader voice-over.
    3. LTX-Video generates short visual clips for each scene.
    4. FFmpeg trims/loops those clips to match the narration duration.
    5. FFmpeg combines visuals + narration + subtitles into the final MP4.

Important:
    - This is designed for local/free operation. No per-video API is required.
    - LTX-Video is GPU-heavy. A CUDA GPU with ~10 GB+ VRAM is a practical starting point
      for the current LTX-Video pipeline; more VRAM gives a much better experience.
    - The script does NOT fabricate factual claims: the article is preserved as the source.
      The LLM is instructed to improve broadcast wording without adding facts.

Windows example:
    python news_video_generator.py --article article.txt

Or:
    python news_video_generator.py --text "India's economy ..."

Prerequisites:
    - Python 3.11/3.12
    - FFmpeg on PATH
    - Ollama on PATH, with a model such as qwen2.5:7b
    - Kokoro installed
    - CUDA PyTorch + Diffusers
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
import torch

# ---------------------------- Configuration ----------------------------

OLLAMA_MODEL = os.environ.get("NEWS_OLLAMA_MODEL", "qwen2.5:7b")
LTX_MODEL = os.environ.get("NEWS_LTX_MODEL", "Lightricks/LTX-Video")

# Kokoro English voices. Change to bm_fable / am_michael for a male presenter.
KOKORO_VOICE = os.environ.get("NEWS_KOKORO_VOICE", "af_heart")
KOKORO_LANG = "a"  # English

FPS = 24
SCENE_SECONDS = 5
WIDTH = 704
HEIGHT = 480
LTX_STEPS = 30

OUTPUT_DIR = Path("output")
WORK_DIR = Path("news_video_work")

# ---------------------------- Utilities ----------------------------

def run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    print("\n$", " ".join(str(x) for x in cmd))
    return subprocess.run(
        cmd,
        check=check,
        text=True,
        capture_output=capture,
    )

def require_command(name: str):
    if shutil.which(name) is None:
        raise RuntimeError(
            f"'{name}' was not found on PATH. Install it and restart the terminal."
        )

def read_article(args) -> str:
    if args.article:
        path = Path(args.article)
        if not path.exists():
            raise FileNotFoundError(f"Article file not found: {path}")
        text = path.read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        print("Paste the complete article. Finish input with Ctrl+Z then Enter on Windows.")
        text = sys.stdin.read()

    text = re.sub(r"\s+", " ", text).strip()
    if len(text) < 80:
        raise ValueError("The article is too short. Please provide the complete article.")
    return text

# ---------------------------- Ollama planning ----------------------------

def ollama_generate(prompt: str) -> str:
    # Ollama's CLI is intentionally used so the script has no Python SDK dependency.
    p = run(
        ["ollama", "run", OLLAMA_MODEL, prompt],
        capture=True,
    )
    return p.stdout.strip()

def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)

    # Find the first JSON object if the model added commentary.
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]

    return json.loads(text)

def create_plan(article: str) -> dict[str, Any]:
    prompt = f"""
You are the senior producer of an English television news channel.

Convert the supplied article into a factual broadcast package.

RULES:
- Preserve all facts from the source article.
- Do not invent names, numbers, quotes, dates, locations, events or causes.
- Do not add outside facts.
- Rewrite only for natural spoken English.
- The narration should sound like a professional neutral news reader.
- Keep the full informational substance of the article.
- Use concise sentences suitable for speech.
- Create 1 scene for roughly every 45-80 spoken words.
- Each scene must have a visual prompt describing realistic broadcast footage.
- Do NOT put text, captions, logos, watermarks or fake newspaper headlines inside generated visuals.
- Visual prompts must describe things that can be safely represented visually.
- Return JSON only.

JSON format:
{{
  "headline": "short headline",
  "narration": "complete spoken script",
  "scenes": [
    {{
      "id": 1,
      "narration": "the portion of narration represented by this scene",
      "visual_prompt": "realistic cinematic news footage prompt"
    }}
  ]
}}

SOURCE ARTICLE:
{article}
"""
    raw = ollama_generate(prompt)
    plan = extract_json(raw)

    if not plan.get("narration") or not plan.get("scenes"):
        raise RuntimeError("Ollama returned an incomplete news plan.")

    # Sanity check that the article wasn't silently replaced by a tiny summary.
    if len(plan["narration"].split()) < max(50, int(len(article.split()) * 0.35)):
        print("Warning: narration is much shorter than the source article.")
        print("The model may have summarized instead of preserving the full article.")

    return plan

# ---------------------------- Kokoro TTS ----------------------------

def make_voiceover(narration: str, output_wav: Path):
    try:
        from kokoro import KPipeline
    except ImportError as e:
        raise RuntimeError(
            "Kokoro is not installed. Install it with: pip install kokoro>=0.9.4 soundfile"
        ) from e

    print("\nGenerating English news-reader voice with Kokoro...")
    pipeline = KPipeline(lang_code=KOKORO_LANG)

    chunks = []
    sample_rate = 24000

    # Kokoro can process long text, but chunks are safer for long articles.
    sentences = re.split(r"(?<=[.!?])\s+", narration)
    current = ""
    for sentence in sentences:
        if not sentence:
            continue
        if len(current) + len(sentence) > 900:
            if current:
                chunks.append(current)
            current = sentence
        else:
            current = (current + " " + sentence).strip()
    if current:
        chunks.append(current)

    all_audio = []
    for i, chunk in enumerate(chunks, 1):
        print(f"  TTS chunk {i}/{len(chunks)}")
        generator = pipeline(chunk, voice=KOKORO_VOICE)
        for _, _, audio in generator:
            all_audio.append(np.asarray(audio, dtype=np.float32))

    if not all_audio:
        raise RuntimeError("Kokoro did not generate any audio.")

    audio = np.concatenate(all_audio)
    sf.write(str(output_wav), audio, sample_rate)

    duration = len(audio) / sample_rate
    print(f"Voice-over duration: {duration:.1f} seconds")
    return duration

# ---------------------------- LTX video generation ----------------------------

def load_ltx():
    from diffusers import LTXPipeline
    print("\nLoading LTX-Video...")
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    pipe = LTXPipeline.from_pretrained(
        LTX_MODEL,
        torch_dtype=dtype,
    )

    if torch.cuda.is_available():
        pipe.to("cuda")
    else:
        print("WARNING: LTX-Video on CPU will be extremely slow.")
        pipe.to("cpu")

    return pipe

def generate_ltx_clip(pipe, prompt: str, output_path: Path):
    negative = (
        "worst quality, blurry, jittery, distorted, malformed people, "
        "extra fingers, text, subtitles, captions, watermark, logo, "
        "cartoon, illustration, low resolution"
    )

    frames = max(25, int(SCENE_SECONDS * FPS) + 1)

    result = pipe(
        prompt=prompt,
        negative_prompt=negative,
        width=WIDTH,
        height=HEIGHT,
        num_frames=frames,
        num_inference_steps=LTX_STEPS,
        guidance_scale=5.0,
    )

    from diffusers.utils import export_to_video
    export_to_video(result.frames[0], str(output_path), fps=FPS)

# ---------------------------- FFmpeg helpers ----------------------------

def media_duration(path: Path) -> float:
    p = run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture=True,
    )
    return float(p.stdout.strip())

def make_srt(plan: dict[str, Any], total_duration: float, output_srt: Path):
    # Allocate scene durations proportional to their narration word counts.
    scenes = plan["scenes"]
    counts = [max(1, len(s["narration"].split())) for s in scenes]
    total_words = sum(counts)

    def timestamp(seconds: float) -> str:
        ms = int(round(seconds * 1000))
        h = ms // 3600000
        ms %= 3600000
        m = ms // 60000
        ms %= 60000
        s = ms // 1000
        ms %= 1000
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    current = 0.0
    lines = []
    for i, scene in enumerate(scenes, 1):
        dur = total_duration * counts[i - 1] / total_words
        start = current
        end = total_duration if i == len(scenes) else current + dur
        lines.append(str(i))
        lines.append(f"{timestamp(start)} --> {timestamp(end)}")
        lines.append(scene["narration"].strip())
        lines.append("")
        current = end

    output_srt.write_text("\n".join(lines), encoding="utf-8")

def build_visual_track(
    clips: list[Path],
    target_duration: float,
    output_visual: Path,
):
    if not clips:
        raise RuntimeError("No generated visual clips.")

    # Each scene clip is looped/trimmed to the target duration of the whole article.
    # FFmpeg's concat demuxer joins them without re-encoding.
    concat_file = WORK_DIR / "concat.txt"
    with concat_file.open("w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve().as_posix()}'\n")

    joined = WORK_DIR / "joined.mp4"
    run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-t", str(target_duration),
            "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
                   f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2",
            "-an",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(joined),
        ]
    )

    actual = media_duration(joined)
    if actual < target_duration - 0.25:
        # Loop the complete visual track if the article narration is longer.
        run(
            [
                "ffmpeg", "-y",
                "-stream_loop", "-1",
                "-i", str(joined),
                "-t", str(target_duration),
                "-an",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                str(output_visual),
            ]
        )
    else:
        shutil.copy2(joined, output_visual)

def mux_final(visual: Path, voice: Path, srt: Path, output: Path):
    # subtitles are burned in. The video remains playable without external subtitle files.
    # Escape Windows path characters for the FFmpeg subtitles filter.
    srt_filter_path = str(srt.resolve()).replace("\\", "/").replace(":", "\\:")
    vf = f"subtitles='{srt_filter_path}':force_style='FontName=Arial,FontSize=20,Outline=2,Shadow=1'"

    run(
        [
            "ffmpeg", "-y",
            "-i", str(visual),
            "-i", str(voice),
            "-vf", vf,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "160k",
            "-shortest",
            "-movflags", "+faststart",
            str(output),
        ]
    )

# ---------------------------- Main ----------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Turn a complete English news article into a narrated AI news video."
    )
    parser.add_argument("--article", help="Path to a UTF-8 .txt article")
    parser.add_argument("--text", help="Article text supplied directly")
    args = parser.parse_args()

    require_command("ffmpeg")
    require_command("ffprobe")
    require_command("ollama")

    if not torch.cuda.is_available():
        print("\nWARNING: CUDA is not available.")
        print("LTX-Video will run on CPU and may be impractically slow.")
        print("For a usable local setup, install a CUDA-enabled PyTorch build and use an NVIDIA GPU.\n")

    OUTPUT_DIR.mkdir(exist_ok=True)
    WORK_DIR.mkdir(exist_ok=True)

    article = read_article(args)

    print("\n1/5 Creating broadcast script and scene plan...")
    plan = create_plan(article)

    (OUTPUT_DIR / "plan.json").write_text(
        json.dumps(plan, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Headline: {plan.get('headline', '')}")
    print(f"Scenes: {len(plan['scenes'])}")

    print("\n2/5 Generating complete news-reader voice-over...")
    voice_path = WORK_DIR / "narration.wav"
    duration = make_voiceover(plan["narration"], voice_path)

    print("\n3/5 Generating AI video scenes with LTX-Video...")
    pipe = load_ltx()

    clips = []
    for idx, scene in enumerate(plan["scenes"], 1):
        clip_path = WORK_DIR / f"scene_{idx:03d}.mp4"
        print(f"\nScene {idx}/{len(plan['scenes'])}: {scene['visual_prompt']}")
        generate_ltx_clip(pipe, scene["visual_prompt"], clip_path)
        clips.append(clip_path)

    print("\n4/5 Synchronizing visuals to narration...")
    srt_path = WORK_DIR / "subtitles.srt"
    make_srt(plan, duration, srt_path)

    visual_path = WORK_DIR / "visual_track.mp4"
    build_visual_track(clips, duration, visual_path)

    print("\n5/5 Rendering final news video...")
    final_path = OUTPUT_DIR / "news_video.mp4"
    mux_final(visual_path, voice_path, srt_path, final_path)

    print("\n==========================================")
    print("DONE")
    print(f"Video:      {final_path.resolve()}")
    print(f"Script:     {(OUTPUT_DIR / 'plan.json').resolve()}")
    print(f"Subtitles:  {srt_path.resolve()}")
    print("==========================================")

if __name__ == "__main__":
    main()
