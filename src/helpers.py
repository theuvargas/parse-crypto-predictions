from .models import (
    NaturalLanguagePrediction,
    ParsedPrediction,
    ParsedPredictionResponse,
    PercentageChange,
    Range,
    Ranking,
    TargetPrice,
    TargetType,
)


def build_single_prompt(item: NaturalLanguagePrediction) -> str:
    return (
        "Input:\n"
        f"Post: '{item.post_text}'\n"
        f"Created at: {item.post_created_at.isoformat()}\n\n"
        "Output:\n"
    )


def build_batch_prompt(items: list[NaturalLanguagePrediction]) -> str:
    lines = [
        "You will receive multiple inputs. Produce one JSON object per entry in a JSON array.\n",
    ]
    for index, item in enumerate(items, start=1):
        lines.append(
            f"Input {index}:\n"
            f"Post: '{item.post_text}'\n"
            f"Created at: {item.post_created_at.isoformat()}\n\n"
        )
    lines.append("Output:\n")
    return "".join(lines)


def infer_target_type(parsed: ParsedPrediction) -> TargetType:
    extracted = parsed.extracted_value
    if isinstance(extracted, TargetPrice):
        return "target_price"
    if isinstance(extracted, PercentageChange):
        return "pct_change"
    if isinstance(extracted, Range):
        return "range"
    if isinstance(extracted, Ranking):
        return "ranking"
    return "none"


def to_response(parsed: ParsedPrediction) -> ParsedPredictionResponse:
    return ParsedPredictionResponse(
        target_type=infer_target_type(parsed),
        extracted_value=parsed.extracted_value,
        bear_bull=parsed.bear_bull,
        timeframe=parsed.timeframe,
        notes=parsed.notes,
    )
