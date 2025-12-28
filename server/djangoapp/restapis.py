import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Get backend URL from environment variables
backend_url = os.getenv("backend_url", "http://localhost:3030")
sentiment_analyzer_url = os.getenv("sentiment_analyzer_url", "http://localhost:5000/")


def get_request(endpoint, **kwargs):
    """
    Generic GET request helper.

    endpoint: string like '/fetchDealers' or '/fetchReviews/dealer/1'
    kwargs: query parameters (optional)
    """
    request_url = backend_url + endpoint
    try:
        print(f"GET from {request_url} params: {kwargs}")
        response = requests.get(request_url, params=kwargs)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Network exception occurred: {e}")
        # Return an empty list dict to avoid breaking callers
        return []


def analyze_review_sentiments(text):
    """
    Call the sentiment analyzer service and return the sentiment label.

    text: review text string
    """
    request_url = sentiment_analyzer_url + "analyze/" + text
    try:
        print(f"GET sentiment from {request_url}")
        response = requests.get(request_url)
        response.raise_for_status()
        result = response.json()

        # If the service returns a dict like {"sentiment": "positive"}
        if isinstance(result, dict) and "sentiment" in result:
            return result["sentiment"]

        # If it already returns a plain string like "positive"
        if isinstance(result, str):
            return result

        # Fallback
        return "neutral"
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")
        return "neutral"


def post_review(data_dict):
    """
    POST a review to the backend.
    """
    request_url = backend_url + "/insert_review"
    try:
        print(f"POST to {request_url} with body: {data_dict}")
        response = requests.post(request_url, json=data_dict)
        response.raise_for_status()
        print(response.json())
        return response.json()
    except Exception as e:
        print(f"Network exception occurred: {e}")
        return {}
