import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import duckdb
from scipy.stats import spearmanr
from sklearn.metrics import (
    accuracy_score,
    ConfusionMatrixDisplay,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
import matplotlib.pyplot as plt
from src import config
from src.models import ParsedPredictionResponse


@dataclass
class AlignedExample:
    prediction_id: str
    prediction: ParsedPredictionResponse
    annotation: ParsedPredictionResponse


def load_annotations() -> dict[str, ParsedPredictionResponse]:
    with open(config.dataset_file) as f:
        dataset = json.load(f)

    annotations = {}
    for entry in dataset:
        annotations[str(entry["id"])] = ParsedPredictionResponse.model_validate(
            {
                "target_type": entry["target_type"],
                "extracted_value": entry.get("extracted_value"),
                "bear_bull": entry["bear_bull"],
                "timeframe": entry["timeframe"],
                "notes": entry["notes"],
            }
        )

    return annotations


def fetch_predictions() -> dict[
    tuple[str, int], list[tuple[str, ParsedPredictionResponse]]
]:
    connection = duckdb.connect(config.db_file, read_only=True)
    try:
        rows = connection.execute(
            """
            SELECT run_id, batch_size, example_id, prediction_id, raw_prediction_json
            FROM prediction_results
            ORDER BY run_id, batch_size, example_id
            """
        ).fetchall()
    finally:
        connection.close()

    grouped = defaultdict(list)
    for run_id, batch_size, example_id, prediction_id, raw_prediction_json in rows:
        if isinstance(raw_prediction_json, str):
            payload = json.loads(raw_prediction_json)
        else:
            payload = raw_prediction_json
        prediction = ParsedPredictionResponse.model_validate(payload)
        resolved_id = (
            prediction.id
            or prediction_id
            or payload.get("id")
            or str(example_id)
        )
        grouped[(str(run_id), batch_size)].append((str(resolved_id), prediction))

    return grouped


def align_predictions(
    predictions: dict[tuple[str, int], list[tuple[str, ParsedPredictionResponse]]],
    annotations: dict[str, ParsedPredictionResponse],
) -> dict[tuple[str, int], list[AlignedExample]]:
    aligned = {}
    for key, items in predictions.items():
        aligned[key] = []
        for prediction_id, prediction in items:
            annotation = annotations.get(prediction_id)
            if annotation is None:
                raise KeyError(
                    f"No annotation found for prediction id {prediction_id}"
                )

            aligned[key].append(
                AlignedExample(
                    prediction_id=prediction_id,
                    prediction=prediction,
                    annotation=annotation,
                )
            )

    return aligned


def serialise_timeframe(model: ParsedPredictionResponse) -> str:
    timeframe = model.timeframe
    return json.dumps(
        {
            "explicit": timeframe.explicit,
            "start": timeframe.start.isoformat() if timeframe.start else None,
            "end": timeframe.end.isoformat() if timeframe.end else None,
        },
        sort_keys=True,
    )


def serialise_extracted_value(model: ParsedPredictionResponse) -> str:
    value = model.extracted_value
    if value is None:
        return "null"

    return json.dumps(value.model_dump(mode="python"), sort_keys=True, default=str)


def print_classification_metrics(
    name: str, y_true: list[str], y_pred: list[str]
) -> None:
    labels = sorted(set(y_true) | set(y_pred))
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(
        y_true,
        y_pred,
        labels=labels,
        average="macro",
    )
    recall = recall_score(
        y_true,
        y_pred,
        labels=labels,
        average="macro",
    )
    f1 = f1_score(
        y_true,
        y_pred,
        labels=labels,
        average="macro",
    )

    print(name)
    print(f"  accuracy: {accuracy:.4f}")
    print(f"  precision: {precision:.4f}")
    print(f"  recall: {recall:.4f}")
    print(f"  f1: {f1:.4f}")


def compute_metrics_for_group(examples: list[AlignedExample]):
    y_true_target = [ex.annotation.target_type for ex in examples]
    y_pred_target = [ex.prediction.target_type for ex in examples]

    labels = sorted(set(y_true_target) | set(y_pred_target))
    matrix = confusion_matrix(y_true_target, y_pred_target, labels=labels)
    print_classification_metrics("target_type", y_true_target, y_pred_target)

    y_true_timeframe = [serialise_timeframe(ex.annotation) for ex in examples]
    y_pred_timeframe = [serialise_timeframe(ex.prediction) for ex in examples]
    exact_timeframe = sum(
        true == pred for true, pred in zip(y_true_timeframe, y_pred_timeframe)
    ) / len(examples)
    print("timeframe")
    print(f"  exact_match: {exact_timeframe:.4f}")

    y_true_value = [serialise_extracted_value(ex.annotation) for ex in examples]
    y_pred_value = [serialise_extracted_value(ex.prediction) for ex in examples]
    exact_value = sum(
        true == pred for true, pred in zip(y_true_value, y_pred_value)
    ) / len(examples)
    print("extracted_value")
    print(f"  exact_match: {exact_value:.4f}")

    true_bear_bull = [ex.annotation.bear_bull for ex in examples]
    pred_bear_bull = [ex.prediction.bear_bull for ex in examples]
    spearman = spearmanr(true_bear_bull, pred_bear_bull)
    print("bear_bull")
    print(f"  spearman: {spearman.statistic:.4f}")

    return labels, matrix


def save_confusion_matrix(
    labels: list[str], matrix, destination: Path, title: str
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    display = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=labels)
    display.plot(cmap="Blues", xticks_rotation=45, colorbar=False)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(destination, dpi=200)
    plt.close()


def run_metrics(aligned: dict[tuple[str, int], list[AlignedExample]]) -> None:
    for (run_id, batch_size), examples in aligned.items():
        print(f"run_id={run_id} batch_size={batch_size}")
        labels, matrix = compute_metrics_for_group(examples)
        image_path = Path(f"report/confusion_matrix/batch-size-{batch_size}.png")
        save_confusion_matrix(
            labels,
            matrix,
            image_path,
            title=f"batch_size={batch_size}",
        )
        print()


def main() -> None:
    annotations = load_annotations()
    predictions = fetch_predictions()
    aligned = align_predictions(predictions, annotations)
    run_metrics(aligned)


if __name__ == "__main__":
    main()
