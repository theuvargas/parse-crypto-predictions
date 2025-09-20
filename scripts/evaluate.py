import argparse
import json
from typing import Any, TypedDict

import requests
from requests import RequestException

from src.models import ExtractedValueType, TargetType, Timeframe
from src.database import init_db

DATASET_PATH = "data/annotated-dataset.json"
API_BASE_URL = "http://localhost:8000"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--batch_sizes",
        nargs="+",
        type=int,
        default=[1, 16],
        help="A list of batch sizes to evaluate.",
    )
    return parser.parse_args()


class DatasetEntry(TypedDict):
    post_text: str
    post_created_at: str
    target_type: TargetType
    extracted_value: ExtractedValueType
    bear_bull: int
    timeframe: Timeframe
    notes: list[str]


class APIResponse(TypedDict):
    target_type: TargetType
    extracted_value: ExtractedValueType
    bear_bull: int
    timeframe: Timeframe
    notes: list[str]


def format_api_input(batch: list[DatasetEntry]) -> list[dict]:
    return [
        {"post_text": item["post_text"], "post_created_at": item["post_created_at"]}
        for item in batch
    ]


def fetch_predictions(endpoint: str, payload: Any) -> list[APIResponse]:
    """Send a POST request and normalize the response to a list."""

    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
    except RequestException as exc:
        raise RuntimeError(f"Request to {url} failed") from exc

    data: list[APIResponse] | APIResponse = response.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]


def evaluate_predictions(true: list[DatasetEntry], predictions: list[APIResponse]):
    """Calculate metrics for the variables.

    - target_type, extracted_value, timeframe: accuracy, precision, recall, F1 score
    - target_type: confusion matrix
    - bear_bull: Spearman correlation
    """
    pass


def main():
    init_db()
    args = parse_args()

    with open(DATASET_PATH) as f:
        dataset: list[DatasetEntry] = json.load(f)

    responses: list[APIResponse] = []
    for batch_size in args.batch_sizes:
        endpoint = "parse_prediction_batch" if batch_size > 1 else "parse_prediction"
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i : i + batch_size]
            input_batch = format_api_input(batch)

            if endpoint == "parse_prediction":
                payload = input_batch[0]
            else:
                payload = {"items": input_batch}

            predictions = fetch_predictions(endpoint, payload)
            print(predictions)
            responses.extend(predictions)

        evaluate_predictions(dataset, responses)


if __name__ == "__main__":
    main()
