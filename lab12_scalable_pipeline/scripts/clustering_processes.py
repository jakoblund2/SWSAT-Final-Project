import argparse
import json
import os

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_PATH = os.path.join(BASE_DIR, "storage", "eo_metadata.json")


def load_metadata(path):
    with open(path, "r") as f:
        return json.load(f)


def run_clustering(data, k):
    features = np.array([[item["brightness"], item["contrast"]] for item in data])
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(features)
    for i, item in enumerate(data):
        item["cluster"] = int(labels[i])
    return data


def visualize_clusters(data):
    scatter = plt.scatter(
        [item["brightness"] for item in data],
        [item["contrast"] for item in data],
        c=[item["cluster"] for item in data],
        cmap="viridis"
    )
    plt.colorbar(scatter, label="Cluster")
    plt.xlabel("Brightness")
    plt.ylabel("Contrast")
    plt.title("EO Product Clusters")
    plt.tight_layout()
    plt.show()


def run_clustering_pipeline(k):
    data = load_metadata(METADATA_PATH)
    print(f"Loaded {len(data)} products")

    data = run_clustering(data, k)
    print(f"Clustering done with k={k}")

    for item in data:
        print(f"{item['eo_product_id']} | cluster={item['cluster']}")

    with open(METADATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

    visualize_clusters(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", type=int, default=3)
    args = parser.parse_args()

    run_clustering_pipeline(args.k)