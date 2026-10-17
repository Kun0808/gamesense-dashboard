# Data card

This document describes the review data used in GameSense: where it comes from, what the files contain, what was done to it, and what to keep in mind when using it.

## 1. Summary

A single snapshot of English-language Google Play reviews of five mobile games, collected in August 2026. No later updates were collected.

| Game | Genre | Reviews | Sentences | Markets in the data |
|---|---|---:|---:|---|
| Royal Match | Casual, match-3 | 3,694 | 5,502 | us (3,693), id (1) |
| Genshin Impact | Open-world RPG, gacha | 7,628 | 16,281 | us (6,114), gb (1,510), id (4) |
| Mobile Legends | MOBA | 8,749 | 15,002 | us (6,061), id (2,688) |
| PUBG Mobile | Battle royale | 7,698 | 10,898 | us (6,054), id (1,644) |
| Arknights | Tower defence, strategy | 6,208 | 14,783 | us (6,082), gb (126) |
| **Total** | | **33,977** | **62,466** | |

The proposal planned about 6,000 reviews per game. Four games reach about 6,000 in the US market alone; Royal Match has fewer usable reviews.

### Date range of the reviews, per game and market

| Game | Market | Reviews | Earliest | Latest |
|---|---|---:|---|---|
| Royal Match | us | 3,693 | 2026-06-11 | 2026-08-21 |
| Royal Match | id | 1 | 2026-08-21 | 2026-08-21 |
| Genshin Impact | us | 6,114 | 2026-05-25 | 2026-08-02 |
| Genshin Impact | gb | 1,510 | 2026-08-02 | 2026-08-21 |
| Genshin Impact | id | 4 | 2026-08-21 | 2026-08-21 |
| Mobile Legends | us | 6,061 | 2026-07-09 | 2026-08-02 |
| Mobile Legends | id | 2,688 | 2026-08-02 | 2026-08-21 |
| PUBG Mobile | us | 6,054 | 2026-07-03 | 2026-08-02 |
| PUBG Mobile | id | 1,644 | 2026-08-02 | 2026-08-21 |
| Arknights | us | 6,082 | 2022-11-21 | 2026-08-01 |
| Arknights | gb | 126 | 2026-08-02 | 2026-08-20 |

**How to read this.** For four of the games the latest US review is dated 1 or 2 August, while the non-US reviews and Royal Match run to 20 or 21 August, so the most recent weeks of those four games contain only non-US reviews. Do not assume that the data is complete up to the end of August, and read the recent weeks of those games with care; the dashboard shows US reviews by default and marks periods with a mixed market. The time span also depends on how many reviews a game receives: Arknights has few reviews per week, so its 6,082 US reviews reach back to November 2022, while Royal Match's 3,693 cover ten weeks.

## 2. Provenance

* **Source.** Public Google Play store pages.
* **Tool.** The Python library `google-play-scraper` (as stated in the project proposal, section 5.1).
* **Collected by.** One team member, in August 2026. The per-game raw files are dated 26 August 2026 (in the file name `{game}_2026-08-26.csv`).
* **Collection code and settings were not kept.** The scraper's language, country and count settings are not recorded. What the saved data shows: the reviews are in English (2 of 33,977 look non-English), the markets are `us`, `gb` and `id`, and each game has roughly 6,000 US reviews, except Royal Match.
* **A bi-weekly update script was written but never used.** The team decided not to collect further updates, because the snapshot already exceeds the proposal's volume target (at least 12,000 reviews) and freezing the data keeps every reported number reproducible.

Because reviews on Google Play change over time, collecting again would not return the same data. The saved snapshot is the basis for reproducing the results.

## 3. Files and columns

### Review files

* `data/raw/{game}/{game}_2026-08-26.csv`: the reviews as saved after collection.
* `data/processed/{game}_clean.csv`: the same rows plus three derived columns. **The two files contain exactly the same reviews and identical values in all shared columns** (checked for every game); cleaning only added columns.

| Column | Type | Description | Non-null share |
|---|---|---|---|
| `app_name` | text | Name of the game | 100% |
| `app_id` | text | Google Play package name, for example `com.dreamgames.royalmatch` | 100% |
| `market` | text | Store market the review was retrieved from (`us`, `gb`, `id`) | 100% |
| `reviewId` | text | Unique id of the review | 100% |
| `userName` | text | Reviewer's display name. **Never used in modelling or reporting and not included in this repository** | 100% |
| `content` | text | Review text | 100% |
| `score` | integer | Star rating, 1 to 5 | 100% |
| `thumbsUpCount` | integer | Number of helpful votes | 100% |
| `reviewCreatedVersion` | text or number | App version at the time of the review (formats differ by game, see below) | 64% to 85% |
| `at` | datetime | When the review was submitted | 100% |
| `replyContent` | text | Developer reply, where there is one. Contextual only; not used by the models | see below |
| `content_clean` | text | **Derived.** Review text with URLs removed and whitespace collapsed | 100% |
| `overall_sentiment_weak` | text | **Derived.** Weak label from the star rating: 1 to 2 stars negative, 3 neutral, 4 to 5 positive | 100% |
| `same_user_repeated_content` | boolean | **Derived.** Flag for repeated content by the same user. True for only 6 reviews (2 Royal Match, 2 Genshin Impact, 2 PUBG Mobile) | 100% |

The derivation of `content_clean` and `overall_sentiment_weak` is implemented in `notebooks/02_gold_annotation.ipynb`, Part 5 (`basic_clean_text`, `score_to_weak_sentiment`). The saved files were produced by an earlier script that is no longer available, so the code in the notebook documents the intended rules; it was not used to regenerate the saved files. The exact rule behind `same_user_repeated_content` was not recorded.

**Coverage of the optional columns, per game**

| Game | `reviewCreatedVersion` | `replyContent` |
|---|---:|---:|
| Royal Match | 84.7% | 0.0% |
| Genshin Impact | 63.9% | 50.5% |
| Mobile Legends | 76.2% | 0.1% |
| PUBG Mobile | 66.1% | 18.6% |
| Arknights | 78.8% | 29.4% |

**Version formats differ by game and have to be normalised before comparing versions**

| Game | Format | Examples | Distinct values |
|---|---|---|---:|
| Royal Match | number (build) | 36561, 37281, 37743 | 58 |
| Genshin Impact | `version_build_build` | `6.7.0_45486583_45768959` (use the part before the first underscore: `6.7.0`) | 57 |
| Mobile Legends | four-part version | `2.1.88.12027` | 121 |
| PUBG Mobile | three-part version | `4.4.0` | 44 |
| Arknights | version with suffix | `14.0.01` | 44 |

### Sentence files

* `data/processed/{game}_sentences.parquet`: one row per sentence (spaCy sentencizer on `content_clean`; fragments shorter than 3 characters are dropped, as implemented in `notebooks/02_gold_annotation.ipynb`, Part 5; the saved files come from the earlier script). Columns: `reviewId`, `sentence_idx`, `sentence_text`, `review_score`, `review_overall_sentiment_weak`, `reviewCreatedVersion`, `at`.
* `data/processed/{game}_sentences_weak.parquet`: the same rows plus `weak_aspects` and `weak_sentiment` (keyword and word-list weak labels used to pre-fill annotation) and `sentence_uid` (`reviewId` + `_` + `sentence_idx`).

62,466 sentences in total; the two sets have the same row counts.

## 4. Preparation steps

The proposal (section 5.1) lists the preparation steps below. This table states what the saved data shows for each.

| Proposal step | What happened |
|---|---|
| English-language filtering | Apparently applied when the reviews were retrieved: only 2 of 33,977 reviews look non-English (at least half of the letters outside ASCII). The exact setting is not recorded. |
| Normalisation | `content_clean`: URLs removed, whitespace collapsed. |
| Duplicate removal | No duplicate `reviewId` remains. |
| Near-duplicate removal | **Not applied.** 1,411 reviews (4.2%) repeat the text of an earlier review, most of them short phrases written by different users (for example "good game"). They were kept. Removing near-duplicate texts changed the overall-sentiment score only slightly (macro-F1 0.664 to 0.657 in the leakage check). |
| Removal of empty or very short entries | Applied: the shortest review text has 3 characters (Royal Match, Mobile Legends, PUBG Mobile) or 4 (Genshin Impact, Arknights). |
| Sentence segmentation | Done with the spaCy sentencizer (see above). |

Repeated texts per game: Royal Match 359, Genshin Impact 149, Mobile Legends 349, PUBG Mobile 436, Arknights 118 (repeated copies after the first occurrence).

## 5. Known limitations

* **Single snapshot.** Results describe reviews up to 21 August 2026 and do not reflect later patches.
* **Retrieval structure.** The US reviews of four games end in early August; the latest weeks are non-US only. Non-US reviews have a different rating profile (for example Genshin Impact: average 3.22 stars in gb against 2.49 in us), so trend and version comparisons should use the US reviews or flag the mix. The dashboard does this.
* **Uneven volumes and windows.** Royal Match has about 3,700 reviews; Arknights covers almost four years with few reviews per month.
* **Missing version information.** 15% to 36% of the reviews have no app version, which limits version-aware analysis.
* **Developer replies** exist for only some games (none for Royal Match) and are not used.
* **Repeated texts were kept** (see above).
* **Self-selected sample.** Reviewers are not representative of all players.

## 6. Privacy and sharing

* The reviews are public Google Play text. User names are present in the saved raw and clean CSV files on the project drive but are **never used**, and they are **not included in this repository** or in the shared data.
* Players sometimes type personal data into their reviews (game ids, e-mail addresses, social handles, phone numbers). A scan of the review text found such patterns in only a few dozen of the 62,466 sentences; developer replies also contain support e-mail addresses and links. In the dashboard data and in the exported data package, e-mail addresses, links, @handles, numbers of eight or more digits and phone-like numbers are replaced by the placeholders `[EMAIL]`, `[URL]`, `[HANDLE]`, `[NUMBER]` and `[PHONE]`. The patterns are conservative, so a few harmless numbers are replaced too. The scan and the export are in `notebooks/10_data_release_export.ipynb`.
* `reviewId` identifies a review, not a person.
* This repository contains aggregated results and the (scrubbed) sentences shown in the dashboard; it does not contain the full review files. The de-identified full data is archived separately (see `docs/REPRODUCING.md`).
