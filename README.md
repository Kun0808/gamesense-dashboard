# GameSense: issue prioritisation from mobile-game reviews

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gamesense-dashboard-plp.streamlit.app)

**Live dashboard:** https://gamesense-dashboard-plp.streamlit.app

GameSense reads Google Play reviews of five mobile games and answers one practical question for a game team: **which problems should we fix first?** It detects which gameplay aspects a review sentence talks about (performance, ads, monetisation, matchmaking, ...), decides whether each mention is negative, and ranks aspects by *negative mentions per 100 review sentences*.

Course project, NUS-ISS Practical Language Processing (PLP), Group 5.
Team: Bao Kun, Li Wen

## What the dashboard shows

| Page | What you can do |
|---|---|
| Issue priority | Pick a game and see its ranked problems, with a reliability flag and the range of ranks across five model runs |
| Trends | Follow an aspect over time (all markets or US only), with weak windows marked |
| Cross-game comparison | Compare the seven aspects shared by all games |
| Review explorer | Read the actual sentences behind the numbers, with filters and CSV download |
| Version analysis | Compare reviews before and after an app update (descriptive only) |
| Method & reliability | Evaluation tables, data and market composition, and limitations |

## Data

- Five games: Royal Match, Genshin Impact, Mobile Legends, PUBG Mobile, Arknights.
- 33,977 English reviews collected from Google Play (collection ends 2026-08-22), split into 62,466 sentences.
- 12 aspects: 7 shared by all games and 5 specific to a game genre (for example gacha rates, matchmaking, cheating).
- A hand-labelled set of 500 sentences (100 per game), plus audit and validation labels, with a second annotator checking a sample (overall agreement kappa about 0.74).

Reviews are public Google Play text. No usernames, profile images or other personal identifiers are included in this repository.

## Method

```
Google Play reviews
   -> sentence split
   -> Task 1  overall review sentiment        (BERT, star-derived labels)
   -> Task 2  aspect detection per sentence   (multi-label BERT, 12 aspects)
   -> Task 3  sentiment of each (sentence, aspect) pair   (BERT, 3 classes)
   -> issue priority = negative mentions per 100 sentences
```

Models are `bert-base-uncased`, fine-tuned and compared with TF-IDF + logistic regression baselines. Task 2 and Task 3 are evaluated with 5-fold cross-validation grouped by review, and Task 3 results are averaged over five random seeds for the dashboard.

## Main results

| Task | Measure | BERT | TF-IDF baseline | Proposal target |
|---|---|---|---|---|
| 1. Overall sentiment | macro-F1 | 0.664 | 0.631 | 0.80 |
| 2. Aspect detection | macro-F1 (threshold 0.30, cross-validated) | 0.611 | 0.397 | 0.70 |
| 3. Aspect sentiment | macro-F1, 3 classes | 0.566 | 0.545 | 0.70 |
| 3. Aspect sentiment | macro-F1, negative vs rest | 0.801 | 0.747 | n/a |

The proposal targets were directional goals set before piloting. They were not reached on the three-class tasks, and we report this openly together with per-aspect results (see the *Method & reliability* page).

## Limitations

- Aspect sentiment was trained on a few hundred labelled pairs; the neutral class is rarely predicted correctly, so negative-vs-rest is the more meaningful measure. The three-class difference between BERT and the baseline is not statistically clear.
- For complaint-dominated aspects (performance, matchmaking, cheating) almost every mention is negative, so their ranking mainly reflects how often they are mentioned.
- Advertisement and account-support sentiment may be over-predicted as negative; paywall has few labelled examples.
- Task 1 is evaluated against star-derived labels, which are only a noisy proxy for what reviewers mean.
- Reviews come from several Play Store markets, and non-US reviews are concentrated in later weeks for some games.
- Version analysis is descriptive, depends on where the comparison window starts, and cannot show that an update caused a change.
- Reviewers are a self-selected sample, not all players.

## Repository structure

```
app.py                  Streamlit dashboard (reads only the files in data/)
requirements.txt        Python dependencies for the dashboard
.streamlit/config.toml  Theme
data/                   Pre-computed results used by the dashboard
  pairs.parquet           (sentence, aspect) predictions with sentiment
  reviews_meta.parquet    review-level metadata
  examples.parquet        representative negative examples
  trend.csv               trend tables by game, aspect and window
  issue_priority_by_game.csv, cross_game_common_*.csv
  version_*.csv, market_composition.csv, nonUS_share_by_window.csv
  task2_*.csv, task3_*.csv, proposal_check.csv, run_manifest.json
src/aspect_taxonomy.py  Aspect names and descriptions
docs/figures/           Figures used in the report
```

Model weights and the raw scraped reviews are not stored here because of their size.

## Run the dashboard locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Reproducing the results

The data preparation, annotation, training, evaluation and analysis were run as Google Colab notebooks that read from a private Google Drive project folder. Their order is:

1. Collection, cleaning and sentence splitting
2. Annotation and agreement checks
3. Baselines and BERT training (Tasks 1 to 3)
4. Full pipeline run: label merging, cross-validation, final models, ensemble, issue priority, version analysis
5. Dashboard data pack and this repository

`data/run_manifest.json` records the model name, seeds and training settings of the final run.
