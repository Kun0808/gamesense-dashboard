# Notebooks

The notebooks are numbered in the order in which they are run; stage 1 (data collection) has no notebook. Every notebook starts with a header table (purpose, inputs, outputs, runtime, dependencies) and sets `PROJECT_ROOT` in its first code cell; all of them were run in Google Colab with a Google Drive project folder (`MyDrive/GameSense`).

| # | Notebook | What it does | Runtime |
|---|---|---|---|
| 1 | (no notebook) | Review snapshot collected in August 2026 with google-play-scraper; the collection code was not kept. See [`docs/DATA.md`](../docs/DATA.md) | n/a |
| 2 | `02_gold_annotation.ipynb` | Build the 500-sentence gold set (taxonomy, applicability, lexicon pre-labels, review tool) | CPU, manual |
| 3 | `03_baselines_and_bert_training.ipynb` | Baselines and BERT for Tasks 1 to 3, Task 2 cross-validation, final models | GPU |
| 4 | `04_full_inference_and_issue_profiles.ipynb` | Score every review and every (sentence, aspect) pair, sentiment audit, Task 3 version 2 | GPU |
| 5 | `05_supplementary_validation.ipynb` | Leakage and duplicate checks, S5 blind validation, data-quality audits | GPU / CPU |
| 6a | `06a_second_annotator_tool.ipynb` | Interactive tool used by the second annotator (80 sentences, blind to the gold labels) | CPU, manual |
| 6b | `06b_inter_annotator_agreement_and_adjudication.ipynb` | Agreement statistics, disagreements and adjudication | CPU |
| 7 | `07_full_pipeline.ipynb` | **Main notebook:** final labels, cross-validation, ensemble, issue priority, analyses, baselines, error analysis | GPU |
| 8 | `08_label_audit.ipynb` | Blind re-labelling of 60 pairs to estimate label noise | CPU, manual |
| 9 | `09_dashboard_data_export.ipynb` | Build the dashboard data and export every generated repository file as one checked zip | CPU |
| 10 | `10_data_release_export.ipynb` | Scan for personal-data patterns and export a de-identified copy of the data | CPU |
| 11 | `11_dashboard_evaluation.ipynb` | Evaluate the published dashboard: recompute its numbers, test every page, check the live link | CPU |

## Which notebook produces what

* Final numbers, tables and figures of the report: notebook 7 (`outputs/final_v4/`).
* The Task 1 model and the Task 2 final model used by notebook 7: notebook 3.
* Full-corpus predictions used by notebooks 7 and 9: notebook 4.
* Labels used for training Task 3: notebooks 2, 4, 5, 6a and 6b (gold, audit, S5 validation, second annotation and adjudication), merged in notebook 7.
* Everything the dashboard reads: notebook 9.
* The de-identified data package for archiving: notebook 10.
* The evaluation of the published dashboard: notebook 11 (results in `docs/EVALUATION.md`).

## Conventions

* Folders under `PROJECT_ROOT`: `data/raw`, `data/processed`, `data/annotation_v2`, `scripts`, `models`, `outputs`.
* `scripts/aspect_taxonomy.py` is the single source of truth for the 12 aspects, their descriptions and keywords. Notebooks import it and never redefine it.
* Output folders carry a version suffix (`final_v4`, `predictions_v4_ens`, `dashboard_v4`) so earlier results are never overwritten.
* `DRY_RUN = True` in notebook 7 runs a short smoke test and writes to `*_dryrun` folders.
* Outputs are cleared in the files committed here; run a notebook to regenerate them. Notebooks that call for human labelling (2, 6, 8) are interactive.

## Not part of the final pipeline

Earlier or superseded notebooks are kept out of this folder on purpose: the first annotation pilot (a zero-shot approach that was dropped), the first Task 3 retraining notebook, the version 3 training notebook (replaced by notebook 7) and a housekeeping notebook that deletes training checkpoints.
