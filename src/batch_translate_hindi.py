import os
import time
from deep_translator import GoogleTranslator

RAW_DIR = "data/raw_transcripts"
OUT_DIR = "data/cleaned_transcripts"
os.makedirs(OUT_DIR, exist_ok=True)

TARGET_EPISODES = {
    "ep004_raw.txt",
    "ep012_raw.txt",
    "ep013_raw.txt",
    "ep016_raw.txt",
    "ep017_raw.txt",
    "ep018_raw.txt"
}

# Split text into safe chunks (< 4500 chars)
def split_chunks(text, limit=4500):
    words = text.split()
    chunks, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 < limit:
            current += " " + w
        else:
            chunks.append(current)
            current = w
    chunks.append(current)
    return chunks


def translate_chunk(chunk, translator, retries=3):
    chunk = chunk.strip()
    if not chunk:
        return ""

    for attempt in range(1, retries + 1):
        try:
            return translator.translate(chunk)
        except Exception as e:
            print(f"    ⚠ Attempt {attempt} failed: {e}")
            if attempt == retries:
                print("    ❌ Skipping this chunk.")
                return ""
            time.sleep(2 * attempt)  # backoff
    return ""


translator = GoogleTranslator(source="auto", target="en")

files = [f for f in os.listdir(RAW_DIR) if f in TARGET_EPISODES]

print(f"Translating {len(files)} episode(s): {files}\n")

for file in files:
    print(f"\n=== Translating {file} ===")
    raw_path = os.path.join(RAW_DIR, file)

    # read raw text
    with open(raw_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = split_chunks(text)
    print(f"  → Split into {len(chunks)} chunks")

    translated_full = ""

    for idx, chunk in enumerate(chunks, start=1):
        print(f"  Translating chunk {idx}/{len(chunks)}...")
        translated_text = translate_chunk(chunk, translator)
        translated_full += translated_text + "\n\n"

        time.sleep(1.5)  # prevent rate-limits

    # Save translated file
    out_name = file.replace("_raw.txt", "_cleaned.txt")
    out_path = os.path.join(OUT_DIR, out_name)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(translated_full)

    print(f"  ✅ Saved: {out_path}")

print("\nAll selected episodes translated!")
