from fastapi import FastAPI
from .agent import agent
from .models import (
    NaturalLanguagePrediction,
    ParsedPredictionResponse,
    PercentageChange,
    Range,
    Ranking,
    TargetPrice,
)
import uvicorn

app = FastAPI()


@app.post("/parse_prediction", response_model=ParsedPredictionResponse)
async def parse_prediction(
    input: NaturalLanguagePrediction,
) -> ParsedPredictionResponse:
    input_text = f"Tweet: '{input.post_text}'\nCreated at: {input.post_created_at}"
    response = await agent.run(input_text)

    print(response)

    parsed = response.output

    target_type = "none"
    if isinstance(parsed.extracted_value, TargetPrice):
        target_type = "target_price"
    elif isinstance(parsed.extracted_value, PercentageChange):
        target_type = "pct_change"
    elif isinstance(parsed.extracted_value, Range):
        target_type = "range"
    elif isinstance(parsed.extracted_value, Ranking):
        target_type = "ranking"

    return ParsedPredictionResponse(
        target_type=target_type,
        extracted_value=parsed.extracted_value,
        bear_bull=parsed.bear_bull,
        timeframe=parsed.timeframe,
        notes=parsed.notes,
    )


def main():
    uvicorn.run("src.main:app", reload=True)


if __name__ == "__main__":
    main()
