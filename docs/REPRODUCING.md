# Reproducing GameSense

This guide explains what can be reproduced, how, and what to expect. There are three levels, from quick to complete.

| Level | What you get | What you need | Effort |
|---|---|---|---|
| **A. Run the dashboard** | The Streamlit application on the saved results | Python, this repository | minutes |
| **B. Rebuild the results and the dashboard data** | Every table, figure and prediction of the report, from the saved intermediate files | Google Colab, the data package, a GPU for notebook 7 | hours |
| **C. Rerun the whole pipeline** | Annotation, model training, full-corpus inference and all analyses | Colab with a GPU, the review snapshot, manual annotation steps | days |

## 1. What cannot be reproduced exactly

* **Data collection.** The reviews are a snapshot from August 2026. The collection code was not kept and Google Play reviews change over time, so collecting again would give different data. Reproduction starts from the saved snapshot. See `docs/DATA.md`.
* **Manual steps.** The gold labels, the second annotator's labels, the adjudication and the blind audit are human judgements. Their saved files are inputs, not outputs.
* **Model training.** Retraining on a GPU is not bit-for-bit reproducible. Seeds are fixed (`42` for the main runs, `1000` to `1004` for the ensemble) and the recipes are recorded in `data/run_manifest.json`, but small differences are expected. The run-to-run variation of the Task 1 and Task 2 models was not measured; for Task 3 the ensemble records the variation across five seeds.

## 2. Environment

* **Dashboard (level A):** Python 3.12 (the version used for testing) and `requirements.txt` (Streamlit, pandas, pyarrow, plotly). Tested with Streamlit 1.65 and Plotly 7.1.
* **Notebooks (levels B and C):** Google Colab. `requirements-pipeline.txt` lists the versions of the final run (Python 3.13, torch 2.11.0, transformers 5.19.0, scikit-learn 1.6.1, pandas 2.2.3, numpy 2.1.3). On Colab most packages are preinstalled; the notebooks run `pip install -U transformers accelerate`. A T4 GPU is enough. A CPU runtime is enough for notebooks 2, 6a, 6b, 8 and 9.
* The model is `bert-base-uncased`, downloaded from the Hugging Face hub on first use.

## 3. Level A: run the dashboard

```bash
git clone https://github.com/Kun0808/gamesense-dashboard.git
cd gamesense-dashboard
pip install -r requirements.txt
streamlit run app.py
```

The dashboard reads only the files in `data/`; no model is run. A hosted copy is at https://gamesense-dashboard-plp.streamlit.app

## 4. Folder layout on the project drive (levels B and C)

The notebooks read and write a Google Drive folder called `GameSense` (set by `PROJECT_ROOT` in the first code cell of each notebook):

```
GameSense/
  scripts/aspect_taxonomy.py        the 12 aspects (also in this repository as src/aspect_taxonomy.py)
  data/raw/{game}/                  review snapshot as saved after collection
  data/processed/                   {game}_clean.csv, {game}_sentences.parquet, {game}_sentences_weak.parquet
  data/annotation_v2/               gold set and annotation samples
  models/                           task1_bert_combined, task2_final, task3_v4, ...
  outputs/                          predictions, supplementary labels, final_v4 tables, dashboard data
```

Fixed inputs that are not produced by any notebook: the review snapshot (`data/raw`, `data/processed`), `scripts/aspect_taxonomy.py`, and the human label files in `outputs/supplementary/` (second annotator, adjudication, validation sample) and `outputs/sentiment_audit.csv`.

## 5. Which notebook does what

Run order and inputs and outputs of every notebook are in `notebooks/README.md` and in the header of each notebook.

| Stage | Notebook | Needs a GPU | Result |
|---|---|---|---|
| 1 | no notebook | | review snapshot (see `docs/DATA.md`) |
| 2 | `02_gold_annotation` | no | gold set |
| 3 | `03_baselines_and_bert_training` | yes | Task 1 and Task 2 models, baselines |
| 4 | `04_full_inference_and_issue_profiles` | yes | predictions for every review and aspect pair |
| 5 | `05_supplementary_validation` | partly | validation sample, leakage and quality checks |
| 6a, 6b | `06a_second_annotator_tool`, `06b_inter_annotator_agreement_and_adjudication` | no | second annotation, agreement, adjudication |
| 7 | `07_full_pipeline` | yes | **all final results** (`outputs/final_v4/`) |
| 8 | `08_label_audit` | no | label-noise estimate |
| 9 | `09_dashboard_data_export` | no | dashboard data and one zip with every generated file of this repository |
| 10 | `10_data_release_export` | no | de-identified copy of the data for archiving (the data package) |
| 11 | `11_dashboard_evaluation` | no | evaluation of the published dashboard (`docs/EVALUATION.md`) |

## 6. Level B: rebuild the results from the saved intermediate files

Prerequisite: the data package (the processed reviews without user names and with personal-data patterns replaced, the label files and the saved predictions; produced by notebook 10) placed in a Drive folder `GameSense` with the layout above, and the Task 1 model in `models/task1_bert_combined`. The data package is archived in the private repository `Kun0808/gamesense-data` (access can be granted on request), separate from the dashboard repository, because the review files are not meant to be published. The model weights are not stored on GitHub because of their size.

1. Open `notebooks/07_full_pipeline.ipynb` in Colab with a T4 GPU.
2. Set `DRY_RUN = True` in the first code cell and run all cells once. This takes a few minutes and writes to `*_dryrun` folders; it checks paths and inputs.
3. Set `DRY_RUN = False` and run all cells. Every cross-validation fold and ensemble seed is saved when finished, so an interrupted run resumes.
4. Open `notebooks/09_dashboard_data_export.ipynb` (CPU) and run it from top to bottom. It builds the dashboard data and downloads `dashboard_data.zip`, which contains the `data/` and `docs/figures/` folders of this repository.

## 7. Level C: rerun the whole pipeline

Run the notebooks in the order of section 5. Notebook 3 trains the Task 1 and Task 2 models, notebook 4 scores the full corpus and creates the audit sample, notebook 5 creates the validation sample and the double-annotation sample, and notebooks 2, 6a and 6b are interactive annotation tools. Plan for manual labelling time.

## 8. Checking that you reproduced the results

These are the numbers produced by the final run.

| Result | Value |
|---|---|
| Reviews / sentences | 33,977 / 62,466 |
| Gold set | 500 sentences (100 per game) |
| Task 3 training table | 757 labelled (sentence, aspect) pairs, 682 reviews |
| Task 1, overall sentiment, held-out test (n=5,097), macro-F1 | BERT 0.664, TF-IDF 0.631 |
| Task 2, aspect detection, 5-fold CV, threshold 0.30, macro-F1 / micro-F1 | BERT 0.611 / 0.680; TF-IDF 0.397 / 0.359; keyword baseline 0.620 / 0.615 |
| Task 3, aspect sentiment, 5-fold CV, macro-F1 (three classes / negative vs rest) | BERT 0.566 / 0.801; TF-IDF 0.545 / 0.747 |
| Agreement with the second annotator | Cohen's kappa about 0.74 overall |
| Blind label audit, random sample of 30 pairs | 6 labels differ (20%), kappa 0.63, no negative/positive flips |
| Top issue per game (negative mentions per 100 sentences) | Royal Match: advertisement; Mobile Legends: matchmaking; Genshin Impact: content progression; PUBG Mobile and Arknights: performance stability |

Notebook 11 checks the published dashboard: 25 of 25 offline checks and 37 of 37 functional scenarios pass (details in `docs/EVALUATION.md`).

Notebook 7 rebuilds the Task 1 test set and checks automatically that its macro-F1 equals the recorded 0.664. The full numbers are in `outputs/final_v4/GameSense_results_v4.xlsx` and `results_registry.json`, and a summary against the proposal's targets is in `data/proposal_check.csv`. If a retrained model gives slightly different values, compare against these within the variation described in section 1.

## 9. Folders that are not needed

The drive also holds earlier versions that were superseded and are kept only for history: `models/task3_final`, `task3_final_v2`, `task3_final_v3*`, `outputs/predictions_v1`, `predictions_v3*`, `dashboard_v2`, `dashboard_v3`, `task3_v3*`, and the notebooks for the first annotation pilot (a zero-shot approach that was dropped because it was unstable) and the version 3 training run (replaced by notebook 7). `checkpoint_cleaning.ipynb` is a housekeeping notebook that deletes training checkpoints to free space.

## 10. Common problems

* **"Required inputs missing" in notebook 7.** The preflight cell lists which files are absent; compare with the inputs in the notebook header.
* **Do not redefine the taxonomy inside a notebook.** Always import `aspect_taxonomy.py`; a copy without the `description` field breaks the annotation tools.
* **Do not upgrade `torch` alone.** Use `pip install -U transformers accelerate` as the notebooks do.
* **Colab disconnects.** Rerun from the top: saved folds, seeds and labelling progress are reused.
* **GPU quota used up.** Notebooks 2, 6a, 6b, 8 and 9 run on a CPU runtime.
