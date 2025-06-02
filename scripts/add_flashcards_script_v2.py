import httpx


##################################
### 
### add new cards by reading contents of CARD_FILE (scripts/new_cards.txt)
### 
##################################


API = "http://127.0.0.1:8000"
CARD_FILE = "scripts/new_cards.txt"  # adjust path if needed

def parse_flashcards(file_path):
    cards = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    i = 0
    while i < len(lines):
        if lines[i].lower().startswith("new flashcard!"):
            try:
                question = lines[i + 1].removeprefix("Q:").strip()
                answer   = lines[i + 2].removeprefix("A:").strip()
                tags_raw = lines[i + 3].removeprefix("Tag(s):").strip()
                tags     = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]
                cards.append((question, answer, tags))
                i += 4
            except IndexError:
                print(f"⚠️ Incomplete flashcard starting at line {i+1}")
                i += 1
        else:
            i += 1
    return cards

def upload_text_asset(text, filename):
    files = {
        "type": (None, "text"),
        "file": (filename, text, "text/plain"),
    }
    res = httpx.post(f"{API}/assets", files=files)
    res.raise_for_status()
    return res.json()["id"]

def create_flashcard(front, back, tags):
    front_id = upload_text_asset(front, "front.txt")
    back_id  = upload_text_asset(back, "back.txt")

    payload = {
        "front_asset_id": front_id,
        "back_asset_id": back_id,
        "tags": tags
    }
    res = httpx.post(f"{API}/cards", json=payload)
    res.raise_for_status()
    print("✅ Imported card:", front[:60], "...")

def main():
    flashcards = parse_flashcards(CARD_FILE)
    print(f"📚 Found {len(flashcards)} flashcards in {CARD_FILE}")

    for front, back, tags in flashcards:
        try:
            create_flashcard(front, back, tags)
        except Exception as e:
            print(f"❌ Failed to create card: {front[:40]}... — {e}")

if __name__ == "__main__":
    main()
