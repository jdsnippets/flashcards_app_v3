#!/usr/bin/env python3
"""
import_flashcards.py
--------------------
Reads import_flashcards.txt (in this same directory), processes only those blocks
with `New card: yes`, uploads text or media to /assets, creates cards with tags.
"""

import os
import sys
import hashlib
import httpx
import argparse
import mimetypes

API = "http://127.0.0.1:8000"


def compute_hash(question: str, answer: str, tags: list[str]) -> str:
    data = question.strip() + "|" + answer.strip() + "|" + ",".join(sorted(tags))
    return hashlib.sha1(data.encode("utf-8")).hexdigest()


def parse_blocks(file_name_path: str) -> list[dict]:
    blocks = []
    with open(file_name_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    idx = 0
    while idx < len(lines):
        if lines[idx].strip().lower() == "new flashcard!":
            # We expect exactly 4 lines after "new flashcard!"
            q_line = lines[idx + 1]
            a_line = lines[idx + 2]
            tags_line = lines[idx + 3]
            newcard_line = lines[idx + 4] if idx + 4 < len(lines) else ""
            start_index = idx
            idx += 5

            question = q_line.replace("Q:", "", 1).strip()
            answer = a_line.replace("A:", "", 1).strip()

            # Handle both "Tags(s):" and "Tag(s):"
            raw_tags = tags_line.replace("Tag(s):", "", 1).strip()
            #--tbdel--|raw_tags = tags_line.replace("Tags(s):", "", 1).replace("Tag(s):", "", 1).strip()
            tags = [t.strip() for t in raw_tags.split(",") if t.strip()]

            is_new = newcard_line.strip().lower().startswith("new card: yes")
            blocks.append({
                "question": question,
                "answer": answer,
                "tags": tags,
                "new": is_new,
                "raw_index": start_index
            })
        else:
            idx += 1

    return blocks


def asset_upload(value: str) -> dict:
    """
    If `value` starts with /media/, upload that file as image/audio.
    Otherwise, treat `value` as plain text and upload as a text asset.
    Returns the JSON‐parsed dict from the /assets response.
    """

    # ---- MEDIA FILE CASE ----
    if value.startswith("/media/"):
        filename = os.path.basename(value)
        script_dir = os.path.dirname(__file__)
        full_path = os.path.join(script_dir, "media", filename)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Media file not found: {full_path}")

        mimetype, _ = mimetypes.guess_type(full_path)
        if mimetype is None:
            raise ValueError(f"Cannot guess MIME type for: {full_path}")

        if mimetype.startswith("image/"):
            type_str = "image"
        elif mimetype.startswith("audio/"):
            type_str = "audio"
        else:
            raise ValueError(f"Unsupported media MIME: {mimetype}")

        print(f"▶️  Uploading media '{filename}' as {type_str} (MIME={mimetype})")
        files = {
            "type": (None, type_str),
            "file": (filename, open(full_path, "rb"), mimetype)
        }

        resp = httpx.post(f"{API}/assets", files=files)
        try:
            resp.raise_for_status()
        except Exception:
            print(f"‼️  /assets returned {resp.status_code}: {resp.text}")
            raise

        asset = resp.json()
        print(f"   ← Created asset id={asset['id']}, path={asset['path']}")
        return asset

    # ---- PLAIN TEXT CASE ----
    else:
        text_blob = value.strip()
        if not text_blob:
            raise ValueError("Cannot upload empty text as an asset.")

        print(f"▶️  Uploading plain text (first 30 chars): '{text_blob[:30]}…'")
        files = {
            "type": (None, "text"),
            "file": ("front.txt", text_blob, "text/plain"),
        }

        resp = httpx.post(f"{API}/assets", files=files)
        try:
            resp.raise_for_status()
        except Exception:
            print(f"‼️  /assets returned {resp.status_code}: {resp.text}")
            raise

        asset = resp.json()
        print(f"   ← Created text asset id={asset['id']}")
        return asset


def main(file_name_path: str):
    print(f"Reading flashcard definitions from: {file_name_path!r}")
    blocks = parse_blocks(file_name_path)
    print(f"📚 Found {len(blocks)} blocks total; filtering for New card: yes…")

    imported_count = 0
    lines = open(file_name_path, "r", encoding="utf-8").read().splitlines()

    for blk in blocks:
        if not blk["new"]:
            print(f"– Skipping (already imported): {blk['question'][:40]}…")
            continue

        print(f"\n📝 Processing: {blk['question'][:60]}… (Tags: {blk['tags']})")

        # 1) Deduplication stub (optional): compute hash, query API if needed…
        card_hash = compute_hash(blk["question"], blk["answer"], blk["tags"])
        # print(f"   • computed hash = {card_hash}")

        # 2) Upload front asset
        try:
            front_asset = asset_upload(blk["question"])
        except Exception as e:
            print(f"❌  Failed to upload front for '{blk['question']}': {e}")
            continue

        # 3) Upload back asset
        try:
            back_asset = asset_upload(blk["answer"])
        except Exception as e:
            print(f"❌  Failed to upload back for '{blk['question']}': {e}")
            continue

        # 4) Create the card
        payload = {
            "front_asset_id": front_asset["id"],
            "back_asset_id": back_asset["id"],
            "tags": blk["tags"]
        }
        card_res = httpx.post(f"{API}/cards", json=payload)
        if card_res.status_code != 200:
            print(f"❌  Failed to create card for '{blk['question']}': HTTP {card_res.status_code} {card_res.text}")
            continue

        print(f"✅  Imported card → \"{blk['question'][:50]}…\"")
        imported_count += 1

        # (Optional) you could mark “New card: yes” → “New card: no” here
        # using blk["raw_index"], rewriting `lines[...]`, then writing back.

    print(f"\n📚 Imported {imported_count} new cards.")
    print("======= !!! REMEMBER to toggle 'New card: yes' → 'New card: no' in the TXT !!! =======\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk‐import flashcards from TXT")
    parser.add_argument(
        "--file-name-path",
        default=os.path.join(os.path.dirname(__file__), "import_flashcards.txt"),
        help=(
            "Path to the TXT file with flashcard blocks. "
            "Default: tools/import_flashcards/import_flashcards.txt"
        ),
    )
    args = parser.parse_args()
    main(args.file_name_path)
