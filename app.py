"""GameSense dashboard: issue prioritisation from mobile-game reviews (aspect-based sentiment analysis).

Reads only pre-computed files in ./data (no model is run here).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "src"))
try:
    from aspect_taxonomy import ASPECT_TAXONOMY
except Exception:                                     # the app still works without the taxonomy file
    ASPECT_TAXONOMY = {}

st.set_page_config(page_title="GameSense", page_icon="🎮", layout="wide")

GAMES = {"royalmatch": "Royal Match", "genshin": "Genshin Impact", "mlbb": "Mobile Legends",
         "pubgm": "PUBG Mobile", "arknights": "Arknights"}
COMMON = ["performance_stability", "monetization_value", "advertisement", "level_difficulty_balance",
          "content_progression", "paywall", "account_support"]
BLUE, GOLD = "#2E5597", "#C9A227"
SENT_COLORS = {"negative": "#C0504D", "neutral": "#9AA5B1", "positive": "#4E9F6B"}
ASPECT_NOTES = {
    "advertisement": "Sentiment for this aspect was flagged in our validation check (the model may over-predict negative). Examples are taken from 1-2 star reviews only.",
    "account_support": "Sentiment for this aspect was flagged in our validation check (the model may over-predict negative). Examples are taken from 1-2 star reviews only.",
    "paywall": "Few labelled examples exist for this aspect, so its sentiment estimate is less reliable.",
    "cheating": "Almost every labelled mention is a complaint, so the negative share is close to 100% and the ranking mostly reflects how often it is mentioned.",
    "matchmaking": "Almost every labelled mention is a complaint, so the negative share is close to 100% and the ranking mostly reflects how often it is mentioned.",
    "performance_stability": "Almost every labelled mention is a complaint, so the negative share is close to 100% and the ranking mostly reflects how often it is mentioned.",
    "grind_progression": "Only a handful of labelled examples exist for this aspect, so treat its sentiment and ranking as indicative only. It is left out of the trend charts.",
}


# ------------------------------------------------------------------ helpers
def aspect_label(a):
    lab = ASPECT_TAXONOMY.get(a, {}).get("label") if isinstance(ASPECT_TAXONOMY, dict) else None
    lab = (lab or str(a).replace("_", " ")).strip()
    return lab[:1].upper() + lab[1:]


@st.cache_data(show_spinner=False)
def read_csv(name, **kw):
    p = DATA / name
    return pd.read_csv(p, **kw) if p.exists() else None


@st.cache_data(show_spinner="Loading data...")
def read_parquet(name):
    p = DATA / name
    return pd.read_parquet(p) if p.exists() else None


@st.cache_data(show_spinner=False)
def read_manifest():
    p = DATA / "run_manifest.json"
    return json.loads(p.read_text()) if p.exists() else {}


def missing(name):
    st.warning(f"`data/{name}` was not found in the repository, so this section cannot be shown.")


def parse_ci(s):
    m = re.findall(r"-?\d+\.?\d*", str(s))
    return (float(m[0]), float(m[1])) if len(m) >= 2 else (np.nan, np.nan)


def game_name(g):
    return GAMES.get(g, g)


def norm_sentiment(series):
    """Overall sentiment may be stored as text or as 0/1/2; return negative / neutral / positive."""
    t = series.astype(str).str.strip().str.lower()
    return t.replace({"0": "negative", "0.0": "negative", "1": "neutral", "1.0": "neutral", "2": "positive", "2.0": "positive"})


def show_table(name, title, caption=None, expanded=False):
    """Show an optional CSV from data/ if it exists."""
    df = read_csv(name)
    if df is None:
        return False
    if str(df.columns[0]).startswith("Unnamed"):
        df = df.rename(columns={df.columns[0]: " "})
    with st.expander(title, expanded=expanded):
        st.dataframe(df, hide_index=True)
        if caption:
            st.caption(caption)
    return True


# ------------------------------------------------------------------ overview
def page_overview():
    st.title("GameSense")
    st.markdown("Which problems should a mobile-game team fix first? GameSense reads Google Play reviews of five games, finds which aspects "
                "players talk about (performance, ads, monetisation, matchmaking, ...), decides whether each mention is negative, "
                "and ranks aspects by **negative mentions per 100 review sentences**. Start here for the big picture, "
                "then open *Issue priority* in the sidebar.")
    meta = read_parquet("reviews_meta.parquet")
    if meta is None:
        return missing("reviews_meta.parquet")
    market = st.radio("Markets", ["All", "US only"], horizontal=True)
    m = meta if market == "All" else meta[meta["market"] == "us"]
    m = m.copy()
    m["Game"] = m["game"].map(game_name)
    m["at"] = pd.to_datetime(m["at"], errors="coerce")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reviews", f"{len(m):,}")
    c2.metric("Review sentences", f"{int(m['n_sentences'].sum()):,}")
    c3.metric("Average stars", f"{m['score'].mean():.2f}")
    if m["at"].notna().any():
        c4.metric("Reviews dated", f"{m['at'].min():%b %Y} - {m['at'].max():%b %Y}")
    t_vol, t_rate, t_sent, t_time = st.tabs(["Review volume", "Star ratings", "Overall sentiment", "Over time"])
    with t_vol:
        v = m.groupby("Game").agg(Reviews=("reviewId", "size"), Sentences=("n_sentences", "sum")).reset_index()
        st.plotly_chart(px.bar(v, x="Game", y="Reviews", text="Reviews", color_discrete_sequence=[BLUE]))
        st.dataframe(v, hide_index=True)
        st.caption("Games differ in how many usable English reviews were collected, so compare rates, not raw counts.")
    with t_rate:
        r = m.dropna(subset=["score"]).groupby(["Game", "score"]).size().reset_index(name="n")
        r["Share"] = 100 * r["n"] / r.groupby("Game")["n"].transform("sum")
        r["Stars"] = r["score"].astype(int).astype(str)
        fig = px.bar(r, x="Game", y="Share", color="Stars", category_orders={"Stars": ["1", "2", "3", "4", "5"]},
                     labels={"Share": "% of reviews"}, color_discrete_sequence=px.colors.sequential.Blues)
        st.plotly_chart(fig)
        st.dataframe(m.groupby("Game")["score"].agg(["mean", "count"]).round(2).rename(columns={"mean": "Average stars", "count": "Reviews"}))
    with t_sent:
        if m["overall"].notna().any():
            o = m.dropna(subset=["overall"]).copy()
            o["Sentiment"] = norm_sentiment(o["overall"])
            share = o.groupby(["Game", "Sentiment"]).size().reset_index(name="n")
            share["Share"] = 100 * share["n"] / share.groupby("Game")["n"].transform("sum")
            fig = px.bar(share, x="Game", y="Share", color="Sentiment", color_discrete_map=SENT_COLORS,
                         category_orders={"Sentiment": ["negative", "neutral", "positive"]}, labels={"Share": "% of reviews"})
            st.plotly_chart(fig)
            st.caption("Overall review sentiment as predicted by the review-level model, which was trained on labels derived from star ratings. "
                       "The neutral class (3-star reviews) is the least reliable.")
        else:
            st.info("Overall sentiment is not available in the data.")
    with t_time:
        if m["at"].notna().any():
            w = m.dropna(subset=["at"]).groupby(["Game", pd.Grouper(key="at", freq="W")]).size().reset_index(name="Reviews")
            st.plotly_chart(px.line(w, x="at", y="Reviews", color="Game", labels={"at": "Week"}))
            st.caption("Each game was collected over a different period, so the date ranges are not the same.")
    with st.expander("What is on the other pages?"):
        st.markdown("- **Issue priority**: ranked problems for one game.\n- **Aspect sentiment**: how negative, neutral and positive mentions split for each aspect.\n"
                    "- **Trends**: aspects over time.\n- **Cross-game comparison**: the seven shared aspects side by side.\n"
                    "- **Review explorer**: the actual sentences, with filters.\n- **Version analysis**: before and after app updates.\n"
                    "- **Method & reliability**: how it was built and where it is weak.")


# ------------------------------------------------------------------ aspect sentiment
def page_aspect_sentiment():
    st.title("Aspect sentiment")
    st.caption("For each aspect: of all sentences that mention it, how many are negative, neutral or positive?")
    pairs = read_parquet("pairs.parquet")
    if pairs is None:
        return missing("pairs.parquet")
    c1, c2, c3 = st.columns(3)
    game = c1.selectbox("Game", list(GAMES), format_func=game_name)
    market = c2.radio("Markets", ["All", "US only"], horizontal=True)
    stars = c3.multiselect("Star rating", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5])
    d = pairs[pairs["game"] == game]
    if market == "US only":
        d = d[d["market"] == "us"]
    d = d[d["stars"].isin(stars)] if stars else d.iloc[0:0]
    if d.empty:
        st.info("No sentences for this selection.")
        return
    min_n = st.slider("Only aspects with at least this many mentions", 1, 200, 20)
    g = d.groupby(["aspect", "sentiment"]).size().unstack(fill_value=0).reindex(columns=["negative", "neutral", "positive"], fill_value=0)
    g["mentions"] = g.sum(axis=1)
    g = g[g["mentions"] >= min_n].sort_values("mentions", ascending=False)
    if g.empty:
        st.info("No aspect reaches that number of mentions; lower the threshold.")
        return
    long = g.reset_index().melt(id_vars=["aspect", "mentions"], value_vars=["negative", "neutral", "positive"], var_name="Sentiment", value_name="n")
    long["Share"] = 100 * long["n"] / long["mentions"]
    long["Aspect"] = long["aspect"].map(aspect_label)
    order = [aspect_label(a) for a in g.index][::-1]
    fig = px.bar(long, x="Share", y="Aspect", color="Sentiment", orientation="h", color_discrete_map=SENT_COLORS,
                 category_orders={"Sentiment": ["negative", "neutral", "positive"], "Aspect": order},
                 labels={"Share": "% of mentions"})
    fig.update_layout(height=max(320, 42 * len(g) + 130), yaxis_title="")
    st.plotly_chart(fig)
    tab = g.copy()
    tab.index = [aspect_label(a) for a in tab.index]
    for c in ("negative", "neutral", "positive"):
        tab[f"{c} %"] = (100 * tab[c] / tab["mentions"]).round(0).astype(int)
    st.dataframe(tab[["mentions", "negative", "neutral", "positive", "negative %", "neutral %", "positive %"]])
    st.caption("The neutral class has very few labelled examples, so neutral shares are the least reliable. "
               "Aspects with few mentions give unstable percentages. Open *Review explorer* to read the sentences behind a bar.")
    flagged = [a for a in g.index if a in ASPECT_NOTES]
    if flagged:
        with st.expander("Reliability notes for aspects shown here"):
            for a in flagged:
                st.markdown(f"**{aspect_label(a)}**: {ASPECT_NOTES[a]}")


# ------------------------------------------------------------------ page 1
def page_priority():
    st.title("Issue priority")
    st.caption("Which problems should a game team fix first? Priority = negative mentions per 100 review sentences "
               "(how often an aspect is mentioned × how often it is mentioned negatively).")
    ip = read_csv("issue_priority_by_game.csv")
    if ip is None:
        return missing("issue_priority_by_game.csv")
    c1, c2 = st.columns(2)
    game = c1.selectbox("Game", list(GAMES), format_func=game_name)
    basis = c2.radio("Priority is based on", ["All reviews", "1-2 star reviews only"], horizontal=True)
    col = "priority_neg_per100" if basis == "All reviews" else "priority_1to2"
    d = ip[ip["game"] == game].copy()
    if col not in d.columns or d[col].dropna().empty:
        st.info("This view is not available for the selected game.")
        return
    d["Aspect"] = d["aspect"].map(aspect_label)
    d = d.dropna(subset=[col]).sort_values(col, ascending=False)
    top = d.iloc[0]
    m1, m2, m3 = st.columns(3)
    m1.metric("Top issue", top["Aspect"])
    m2.metric("Negative mentions per 100 sentences", f"{top[col]:.1f}")
    m3.metric("Review sentences analysed", f"{int(top['n_sentences']):,}")

    err = (d["neg_share_sd_seeds"].fillna(0) * d["mentions_per100"]) if (col == "priority_neg_per100" and "neg_share_sd_seeds" in d) else None
    plot = d.sort_values(col).assign(err=None if err is None else err.reindex(d.sort_values(col).index))
    fig = px.bar(plot, x=col, y="Aspect", orientation="h", color="reliability",
                 color_discrete_map={"ok": BLUE, "check": GOLD}, error_x="err" if err is not None else None,
                 labels={col: "Negative mentions per 100 sentences", "reliability": "Reliability"})
    fig.update_layout(height=max(320, 42 * len(plot) + 130), yaxis_title="", legend_title_text="Reliability check")
    st.plotly_chart(fig)
    st.caption("Blue = no reliability concern recorded. Gold = check the notes in the table before relying on this aspect. "
               "Error bars (all-reviews view) show how much the value moved across five ensemble runs.")

    t = pd.DataFrame({
        "Rank": d["rank"].astype(int) if basis == "All reviews" else range(1, len(d) + 1),
        "Aspect": d["Aspect"],
        "Negative mentions /100 sentences": d[col].round(2),
        "Mentions /100 sentences": d["mentions_per100"].round(2),
        "Negative share": (100 * d["neg_share"]).round(0).astype(int).astype(str) + "%",
        "Rank range across runs": d["rank_min_seeds"].astype("Int64").astype(str) + "-" + d["rank_max_seeds"].astype("Int64").astype(str)
        if "rank_min_seeds" in d else "",
        "Reliability": d["reliability"],
        "Notes": d["reliability_notes"].fillna(""),
    })
    st.dataframe(t, hide_index=True)
    with st.expander("How to read this page"):
        st.markdown(
            "- **Priority** combines frequency and negativity, so a rarely mentioned but always-negative aspect can rank below a frequently mentioned, mostly-negative one.\n"
            "- **Rank range across runs** shows the best and worst rank the aspect received over five model runs with different random seeds; a narrow range means the ranking is stable.\n"
            "- **1-2 star view** is a stricter check: it only counts mentions that appear in low-rated reviews.\n"
            "- Aspects marked *check* have a recorded reliability concern (see the Method & reliability page).")


@st.cache_data(show_spinner=False)
def nonus_windows(game, wd):
    """Share of non-US reviews in each trend window (same window grid as trend.csv)."""
    meta = read_parquet("reviews_meta.parquet")
    if meta is None:
        return pd.DataFrame(columns=["window_start", "n", "non_us"])
    d = meta[meta["game"] == game].copy()
    d["at"] = pd.to_datetime(d["at"], errors="coerce")
    d = d.dropna(subset=["at"])
    if d.empty:
        return pd.DataFrame(columns=["window_start", "n", "non_us"])
    t0 = d["at"].min().normalize()
    d["win"] = ((d["at"] - t0).dt.days // wd).astype(int)
    out = d.groupby("win").agg(n=("reviewId", "size"), non_us=("market", lambda m: float((m != "us").mean()))).reset_index()
    out["window_start"] = t0 + pd.to_timedelta(out["win"] * wd, unit="D")
    return out[["window_start", "n", "non_us"]]


NONUS_FLAG = 0.20      # windows with at least this share of non-US reviews are shaded in the all-markets view


# ------------------------------------------------------------------ page 2
def page_trends():
    st.title("Trends over time")
    tr = read_csv("trend.csv", parse_dates=["window_start"])
    if tr is None:
        return missing("trend.csv")
    c1, c2, c3 = st.columns(3)
    game = c1.selectbox("Game", list(GAMES), format_func=game_name)
    scope = c2.radio("Markets", ["all", "us"], index=1, format_func=lambda s: "All markets" if s == "all" else "US only", horizontal=True)
    metric = c3.selectbox("Metric", ["negative_per100", "mentions_per100"],
                          format_func=lambda m: "Negative mentions per 100 sentences" if m == "negative_per100" else "All mentions per 100 sentences")
    d = tr[(tr["game"] == game) & (tr["market_scope"] == scope)].copy()
    if d.empty:
        st.info("No trend data for this selection.")
        return
    order = d.groupby("aspect")["negative_mentions"].sum().sort_values(ascending=False).index.tolist()
    chosen = st.multiselect("Aspects", order, default=order[:3], format_func=aspect_label)
    if not chosen:
        st.info("Select at least one aspect.")
        return
    d = d[d["aspect"].isin(chosen)].sort_values("window_start")
    d["Aspect"] = d["aspect"].map(aspect_label)
    fig = px.line(d, x="window_start", y=metric, color="Aspect", markers=True,
                  labels={"window_start": "Window start", metric: "per 100 sentences"})
    weak = d[~d["reliable_window"].astype(bool)].dropna(subset=[metric])
    if not weak.empty:
        fig.add_trace(go.Scatter(x=weak["window_start"], y=weak[metric], mode="markers", name="Window with <100 reviews",
                                 marker=dict(symbol="x", size=11, color="black")))
    fig.update_layout(height=460, legend_title_text="")
    vs_tbl = read_csv("version_windows_and_stars.csv")
    if vs_tbl is not None and st.checkbox("Mark known app updates", value=False):
        for _, r in vs_tbl[vs_tbl["game"] == game].iterrows():
            x = pd.to_datetime(r["first_seen"], errors="coerce")
            if pd.notna(x):
                fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=1, yref="paper", line=dict(color="grey", dash="dash"))
                fig.add_annotation(x=x, y=1, yref="paper", text=f"v{r['version']}", showarrow=False, yanchor="bottom")
    wd = int(d["window_days"].iloc[0])
    shaded = 0
    if scope == "all":
        nu = nonus_windows(game, wd)
        for _, r in nu[nu["non_us"] >= NONUS_FLAG].iterrows():
            fig.add_shape(type="rect", x0=r["window_start"], x1=r["window_start"] + pd.Timedelta(days=wd), y0=0, y1=1, yref="paper",
                          fillcolor="orange", opacity=0.15, line_width=0, layer="below")
            shaded += 1
    st.plotly_chart(fig)
    st.caption(f"Each point is a {wd}-day window. Black crosses mark windows with fewer than 100 reviews: treat those with caution. "
               "Rates are per 100 review sentences so that busy and quiet periods are comparable.")
    if scope == "all":
        if shaded:
            st.warning(f"Orange bands mark windows where at least {int(NONUS_FLAG * 100)}% of the reviews come from non-US markets. "
                       "Those reviews were collected in a later batch, so a jump inside a band may reflect a different mix of reviewers rather than a real change. "
                       "Switch to *US only* (the default) to compare like with like.")
        else:
            st.info("This game has no window with a large share of non-US reviews.")
    else:
        st.caption("US reviews only: the reviewer mix is consistent across windows. Windows with no US reviews have no point.")
    with st.expander("Window sizes"):
        st.dataframe(d[["Aspect", "window_start", "n_reviews", "n_sentences", "mentions", "negative_mentions"]]
                     .rename(columns={"window_start": "Window start", "n_reviews": "Reviews", "n_sentences": "Sentences",
                                      "mentions": "Mentions", "negative_mentions": "Negative mentions"}), hide_index=True)


# ------------------------------------------------------------------ page 3
def page_cross():
    st.title("Cross-game comparison")
    st.caption("Only the seven aspects shared by all five games are compared here. Genre-specific aspects "
               "(gacha rates, matchmaking, cheating, grind...) are shown only on the per-game pages.")
    cg, cs = read_csv("cross_game_common_priority.csv", index_col=0), read_csv("cross_game_common_neg_share.csv", index_col=0)
    if cg is None:
        return missing("cross_game_common_priority.csv")

    def prep(df):
        df = df.rename(columns=game_name)
        df.index = [aspect_label(a) for a in df.index]
        return df
    tab1, tab2 = st.tabs(["Negative mentions per 100 sentences", "Negative share of mentions"])
    with tab1:
        p = prep(cg)
        st.plotly_chart(px.imshow(p, text_auto=".1f", aspect="auto", color_continuous_scale="Blues",
                                  labels=dict(color="per 100 sentences")))
        st.dataframe(p.round(2))
    with tab2:
        if cs is None:
            missing("cross_game_common_neg_share.csv")
        else:
            p = prep(cs)
            st.plotly_chart(px.imshow(p, text_auto=".2f", aspect="auto", color_continuous_scale="Oranges",
                                      labels=dict(color="share negative")))
            st.caption("Share of an aspect's mentions that are negative. It does not account for how often the aspect is mentioned, "
                       "so read it together with the priority view.")
    st.info("Games differ in reviewer mix and markets, so compare patterns rather than treating small differences as meaningful.")


# ------------------------------------------------------------------ page 4
def page_explorer():
    st.title("Review explorer")
    st.caption("Look at the actual sentences behind the numbers.")
    pairs, ex = read_parquet("pairs.parquet"), read_parquet("examples.parquet")
    if pairs is None or ex is None:
        return missing("pairs.parquet / examples.parquet")
    mode = st.radio("Show", ["Representative negative examples", "Browse all matching sentences"], horizontal=True)
    base = ex.copy() if mode.startswith("Representative") else pairs.copy()
    c1, c2, c3 = st.columns(3)
    game = c1.selectbox("Game", ["All games"] + list(GAMES), format_func=lambda g: g if g == "All games" else game_name(g))
    aspects = sorted(base["aspect"].dropna().unique())
    asp = c2.selectbox("Aspect", ["All aspects"] + aspects, format_func=lambda a: a if a == "All aspects" else aspect_label(a))
    market = c3.radio("Markets", ["All", "US only"], horizontal=True)
    vbase = base if game == "All games" else base[base["game"] == game]
    versions = vbase["version"].dropna().astype(str).value_counts().head(40).index.tolist()
    c4, c5, c6 = st.columns(3)
    stars = c4.multiselect("Star rating", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5])
    ver = c5.selectbox("App version", ["All versions"] + versions)
    if mode.startswith("Browse"):
        sent = c6.multiselect("Sentiment", ["negative", "neutral", "positive"], default=["negative"])
    else:
        sent = ["negative"]
    text = st.text_input("Sentence contains (optional)")
    at = pd.to_datetime(base["at"], errors="coerce")
    if at.notna().any():
        lo, hi = at.min().date(), at.max().date()
        dr = st.date_input("Review date", value=(lo, hi), min_value=lo, max_value=hi)
        dr = dr if isinstance(dr, (tuple, list)) and len(dr) == 2 else (lo, hi)
    else:
        dr = None

    d = base
    if game != "All games":
        d = d[d["game"] == game]
    if asp != "All aspects":
        d = d[d["aspect"] == asp]
    if market == "US only":
        d = d[d["market"] == "us"]
    if ver != "All versions":
        d = d[d["version"].astype(str) == ver]
    d = d[d["stars"].isin(stars)] if stars else d.iloc[0:0]
    if "sentiment" in d.columns:
        d = d[d["sentiment"].isin(sent)]
    if text.strip():
        d = d[d["sentence_text"].fillna("").str.contains(text.strip(), case=False, regex=False)]
    if dr is not None:
        a = pd.to_datetime(d["at"], errors="coerce")
        d = d[(a >= pd.Timestamp(dr[0])) & (a < pd.Timestamp(dr[1]) + pd.Timedelta(days=1))]
    if asp in ASPECT_NOTES:
        st.warning(ASPECT_NOTES[asp])

    sort_col = "rank_score" if mode.startswith("Representative") else ("p_negative" if "negative" in sent else "p_aspect")
    d = d.sort_values(sort_col, ascending=False)
    st.markdown(f"**{len(d):,}** matching sentences")
    if d.empty:
        return
    n = st.slider("How many to show", 10, 500, 100, step=10)
    show = d.head(n)
    out = pd.DataFrame({
        "Game": show["game"].map(game_name), "Aspect": show["aspect"].map(aspect_label), "Sentence": show["sentence_text"],
        "Stars": show["stars"], "P(negative)": show["p_negative"].round(2),
        "Run-to-run spread": show["p_negative_seed_std"].round(2), "Version": show["version"], "Date": pd.to_datetime(show["at"]).dt.date})
    st.dataframe(out, hide_index=True)
    st.download_button("Download the shown rows (CSV)", out.to_csv(index=False).encode("utf-8"), file_name="gamesense_sentences.csv", mime="text/csv")
    if mode.startswith("Representative"):
        st.caption("Representative examples are negative sentences with high aspect and sentiment confidence that stayed negative across all five model runs.")


# ------------------------------------------------------------------ page 5
def page_version():
    st.title("Version analysis")
    st.warning("Descriptive only. These comparisons show what changed around an app update, not what the update caused: "
               "other things (events, seasons, who is reviewing) change at the same time.")
    vs, va, bs = read_csv("version_windows_and_stars.csv"), read_csv("version_aspect_changes.csv"), read_csv("version_boundary_sensitivity.csv")
    if vs is None:
        return missing("version_windows_and_stars.csv")
    show = vs.copy()
    show["game"] = show["game"].map(game_name)
    st.subheader("14-day windows before and after each update")
    st.dataframe(show.rename(columns={"game": "Game", "version": "Version", "first_seen": "First seen", "n_pre": "Reviews before", "n_post": "Reviews after",
                                      "post_share_on_new_version": "Share on new version (after)", "usable(>=100 each)": "Enough reviews (>=100 each)",
                                      "stars_pre": "Stars before", "stars_post": "Stars after", "stars_delta": "Change", "stars_delta_95CI": "95% interval",
                                      "CI_excludes_0": "Interval excludes 0"}), hide_index=True)
    st.caption("When the interval includes 0 the change is not distinguishable from noise. Only part of the reviews after an update come from the new version.")

    if bs is not None and not bs.empty:
        st.subheader("Does the result depend on where the window starts?")
        trans = sorted(bs["transition"].unique())
        c1, c2 = st.columns(2)
        sel = c1.selectbox("Update", trans)
        sub = c2.radio("Markets", sorted(bs["subset"].unique()), horizontal=True)
        d = bs[(bs["transition"] == sel) & (bs["subset"] == sub)].copy()
        ci = d["delta_95CI"].map(parse_ci)
        d["lo"], d["hi"] = [c[0] for c in ci], [c[1] for c in ci]
        fig = go.Figure(go.Scatter(x=d["stars_delta"], y=d["window_anchor"], mode="markers", marker=dict(size=10, color=BLUE),
                                   error_x=dict(type="data", symmetric=False, array=(d["hi"] - d["stars_delta"]).tolist(),
                                                arrayminus=(d["stars_delta"] - d["lo"]).tolist())))
        fig.add_vline(x=0, line_dash="dash", line_color="grey")
        fig.update_layout(height=340, xaxis_title="Change in average stars (after - before)", yaxis_title="Window start")
        st.plotly_chart(fig)
        if not d.empty:
            k = int(d["CI_excludes_0"].astype(bool).sum())
            st.markdown(f"Across **{len(d)}** window choices, the star change ranges from **{d['stars_delta'].min():+.2f}** to "
                        f"**{d['stars_delta'].max():+.2f}**; the interval excludes 0 in **{k}** of {len(d)}.")
            if 0 < k < len(d):
                st.info("The conclusion changes with the window choice, so report it as sensitive to where the window starts.")

    if va is not None and not va.empty:
        st.subheader("Which aspects changed?")
        va = va.copy()
        va["transition"] = va["game"].astype(str) + " " + va["version"].astype(str)
        sel2 = st.selectbox("Update (aspect view)", sorted(va["transition"].unique()))
        d = va[va["transition"] == sel2].copy()
        ci = d["delta_95CI"].map(parse_ci)
        d["lo"], d["hi"] = [c[0] for c in ci], [c[1] for c in ci]
        d["Aspect"] = d["aspect"].map(aspect_label)
        fig = go.Figure(go.Bar(x=d["delta"], y=d["Aspect"], orientation="h",
                               marker_color=np.where(d["CI_excludes_0"].astype(bool), BLUE, "#B0B7C3"),
                               error_x=dict(type="data", symmetric=False, array=(d["hi"] - d["delta"]).tolist(), arrayminus=(d["delta"] - d["lo"]).tolist())))
        fig.add_vline(x=0, line_dash="dash", line_color="grey")
        fig.update_layout(height=max(300, 55 * len(d) + 120), xaxis_title="Change in reviews with a negative mention (per 100 reviews)", yaxis_title="")
        st.plotly_chart(fig)
        st.caption("Blue bars: interval excludes 0. Grey: not distinguishable from no change. Several aspects are compared at once, "
                   "so a few intervals can exclude 0 by chance alone.")
        if d["caution"].fillna("").ne("").any():
            st.warning("Aspects marked with a sentiment-reliability concern: " + ", ".join(d.loc[d["caution"].fillna("") != "", "Aspect"]) + ".")


# ------------------------------------------------------------------ page 6
def page_method():
    st.title("Method and reliability")
    st.markdown("**Pipeline.** Google Play reviews → sentence split → **Task 2** aspect detection (12 aspects, multi-label BERT) → "
                "**Task 3** aspect-level sentiment (BERT on sentence + aspect) → issue priority = negative mentions per 100 sentences. "
                "Task 1 (overall review sentiment) is trained on star-derived labels.")
    t_chk, t_base, t3, t2, t_err, t_mk, t_lim = st.tabs(["Targets vs results", "Baselines", "Aspect sentiment (Task 3)", "Aspect detection (Task 2)",
                                                         "Error analysis", "Data and markets", "Limitations"])
    with t_chk:
        df = read_csv("proposal_check.csv")
        if df is not None:
            st.dataframe(df, hide_index=True)
        else:
            missing("proposal_check.csv")
        st.caption("The numeric targets in the project proposal were set as directional goals before piloting.")
    with t_base:
        st.caption("Simple non-deep-learning baselines, evaluated on the same labelled data. Sentence-level lexicons do not know which aspect "
                   "a sentence is about, so they are weak for aspect sentiment by construction.")
        shown = False
        for name, title in [("baselines_task2.csv", "Task 2: aspect detection"), ("baselines_task3.csv", "Task 3: aspect sentiment")]:
            df = read_csv(name)
            if df is not None:
                shown = True
                st.markdown(f"**{title}**")
                st.dataframe(df, hide_index=True)
        if not shown:
            st.info("Baseline tables are not in the repository yet.")
    with t3:
        o, a = read_csv("task3_overall.csv"), read_csv("task3_by_aspect.csv")
        if o is not None:
            st.markdown("**Overall (5-fold cross-validation, grouped by review)**")
            st.dataframe(o, hide_index=True)
        if a is not None:
            st.markdown("**By aspect.** Compare *acc_negVsRest_BERT* with *acc_if_all_negative*: where they are close, the model adds little beyond "
                        "predicting 'negative' for everything.")
            st.dataframe(a, hide_index=True)
        st.caption("The neutral class has very few labelled examples and is rarely predicted correctly, so negative-vs-rest is the more meaningful measure.")
        aud = read_csv("label_audit_summary.csv")
        if aud is not None:
            st.markdown("**Label audit.** The annotator re-labelled 60 sentence-aspect pairs without seeing the original labels or the model's predictions: "
                        "30 chosen at random and 30 where the cross-validated model most confidently disagreed with the label.")
            st.dataframe(aud, hide_index=True)
            st.caption("In the random sample no label flipped between negative and positive; the differences involved the neutral class or whether the aspect "
                       "was mentioned at all. The same person did the original labelling and the audit, so this measures consistency over time, "
                       "not independent agreement, and probably understates label noise. With 30 pairs per sample the intervals are wide.")
        cm = DATA.parent / "docs" / "figures" / "task3_confusion.png"
        if cm.exists():
            st.image(str(cm), caption="Task 3 confusion matrix (out-of-fold)", width=420)
    with t2:
        o, a = read_csv("task2_overall.csv"), read_csv("task2_by_aspect.csv")
        if o is not None:
            st.dataframe(o, hide_index=True)
        if a is not None:
            st.dataframe(a, hide_index=True)
    with t_err:
        st.caption("Where and why the models go wrong. Language markers are simple rules (for example, a sentence containing 'but') used only to show "
                   "where errors cluster; they do not prove the cause of an error.")
        e1, e2, e3 = st.tabs(["Overall review sentiment (Task 1)", "Aspect detection (Task 2)", "Aspect sentiment (Task 3)"])
        with e1:
            found = [show_table("task1_overall.csv", "Per-class precision and recall", expanded=True),
                     show_table("task1_confusion.csv", "Confusion matrix (rows: star-derived label, columns: model)"),
                     show_table("task1_by_star.csv", "What the model predicts for each star rating",
                                "3-star reviews carry the 'neutral' label; if they are spread across all three predictions, the neutral class is not well defined by stars."),
                     show_table("task1_by_game.csv", "Performance by game"),
                     show_table("task1_error_by_marker.csv", "Error rate with vs without each language marker"),
                     show_table("task1_error_examples.csv", "Confidently wrong examples")]
            if not any(found):
                st.info("Task 1 error-analysis tables are not in the repository yet.")
        with e2:
            found = [show_table("task2_by_game.csv", "Performance by game", expanded=True),
                     show_table("task2_by_aspect_all_models.csv", "Per aspect: keyword baseline vs TF-IDF vs BERT",
                                "Aspects with few gold examples have unstable scores."),
                     show_table("task2_confusable_aspects.csv", "Aspects that get mixed up",
                                "In sentences with both a miss and a false alarm: which aspect was predicted instead of which was missed."),
                     show_table("task2_error_by_marker.csv", "Share of sentences with a wrong aspect, with vs without each marker"),
                     show_table("task2_error_examples.csv", "Most confident misses and false alarms")]
            if not any(found):
                st.info("Task 2 error-analysis tables are not in the repository yet.")
        with e3:
            found = [show_table("task3_error_by_marker.csv", "Error rate with vs without each language marker", expanded=True),
                     show_table("task3_error_examples.csv", "Most confident missed complaints and false alarms")]
            if not any(found):
                st.info("Task 3 error-analysis tables are not in the repository yet.")
    with t_mk:
        m, n = read_csv("market_composition.csv"), read_csv("nonUS_share_by_window.csv")
        if m is not None:
            st.markdown("**Reviews by game and market**")
            st.dataframe(m, hide_index=True)
        if n is not None and not n.empty:
            n = n.copy(); n["game"] = n["game"].map(game_name)
            st.markdown("**Share of non-US reviews per window (games with any)**")
            fig = px.line(n, x="window_start", y="nonUS_%", color="game", markers=True, labels={"window_start": "Window start", "nonUS_%": "Non-US share (%)"})
            fig.update_layout(height=340)
            st.plotly_chart(fig)
    with t_lim:
        st.markdown(
            "- **Small labelled set.** Aspect sentiment was trained on a few hundred labelled sentence-aspect pairs, so rare aspects have very little evidence.\n"
            "- **Neutral sentiment** is rarely predicted correctly; headline results use negative-vs-rest.\n"
            "- **Complaint-dominated aspects** (performance, matchmaking, cheating) are almost always negative, so their ranking mainly reflects how often they are mentioned.\n"
            "- **Flagged aspects.** Advertisement and account support sentiment may be over-predicted as negative; paywall has few labelled examples.\n"
            "- **Overall review sentiment** is evaluated against star-derived labels, which are a noisy proxy for what reviewers mean.\n"
            "- **Reviewer mix.** Reviews come from several Play Store markets, and non-US reviews are concentrated in later weeks for some games.\n"
            "- **Version analysis** is descriptive, depends on where the window starts, and cannot establish that an update caused a change.\n"
            "- **Self-selected sample.** Reviewers are not representative of all players.")


# ------------------------------------------------------------------ main
PAGES = {"Overview": page_overview, "Issue priority": page_priority, "Aspect sentiment": page_aspect_sentiment,
         "Trends": page_trends, "Cross-game comparison": page_cross,
         "Review explorer": page_explorer, "Version analysis": page_version, "Method & reliability": page_method}
st.sidebar.title("🎮 GameSense")
st.sidebar.caption("Aspect-based sentiment analysis of mobile-game reviews")
page = st.sidebar.radio("Page", list(PAGES))
PAGES[page]()
man = read_manifest()
if man:
    st.sidebar.divider()
    st.sidebar.caption(f"Results built: {str(man.get('timestamp_utc', ''))[:10]}  \nModel: {man.get('model', '')}")
