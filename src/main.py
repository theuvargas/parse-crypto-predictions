from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4
import uvicorn
from fastapi import FastAPI
from .agent import run_agent, run_batch_agent
from .config import model_name
from .database import init_db, log_usage_event
from .helpers import to_response
from .models import (
    BatchPredictionRequest,
    NaturalLanguagePrediction,
    ParsedPredictionResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/parse_prediction", response_model=ParsedPredictionResponse)
async def parse_prediction(
    input: NaturalLanguagePrediction,
) -> ParsedPredictionResponse:
    batch_id = str(uuid4())
    started = perf_counter()
    try:
        parsed, usage = await run_agent(input)
    except Exception as exc:
        elapsed_ms = (perf_counter() - started) * 1000
        log_usage_event(
            model_name=model_name,
            usage=None,
            batch_id=batch_id,
            batch_size=1,
            latency_ms=elapsed_ms,
            succeeded=False,
        )
        raise exc

    elapsed_ms = (perf_counter() - started) * 1000
    log_usage_event(
        model_name=model_name,
        usage=usage,
        batch_id=batch_id,
        batch_size=1,
        latency_ms=elapsed_ms,
        succeeded=True,
    )
    return to_response(parsed, prediction_id=input.id)


@app.post("/parse_prediction_batch", response_model=list[ParsedPredictionResponse])
async def parse_prediction_batch(
    request: BatchPredictionRequest,
) -> list[ParsedPredictionResponse]:
    if not request.items:
        return []

    batch_size = len(request.items)
    batch_id = str(uuid4())
    started = perf_counter()
    try:
        parsed_list, usage = await run_batch_agent(request.items)
    except Exception as exc:
        elapsed_ms = (perf_counter() - started) * 1000
        log_usage_event(
            model_name=model_name,
            usage=None,
            batch_id=batch_id,
            batch_size=batch_size,
            latency_ms=elapsed_ms,
            succeeded=False,
        )
        raise exc

    elapsed_ms = (perf_counter() - started) * 1000
    log_usage_event(
        model_name=model_name,
        usage=usage,
        batch_id=batch_id,
        batch_size=batch_size,
        latency_ms=elapsed_ms,
        succeeded=True,
    )

    if len(parsed_list) != batch_size:
        raise ValueError(
            "Batch parsing returned a different number of predictions than inputs"
        )

    return [
        to_response(parsed_item, prediction_id=source_item.id)
        for parsed_item, source_item in zip(parsed_list, request.items)
    ]


def main() -> None:
    uvicorn.run("src.main:app", reload=True)


if __name__ == "__main__":
    main()
