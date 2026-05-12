"""
Edo Corpus Scraper
===================
Sources:
  1. Agheyisi Corpus       — 4 folktales (Edo + English, parallel)
  2. Agheyisi Dictionary   — Edo-English dictionary, letter pages under master/
  3. Melzian Dictionary    — Bini-English dictionary, letter pages under master/
  4. Thomas Dictionary     — letter pages under Thomas/text/
  5. Thomas Corpus         — 27 stories under Thomas/corpus/text/
  6. Egharevba Chapters    — biography, chapter pages under Egharevba/text/
  7. Bristol PDF           — welfare leaflet PDF

Outputs:
  edo_corpus/raw/                        — one JSONL per source
  edo_corpus/parallel/                   — Edo-English sentence pairs
  edo_corpus/edo_monolingual_corpus.jsonl
  edo_corpus/edo_plain.txt               — one line per sentence (tokenizer-ready)

Run:
  pip install requests beautifulsoup4 lxml pdfplumber
  python3 edo_scraper.py
"""

import requests
from bs4 import BeautifulSoup
import json, time, re, unicodedata
from urllib.parse import urljoin
from pathlib import Path
from collections import Counter

# ── Directories ───────────────────────────────────────────────────────────────
OUT = Path("edo_corpus")
OUT.mkdir(exist_ok=True)
(OUT / "raw").mkdir(exist_ok=True)
(OUT / "parallel").mkdir(exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; EdoCorpusResearch/1.0; academic NLP)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
})


# ── Core utilities ────────────────────────────────────────────────────────────

def fetch(url, retries=3, delay=1.0):
    for i in range(retries):
        try:
            r = SESSION.get(url, timeout=20)
            r.raise_for_status()
            r.encoding = "utf-8"
            return r.text
        except Exception as e:
            print(f"    [attempt {i+1}/{retries}] {e}")
            time.sleep(delay * (i + 1))
    print(f"  FAILED: {url}")
    return None


def make_soup(html):
    return BeautifulSoup(html, "lxml")


def clean(text):
    """NFC-normalize and collapse whitespace."""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def save_jsonl(records, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  -> {len(records):>5} records  {path.name}")
    return records


# ── Edo / English detection ───────────────────────────────────────────────────

# Characters used in properly-marked Edo that almost never appear in English
EDO_MARKERS = set("ẹọẸỌɛƐɔɽãÃr̅R̅")

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

def has_edo_markers(text):
    return any(c in EDO_MARKERS for c in text)

def is_english_only(text):
    """Return True if the line should be discarded as English metadata."""
    text = text.strip()
    if not text or len(text) < 3:
        return True
    if has_edo_markers(text):
        return False
    # Structural label: "06 ENG -", "AGH -", "EDO -"
    if re.match(r"^(\d+\s+)?(ENG|AGH|EDO)\s*[-]", text):
        return True
    words = re.findall(r"[a-zA-Z]+", text.lower())
    if len(words) < 3:
        return False
    en_ratio = sum(1 for w in words if w in EN_STOPS) / len(words)
    return en_ratio > 0.65


# ── 1. Agheyisi Corpus — 4 folktales ─────────────────────────────────────────

def scrape_agheyisi_corpus():
    """
    Index:  centreforedostudies.be/Agheyisi-corpus/index.html
    Tales:  .../corpus/tale1.html through tale4.html

    Bold elements come in numbered triples:
      "N. <Edo>"   "N. <Literal English>"   "N. <Free English>"
    """
    print("\n[1/6] Agheyisi Corpus (4 folktales + parallel data)")
    base = "https://centreforedostudies.be/Agheyisi-corpus/corpus/"
    tale_urls = [f"{base}tale{i}.html" for i in range(1, 5)]

    mono, parallel = [], []

    for url in tale_urls:
        tale = url.split("/")[-1].replace(".html", "")
        html = fetch(url)
        if not html:
            continue
        s = make_soup(html)
        bolds = [clean(b.get_text()) for b in s.find_all("b") if clean(b.get_text())]

        i = 0
        while i < len(bolds):
            m = re.match(r"^(\d+)[.]\s*(.+)", bolds[i])
            if m:
                edo_text = m.group(2).strip()
                literal  = re.sub(r"^\d+[.]\s*", "", bolds[i+1]).strip() if i+1 < len(bolds) else ""
                free_en  = re.sub(r"^\d+[.]\s*", "", bolds[i+2]).strip() if i+2 < len(bolds) else ""

                if edo_text and not is_english_only(edo_text):
                    mono.append({"text": edo_text, "source": f"agheyisi_corpus_{tale}", "lang": "edo"})
                    if free_en:
                        parallel.append({
                            "edo": edo_text,
                            "english_literal": literal,
                            "english_free": free_en,
                            "source": f"agheyisi_corpus_{tale}",
                        })
                i += 3
            else:
                i += 1
        time.sleep(0.8)

    save_jsonl(mono,     OUT / "raw"      / "agheyisi_corpus.jsonl")
    save_jsonl(parallel, OUT / "parallel" / "agheyisi_parallel.jsonl")
    print(f"       {len(parallel)} parallel pairs")
    return mono


# ── 2. Agheyisi Dictionary ────────────────────────────────────────────────────

def scrape_agheyisi_dictionary():
    """
    Contents: .../Agheyisi-epub-final/OEBPS/Text/Contents.html
    Letter pages linked as: master/letter00.html ... letterNN.html

    Each entry: <a href="..."><b>headword [tone]</b></a>
    Bold elements outside anchors = example sentences in Edo.
    """
    print("\n[2/6] Agheyisi Dictionary")
    contents_url = "https://centreforedostudies.be/Agheyisi-epub-final/OEBPS/Text/Contents.html"
    html = fetch(contents_url)
    if not html:
        return []

    s = make_soup(html)
    letter_links = sorted(set(
        urljoin(contents_url, a["href"])
        for a in s.find_all("a", href=True)
        if re.search(r"master/letter\d+\.html", a["href"])
    ))
    print(f"    {len(letter_links)} letter pages")

    records = []
    for url in letter_links:
        html = fetch(url)
        if not html:
            continue
        s = make_soup(html)

        # Headwords: bold inside an anchor
        for a_tag in s.find_all("a", href=True):
            b = a_tag.find("b")
            if not b:
                continue
            text = clean(b.get_text())
            headword = re.sub(r"\s*\[.*?\]", "", text).strip()  # strip [tone]
            if len(headword) >= 1 and not is_english_only(headword):
                records.append({"text": headword, "source": "agheyisi_dictionary", "lang": "edo"})

        # Example sentences: bold NOT inside an anchor
        for b in s.find_all("b"):
            if b.find_parent("a"):
                continue
            text = clean(b.get_text())
            if len(text) > 3 and not is_english_only(text):
                records.append({"text": text, "source": "agheyisi_dictionary_example", "lang": "edo"})

        time.sleep(0.8)

    save_jsonl(records, OUT / "raw" / "agheyisi_dictionary.jsonl")
    return records


# ── 3. Melzian Dictionary ─────────────────────────────────────────────────────

def scrape_melzian_dictionary():
    """
    Contents: .../Melzian-epub-final/OEBPS/Text/Contents.html
    Letter pages: .../master/letter01.html ... letterNN.html

    Same structure as Agheyisi: <a><b>headword [tone]</b></a> + definition.
    """
    print("\n[3/6] Melzian Dictionary (Bini Language)")
    contents_url = "https://centreforedostudies.be/Melzian-epub-final/OEBPS/Text/Contents.html"
    html = fetch(contents_url)
    if not html:
        return []

    s = make_soup(html)
    letter_links = sorted(set(
        urljoin(contents_url, a["href"])
        for a in s.find_all("a", href=True)
        if re.search(r"master/letter\d+\.html", a["href"])
    ))
    print(f"    {len(letter_links)} letter pages")

    records = []
    for url in letter_links:
        html = fetch(url)
        if not html:
            continue
        s = make_soup(html)

        for a_tag in s.find_all("a", href=True):
            b = a_tag.find("b")
            if not b:
                continue
            text = clean(b.get_text())
            headword = re.sub(r"\s*\[.*?\]", "", text).strip()
            if len(headword) >= 1 and not is_english_only(headword):
                records.append({"text": headword, "source": "melzian_dictionary", "lang": "edo"})

        for b in s.find_all("b"):
            if b.find_parent("a"):
                continue
            text = clean(b.get_text())
            if len(text) > 3 and not is_english_only(text):
                records.append({"text": text, "source": "melzian_dictionary_example", "lang": "edo"})

        time.sleep(0.8)

    save_jsonl(records, OUT / "raw" / "melzian_dictionary.jsonl")
    return records


# ── 4. Thomas Dictionary ──────────────────────────────────────────────────────

def scrape_thomas_dictionary():
    """
    Index: .../Thomas/text/index.html
    Letter pages: .../Thomas/text/xx00.html ... xx19.html

    Headwords are <b>Word</b> followed by English definition and cross-refs.
    Thomas uses older orthography — fewer diacritics but still valid Edo.
    """
    print("\n[4/6] Thomas Dictionary")
    index_url = "https://centreforedostudies.be/Thomas/text/index.html"
    html = fetch(index_url)
    if not html:
        return []

    s = make_soup(html)
    letter_links = sorted(set(
        urljoin(index_url, a["href"])
        for a in s.find_all("a", href=True)
        if re.search(r"xx\d+\.html", a["href"])
    ))
    print(f"    {len(letter_links)} letter pages")

    records = []
    for url in letter_links:
        html = fetch(url)
        if not html:
            continue
        s = make_soup(html)
        for b in s.find_all("b"):
            text = clean(b.get_text())
            if len(text) < 2 or len(text) > 80:
                continue
            if is_english_only(text):
                continue
            records.append({"text": text, "source": "thomas_dictionary", "lang": "edo"})
        time.sleep(0.8)

    save_jsonl(records, OUT / "raw" / "thomas_dictionary.jsonl")
    return records


# ── 5. Thomas Corpus — 27 stories ────────────────────────────────────────────

def scrape_thomas_corpus():
    """
    Index: .../Thomas/corpus/index.html
    Pages: .../Thomas/corpus/text/corpus-17.html ... corpus-NN.html

    Each bold element is prefixed:
      "05 AGH - <Edo, Agheyisi transcription>"   <- primary Edo
      "05 EDO - <Edo, Thomas orthography>"
      "06 ENG - <English translation>"

    AGH lines are the cleanest Edo. We pair AGH + ENG for parallel data.
    """
    print("\n[5/6] Thomas Corpus (27 stories + parallel data)")
    index_url = "https://centreforedostudies.be/Thomas/corpus/index.html"
    html = fetch(index_url)
    if not html:
        return []

    s = make_soup(html)
    page_links = sorted(set(
        urljoin(index_url, a["href"])
        for a in s.find_all("a", href=True)
        if re.search(r"text/corpus-\d+\.html", a["href"])
    ))
    print(f"    {len(page_links)} corpus pages")

    agh_pat = re.compile(r"^(\d+)\s+AGH\s*[-]\s*(.+)")
    eng_pat = re.compile(r"^(\d+)\s+ENG\s*[-]\s*(.+)")

    mono, parallel = [], []

    for url in page_links:
        html = fetch(url)
        if not html:
            continue
        s = make_soup(html)

        # AGH and EDO lines share a single <b> tag separated by \n.
        # Split each bold by newline BEFORE cleaning so the regex sees
        # each line individually e.g.:
        #   "05 AGH - Azuambili...\n05 EDO - Azuambi͉li..."
        # becomes two separate strings we can match independently.
        raw_lines = []
        for b in s.find_all("b"):
            for subline in b.get_text().splitlines():
                subline = unicodedata.normalize("NFC", subline).strip()
                if subline:
                    raw_lines.append(subline)

        lines = {}
        for subline in raw_lines:
            m_agh = agh_pat.match(subline)
            m_eng = eng_pat.match(subline)
            if m_agh:
                lines.setdefault(int(m_agh.group(1)), {})["agh"] = m_agh.group(2).strip()
            elif m_eng:
                lines.setdefault(int(m_eng.group(1)), {})["eng"] = m_eng.group(2).strip()

        for num in sorted(lines):
            agh = lines[num].get("agh", "")
            eng = lines[num].get("eng", "")
            if agh and not is_english_only(agh):
                page_id = url.split("/")[-1].replace(".html", "")
                mono.append({"text": agh, "source": "thomas_corpus", "lang": "edo", "page": page_id})
                if eng:
                    parallel.append({"edo": agh, "english": eng, "source": "thomas_corpus", "page": page_id})

        time.sleep(0.8)

    save_jsonl(mono,     OUT / "raw"      / "thomas_corpus.jsonl")
    save_jsonl(parallel, OUT / "parallel" / "thomas_parallel.jsonl")
    print(f"       {len(parallel)} parallel pairs")
    return mono


# ── 6. Egharevba Biography — chapters ────────────────────────────────────────

def scrape_egharevba():
    """
    Index: .../Egharevba/index.html
    Chapters: .../Egharevba/text/Chapter-01.html ... Chapter-NN.html

    Pure Edo prose autobiography. Every line of text is in a <b> tag.
    No English translation present.
    """
    print("\n[6/6] Egharevba — Itan ẹdagbọn mwen (Edo autobiography)")
    index_url = "https://centreforedostudies.be/Egharevba/index.html"
    html = fetch(index_url)
    if not html:
        return []

    s = make_soup(html)
    chapter_links = sorted(set(
        urljoin(index_url, a["href"])
        for a in s.find_all("a", href=True)
        if re.search(r"text/Chapter-\d+\.html", a["href"], re.IGNORECASE)
    ))
    print(f"    {len(chapter_links)} chapters")

    records = []
    for url in chapter_links:
        html = fetch(url)
        if not html:
            continue
        s = make_soup(html)
        chapter_id = url.split("/")[-1].replace(".html", "")
        for b in s.find_all("b"):
            text = clean(b.get_text())
            if len(text) < 3 or is_english_only(text):
                continue
            records.append({
                "text": text,
                "source": "egharevba_biography",
                "lang": "edo",
                "chapter": chapter_id,
            })
        time.sleep(0.8)

    save_jsonl(records, OUT / "raw" / "egharevba_biography.jsonl")
    return records


# ── 7. Bristol PDF — extract automatically ───────────────────────────────

def scrape_bristol_pdf():
    print("\n[7/7] Bristol welfare leaflet (PDF extraction)")
    pdf_url = "https://centreforedostudies.be/Bristol/welfare-attendance-leaflet-edo.pdf"
    pdf_path = Path("bristol_welfare_leaflet.pdf")
    
    # Download if not present
    if not pdf_path.exists():
        print("    Downloading PDF...")
        try:
            r = SESSION.get(pdf_url, timeout=20)
            r.raise_for_status()
            with open(pdf_path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            print(f"    FAILED to download: {e}")
            return []
    
    # Extract text
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = '\n'.join(p.extract_text() or '' for p in pdf.pages)
    except ImportError:
        print("    pdfplumber not installed, skipping")
        return []
    except Exception as e:
        print(f"    FAILED to extract text: {e}")
        return []
    
    # Process lines
    records = []
    for line in text.split('\n'):
        line = clean(line)
        if len(line) >= 3 and not is_english_only(line):
            records.append({"text": line, "source": "bristol_welfare_leaflet", "lang": "edo"})
    
    save_jsonl(records, OUT / "raw" / "bristol_leaflet.jsonl")
    return records


# ── Combine & deduplicate ─────────────────────────────────────────────────────

def build_corpus(all_records):
    print("\n── Building combined corpus ──────────────────────────")
    seen = set()
    unique = []
    for r in all_records:
        key = unicodedata.normalize("NFC", r["text"].strip().lower())
        if key and key not in seen:
            seen.add(key)
            unique.append(r)

    save_jsonl(unique, OUT / "edo_monolingual_corpus.jsonl")

    with open(OUT / "edo_plain.txt", "w", encoding="utf-8") as f:
        for r in unique:
            f.write(r["text"] + "\n")
    print(f"  -> plain text  edo_plain.txt")

    print(f"\n{'='*54}")
    print(f"  CORPUS SUMMARY")
    print(f"{'='*54}")
    print(f"  Total unique monolingual records : {len(unique):,}")
    for src, n in Counter(r["source"] for r in unique).most_common():
        print(f"    {src:<42} {n:>5}")

    total_par = 0
    for pf in sorted((OUT / "parallel").glob("*.jsonl")):
        with open(pf, encoding="utf-8") as f:
            n = sum(1 for _ in f)
        total_par += n
        print(f"  [parallel] {pf.name:<38} {n:>5} pairs")
    print(f"  Total parallel pairs             : {total_par:,}")
    print(f"{'='*54}")
    print(f"  Output directory: {OUT.resolve()}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    all_records = []
    all_records += scrape_agheyisi_corpus()
    all_records += scrape_agheyisi_dictionary()
    all_records += scrape_melzian_dictionary()
    all_records += scrape_thomas_dictionary()
    all_records += scrape_thomas_corpus()
    all_records += scrape_egharevba()
    all_records += scrape_bristol_pdf()
    build_corpus(all_records)
