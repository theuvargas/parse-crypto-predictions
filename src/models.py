from typing import Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from pydantic_extra_types.currency_code import ISO4217


class BasePrediction(BaseModel):
    """The base class for all prediction types"""

    asset: str = Field(description="The crypto's ticker e.g. BTC, ETH")
    currency: ISO4217 = Field(
        description="The fiat's ticker used to make the prediction e.g. USD, EUR"
    )


class TargetPrice(BasePrediction):
    """The price prediction for an asset in a given currency"""

    price: float = Field(description="An explicit prediction value")


class PercentageChange(BasePrediction):
    """The percentage change prediction for an asset in a given currency"""

    percentage: float = Field(
        description="A relative prediction value, e.g., for a 10.5% increase, use 10.5, for a 5% decrease, use -5.0"
    )


class Range(BasePrediction):
    """The range prediction for an asset in a given currency"""

    min: float = Field(ge=0, description="The lower bound of the predicted price range")
    max: float = Field(ge=0, description="The upper bound of the predicted price range")


class Ranking(BasePrediction):
    """The ranking prediction for an asset"""

    ranking: int


class Timeframe(BaseModel):
    """The timeframe where the prediction is valid"""

    explicit: bool = Field(
        description="Wether the post defines an explicit timeframe for the prediction or not"
    )
    start: datetime | None = Field(
        None, description="The start timestamp of the prediciton"
    )
    end: datetime | None = Field(
        None, description="The end timestamp of the prediction"
    )

    @field_validator("start", "end")
    @classmethod
    def validate_datetimes_are_utc(cls, v: datetime | None):
        if v is None:
            return v

        offset = v.utcoffset()
        if offset is None:
            raise ValueError("datetime must be timezone-aware")

        if offset.total_seconds() != 0:
            raise ValueError("datetime must be in UTC")

        return v


class ParsedPrediction(BaseModel):
    """A prediction related to the value of a cryptocurrency"""

    extracted_value: TargetPrice | PercentageChange | Range | Ranking | None = Field(
        description="The prediction extracted values or None"
    )
    bear_bull: int = Field(
        ge=-100,
        le=100,
        description="An assesment of the post sentiment, ranging from -100 (very bearish) to 100 (very bullish)",
    )
    timeframe: Timeframe = Field(
        description="The timeframe where the prediction is valid"
    )
    notes: list[str] = Field(description="Reasoning for parsing decisions")


TargetType = Literal["target_price", "pct_change", "range", "ranking", "none"]
ExtractedValueType = TargetPrice | PercentageChange | Range | Ranking | None


class ParsedPredictionResponse(BaseModel):
    """Response returned by the FastAPI endpoint"""

    id: str | None = Field(
        default=None, description="Unique identifier for the source prediction"
    )
    target_type: TargetType
    extracted_value: ExtractedValueType
    bear_bull: int
    timeframe: Timeframe
    notes: list[str]


examples = {
    "items": [
        {
            "post_text": "SOL will double once mainnet upgrade ships",
            "post_created_at": "2025-02-14T08:15:00Z",
        },
        {
            "post_text": "ETH stuck between $2.8k-$3.2k for the next month",
            "post_created_at": "2025-02-14T09:45:00Z",
        },
        {
            "post_text": "Expect XRP to slide 15% this quarter",
            "post_created_at": "2025-02-14T10:05:00Z",
        },
        {
            "post_text": "BTC will reach $80k before year end 🚀",
            "post_created_at": "2025-01-05T12:00:00Z",
        },
    ]
}


class NaturalLanguagePrediction(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [examples["items"][0]]})
    id: str | None = Field(
        default=None, description="Unique identifier for the prediction"
    )
    post_text: str = Field(description="The text of the post")
    post_created_at: datetime = Field(description="Creation date of the post")


class BatchPredictionRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [examples]})
    items: list[NaturalLanguagePrediction] = Field(
        default_factory=list,
        description="Collection of posts to parse in a single request",
    )
