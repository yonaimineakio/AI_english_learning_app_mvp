from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from app.services.ai.google_tts_provider import GoogleTTSProvider


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Google Cloud Text-to-Speech smoke test (writes MP3)."
    )
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument("--language", default=None, help="e.g. en-US (optional)")
    parser.add_argument("--voice", default=None, help="Voice name (optional)")
    parser.add_argument("--rate", type=float, default=None, help="Speaking rate (optional)")
    parser.add_argument(
        "--out",
        default="tts_output.mp3",
        help="Output MP3 path (default: ./tts_output.mp3)",
    )
    return parser.parse_args()


async def run() -> int:
    args = parse_args()
    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    async with GoogleTTSProvider() as tts_provider:
        audio_bytes = await tts_provider.synthesize_speech(
            text=args.text,
            language_code=args.language,
            voice_name=args.voice,
            speaking_rate=args.rate,
        )

    out_path.write_bytes(audio_bytes)
    print(f"Wrote {len(audio_bytes)} bytes -> {out_path}")
    return 0


def main() -> int:
    try:
        return asyncio.run(run())
    except Exception as exc:
        print(f"TTS smoke test failed: {exc!r}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
