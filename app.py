from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'

# ----------------------------------------------------------------------------[ Model & Data Loading ]----------------------------------------------------------------------------------------------------
with open("model/model.pkl", "rb") as f:
    model_data = pickle.load(f)

knn = model_data["knn"]
X_pca = model_data["X_pca"]
clusters = model_data["clusters"]
names = model_data["names"]
ages = model_data["ages"]

df_interface = pd.read_csv("dataset/interface_data.csv")
df_clean = pd.read_csv("dataset/clean_data.csv")

df_interface['clean_name'] = df_interface['name'].astype(str).str.strip().str.lower()
game_list = sorted(list(set(names)))

# ----------------------------------------------------------------------------[ Helpers Functions ]----------------------------------------------------------------------------------------------------
def get_recommendations(game_name, user_age, n_recommendations=5):
    if game_name not in game_list: return []
    
    game_idx = np.where(names == game_name)[0][0]
    game_cluster = clusters[game_idx]
    
    cluster_indices = set(np.where(clusters == game_cluster)[0])
    distances, indices = knn.kneighbors(X_pca[game_idx].reshape(1, -1), n_neighbors=len(names))
    
    results = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx == game_idx or idx not in cluster_indices: continue
        if ages[idx] > user_age: continue
            
        results.append({"name": names[idx], "similarity": round((1 - distance) * 100, 2)})
        
        if len(results) == n_recommendations: break
            
    return results


def _safe_get_val(row, col_name, default="N/A", df_cols=None):
    if col_name in df_cols:
        val = row[col_name]
        if pd.notna(val) and str(val).strip().lower() != 'nan':
            return str(val)
    return default


def get_game_info(game_name):
    target_name = str(game_name).strip().lower()   
    game_row = df_interface[df_interface['clean_name'] == target_name]
    
    if game_row.empty:
        return {
            "name": game_name,
            "header_image": "",
            "short_description": "No description available.",
            "categories": "N/A",
            "genres": "N/A"
        }
    
    row = game_row.iloc[0]
    cols = df_interface.columns
    
    return {
        "name": game_name,
        "header_image": _safe_get_val(row, "header_image", "", cols),
        "short_description": _safe_get_val(row, "short_description", "No description available.", cols),
        "categories": _safe_get_val(row, "categories", "N/A", cols),
        "genres": _safe_get_val(row, "genres", "N/A", cols)
    }

# ----------------------------------------------------------------------------[ Route ]----------------------------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_name = request.form.get("name", "").strip()
        user_age = request.form.get("age", "").strip()
        
        if user_name.lower() == "admin":
            return redirect(url_for("dashboard"))
            
        session['user_name'] = user_name
        session['user_age'] = int(user_age) if user_age.isdigit() else 20
        return redirect(url_for("Steam_recommendation_System"))
    return render_template("home.html")

@app.route("/Steam_recommendation_System", methods=["GET", "POST"])
def Steam_recommendation_System():
    if 'user_name' not in session: return redirect(url_for("home"))
    
    selected_game = request.form.get("game") if request.method == "POST" else None
    
    recommendations = []
    selected_info = None
    
    if selected_game:
        selected_info = get_game_info(selected_game)
        recs = get_recommendations(selected_game, session['user_age'])
        for rec in recs:
            info = get_game_info(rec["name"])
            info["similarity"] = rec["similarity"]
            recommendations.append(info)
            
    return render_template("srs.html", games=game_list, selected_info=selected_info, recommendations=recommendations)

@app.route("/dashboard")
def dashboard():
    total_games = len(df_clean)
    avg_price = round(df_clean['price_sar'].mean(), 2) if 'price_sar' in df_clean.columns else 0
    
    summary_stats = {
        "total_games": total_games,
        "avg_price": avg_price
    }

    preview_columns = ['name', 'release_year', 'price_sar', 'is_free', 'discount_pct', 'required_age', 'positive_reviews']
    preview_columns = [col for col in preview_columns if col in df_clean.columns]
    top_5_rows = df_clean[preview_columns].head(5).to_dict(orient='records')

    charts_data = [
        {
            "id": "chart1_hist",
            "title": "Numerical Variables Distribution (Histograms)",
            "image_filename": "img/chart1_hist.png",
            "insight": "Most numerical variables like reviews, playtimes, and concurrent users show a severe right-skewed distribution. This mathematically confirms that the vast majority of games have low engagement metrics, while a few blockbuster titles hold massive numbers. Conversely, release years are left-skewed, showing rapid growth in game releases in recent years."
        },
        {
            "id": "chart2_age",
            "title": "Games by Required Age",
            "image_filename": "img/chart2_age.png",
            "insight": "An overwhelming majority of games are rated 0, meaning they have no age restrictions and are suitable for everyone. The next prominent category is 17+, while other ratings are nearly non-existent. This reveals a clear strategy by developers to target the widest possible audience."
        },
        {
            "id": "chart3_boxplot",
            "title": "Boxplots of Release Year & Price",
            "image_filename": "img/chart3_boxplot.png",
            "insight": "The boxplots clearly identify statistical outliers. For release years, games launched before 2005 are considered outliers. For prices, the median price sits below 50 SAR, and any game priced above 170 SAR is flagged as an outlier, proving that high premium prices are exceptions on Steam."
        },
        {
            "id": "chart4_categ",
            "title": "Top Genres, Categories, Tags, Developers & Publishers",
            "image_filename": "img/chart4_categ.png",
            "insight": "Indie, Action, and Adventure are the dominant genres and tags in terms of volume. When looking at industry leaders, Capcom ranks high among developers, while Sega and Ubisoft lead as publishers. This highlights a market balanced between high-volume indie creation and high-revenue corporate publishing."
        },
        {
            "id": "chart5_bool",
            "title": "Binary Features Comparison (Boolean)",
            "image_filename": "img/chart5_bool.png",
            "insight": "Paid games dominate the platform compared to free-to-play options. In terms of OS compatibility, Windows is universally supported, whereas Mac is supported by less than half of the catalog, and Linux compatibility drops even lower, emphasizing platform accessibility barriers."
        },
        {
            "id": "chart6_corr",
            "title": "Correlation Matrix of Steam Game Features",
            "image_filename": "img/chart6_corr.png",
            "insight": "There is a near-perfect positive correlation (0.98) between recommendations, positive reviews, negative reviews, and peak concurrent users. This shows that popularity and player base scale all review metrics simultaneously. Meanwhile, price and achievement counts show almost no linear relationship with popularity."
        }
    ]

    return render_template(
        "dashboard.html", 
        summary_stats=summary_stats,
        preview_columns=preview_columns,
        top_5_rows=top_5_rows,
        charts_data=charts_data
    )

if __name__ == "__main__":
    app.run(debug=True)