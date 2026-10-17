# GameSense: issue prioritisation from mobile-game reviews

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gamesense-dashboard-plp.streamlit.app)

**Live dashboard:** https://gamesense-dashboard-plp.streamlit.app

GameSense reads Google Play reviews of five mobile games and answers one practical question for a game team: **which problems should we fix first?** It detects which gameplay aspects a review sentence talks about (performance, ads, monetisation, matchmaking, ...), decides whether each mention is negative, and ranks aspects by *negative mentions per 100 review sentences*.

Course project, NUS-ISS Practical Language Processing (PLP), Group 5.
Team: Bao Kun, Li Wen, [add the other members].

## What the dashboard shows

| Page | What you can do |
|---|---|
| Overview | Review volume, star ratings, overall sentiment and review counts over time |
| Issue priority | Pick a game and see its ranked problems, with a reliability flag and the range of ranks across five model runs |
| Aspect sentiment | How negative, neutral and positive the mentions of each aspect are |
| Trends | Follow an aspect over time (US reviews by default), with weak windows and mixed-market periods marked |
| Cross-game comparison | Compare the seven aspects shared by all games |
| Review explorer | Read the actual sentences behind the numbers; filter by game, aspect, rating, app version, date and sentiment |
| Version analysis | Compare reviews before and after an app update (descriptive only), including how sensitive the result is to the window |
| Method & reliability | Baselines, error analysis, label audit, evaluation tables, data and market composition, limitations |

## Data

* A fixed snapshot of **33,977 English-language Google Play reviews** (62,466 sentences) of Royal Match, Genshin Impact, Mobile Legends, PUBG Mobile and Arknights, collected in August 2026; the latest review is dated 21 August 2026. No later updates were collected.
* 12 aspects: 7 shared by all games and 5 specific to a game genre (for example gacha rates, matchmaking, cheating).
* A hand-labelled set of 500 sentences (100 per game) plus audit and validation labels (757 labelled aspect-sentiment pairs in total), with a second annotator checking part of the gold set (Cohen's kappa about 0.74).

Reviews are public Google Play text. No usernames, profile images or other personal identifiers are included in this repository, and e-mail addresses, links, @handles and long numbers (possible game ids) are removed from the sentences shown in the dashboard. See [`docs/DATA.md`](docs/DATA.md) for the data card: provenance, columns, preparation steps, quality checks and limitations.

## Method

```
Google Play reviews
   -> sentence split
   -> Task 1  overall review sentiment        (BERT, star-derived labels)
   -> Task 2  aspect detection per sentence   (multi-label BERT, 12 aspects)
   -> Task 3  sentiment of each (sentence, aspect) pair   (BERT, 3 classes)
   -> issue priority = negative mentions per 100 sentences
```

Models are `bert-base-uncased`, fine-tuned and compared with TF-IDF + logistic regression baselines and with keyword/lexicon baselines. Task 2 and Task 3 are evaluated with 5-fold cross-validation grouped by review, and Task 3 results are averaged over five random seeds for the dashboard.

## Main results

| Task | Measure | BERT | TF-IDF baseline | Keyword / lexicon baseline | Proposal target |
|---|---|---|---|---|---|
| 1. Overall sentiment | macro-F1 | 0.664 | 0.631 | n/a | 0.80 |
| 2. Aspect detection | macro-F1 (threshold 0.30, cross-validated) | 0.611 | 0.397 | 0.620 | 0.70 |
| 3. Aspect sentiment | macro-F1, 3 classes | 0.566 | 0.545 | 0.461 | 0.70 |
| 3. Aspect sentiment | macro-F1, negative vs rest | 0.801 | 0.747 | 0.609 | n/a |

For Task 3 the lexicon baseline is the Hu & Liu opinion lexicon with negation handling, applied to the whole sentence (it does not know which aspect is meant).

The proposal targets were directional goals set before piloting. They were not reached on the three-class tasks, and we report this openly. The neutral class is the main reason: it is only 5% of the reviews, its F1 is 0.25 in Task 1, and Task 3 has about 35 neutral pairs. Negative and positive F1 in Task 1 are 0.86 and 0.89. In Task 2 the keyword baseline is slightly ahead on macro-F1 only because one aspect has 4 labelled examples; without it BERT scores 0.666 against 0.615. The keyword baseline also benefits from the keyword pre-filling used during annotation.

Further evidence is on the *Method & reliability* page: errors cluster in sentences with contrast words ("but", "however") and in rare aspects, and a blind re-labelling of 60 pairs found no negative/positive flips in a random sample of 30 (differences involved the neutral class or whether the aspect was mentioned).

## Limitations

* Aspect sentiment was trained on a few hundred labelled pairs; the neutral class is rarely predicted correctly, so negative-vs-rest is the more meaningful measure. The three-class difference between BERT and the baseline is not statistically clear.
* For complaint-dominated aspects (performance, matchmaking, cheating) almost every mention is negative, so their ranking mainly reflects how often they are mentioned.
* Advertisement and account-support sentiment may be over-predicted as negative; paywall has few labelled examples.
* Task 1 is evaluated against star-derived labels, which are only a noisy proxy for what reviewers mean.
* The data is a fixed snapshot. For four games the US reviews end in early August, so the latest weeks contain only non-US reviews; the dashboard uses US reviews by default for trends.
* About 4% of the reviews repeat the text of an earlier review and were kept.
* Version analysis is descriptive, depends on where the comparison window starts, and cannot show that an update caused a change.
* The label audit was done by the original annotator, so it measures consistency over time and probably understates label noise.
* Reviewers are a self-selected sample, not all players.

## Repository structure

```
app.py                       Streamlit dashboard (reads only the files in data/)
requirements.txt             Python dependencies of the dashboard
requirements-pipeline.txt    Python dependencies of the notebooks
.streamlit/config.toml       Theme
data/                        Pre-computed results used by the dashboard
  pairs.parquet                (sentence, aspect) predictions with sentiment
  reviews_meta.parquet         review-level metadata
  examples.parquet             representative negative examples
  trend.csv                    trend tables by game, aspect and window
  issue_priority_by_game.csv, cross_game_common_*.csv
  version_*.csv, market_composition.csv, nonUS_share_by_window.csv
  task1_*.csv, task2_*.csv, task3_*.csv, baselines_*.csv, label_audit_summary.csv
  proposal_check.csv, run_manifest.json
src/aspect_taxonomy.py       The 12 aspects: names, definitions, keywords
notebooks/                   The analysis notebooks, numbered in run order (see notebooks/README.md)
docs/DATA.md                 Data card
docs/REPRODUCING.md          How to reproduce the results
docs/figures/                Figures used in the report
```

Model weights and the full review files (they contain user names) are not stored here because of their size and privacy.

## Run the dashboard locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Reproducing the results

The analysis was run as Google Colab notebooks on a Google Drive project folder. [`docs/REPRODUCING.md`](docs/REPRODUCING.md) explains three levels (run the dashboard, rebuild the results, rerun the whole pipeline), the environment, the folder layout, what cannot be reproduced exactly and the numbers to check against. The notebooks and their run order are in [`notebooks/`](notebooks/README.md). The de-identified data package is archived in a separate private repository (`Kun0808/gamesense-data`); access can be granted on request.
