# Notes on process and solution for the Tempus Data Engineering airflow challenge.

[Code is available here](https://github.com/larcat/challenges/tree/master/data-engineer-airflow-challenge)
  `https://github.com/larcat/challenges/tree/master/data-engineer-airflow-challenge`

1. In order to get the local environment working, I had to make some modifications to the `Dockerfile`. This is an existing issue in the `docker-airflow` repo. Specifics are commented with the change in the `Dockerfile`.

2. I wouldn't use a dotenv for secrets handling for something like this in production (I'd likely use AWS parameter store for this type of task or whatever the existing method on the team was), but didn't want to submit something with a cleartext 'secret' in it, thus the use of dotenv for handling the API key and AWS secrets.

3. The developer/free level of the News API doesn't allow you to grab additional pages in paginated queries. The number of top headlines returned per source isn't strictly documented in the News API docs, but a bit of trial and error made it look like 10. That informed how I structured my API calls to try and get the maximum number of responses given the limitation of 100/day for the free tier:

4. I started down the path of parallelizing the headlines calls with a BranchingPythonOperator but apparently that's not the intended usecase for those, so abandoned that.

5. No boto3 neccessary, just the s3fs dependency and direct pandas writing. No messing around with io.

6. The results bucket is public via the console or CLI at `s3://tempus-challenge-dm/` / `aws s3 ls s3://tempus-challenge-dm/`

## TODOS
1. Add in pagination/greater than 100 sources checks for `get_sources` -- it's close to 100.
2. Add pagination handling for `get_topic_headlines` function -- When sources goes over 100 it could fail.
3. Empty dataset/pandas df handling (writes empty objects at the moment.)
4. Handling for maxing out current API-limits gracefully.
5. Add mock data for the tests rather than the unneccessary API calls.

## Requirements
- [x] Use Airflow to construct a new data pipeline (DAG) named 'tempus_challenge_dag'.
- [x] Data pipeline must be scheduled to run once a day.
- [x] Data pipeline will:
  - [x] Retrieve all English news sources.
  - [x] For each news source, retrieve the top headlines.
    - [x] Top headlines must be flattened into a CSV file. CSV Filename: `<pipeline_execution_date>_top_headlines.csv`
    - [x] Result CSV must be uploaded to the following s3 location `<s3_bucket>/<source_name>`
- [x] The solution must contain at least one test for your headline transformation.
- [x] The solution must be start-able via `make run`.
- [x] The solution must be pep-8 compliant.
- [x] Bonus: Build a separate pipeline that uses the following keywords instead of English news sources: Tempus Labs, Eric Lefkofsky, Cancer, Immunotherapy
- [x] Bonus: Write an integration test for any of the external services your solution connects to.


