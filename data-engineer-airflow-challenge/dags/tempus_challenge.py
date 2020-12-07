import os
import requests
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
HEADERS = {'x-api-key': NEWS_API_KEY}
BASE_URL = 'https://newsapi.org/v2/'
TOPIC_STRINGS = ['Tempus Labs', 'Eric Lefkofsky', 'Cancer', 'Immunotherapy']
DATE_STR = '{:%Y-%m-%d}'.format(datetime.today())
BUCKET = 's3://tempus-challenge-dm/'
SUFFIX = '_top_headlines.csv'


def get_sources(**kwargs):
    """
    Grabs the english sources from News API.
    """
    source_ids = []
    sources_url = BASE_URL + 'sources'
    payload = {'language': 'en'}
    sources = requests.get(sources_url, params=payload, headers=HEADERS)
    sources = sources.json()
    for source in sources['sources']:
        source_ids.append(source['id'])
    print('Source_ids: {}'.format(source_ids))
    return source_ids


def get_headlines(manual_ids=None, **context):
    """
    Grabs the headlines for the identified sources in chunks.
    Going off of the 10 per source that seems to be true, and 100 max per pull
    Checked against the current total results for an all-sources call. Matched.
    """
    # Control logic for testing dimensionality of result
    if manual_ids is None:
        source_ids = context['task_instance'] \
            .xcom_pull(task_ids='getting_sources')
    else:
        source_ids = manual_ids
    size = 10  # Block size for pulling headlines
    top_url = BASE_URL + 'top-headlines'
    payload = {'pageSize': 100}
    # Get expected number of headlines
    payload['sources'] = ', '.join(source_ids)
    result = requests.get(top_url, params=payload, headers=HEADERS)
    result_parsed = result.json()
    expected_results = result_parsed['totalResults']
    articles = list()
    # Loop through chunks of 10 sources at once
    for i in range(0, len(source_ids), size):
        block = source_ids[i:i + size]
        payload['sources'] = ', '.join(block)
        print('Pulling headlines for: {}'.format(payload['sources']))
        result = requests.get(top_url, params=payload, headers=HEADERS)
        result_parsed = result.json()  # Requests built in works fine here
        articles.extend(result_parsed['articles'])
    # This is our data transform. Works fine off the shelf, so...
    articles_df = pd.io.json.json_normalize(articles)
    actual_results = len(articles_df)
    # Because we can't guarantee the order headlines come in above, so we
    # break it apart after stitching the original df -- Again, mostly to
    # save API calls.
    if manual_ids is None:  # For testing
        for source in articles_df['source.id'].unique().tolist():
            cur_s3_obj = '{}{}/{}{}'.format(BUCKET, source, DATE_STR, SUFFIX)
            cur_df = articles_df[articles_df['source.id'] == source]
            cur_df.to_csv(cur_s3_obj, index=False)
    return {'expected_results': expected_results,
            'actual_results': actual_results}


def get_topic_headlines(**context):
    """
    Grabs the headlines for the topics in chunks.
    """
    everything_url = BASE_URL + 'everything'
    payload = {'pageSize': 100}
    headers = {'x-api-key': NEWS_API_KEY}
    articles = list()
    # Loop through chunks of 10 sources at once
    for topic in TOPIC_STRINGS:
        q = topic
        pretty_topic = topic.lower().replace(' ', '-')
        payload['q'] = q
        payload['from'] = DATE_STR
        print('Pulling headlines for: {}'.format(payload['q']))
        result = requests.get(everything_url, params=payload, headers=headers)
        result_parsed = result.json()  # Requests built in works fine here
        articles = result_parsed['articles']
        articles_df = pd.io.json.json_normalize(articles)
        cur_s3_obj = '{}{}/{}{}'.format(BUCKET, pretty_topic, DATE_STR, SUFFIX)
        articles_df.to_csv(cur_s3_obj, index=False)
