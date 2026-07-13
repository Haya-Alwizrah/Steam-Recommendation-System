# Steam Recommendation System

Steam Recommendation System is a project focused on Exploratory Data Analysis (EDA), with the addition of an unsupervised machine learning model to build a game recommendation system, developed as part of the Tuwaiq Academy (Data Science and Artificial Intelligence) Bootcamp.

Live Demo: ....

---
# Exploratory Data Analysis (EDA)

## Dataset Information
- df.info()
```
bool(5), float64(2), int64(12), object(10)
```

- df.columns:
```
Index(['app_id', 'name', 'release_date', 'coming_soon', 'price_usd', 'is_free',
       'discount_pct', 'developer', 'publisher', 'genres', 'categories',
       'tags', 'platforms_win', 'platforms_mac', 'platforms_linux',
       'metacritic_score', 'recommendations', 'positive_reviews',
       'negative_reviews', 'estimated_owners', 'avg_playtime_forever',
       'avg_playtime_2weeks', 'median_playtime', 'peak_ccu', 'required_age',
       'dlc_count', 'achievements', 'short_description', 'header_image'],
      dtype='object')
```
---
## Missing values:
```
release_date         0.468227
developer            0.535117
publisher            0.802676
genres               0.535117
categories           0.602007
tags                 0.401338
metacritic_score    63.879599
estimated_owners     0.334448
dtype: float64
```
- Dropped the ذmetacritic_scoreذ column due to the high percentage of missing values.
- Removed rows containing missing values in the remaining columns.

---
# Duplicate Records:
`df.duplicated().sum()` showed that there were no completely duplicated rows. However, when examining the name column, we found two games with duplicate names but different values in other columns.

`df["name"].value_counts()`
```
Time Gentlemen, Please! and Ben There, Dan That! Special Edition  Double Pack    2
Call of Duty®: WWII                                                              2
```
To keep the most reliable record, we sorted the DataFrame by positive_reviews in descending order and kept the first occurrence of each game.
```
df = df.sort_values(by='positive_reviews', ascending=False).reset_index(drop=True)
df = df.drop_duplicates(subset=['name'], keep='first')
```
---
## Data Preprocessing:

- `estimated_owners`:
The original values were stored as ranges (e.g., 1,000,000 .. 2,000,000), which Pandas interpreted as object type. We created a function to split each range into its lower and upper bounds, then replaced the range with its average value.

- `genres`, `categories`, `tags`:
These columns contained multiple values within a single cell. We split each value into separate columns and added prefixes to the generated columns to avoid duplicate column names.
generated columns count:
  - genres: 24
  - categories: 56
  - tags: 397

- drop constant:
During the exploration, we found that `coming_soon` and `platforms_win` each contained only a single unique value, so they were removed because they provide no useful information for analysis or modeling.

- `release_date`:
The original values were stored as dates such as `May 17, 2022`, which Pandas treated as object type. We used a regular expression (Regex) to extract only the release year.

- Price Conversion:
We converted the `price_usd` column to `price_sar` by multiplying each value by 3.75.
