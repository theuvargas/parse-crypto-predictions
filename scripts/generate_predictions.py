import argparse
import json
from typing import Any, TypedDict
from uuid import UUID, uuid4

import requests
from requests import RequestException

from src.models import ExtractedValueType, TargetType, Timeframe
from src.database import init_db, latest_example_id, log_predictions

DATASET_PATH = "data/annotated-dataset.json"
API_BASE_URL = "http://localhost:8000"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--batch-sizes",
        nargs="+",
        type=int,
        default=[1, 16],
        help="A list of batch sizes to evaluate.",
    )
    parser.add_argument(
        "--run-id",
        type=UUID,
        default=None,
        help="Existing run identifier to resume; defaults to a new UUID",
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
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
    except RequestException as exc:
        raise RuntimeError(f"Request to {url} failed") from exc

    data: list[APIResponse] | APIResponse = response.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]


def log_prediction_results(
    run_id: UUID,
    batch_id: int,
    batch_size: int,
    predictions: list[APIResponse],
):
    for i, pred in enumerate(predictions):
        log_predictions(
            run_id=run_id,
            batch_id=batch_id,
            batch_size=batch_size,
            example_id=batch_id + i,
            raw_prediction_json=pred,
        )


def main():
    init_db()
    args = parse_args()
    run_id = args.run_id or uuid4()

    with open(DATASET_PATH) as f:
        dataset: list[DatasetEntry] = json.load(f)

    for batch_size in args.batch_sizes:
        endpoint = "parse_prediction_batch" if batch_size > 1 else "parse_prediction"
        last_example = latest_example_id(run_id, batch_size)
        start_index = (last_example + 1) if last_example is not None else 0
        if start_index >= len(dataset):
            print(
                f"Run {run_id} already processed all examples for batch size {batch_size}"
            )
            continue

        print(
            f"Processing run {run_id} batch size {batch_size} starting from example {start_index}"
        )

        for i in range(start_index, len(dataset), batch_size):
            print(f"Processing batch {i}...")
            batch = dataset[i : i + batch_size]
            input_batch = format_api_input(batch)

            if endpoint == "parse_prediction":
                payload = input_batch[0]
            else:
                payload = {"items": input_batch}

            predictions = fetch_predictions(endpoint, payload)

            log_prediction_results(
                run_id=run_id,
                batch_id=i,
                batch_size=batch_size,
                predictions=predictions,
            )

        print(f"Completed run {run_id} for batch size {batch_size}")


if __name__ == "__main__":
    main()
