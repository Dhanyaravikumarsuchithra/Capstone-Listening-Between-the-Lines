import json
import os

input_path = "data/raw_transcripts/ep03_raw.json"
output_path = "data/raw_transcripts/ep03_raw.txt"

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Handle different possible JSON structures

entries = None

# CASE 1: data = [ { "text": ... }, ... ]
if isinstance(data, list):
    if len(data) > 0 and isinstance(data[0], dict):
        entries = data
    # CASE 2: data = [ [ { "text": ... }, ... ] ]
    elif len(data) > 0 and isinstance(data[0], list):
        entries = data[0]

elif isinstance(data, dict):
    # Just in case we ever get: { "something": [ { "text": ... } ] }
    first_key = list(data.keys())[0]
    entries = data[first_key]

if entries is None:
    raise ValueError("Unexpected JSON structure, cannot find entries")

os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    for entry in entries:
        if isinstance(entry, dict) and "text" in entry:
            f.write(entry["text"] + "\n")

print("✅ JSON → TXT conversion complete")
print("📁 Saved to:", output_path)
