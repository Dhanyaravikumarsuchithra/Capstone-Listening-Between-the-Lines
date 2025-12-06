import os
import time
from deep_translator import GoogleTranslator

RAW_DIR = "data/raw_transcripts"
CLEAN_DIR = "data/cleaned_transcripts"

MAX_CHARS = 4500  


def split_into_chunks(text: str, max_len: int = MAX_CHARS):
    """
    Split long text into chunks <= max_len characters.
    We try to split on line boundaries to keep things readable.
    """
    lines = text.split("\n")
    chunks = []
    current_lines = []
    current_len = 0

    for line in lines:
        
        if len(line) > max_len:
            
            if current_lines:
                chunks.append("\n".join(current_lines))
                current_lines = []
                current_len = 0

            
            start = 0
            while start < len(line):
                end = start + max_len
                chunks.append(line[start:end])
                start = end
            continue

        
        if current_len + len(line) + 1 <= max_len:
            current_lines.append(line)
            current_len += len(line) + 1
        else:
           
            chunks.append("\n".join(current_lines))
            current_lines = [line]
            current_len = len(line)

    if current_lines:
        chunks.append("\n".join(current_lines))

    return chunks


def translate_chunk(chunk: str, translator: GoogleTranslator) -> str:
    """
    Translate a single chunk. Translator object is reused across chunks.
    """
    
    chunk = chunk.strip()
    if not chunk:
        return ""
    return translator.translate(chunk)


def translate_file(raw_path: str, clean_path: str):
    """Translate a single raw transcript file to English and save it."""
    print(f"  Reading: {raw_path}")
    with open(raw_path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("  ⚠ Empty file, skipping.")
        return

    chunks = split_into_chunks(text, MAX_CHARS)
    print(f"  Text length: {len(text)} chars → {len(chunks)} chunk(s)")

    translator = GoogleTranslator(source="auto", target="en")
    translated_chunks = []

    for i, chunk in enumerate(chunks, start=1):
        print(f"    Translating chunk {i}/{len(chunks)}...")
        try:
            translated = translate_chunk(chunk, translator)
            translated_chunks.append(translated)
        except Exception as e:
            print(f"     Failed translating chunk {i}: {e}")
            
            translated_chunks.append("")  #

        
        time.sleep(1)

    full_translated = "\n".join(translated_chunks)

    os.makedirs(os.path.dirname(clean_path), exist_ok=True)
    with open(clean_path, "w", encoding="utf-8") as out:
        out.write(full_translated)

    print(f"   Saved translated file → {clean_path}")


def main():
    if not os.path.isdir(RAW_DIR):
        print(f"Folder not found: {RAW_DIR}")
        return

    files = sorted(
        f for f in os.listdir(RAW_DIR)
        if f.endswith("_raw.txt")
    )

    if not files:
        print(f"No *_raw.txt files found in {RAW_DIR}")
        return

    print(f"Found {len(files)} raw TXT file(s) in {RAW_DIR}")

    for fname in files:
        ep_id = os.path.splitext(fname)[0]   
        clean_name = ep_id.replace("_raw", "_cleaned") + ".txt"

        raw_path = os.path.join(RAW_DIR, fname)
        clean_path = os.path.join(CLEAN_DIR, clean_name)

    
        if os.path.exists(clean_path):
            print(f"\nSkipping {fname} (already exists: {clean_name})")
            continue

        print(f"\nTranslating {fname} → {clean_name}")
        translate_file(raw_path, clean_path)

    print("\n Batch translation complete.")


if __name__ == "__main__":
    main()
