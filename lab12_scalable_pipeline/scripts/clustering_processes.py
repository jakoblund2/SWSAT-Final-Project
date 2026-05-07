import argparse
import json
import os

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.cluster import KMeans

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_PATH = os.path.join(BASE_DIR, "storage", "eo_metadata.json")
RESULTS_PATH = os.path.join(BASE_DIR, "storage", "eo_results_clustering.json")


def load_metadata(path):
    with open(path, "r") as f:
        return json.load(f)


def run_clustering(data, k):
    features = np.array([[item["brightness"], item["contrast"]] for item in data])
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(features)
    centers = kmeans.cluster_centers_

    center_scores = [(c[0] + c[1]) / 2 for c in centers]
    sorted_ids = sorted(range(k), key=lambda i: center_scores[i])
    meanings = ["low_quality", "medium_quality", "high_quality"]
    meaning_map = {sorted_ids[i]: meanings[i] for i in range(k)}

    for i, item in enumerate(data):
        cid = int(labels[i])
        item["cluster"] = cid
        item["cluster_center"] = round(center_scores[cid], 4)
        item["cluster_meaning"] = meaning_map[cid]
    return data


def visualize_clusters(data, save_path=None):
    df = pd.DataFrame({
        "brightness": [item["brightness"] for item in data],
        "contrast":   [item["contrast"]   for item in data],
        "cluster":    [item["cluster_meaning"] for item in data],
    })

    plt.figure(figsize=(9, 6))
    sns.scatterplot(
        data=df,
        x="brightness",
        y="contrast",
        hue="cluster",
        palette={"low_quality": "#d62728", "medium_quality": "#ff7f0e", "high_quality": "#2ca02c"},
        s=80,
        alpha=0.8
    )
    plt.title("EO Product Clustering (K-means, k=3)", fontsize=14)
    plt.xlabel("Brightness")
    plt.ylabel("Contrast")
    plt.legend(title="Cluster", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Cluster plot saved to {save_path}")

    plt.show()


def run_clustering_pipeline(k):
    if os.path.exists(RESULTS_PATH):
        data = load_metadata(RESULTS_PATH)
    else:
        data = load_metadata(METADATA_PATH)
    print(f"Loaded {len(data)} products")

    data = run_clustering(data, k)
    print(f"Clustering done with k={k}")

    for item in data:
        print(f"{item['eo_product_id']} | cluster={item['cluster']}")

    with open(RESULTS_PATH, "w") as f:
        json.dump(data, f, indent=2)

    visualize_clusters(data, save_path=os.path.join(BASE_DIR, "storage", "cluster_plot.png"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", type=int, default=3)
    args = parser.parse_args()

    run_clustering_pipeline(args.k)
