"""Script to run a clustering algorithm over the classified comments"""
import argparse
import pandas as pd
from sklearn.cluster import KMeans


def main(source=None, output_path=None):
    df = pd.read_parquet(source)

    df_for_clustering = df[["sentiment_negative", "sentiment_neutral", "sentiment_positive"]]

    kmeans = KMeans(n_clusters=3).fit(df_for_clustering)
    # centroids = kmeans.cluster_centers_
    # print(centroids)

    df['clusters'] = kmeans.labels_
    df.to_csv(output_path + '/' + 'final_result.csv', index=False, encoding='utf-8')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_data", help="Input files to process")
    parser.add_argument("-o", "--output_data", help="Output files to process")
    args = parser.parse_args()

    main(source=args.input_data, output_path=args.output_data)
