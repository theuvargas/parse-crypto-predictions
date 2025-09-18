from datetime import datetime
from fastapi import FastAPI
from .models import NaturalLanguagePrediction, ParsedPrediction, Timeframe
import uvicorn

app = FastAPI()


@app.post("/parse_prediction", response_model=ParsedPrediction)
async def parse_prediction(input: NaturalLanguagePrediction) -> ParsedPrediction:
    return ParsedPrediction(
        target_type="none",
        bear_bull=0,
        timeframe=Timeframe(explicit=False, start=datetime.now(), end=datetime.now()),
        notes=[],
    )


def main():
    uvicorn.run(app)


if __name__ == "__main__":
    main()
