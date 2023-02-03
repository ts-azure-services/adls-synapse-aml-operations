"""Script to get sentiment off customer reviews"""
import argparse
import time
import pandas as pd
from mltable import from_delta_lake
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../../')))
from authenticate.authenticate import auth_var


def sample_analyze_sentiment(documents) -> None:
    sentiment_list = []
    endpoint, key = auth_var['text_analytics_endpoint'], auth_var['text_analytics_key']
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    if len(documents) > 0:
        for doc in documents:
            result = text_analytics_client.analyze_sentiment([doc], show_opinion_mining=False)
            if result:
                sentiment_list.append(result[0].sentiment)
                time.sleep(0.2)
    else:
        raise ValueError('Length of list is zero.')
    return sentiment_list


def main(source=None, output_path=None):
    mltable_version = from_delta_lake(
            delta_table_uri=source,
            timestamp_as_of='2023-01-15T00:00:00Z',
            )
    df = mltable_version.to_pandas_dataframe()
    print(df.head())
    print(len(df))

    # Get column of comments
    reviews = df['customer_review'].to_list()

    sentiments = sample_analyze_sentiment(reviews)
    assert len(sentiments) == len(reviews)

    if len(sentiments) == len(df):
        df['sentiments'] = sentiments

        # Get dummy columns on sentiment, to allow for downstream clustering
        df = pd.get_dummies(df, prefix=['sentiment'], columns=['sentiments'])

        df.to_parquet(output_path + "/" + "sentiment.parquet")
    else:
        raise ValueError('Sentiments returned are different than the dataframe.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_data", help="Input files to process")
    parser.add_argument("-o", "--output_data", help="Output files to process")
    args = parser.parse_args()

    main(source=args.input_data, output_path=args.output_data)
