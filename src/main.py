from contextlib import asynccontextmanager
from fastapi import FastAPI
from .agent import agent, model_name
from .models import (
    NaturalLanguagePrediction,
    ParsedPredictionResponse,
    PercentageChange,
    Range,
    Ranking,
    TargetPrice,
)
import uvicorn
from .database import init_db, log_token_usage


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/parse_prediction", response_model=ParsedPredictionResponse)
async def parse_prediction(
    input: NaturalLanguagePrediction,
) -> ParsedPredictionResponse:
    input_text = f"Post: '{input.post_text}'\nCreated at: {input.post_created_at}"
    response = await agent.run(input_text)

    parsed = response.output

    # programatically finds the target_type to save some tokens
    # and avoid hallucinations
    target_type = "none"
    if isinstance(parsed.extracted_value, TargetPrice):
        target_type = "target_price"
    elif isinstance(parsed.extracted_value, PercentageChange):
        target_type = "pct_change"
    elif isinstance(parsed.extracted_value, Range):
        target_type = "range"
    elif isinstance(parsed.extracted_value, Ranking):
        target_type = "ranking"

    usage = response.usage()
    log_token_usage(
        model_name=model_name,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
    )

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
