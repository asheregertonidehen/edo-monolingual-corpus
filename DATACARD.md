# Edo Dataset Datacard

## Dataset Summary

A 420KB monolingual corpus of **Edo** (also called Bini), a Niger-Congo tonal language spoken primarily in Edo State, Nigeria. Compiled from six scholarly sources digitised by the [Centre for Edo Studies](https://centreforedostudies.be/) and supplementary public domain materials. To our knowledge this is the first openly released, documented Edo text dataset designed for NLP research. The corpus encompasses 12,646 unique records covering multiple text domains: prose narrative autobiography, folktales, dictionary headwords with example sentences, and a practical welfare document. Text has been cleaned, normalised to NFC Unicode, and deduplicated. All records are monolingual Edo; English translations have been systematically removed.

## Language

**Language:** Edo (Bini)  
**ISO 639-3 code:** bin  
**Script:** Latin with diacritics  
**Orthographic standard:** Standard Edo orthography including underdots (ẹ, ọ), tone marks (à, á, ǎ, â), other diacritics (ṣ, ṛ̅, etc.)  
**Unicode normalisation:** NFC applied throughout  
**Character set:** 19 Edo-specific diacritical characters + standard Latin letters

## Source Descriptions

### 1. Agheyisi Corpus (Folktales)
**Type:** Narrative prose (folktales)  
**Domain:** Traditional storytelling  
**Original URL:** https://centreforedostudies.be/Agheyisi-corpus/  
**Records:** 164 sentences (4 folktales)  
**License:** Scholarly digitisation (public domain)  
**Notes:** Clean narrative Edo text, originally bilingual but English translations removed for this dataset. Represents natural conversational and narrative Edo.  

### 2. Agheyisi Dictionary
**Type:** Lexical reference  
**Domain:** Edo-English bilingual dictionary  
**Original URL:** https://centreforedostudies.be/Agheyisi-epub-final/  
**Records:** 2,206 headwords + 3,179 example sentences = 5,385 total  
**License:** Scholarly digitisation (public domain)  
**Notes:** Dictionary headwords extracted with tone marks. Example sentences provide usage context for lexical items. Important resource for low-frequency and specialized vocabulary.  

### 3. Melzian Dictionary  
**Type:** Lexical reference  
**Domain:** Edo-English bilingual dictionary (historical orthography)  
**Original URL:** https://centreforedostudies.be/Melzian-epub-final/  
**Records:** 1,541 headwords + 3,722 example sentences = 5,263 total  
**License:** Scholarly digitisation (public domain)  
**Notes:** Older orthographic conventions than modern standard; provides diachronic insight into language variation. Includes both standard and variant spellings.  

### 4. Thomas Dictionary
**Type:** Lexical reference  
**Domain:** Edo dictionary (historical orthography)  
**Original URL:** https://centreforedostudies.be/Thomas/text/  
**Records:** 279 headwords  
**License:** Scholarly digitisation (public domain)  
**Notes:** Represents older transcription conventions. Non-standard combining marks were removed during cleaning while preserving base characters. Smaller set than other dictionaries but valuable for historical comparison.  

### 5. Thomas Corpus (Stories)
**Type:** Narrative prose  
**Domain:** Traditional stories and cultural narratives  
**Original URL:** https://centreforedostudies.be/Thomas/corpus/  
**Records:** 1,023 sentences (27 stories)  
**License:** Scholarly digitisation (public domain)  
**Notes:** Most extensive narrative source. Stories marked with contextual metadata (story/page information). Represents diverse narrative genres and vocabulary.  

### 6. Egharevba Biography
**Type:** Prose autobiography  
**Domain:** Personal narrative (historical)  
**Original URL:** https://centreforedostudies.be/Egharevba/  
**Records:** 2,393 sentences  
**License:** Scholarly digitisation (public domain)  
**Notes:** Pure Edo prose autobiography ("Itan ẹdagbọn mwen" — "The Life Story of My People"). No English translation. Represents formal written Edo and provides genre diversity. Includes chapter-level metadata.  

### 7. Bristol Welfare Leaflet
**Type:** Practical/instructional document  
**Domain:** Public health information  
**Original URL:** https://centreforedostudies.be/Bristol/  
**Format:** PDF (automatically extracted)  
**Records:** 57 sentences  
**License:** Public domain  
**Notes:** Modern practical Edo text. Demonstrates use of Edo for contemporary civic/health communication. Smaller contribution but important for domain diversity.

## Data Fields

### Monolingual File (edo_cleaned.jsonl / edo_cleaned.txt)
Each record contains:

- **text** (string): The Edo sentence or phrase, NFC-normalised, with whitespace cleaned
- **source** (string): Identifier for originating source, formatted as `{source}_{subtype}`, e.g.:
  - `agheyisi_corpus_tale1`
  - `agheyisi_dictionary`
  - `agheyisi_dictionary_example`
  - `thomas_corpus`
  - `thomas_dictionary`
  - `egharevba_biography`
  - `bristol_welfare_leaflet`
  - `melzian_dictionary`
  - `melzian_dictionary_example`
- **lang** (string): Always `"edo"`
- **chapter** (string, optional): Chapter identifier for Egharevba records (e.g., `"Chapter-01"`)
- **page** (string, optional): Page/story identifier for Thomas corpus records (e.g., `"corpus-17"`)

### File Formats
- **edo_cleaned.jsonl**: Structured format, one JSON record per line
- **edo_cleaned.txt**: Plain text, one sentence per line (whitespace-separated, no newlines within records)

## Data Cleaning & Normalization

**Processing steps applied:**
1. **Non-standard combining marks removed**: Thomas dictionary entries had non-standard Unicode combining marks (U+030D, U+0309, U+035E, etc.) that were stripped while preserving base characters
2. **English translation removal**: Monolingual dataset — parallel English translations systematically removed (>85% ASCII content, stopword ratio > 50%)
3. **Unicode normalisation**: All text normalised to NFC form
4. **Deduplication**: Identical records (case-insensitive) removed; 19,657 raw records → 12,646 unique records
5. **Whitespace cleaning**: Multiple spaces collapsed to single space; leading/trailing whitespace stripped
6. **Validation**: Corpus entries required to contain at least one Edo-specific diacritical character; dictionary headwords validated for length and format

**Markers used for Edo language identification:**
```
ẹọẸỌɛƐɔɽãÃṣṢʼʻẽẼõÕ
```

## Dataset Statistics

| Metric | Value |
|--------|-------|
| **Total records** | 12,646 |
| **Total size** | 420 KB (plain text) |
| **Unique sentences** | 12,646 (100% unique after deduplication) |
| **Average record length** | 42 characters |
| **Longest record** | 458 characters |
| **Records with tone marks** | ~95% |
| **Records with underdots** | ~87% |

### Breakdown by Source

| Source | Records | Percentage | Type |
|--------|---------|-----------|------|
| Agheyisi Dictionary & Examples | 5,385 | 42.6% | Lexical |
| Melzian Dictionary & Examples | 5,263 | 41.6% | Lexical |
| Egharevba Biography | 2,393 | 18.9% | Narrative |
| Thomas Corpus | 1,023 | 8.1% | Narrative |
| Agheyisi Corpus (Folktales) | 164 | 1.3% | Narrative |
| Bristol Welfare Leaflet | 57 | 0.5% | Instructional |
| Thomas Dictionary | 279 | 2.2% | Lexical |

### Domain Distribution

| Domain | Records | Percentage |
|--------|---------|-----------|
| **Lexical (dictionaries)** | 9,168 | 72.5% |
| **Narrative (stories/biography)** | 3,580 | 28.3% |
| **Instructional** | 57 | 0.5% |
| **Prose** | 12,646 | 100% |

## Data Collection Methodology

All source texts were digitised by the [Centre for Edo Studies](https://centreforedostudies.be/) through scholarly research and are made available for academic use. Extraction and cleaning were performed programmatically with manual review of edge cases. No synthetic data or machine translation was used.

## Ethical Considerations

- All source materials are from public domain scholarly digitisations or materials explicitly made public for educational use
- Dataset preserves historical orthographic variants, providing diachronic perspective on language
- Dictionary entries maintain tone marks and diacritical marks as attested in original sources
- No personally identifiable information in corpus
- Suitable for training language models, conducting linguistic analysis, and supporting Edo language technology development

## Limitations

- **Orthographic variation**: Older sources (Thomas, Melzian) use non-standard orthography compared to modern Edo; users should be aware of this variation
- **Domain bias**: Lexical sources (dictionaries) comprise 72.5% of corpus; narrative/contemporary text underrepresented
- **Size**: 12.6K sentences is small by modern NLP standards; best suited for linguistic analysis, dictionary/lexicon development, and initial model pretraining rather than large-scale deep learning
- **Tonal annotation**: Tone marks present but not structurally annotated; no separate morphological/syntactic annotation
- **Historical**: Some texts date to mid-20th century; contemporary Edo may differ

## Recommended Citation

```bibtex
@dataset{edo_corpus_2024,
  title={Edo (Bini) Monolingual Text Corpus},
  author={[Your Name/Organization]},
  year={2024},
  url={https://github.com/[your-repo]},
  note={Compiled from sources digitised by the Centre for Edo Studies}
}
```

## Further Information

- **Centre for Edo Studies:** https://centreforedostudies.be/
- **Edo language (Ethnologue):** https://www.ethnologue.com/language/bin/
- **ISO 639-3 (Edo):** https://iso639-3.sil.org/code/bin

---

**Dataset Version:** 1.0  
**Last Updated:** May 2024  
**License:** Public Domain (all sources are public domain digitisations)
