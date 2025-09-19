from pydantic_ai import Agent
from dotenv import load_dotenv
from .models import ParsedPrediction

load_dotenv()

few_shot = """
Input:
"Post: 'Disagree with this take. PEPE will crack top 10 by market cap this cycle, not crash 🐸💎'
Created at: 2025-08-25T12:00:00Z"

Output:
{
  "target_type": "ranking",
  "extracted_value": {
    "asset": "PEPE",
    "ranking": 10,
    "currency": "USD"
  },
  "timeframe": {
    "explicit": false,
    "start": null,
    "end": null
  },
  "bear_bull": 65,
  "notes": [
    "Market cap ranking assumed",
    "This cycle is vague timeframe",
    "Quote tweet disagreeing with @bearish_analyst's bearish prediction",
    "Frog and diamond emojis indicate strong bullish sentiment",
    "USD market cap ranking context"
  ]
}

Input:
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

Input:
"Post: 'ETH consolidating between $3,200-$3,800 next month. Chart analysis attached 📊',
post_created_at": "2025-08-25T12:00:00Z"

Output:
{
  "target_type": "range",
  "extracted_range": {
    "asset": "ETH",
    "min": 3200,
    "max": 3800,
    "currency": "USD"
  },
  "timeframe": {
    "explicit": true,
    "start": "2025-08-25T12:00:00Z",
    "end": "2025-09-25T23:59:59Z"
  },
  "bear_bull": 15,
  "notes": [
    "Next month calculated from post date",
    "Chart analysis image attached - technical analysis basis",
    "Consolidation suggests neutral-to-slightly-bullish sentiment",
    "Assumed USD currency"
  ]
}
"""

instructions = (
    "You are an expert in cryptocurrency and general trading jargon. "
    "Your objective is to extract information from crypto-related "
    "predictions in natural language into parseable JSON data."
    "\n\n"
    "Instructions:"
    "\n\n"
    "- Dates: Any extracted date must be in the UTC ISO4601 format"
    "- Assumptions: For each of your assumptions and normalization "
    "decisions, make a new single-phrase entry in the 'notes' list"
    "- If the user doesn't specify the start of the timeframe, consider "
    "the post creation date as the start"
    "\n\n"
    f"Examples:\n\n{few_shot}"
)

agent = Agent(
    "google-gla:gemini-2.5-flash",
    output_type=ParsedPrediction,
    instructions=instructions,
    model_settings={"temperature": 0.3},
)
