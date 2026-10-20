# Offline model-evaluation figures for GameSense.
# The numbers are copied from the result tables of the final run (outputs/final_v4, shown on the dashboard's "Method & reliability" page):
#   Fig 1: task1/task2/task3 overall tables and baselines; Fig 2: Task 1 per-class F1 and predictions per star rating;
#   Fig 3: task2_by_aspect_all_models; Fig 4: label_audit_summary and the second-annotator agreement summary.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
BLUE, GREY, ORANGE, GREEN, RED, INK, LG = "#2E5597", "#9AA5B1", "#C9741B", "#4E9F6B", "#C0504D", "#1F2937", "#E5E7EB"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#9CA3AF", "axes.titleweight": "bold", "axes.titlesize": 13, "figure.facecolor": "white"})

# ---------- Figure 1: macro-F1 against baselines and targets
fig, ax = plt.subplots(figsize=(11, 5.6))
groups = ["Task 1\noverall sentiment\n(3 classes)", "Task 2\naspect detection\n(macro-F1)", "Task 3\naspect sentiment\n(3 classes)", "Task 3\nnegative vs rest"]
bert = [0.664, 0.611, 0.566, 0.801]; tfidf = [0.631, 0.397, 0.545, 0.747]; lex = [np.nan, 0.620, 0.461, 0.609]; target = [0.80, 0.70, 0.70, np.nan]
x = np.arange(4); w = 0.24
for dx, vals, col, lab in ((-w, tfidf, GREY, "TF-IDF baseline"), (0, lex, ORANGE, "Keyword / lexicon baseline"), (w, bert, BLUE, "BERT")):
    b = ax.bar(x + dx, [0 if np.isnan(v) else v for v in vals], w, color=col, label=lab)
    for xi, v in zip(x + dx, vals):
        if not np.isnan(v): ax.text(xi, v + 0.012, f"{v:.3f}", ha="center", fontsize=9.5, color=INK)
for xi, t in zip(x, target):
    if not np.isnan(t): ax.plot([xi - 0.4, xi + 0.4], [t, t], color=RED, ls="--", lw=1.6); ax.text(xi, t + 0.012, f"target {t:.2f}", color=RED, fontsize=9, va="bottom", ha="center", bbox=dict(fc="white", ec="none", pad=1.2))
ax.set_xticks(x); ax.set_xticklabels(groups); ax.set_ylim(0, 0.95); ax.set_ylabel("macro-F1")
ax.set_title("BERT beats TF-IDF on every task, but none of the three proposal targets was reached", loc="left")
ax.text(0 , 0.025, "n/a", ha="center", fontsize=9, color="#6B7280")
ax.legend(frameon=False, loc="upper left", ncol=3, bbox_to_anchor=(0, 1.0))
fig.text(0.01, 0.005, "Task 1: held-out test (5,097 reviews). Tasks 2 and 3: 5-fold cross-validation grouped by review. Task 2 threshold 0.30. Task 3 lexicon baseline: Hu & Liu opinion lexicon with negation.\nIn Task 2 the keyword baseline is slightly ahead only because of one aspect with 4 examples (BERT scores 0 on it).", fontsize=8.5, color="#6B7280")
fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig("fig1_macro_f1_vs_baselines_and_targets.png", dpi=170); plt.close(fig)

# ---------- Figure 2: the neutral class
fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2), gridspec_kw={"width_ratios": [1.25, 1]})
ax = axes[0]; cls = ["negative", "neutral", "positive"]; f1 = [0.859, 0.248, 0.885]; share = [2090, 253, 2754]; tot = sum(share)
bars = ax.bar(cls, f1, color=[RED, GREY, GREEN], width=0.6)
for b, v, s in zip(bars, f1, share): ax.text(b.get_x() + b.get_width() / 2, v + 0.015, f"F1 {v:.2f}", ha="center", fontsize=11, fontweight="bold", color=INK); ax.text(b.get_x() + b.get_width() / 2, 0.03, f"{100 * s / tot:.0f}% of reviews\n(n = {s:,})", ha="center", fontsize=9.5, color="white" if v > 0.3 else INK)
ax.set_ylim(0, 1.05); ax.set_ylabel("F1"); ax.set_title("Task 1: neutral is the weak class", loc="left")
ax = axes[1]
stars = ["1", "2", "3", "4", "5"]; neg = [87.1, 65.0, 31.6, 14.3, 5.1]; neu = [7.0, 23.3, 37.5, 31.1, 5.2]; pos = [5.9, 11.7, 30.8, 54.6, 89.7]
ax.bar(stars, neg, color=RED, label="predicted negative"); ax.bar(stars, neu, bottom=neg, color=GREY, label="predicted neutral"); ax.bar(stars, pos, bottom=np.array(neg) + np.array(neu), color=GREEN, label="predicted positive")
for i in range(5):
    for val, bot in ((neg[i], 0), (neu[i], neg[i]), (pos[i], neg[i] + neu[i])):
        if val >= 9: ax.text(i, bot + val / 2, f"{val:.0f}%", ha="center", va="center", fontsize=9, color="white")
ax.set_xlabel("star rating of the review (3 stars carry the neutral label)"); ax.set_ylabel("% of reviews"); ax.set_ylim(0, 100); ax.set_title("What the model predicts per star rating", loc="left")
ax.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
fig.suptitle("The gap to the targets comes mainly from the neutral class", x=0.01, ha="left", fontsize=14, fontweight="bold", y=0.99)
fig.text(0.01, 0.005, "Task 3 has about 35 neutral pairs and recovers 2 of them.", fontsize=9, color="#6B7280")
fig.tight_layout(rect=(0, 0.03, 1, 0.94)); fig.savefig("fig2_neutral_class.png", dpi=170); plt.close(fig)

# ---------- Figure 3: Task 2 F1 per aspect
asp = ["performance_stability", "monetization_value", "advertisement", "level_difficulty_balance", "content_progression", "paywall", "gacha_rates", "character_operator_balance", "matchmaking", "cheating", "grind_progression", "account_support"]
sup = [71, 42, 18, 35, 78, 22, 25, 24, 40, 15, 4, 58]
t = [0.278, 0.290, 0.714, 0.365, 0.298, 0.632, 0.500, 0.322, 0.578, 0.308, 0.000, 0.476]
b_ = [0.738, 0.710, 0.971, 0.611, 0.581, 0.612, 0.625, 0.481, 0.789, 0.364, 0.000, 0.845]
k = [0.678, 0.696, 0.381, 0.500, 0.516, 0.743, 0.609, 0.612, 0.725, 0.529, 0.667, 0.779]
order = np.argsort(b_)[::-1]; y = np.arange(12)[::-1]; h = 0.26
fig, ax = plt.subplots(figsize=(11, 7))
for dy, vals, col, lab in ((h, t, GREY, "TF-IDF"), (0, k, ORANGE, "Keyword"), (-h, b_, BLUE, "BERT")):
    ax.barh(y + dy, [vals[i] for i in order], h, color=col, label=lab)
ax.set_yticks(y); ax.set_yticklabels([f"{asp[i].replace('_', ' ')}  (n={sup[i]})" for i in order]); ax.set_xlim(0, 1.08); ax.set_xlabel("F1 at threshold 0.30 (5-fold cross-validation)")
for yi, i in zip(y, order): ax.text(b_[i] + 0.012, yi - h, f"{b_[i]:.2f}", va="center", fontsize=8.5, color=BLUE)
ax.legend(frameon=False, loc="lower right"); fig.suptitle("Task 2: BERT is ahead on 8 of 12 aspects; keywords win on 4 with literal wording", x=0.01, ha="left", fontsize=14, fontweight="bold", y=0.985)
fig.text(0.01, 0.005, "n = number of gold sentences with the aspect. Keywords win on paywall, character operator balance, cheating and grind progression (4 examples, so that score is not reliable).", fontsize=8.5, color="#6B7280")
fig.tight_layout(rect=(0, 0.03, 1, 0.95)); fig.savefig("fig3_task2_f1_per_aspect.png", dpi=170); plt.close(fig)

# ---------- Figure 4: label quality
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
ax = axes[0]; names = ["random\nsample (n=30)", "most confident\ndisagreements (n=30)"]; diff = [6, 14]; lo = [0.10, 0.30]; hi = [0.37, 0.64]
vals = [d / 30 for d in diff]; ax.bar(names, vals, color=[BLUE, ORANGE], width=0.5, yerr=[[v - l for v, l in zip(vals, lo)], [h_ - v for v, h_ in zip(vals, hi)]], capsize=6, ecolor=INK)
for i, (v, d) in enumerate(zip(vals, diff)): ax.text(i, hi[i] + 0.035, f"{d} of 30 differ ({100 * v:.0f}%)", ha="center", fontsize=10, color=INK)
ax.set_ylim(0, 0.85); ax.set_ylabel("share of labels that differ on blind re-labelling"); ax.set_title("Blind re-labelling of 60 pairs", loc="left")
ax = axes[1]; ax.axis("off")
rows = [("Second annotator agreement", "kappa 0.74 (95% CI 0.63 to 0.84)"), ("Sentences double-annotated", "80 (16% of the gold set)"), ("Disagreements adjudicated", "45"),
        ("Blind random sample", "no negative / positive flips"), ("Blind random sample, kappa", "0.63"), ("Confident disagreements that agree\nwith the model after re-labelling", "9 of 14")]
ax.set_title("Label quality at a glance", loc="left")
for i, (a, b2) in enumerate(rows):
    yy = 0.92 - i * 0.155; ax.text(0.0, yy, a, fontsize=10.5, color=INK, va="center", transform=ax.transAxes); ax.text(1.0, yy, b2, fontsize=10.5, color=BLUE, va="center", ha="right", fontweight="bold", transform=ax.transAxes)
    ax.plot([0, 1], [yy - 0.07, yy - 0.07], color=LG, lw=1, transform=ax.transAxes)
fig.text(0.01, 0.005, "The re-labelling was done by the original annotator, so it measures consistency over time and probably understates label noise.", fontsize=8.5, color="#6B7280")
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("fig4_label_quality.png", dpi=170); plt.close(fig)
print("done")
