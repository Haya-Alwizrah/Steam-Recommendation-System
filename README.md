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
- Dropped the `metacritic_score` column due to the high percentage of missing values.
- Removed rows containing missing values in the remaining columns.

---
## Duplicate Records:
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

- `developer`, `publisher`, `genres`, `categories`, `tags`:
These columns contained multiple values within a single cell. We split each value into separate columns using one-hot encoding and added prefixes to the generated columns to avoid duplicate column names.
generated columns count:
  - developer: 1291
  - publisher: 926
  - genres: 24
  - categories: 56
  - tags: 397

- drop constant:
During the exploration, we found that `coming_soon` and `platforms_win` each contained only a single unique value, so they were removed because they provide no useful information for analysis or modeling.

- `release_date`:
The original values were stored as dates such as `May 17, 2022`, which Pandas treated as object type. We used a regular expression (Regex) to extract only the release year.

- Price Conversion:
We converted the `price_usd` column to `price_sar` by multiplying each value by 3.75.

---
# Models:

## Feature Scaling

Before training the models, all numerical features were standardized using `StandardScaler`.

Several numerical columns, including: (recommendations, positive_reviews, negative_reviews, estimated_owners, avg_playtime_forever, avg_playtime_2weeks, median_playtime, peak_ccu, dlc_count, achievements)

showed highly skewed distributions. To reduce the impact of extreme values and improve model performance, a `log1p()` transformation was applied before scaling.

## Principal Component Analysis (PCA)

After preprocessing and one-hot encoding, the dataset contained a large number of features. To reduce dimensionality while preserving the most important information, Principal Component Analysis (PCA) was applied.

```python
pca = PCA(n_components=0.95, random_state=42)
```

The model reduced the dataset from 2712 features to 359 principal components while retaining 95% of the variance.

Benefits of PCA:
* Reduces computational complexity.
* Removes redundant information.
* Improves clustering efficiency.
* Enhances recommendation system performance.

## K-Means Clustering

As this project is based on **unsupervised learning**, K-Means clustering was used to group similar games together.

To determine the optimal number of clusters, the **Elbow Method** was applied by testing multiple values of `k`.

```python
kmeans = KMeans(n_clusters=7, random_state=42, n_init="auto")
```

Based on the Elbow Method results, the dataset was divided into **7 clusters**.

The clustering step helps organize games with similar characteristics into the same group, improving the quality of recommendations.

## Recommendation System (K-Nearest Neighbors)

To generate recommendations, a **K-Nearest Neighbors (KNN)** model was trained using cosine similarity.

```python
knn = NearestNeighbors(n_neighbors=6, metric="cosine")
```

### Recommendation Process

1. The user selects a game.
2. The selected game is transformed into the PCA feature space.
3. KNN searches for the most similar games using cosine similarity.
4. The system returns the 5 nearest games as recommendations.

### Why Cosine Similarity?
Cosine similarity measures how similar two games are based on the direction of their feature vectors rather than their absolute values. This makes it particularly suitable for recommendation systems, where games may vary greatly in popularity or playtime but still share similar characteristics.

---

## Model Pipeline

```text
Raw Data
    ↓
Data Preprocessing
    ↓
Log Transformation
    ↓
StandardScaler
    ↓
PCA (95% Variance Retained)
    ↓
K-Means Clustering (7 Clusters)
    ↓
KNN Recommendation System
    ↓
Top 5 Recommended Games
```

