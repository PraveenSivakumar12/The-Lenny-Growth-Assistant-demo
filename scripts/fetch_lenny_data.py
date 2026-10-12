#!/usr/bin/env python3
"""Fetch the official Lenny's Data starter transcript pack for local/runtime use.

Raw transcript files and derived full-text chunks are intentionally not committed
or included in the container image. See the source repository's LICENSE.md before
using or redistributing the dataset.
"""
from __future__ import annotations

import argparse
import io
import shutil
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

SOURCE_REPO = "https://github.com/LennysNewsletter/lennys-newsletterpodcastdata"
ARCHIVE_URL = "https://codeload.github.com/LennysNewsletter/lennys-newsletterpodcastdata/zip/refs/heads/main"


def fetch_transcripts(project_root: Path, force: bool = False) -> int:
    target = project_root / "data" / "transcripts"
    target.mkdir(parents=True, exist_ok=True)
    current = [
        p for p in target.glob("*.md")
        if p.name.lower() not in {"license.md", "readme.md"}
    ]
    if not force and len(current) >= 20 and (target / "index.json").is_file():
        print(f"Using {len(current)} existing transcript files in {target}")
        return len(current)

    request = urllib.request.Request(
        ARCHIVE_URL,
        headers={"User-Agent": "Lenny-Growth-Assistant/1.0 (transcript-bootstrap)"},
    )
    print(f"Downloading the official starter dataset from {SOURCE_REPO}")
    with urllib.request.urlopen(request, timeout=90) as response:
        archive_bytes = response.read()

    found_transcripts: dict[str, bytes] = {}
    catalog: bytes | None = None
    license_text: bytes | None = None
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for member in archive.namelist():
            path = PurePosixPath(member)
            parts = path.parts
            if path.is_dir():
                continue
            if "podcasts" in parts and path.suffix.lower() == ".md":
                # Flatten transcript filenames to match the ingestion pipeline.
                found_transcripts[path.name] = archive.read(member)
            elif path.name == "index.json" and "podcasts" not in parts:
                catalog = archive.read(member)
            elif path.name.lower() == "license.md" and license_text is None:
                license_text = archive.read(member)

    if not found_transcripts:
        raise RuntimeError("The official source archive contained no podcast Markdown files.")
    if catalog is None:
        raise RuntimeError("The official source archive did not contain the expected index.json catalog.")

    # Replace old transcript inputs only after a valid archive was downloaded.
    for path in current:
        path.unlink(missing_ok=True)
    for filename, content in found_transcripts.items():
        (target / filename).write_bytes(content)
    (target / "index.json").write_bytes(catalog)
    if license_text:
        (target / "LICENSE.md").write_bytes(license_text)

    print(f"Fetched {len(found_transcripts)} podcast transcripts. Raw data is local/runtime-only.")
    return len(found_transcripts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Download again even if a local copy exists.")
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    fetch_transcripts(project_root, force=args.force)


if __name__ == "__main__":
    main()
