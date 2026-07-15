from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import numpy as np
import pickle
import os

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

# ----------------------------------------------------------------------------[ Helpers Functions ]----------------------------------------------------------------------------------------------------
def get_recommendations(game_name, user_age, n_recommendations=5):
    if game_name not in names or knn is None: return []
    game_idx = np.where(names == game_name)[0][0]
    game_cluster = clusters[game_idx]
    
    cluster_indices = np.where(clusters == game_cluster)[0]
    distances, indices = knn.kneighbors(X_pca[game_idx].reshape(1, -1), n_neighbors=len(names))
    
    results = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx == game_idx or idx not in cluster_indices: continue
        if ages[idx] > user_age: continue
        results.append({"name": names[idx], "similarity": round((1 - distance) * 100, 2)})
        if len(results) == n_recommendations: break
    return results

def get_game_info(game_name):
    target_name = str(game_name).strip().lower()
    game_row = df_interface[df_interface['name'].astype(str).str.strip().str.lower() == target_name]
    if game_row.empty:
        return {
            "name": game_name,
            "header_image": "",
            "short_description": "No description available.",
            "categories": "N/A",
            "genres": "N/A"}
    
    row = game_row.iloc[0]
    def safe_get(col, default):
        if col in df_interface.columns:
            val = row[col]
            if pd.notna(val) and str(val).strip().lower() != 'nan': return str(val)
        return default
        
    return {
        "name": game_name,
        "header_image": safe_get("header_image", ""),
        "short_description": safe_get("short_description", "No description available."),
        "categories": safe_get("categories", "N/A"),
        "genres": safe_get("genres", "N/A")
    }

# ----------------------------------------------------------------------------[ Route ]----------------------------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
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
    
    game_list = sorted(list(set(names)))
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
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)