"""Extract one public webpage as text or Markdown, optionally into a local file.

Set EDU_SHARING_TEXT_EXTRACTION_URL for an explicit service. Alternatively set
EDU_SHARING_URL for the repository.<domain> / text-extraction.<domain> convention.
Then run: python docs/examples/26_extract_page.py https://wirlernenonline.de \
    --method browser --format markdown --output page.md

The browser runs on the service; this example needs no local browser. It reads
one page and does not crawl links or write anything into the repository.
"""

import argparse
import asyncio
import os
from pathlib import Path

from edusharing.extraction import ExtractedText, TextExtraction


async def save_page(
    service: TextExtraction, url: str, *, method: str,
    output_format: str, output: Path | None = None,
) -> ExtractedText:
    result = await service.text_of(url, method=method, output_format=output_format)
    if not result.text:
        print(f"No text: {result.reason}; {result.detail}")
    elif output is not None:
        output.write_text(result.text, encoding="utf-8")
        print(f"Saved {result.char_count} characters to {output}")
    else:
        print(result.text)
    return result


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?")
    parser.add_argument("--method", choices=("simple", "browser"), default="simple")
    parser.add_argument("--format", choices=("txt", "markdown"), default="txt")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    explicit = os.environ.get(TextExtraction.ENV_BASE_URL, "").strip()
    repository_url = os.environ.get("EDU_SHARING_URL", "").strip()
    if not args.url or not (explicit or repository_url):
        print("Set EDU_SHARING_TEXT_EXTRACTION_URL or EDU_SHARING_URL, then pass a webpage URL.")
        return 0
    service = (TextExtraction.from_env() if explicit
               else TextExtraction.from_repository(repository_url))
    async with service:
        result = await save_page(service, args.url, method=args.method,
                                 output_format=args.format, output=args.output)
    return 0 if result.text else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
