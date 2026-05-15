#!/usr/bin/env python3
"""
Edo Dataset Cleaner
===================
Cleans and normalizes Edo corpus records by:
  1. Removing non-standard combining marks (especially Thomas dictionary)
  2. Filtering English-only text
  3. Normalizing Unicode to NFC
  4. Handling quotation mark edge cases
"""

import json
import unicodedata
import re
from pathlib import Path

# Edo markers and English stopwords ──────────────────────────────────────

# Only include characters with diacritics (exclude plain ASCII r/R)
EDO_MARKERS = set("ẹọẸỌɛƐɔɽãÃṣṢʼʻẽẼõÕ")

EN_STOPS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "is","are","was","were","be","been","have","has","had","do","does","did",
    "will","would","could","should","may","might","he","she","it","they","we",
    "you","i","me","him","her","us","them","his","its","our","your","their",
    "this","that","these","those","not","no","so","if","as","by","from",
    "then","when","where","what","which","who","how","all","also","one","two",
    "said","into","just","than","very","such","after","before","often","used",
    "see","note","page","cf","ibid","some","many","more","most","other","each",
    "both","same","only","can","any","out","up","about","using","meaning",
}

# Non-standard combining marks to remove (mainly from Thomas dictionary)
# These are combining marks not in the standard Edo orthography
NON_STANDARD_COMBINING = {
    '\u030d',  # combining vertical line above
    '\u0309',  # combining hook above
    '\u033d',  # combining x above
    '\u0345',  # combining greek letter iota below
    '\u035c',  # combining double breve below
    '\u0364',  # combining e above
    '\u0365',  # combining a above
    '\u036a',  # combining l above
    '\u036b',  # combining m above
    '\u036c',  # combining n above
    '\u036d',  # combining o above
    '\u036e',  # combining r above
    '\u036f',  # combining t above
    '\u0349',  # combining right half ring below
    '\u035e',  # combining double macron
    '\u035f',  # combining double macron below
    '\u035b',  # combining zigzag above
    '\u0360',  # combining double tilde
    '\u0361',  # combining inverted breve
    '\u033e',  # combining tilde overlay
}

# ── Utilities ─────────────────────────────────────────────────────────────

def has_edo_markers(text):
    """Check if text contains Edo-specific diacritics."""
    return any(c in EDO_MARKERS for c in text)

def remove_non_standard_marks(text):
    """Remove non-standard combining marks while preserving base characters."""
    cleaned = []
    for char in text:
        # Keep the character if it's not a non-standard combining mark
        if char not in NON_STANDARD_COMBINING:
            cleaned.append(char)
    return ''.join(cleaned)

def is_english_only(text):
    """Return True if the line should be discarded as English metadata."""
    text = text.strip()
    if not text or len(text) < 3:
        return True
    if has_edo_markers(text):
        return False
    
    # If it's quoted and has no Edo markers, it's likely English
    if (text.startswith('"') or text.startswith("'")) and not has_edo_markers(text):
        return True
    
    # Count alphabetic characters: ASCII vs non-ASCII
    ascii_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    total_alpha = sum(1 for c in text if c.isalpha())
    
    # Calculate ASCII ratio
    ascii_ratio = ascii_chars / total_alpha if total_alpha > 0 else 1.0
    
    # If mostly ASCII letters, it's English
    if ascii_ratio > 0.85:  # More than 85% ASCII = English
        return True
    
    # High stopword ratio = English
    words = re.findall(r'[a-zA-Z]+', text.lower())
    if len(words) >= 2:
        en_ratio = sum(1 for w in words if w in EN_STOPS) / len(words)
        if en_ratio > 0.5:
            return True
    
    # Common English sentence starters (with stricter ASCII check)
    en_starters = (
        'as ', 'at ', 'he ', 'she ', 'they ', 'it ', 'the ', 'this ', 'that ',
        'a ', 'an ', 'and ', 'but ', 'for ', 'to ', 'in ', 'on ', 
        'after ', 'before ', 'when ', 'where ', 'which ', 'there ', 'all '
    )
    if any(text.lower().startswith(s) for s in en_starters):
        if ascii_ratio > 0.80:
            return True
    
    return False

def normalize_record(record):
    """
    Clean and normalize a single record.
    
    Steps:
      1. Extract text
      2. Remove non-standard combining marks (esp. Thomas dictionary)
      3. Normalize to NFC
      4. Strip whitespace
      5. Filter out English-only content
      6. Require at least one Edo marker for non-dictionary entries
    """
    text = record.get("text", "").strip()
    if not text:
        return None
    
    # Step 1: Remove non-standard combining marks
    text = remove_non_standard_marks(text)
    
    # Step 2: Normalize Unicode to NFC
    text = unicodedata.normalize("NFC", text)
    
    # Step 3: Clean up quotation marks and extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Step 4: Remove lines with unclosed quotes or obvious artifacts
    if text.count('"') % 2 != 0 and '`' in text:
        return None  # Malformed quotes with backticks
    
    # Step 5: Filter English-only text
    if is_english_only(text):
        return None
    
    # Step 6: For corpus/narrative sources, require actual Edo markers
    # Dictionary entries can be simpler (just word headwords)
    source = record.get("source", "")
    is_dict_source = "dictionary" in source.lower() or "leaflet" in source.lower()
    
    if not is_dict_source and not has_edo_markers(text):
        # Narrative/corpus entries must have Edo diacritics
        return None
    
    # Return cleaned record
    return {
        "text": text,
        "source": source,
        "lang": "edo"
    }

# ── Main processing ───────────────────────────────────────────────────────

def clean_corpus():
    """Load, clean, and output the corpus."""
    
    corpus_dir = Path("edo_corpus")
    output_dir = Path("edo_dataset")
    output_dir.mkdir(exist_ok=True)
    
    # Output files
    jsonl_out = output_dir / "edo_cleaned.jsonl"
    txt_out = output_dir / "edo_cleaned.txt"
    
    # Process all raw JSONL files
    print("Processing corpus files...")
    seen = set()
    records = []
    
    for raw_file in sorted(corpus_dir.glob("raw/*.jsonl")):
        print(f"  Reading {raw_file.name}...")
        with open(raw_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line)
                    cleaned = normalize_record(record)
                    
                    if cleaned:
                        # Deduplicate by normalized text
                        key = cleaned["text"].lower()
                        if key not in seen:
                            seen.add(key)
                            records.append(cleaned)
                except json.JSONDecodeError:
                    print(f"    ⚠ Skipped malformed JSON at line {line_num}")
                    continue
    
    print(f"\n✓ Loaded and cleaned {len(records)} unique records")
    
    # Write JSONL output
    with open(jsonl_out, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  → {jsonl_out.name}  ({len(records)} records)")
    
    # Write plain text output
    with open(txt_out, "w", encoding="utf-8") as f:
        for r in records:
            f.write(r["text"] + "\n")
    print(f"  → {txt_out.name}")
    
    # Summary by source
    print(f"\n{'─'*60}")
    print(f"  SUMMARY BY SOURCE")
    print(f"{'─'*60}")
    
    source_counts = {}
    for r in records:
        src = r["source"]
        source_counts[src] = source_counts.get(src, 0) + 1
    
    for src in sorted(source_counts.keys()):
        print(f"    {src:<40} {source_counts[src]:>6}")
    
    print(f"{'─'*60}")
    print(f"  Total records                    : {len(records):>6}")
    print(f"  Output directory                 : {output_dir.resolve()}")
    print(f"{'─'*60}")

if __name__ == "__main__":
    clean_corpus()
