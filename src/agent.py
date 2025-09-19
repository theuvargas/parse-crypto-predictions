from pydantic_ai import Agent
from dotenv import load_dotenv
from .models import ParsedPrediction

load_dotenv()

few_shot = """
"Post: 'Disagree with this take. PEPE will crack top 10 by market cap this cycle, not crash 🐸💎'
Created at: 2025-08-25T12:00:00Z"

Output:
{
  "target_type": "none",
  "timeframe": {
    "explicit": false,
    "start": null,
    "end": null
  },
  "bear_bull": -20,
  "notes": [
    "No measurable prediction made",
    "Retweet with additional commentary by @former_crypto_bull",
    "General market volatility observation only",
    "Slight negative sentiment due to uncertainty and anti-prediction stance",
    "Shrugging emoji indicates resignation/uncertainty"
  ]
}

"Post: 'RT @sol_predictions: SOL down 40% from here, bear market incoming 📉'
Created at: 2025-08-25T12:00:00Z"

Output:
{
  "target_type": "pct_change",
  "extracted_value": {
    "asset": "SOL",
    "percentage": -40,
    "currency": "USD"
  },
  "timeframe": {
    "explicit": false,
    "start": null,
    "end": null
  },
  "bear_bull": -75,
  "notes": [
    "No specific timeframe mentioned",
    "Retweet - original prediction by @sol_predictions",
    "Bear market language indicates strong negative sentiment",
    "Assumed USD currency"
  ]
}
"""

instructions = (
    "You are an expert in cryptocurrency and general trading jargon. "
    "Your objective is to extract information from crypto-related "
    "predictions in natural language into parseable JSON data.\n\n"
    "Instructions:\n\n"
    "- Dates: Any extracted date must be in the UTC ISO4601 format"
    "- Assumptions: For each of your assumptions and normalization "
    "decisions, should make a new single-phrase entry in the 'notes' "
    "list.\n\n"
    f"Examples:\n\n{few_shot}"
)

agent = Agent(
    "google-gla:gemini-2.5-flash",
    output_type=ParsedPrediction,
    instructions=instructions,
    model_settings={"temperature": 0.3},
)
