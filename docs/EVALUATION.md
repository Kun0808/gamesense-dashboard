# Dashboard evaluation

The dashboard is evaluated at two levels: **offline** (are the numbers it shows correct?) and **online** (does the live system work for a user?). The model evaluation (cross-validation, baselines, error analysis, label audit) is separate and is reported on the dashboard's *Method & reliability* page and in `docs/DATA.md` and `README.md`.

The evaluation is reproducible with `notebooks/11_dashboard_evaluation.ipynb`. The numbers below come from one run of that notebook against the published repository.

## Run it yourself

No Google Drive and no account is needed. Open the notebook in Google Colab and run the cells from top to bottom (about 2 minutes, CPU):

[Open `11_dashboard_evaluation.ipynb` in Colab](https://colab.research.google.com/github/Kun0808/gamesense-dashboard/blob/main/notebooks/11_dashboard_evaluation.ipynb)

The notebook clones this public repository, recomputes the numbers, tests the pages and requests the public dashboard link.

## Summary

| Level | Question | Method | Result |
|---|---|---|---|
| Offline | Are the numbers on the dashboard correct? | 25 checks recompute what the dashboard shows from its own base tables | 25 of 25 passed |
| Online, functional | Does every page and filter work? | 37 scenarios with Streamlit's test runner (8 pages, 5 games on 3 pages, main filters, content assertions) | 37 of 37 passed |
| Online, live link | Does the public link answer without a login? | Two plain HTTP requests | Status 200 on both, about 1 second |
| Online, users | Can a new user find the answers? | Task test with new users | To be added |

## Offline correctness: what was recomputed

| Area | Checks | What is compared |
|---|---:|---|
| Data | 8 | 33,977 reviews, 62,466 sentences and 34,800 pairs match the documented totals; review ids unique; no duplicate (sentence, aspect) pair; every pair belongs to a known review; sentiment labels and probabilities in range; ratings between 1 and 5; every aspect is in the taxonomy |
| Issue priority | 5 | Every (game, aspect) of the ranking can be recomputed; negative mentions and mentions per 100 sentences equal the recomputed values (largest difference 0.0005, which is rounding); the top issue of every game has the highest recomputed priority; the cross-game table equals the per-game ranking for the seven shared aspects |
| Trends | 5 | Summed over all windows, negative mentions and mentions equal the pair counts for all 44 (game, aspect) combinations, for all markets and for US reviews only; windows with fewer than 100 reviews are flagged |
| Examples | 2 | All 1,272 example sentences are negative pairs of the same game and aspect; examples of the flagged aspects come only from 1 to 2 star reviews |
| Version analysis | 3 | Window sizes and mean stars of Royal Match build 37281 (634 and 709 reviews), build 37743 (796 and 774) and Genshin Impact 6.7.0 (1,283 and 1,293) are recomputed from the review table and match |
| Privacy | 2 | No e-mail address, link, @handle or long number in the dashboard text; no user-name column in any dashboard table |

## Online: functional test and live link

* **Pages and filters.** All eight pages open without an error. The three game-specific pages (issue priority, aspect sentiment, trends) work for all five games. The main filters (1 to 2 star view, all markets and US only, update markers, review explorer search and sentiment filter, flagged-aspect warning) work.
* **What the screen shows.** The Overview page shows 33,977 reviews and 62,466 sentences. The top issue shown for each game has the highest recomputed priority:

| Game | Top issue shown | Negative mentions per 100 sentences |
|---|---|---:|
| Royal Match | Advertisements | 9.43 |
| Genshin Impact | Content & Progression | 15.81 |
| Mobile Legends | Matchmaking & Community | 22.63 |
| PUBG Mobile | Performance & Stability | 13.99 |
| Arknights | Performance & Stability | 10.21 |

* **Speed.** Opening a page for the first time took 1.6 to 4.0 seconds, because the data is loaded; later interactions had a median of 0.2 seconds (largest 4.0 seconds). These times were measured on a Colab CPU, not on Streamlit Cloud.
* **Live link.** The public link answers with status 200 in about 1 second, without a login. The Streamlit Community Cloud health path returns the app page, so it is not a separate health signal.

## Limits of this evaluation

* The test runner simulates user actions without a browser, so it does not check visual layout.
* The checks show that the dashboard is consistent with its base tables; they do not show that the models are right. That is the role of the offline model evaluation.
* No user task test has been run yet; the planned protocol is five fixed questions with new users (answers, time and a three-item rating), reported with the number of users.
