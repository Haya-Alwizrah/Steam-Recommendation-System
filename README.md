# Steam Recommendation System

Steam Recommendation System is a project focused on Exploratory Data Analysis (EDA), with the addition of an unsupervised machine learning model to build a game recommendation system, developed as part of the Tuwaiq Academy (Data Science and Artificial Intelligence) Bootcamp.

Live Demo: ....

---
# EDA:

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
- drop column `metacritic_score`.
- drop row
---
# duplicates:
the result from `df.duplicated().sum()` showing no duplicates, howover when we explore date columns we found there are duplicate of 2 games name will there value is differnt:

`df["name"].value_counts()`
```
Time Gentlemen, Please! and Ben There, Dan That! Special Edition  Double Pack    2
Call of Duty®: WWII                                                              2
```
so we sort the dataframe based on `positive_reviews` then take first game.
```
df = df.sort_values(by='positive_reviews', ascending=False).reset_index(drop=True)
df = df.drop_duplicates(subset=['name'], keep='first')
```
---
## handle columns value:

- `estimated_owners`:
the orgonal value is like `1,000,000 .. 2,000,000` which i pandas catagorize it as object type, so create function that for each row split the 2 number and take the mean as new value.

- `genres`, `categories`, `tags`:
this 3 columns countain multivalue in one ceil, so to handle this we split each value in new column (like one hot encoding) and add prefix to each column name to avoid same name.

- drop constant:
while explor dataframe we found `coming_soon`, `platforms_win` have only one value, so we drop these columns

- `release_date`:
the orgonal value is like `May 17, 2022` which i pandas catagorize it as object type, so with regex we take only the year as new value.

- `price_usd` to `price_sar`:
we change the price from usd to sar by multply it by 3.75
