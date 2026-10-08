# ============================================================
# TRENDING TOPICS ANALYZER
# Minor Project
#
# Data Structures Used:
# 1. HashMap (Python Dictionary) - keyword frequency counting
# 2. Min Heap (heapq) - Top-K selection
# ============================================================

import re
import time
import heapq

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Trending Topics Analyzer",
    page_icon="",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 18px;
    color: #777;
    margin-bottom: 25px;
}

.section-title {
    font-size: 26px;
    font-weight: 700;
}

.metric-box {
    padding: 15px;
    border-radius: 12px;
    background-color: #f7f8fc;
    border: 1px solid #e5e7eb;
}

.trend-box {
    padding: 18px;
    border-radius: 14px;
    background-color: #fff7f2;
    border: 1px solid #eeeeee;
}
/* Tabs */
button[data-baseweb="tab"] {
    font-size: 22px !important;
    font-weight: 600 !important;
    padding: 18px 30px !important;
    min-height: 65px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #17203a !important;
    font-weight: 700 !important;
}

div[data-baseweb="tab-list"] {
    gap: 12px !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title"> Trending Topics Analyzer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Discover what is gaining attention in the news using HashMap and Min Heap'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# STOP WORDS
# ============================================================

stop_words = {
    "the", "and", "for", "are", "but", "not", "you",
    "all", "can", "was", "this", "that", "with",
    "from", "they", "will", "what", "when", "your",
    "about", "just", "into", "than", "then", "been",
    "were", "more", "some", "how", "why", "who",
    "its", "his", "her", "she", "has", "have",
    "had", "new", "after", "says", "over", "out",
    "one", "our", "get", "here"
}


# ============================================================
# MONTH NAMES
# ============================================================

month_names = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


# ============================================================
# LOAD DATASET
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_json(
        "News_Category_Dataset_v3.json",
        lines=True
    )

    df["date"] = pd.to_datetime(df["date"])

    df["year"] = df["date"].dt.year

    df["month"] = df["date"].dt.month

    return df


df = load_data()


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_words(text):

    words = re.findall(
        r"[a-z]+",
        str(text).lower()
    )

    result = []

    for word in words:

        if (
            len(word) > 2
            and word not in stop_words
        ):
            result.append(word)

    return result


# ============================================================
# HASHMAP WORD COUNT
# ============================================================

def count_words(headlines):

    # HashMap
    counts = {}

    for headline in headlines:

        for word in clean_words(headline):

            if word in counts:
                counts[word] += 1

            else:
                counts[word] = 1

    return counts


# ============================================================
# MIN HEAP TOP-K
# ============================================================

def top_k(scores, k):

    # Min Heap
    heap = []

    for word, score in scores.items():

        heapq.heappush(
            heap,
            (score, word)
        )

        if len(heap) > k:

            heapq.heappop(heap)

    return sorted(
        heap,
        reverse=True
    )


# ============================================================
# GET MONTH DATA
# ============================================================

def get_month(data, year, month):

    return data[
        (data["year"] == year)
        &
        (data["month"] == month)
    ]


# ============================================================
# PREVIOUS MONTH
# ============================================================

def previous_month(year, month):

    if month == 1:

        return year - 1, 12

    return year, month - 1


# ============================================================
# TREND SCORE
# ============================================================

def trend_scores(
    now_counts,
    prev_counts,
    min_count
):

    scores = {}

    for word in now_counts:

        now = now_counts[word]

        before = prev_counts.get(
            word,
            0
        )

        if now >= min_count:

            # Laplace smoothing
            score = (
                (now + 1)
                /
                (before + 1)
            )

            scores[word] = round(
                score,
                2
            )

    return scores


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🔥 Trending Topics")

st.sidebar.markdown("---")

st.sidebar.subheader("Settings")


# Dataset years
available_years = sorted(
    df["year"].unique()
)

year = st.sidebar.selectbox(
    "Year",
    available_years,
    index=len(available_years) - 1
)


# Month
month = st.sidebar.selectbox(
    "Month",
    list(range(1, 13)),
    index=5,
    format_func=lambda m:
        month_names[m - 1]
)


# Category
category = st.sidebar.selectbox(
    "Category",
    ["All"]
    +
    sorted(
        df["category"].unique()
    )
)


# Top K
k = st.sidebar.slider(
    "Top K",
    3,
    20,
    10
)


# Minimum mentions
min_count = st.sidebar.slider(
    "Minimum mentions",
    1,
    10,
    3
)


st.sidebar.markdown("---")

st.sidebar.info(
    """
### Algorithms

**HashMap**

Used for keyword frequency counting.

**Min Heap**

Used to efficiently find Top-K topics.

### Trend

Current month is compared
with the previous month.
"""
)


# ============================================================
# FILTER DATA
# ============================================================

data = df

if category != "All":

    data = df[
        df["category"] == category
    ]


# ============================================================
# CURRENT + PREVIOUS MONTH
# ============================================================

this_month = get_month(
    data,
    year,
    month
)

previous_year, previous_month_number = previous_month(
    year,
    month
)

last_month = get_month(
    data,
    previous_year,
    previous_month_number
)


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title"> Dashboard Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Articles",
        f"{len(df):,}"
    )

with col2:

    st.metric(
        "Categories",
        df["category"].nunique()
    )

with col3:

    st.metric(
        f" {month_names[month - 1]} {year}",
        f"{len(this_month):,}"
    )

with col4:

    st.metric(
        f"{month_names[previous_month_number - 1]} {previous_year}",
        f"{len(last_month):,}"
    )


st.markdown("---")


# ============================================================
# CURRENT SELECTION
# ============================================================

st.write(
    f"### Current Analysis: "
    f"{month_names[month - 1]} {year}"
)

if category == "All":

    st.caption(
        "Showing all news categories."
    )

else:

    st.caption(
        f"Showing category: **{category}**"
    )


# ============================================================
# COUNT WORDS
# ============================================================

now_counts = count_words(
    this_month["headline"]
)

prev_counts = count_words(
    last_month["headline"]
)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        " Top Words",
        " Trending",
        " Search a Word",
        " By Category",
        " Heap vs Sort"
    ]
)


# ============================================================
# TAB 1 — TOP WORDS
# ============================================================

with tab1:

    st.subheader(
        " Most Frequent Words"
    )

    st.write(
        "These are the words appearing most frequently "
        "in headlines for the selected month."
    )

    result = top_k(
        now_counts,
        k
    )

    if len(result) == 0:

        st.warning(
            "No headlines found for this selection."
        )

    else:

        table = pd.DataFrame(
            result,
            columns=[
                "count",
                "word"
            ]
        )

        table = table[
            [
                "word",
                "count"
            ]
        ]

        # Chart
        st.bar_chart(
            table.set_index(
                "word"
            ),
            use_container_width=True
        )

        # Table
        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True
        )

        # Download
        st.download_button(
            "Download CSV",
            table.to_csv(
                index=False
            ),
            file_name="top_words.csv",
            mime="text/csv"
        )


# ============================================================
# TAB 2 — TRENDING
# ============================================================

with tab2:

    st.subheader(
        "Trending Words"
    )

    st.write(
        "Trend score = "
        "(current month count + 1) / "
        "(previous month count + 1)"
    )

    scores = trend_scores(
        now_counts,
        prev_counts,
        min_count
    )

    result = top_k(
        scores,
        k
    )

    if len(result) == 0:

        st.warning(
            "Nothing is trending here. "
            "Try a lower minimum mention value "
            "or another month."
        )

    else:

        rows = []

        for score, word in result:

            previous_count = prev_counts.get(
                word,
                0
            )

            current_count = now_counts[word]

            # Convert ratio into percentage growth
            growth = (
                (current_count - previous_count)
                /
                (previous_count + 1)
            ) * 100

            rows.append(
                [
                    word,
                    previous_count,
                    current_count,
                    round(score, 2),
                    round(growth, 2)
                ]
            )

        table = pd.DataFrame(
            rows,
            columns=[
                "word",
                "last month",
                "this month",
                "trend score",
                "growth (%)"
            ]
        )


        # Top trend
        st.success(
            "Top trending word: "
            +
            table["word"].iloc[0].title()
        )


        # Chart
        st.bar_chart(
            table.set_index(
                "word"
            )["growth (%)"],
            use_container_width=True
        )


        # Table
        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True
        )


# ============================================================
# TAB 3 — SEARCH
# ============================================================

with tab3:

    st.subheader(
        "Search a Word"
    )

    st.write(
        "Search for a word and see how often it "
        "appears in the news over time."
    )

    word = st.text_input(
        "Enter a word or topic",
        "trump"
    ).lower().strip()

    only_year = st.checkbox(
        "Only show the selected year"
    )

    if word != "":

        found = data[
            data["headline"]
            .str
            .lower()
            .str
            .contains(
                word,
                regex=False,
                na=False
            )
        ]

        if only_year:

            found = found[
                found["year"] == year
            ]


        # ---------------------------------------------
        # SEARCH RESULT
        # ---------------------------------------------

        st.markdown("---")

        st.metric(
            f" Headlines containing '{word}'",
            len(found)
        )


        if len(found) > 0:

            # Monthly trend
            per_month = (
                found
                .groupby(
                    found["date"]
                    .dt
                    .to_period("M")
                )
                .size()
            )

            per_month.index = (
                per_month.index
                .to_timestamp()
            )

            st.subheader(
                " Topic Frequency Over Time"
            )

            st.line_chart(
                per_month,
                use_container_width=True
            )


            # Latest headlines
            st.subheader(
                " Latest Headlines"
            )

            latest = (
                found
                .sort_values(
                    "date",
                    ascending=False
                )
                .head(15)
            )

            st.dataframe(
                latest[
                    [
                        "date",
                        "category",
                        "headline"
                    ]
                ],
                hide_index=True,
                use_container_width=True
            )

        else:

            st.warning(
                f"No headlines found containing '{word}'."
            )


# ============================================================
# TAB 4 — CATEGORY
# ============================================================

with tab4:

    st.subheader(
        " Top Words in Each Category"
    )

    st.write(
        "For the selected month, the Top 5 words "
        "are displayed for each category."
    )

    month_all = get_month(
        df,
        year,
        month
    )

    rows = []

    for cat in sorted(
        month_all["category"].unique()
    ):

        cat_data = month_all[
            month_all["category"] == cat
        ]

        # Ignore categories with very little data
        if len(cat_data) < 20:
            continue

        counts = count_words(
            cat_data["headline"]
        )

        best = top_k(
            counts,
            5
        )

        words = ", ".join(
            [
                word
                for count, word in best
            ]
        )

        rows.append(
            [
                cat,
                len(cat_data),
                words
            ]
        )


    if len(rows) == 0:

        st.warning(
            "Not enough data for this month."
        )

    else:

        category_table = pd.DataFrame(
            rows,
            columns=[
                "category",
                "headlines",
                "top words"
            ]
        )

        st.dataframe(
            category_table,
            hide_index=True,
            use_container_width=True
        )


# ============================================================
# TAB 5 — HEAP VS SORT
# ============================================================

with tab5:

    st.subheader(
        " Why Use a Heap?"
    )

    st.markdown(
        """
### Min Heap

Instead of sorting every word, a Min Heap
keeps only the **Top K elements**.

For `N` words and `K` required results:

**Heap:** `O(N log K)`

**Full Sorting:** `O(N log N)`

Therefore, when `K` is much smaller than `N`,
a heap can be more efficient.
"""
    )


    st.markdown("---")

    if st.button(
        "Run Performance Test"
    ):

        with st.spinner(
            "Running performance test..."
        ):

            # -----------------------------------------
            # Count complete dataset
            # -----------------------------------------

            all_counts = count_words(
                df["headline"]
            )

            items = list(
                all_counts.items()
            )

            st.write(
                "Unique words:",
                len(items)
            )


            # -----------------------------------------
            # HEAP
            # -----------------------------------------

            start = time.time()

            for _ in range(5):

                heap = []

                for word, count in items:

                    if len(heap) < 10:

                        heapq.heappush(
                            heap,
                            (count, word)
                        )

                    elif count > heap[0][0]:

                        heapq.heapreplace(
                            heap,
                            (count, word)
                        )

            heap_time = (
                time.time() - start
            ) / 5


            # -----------------------------------------
            # SORT
            # -----------------------------------------

            start = time.time()

            for _ in range(5):

                sorted_items = sorted(
                    items,
                    key=lambda x: x[1],
                    reverse=True
                )[:10]

            sort_time = (
                time.time() - start
            ) / 5


            # -----------------------------------------
            # RESULTS
            # -----------------------------------------

            result = pd.DataFrame(
                {
                    "method": [
                        "Min Heap",
                        "Full Sort"
                    ],
                    "time (seconds)": [
                        heap_time,
                        sort_time
                    ]
                }
            )


            st.subheader(
                "Performance Comparison"
            )

            st.bar_chart(
                result.set_index(
                    "method"
                ),
                use_container_width=True
            )


            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    " Heap",
                    f"{heap_time:.4f} sec"
                )

            with col2:

                st.metric(
                    "Full Sort",
                    f"{sort_time:.4f} sec"
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Trending Topics Analyzer | "
    "Minor Project | "
    "HashMap + Min Heap | "
    "HuffPost News Category Dataset"
)