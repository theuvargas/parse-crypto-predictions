from dotenv import load_dotenv
from pydantic_ai import Agent, RunUsage
from . import config
from .helpers import build_batch_prompt, build_single_prompt
from .models import NaturalLanguagePrediction, ParsedPrediction

load_dotenv()

few_shot = """
Input:
"Post: 'BTC breaking $80,000 before end of year! 🚀',
Created at: 2025-08-25T12:00:00Z"

Output:
{
  "extracted_value": {
    "asset": "BTC",
    "price": 80000,
    "currency": "USD"
  },
  "timeframe": {
    "explicit": true,
    "start": "2025-08-25T12:00:00Z",
    "end": "2025-12-31T23:59:59Z"
  },
  "bear_bull": 78,
  "notes": [
    "End of year converted to December 31st",
    "Assumed USD currency",
    "Quote tweet - prediction attributed to @crypto_bull_2024",
    "Rocket emoji indicates high bullish sentiment"
  ]
}

Input:
"Post: 'RT @sol_predictions: SOL down 40% from here, bear market incoming 📉'
Created at: 2025-08-25T12:00:00Z"

Output:
{
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
Created at: 2025-08-25T12:00:00Z"

Output:
{
  "extracted_value": {
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

Input:
"Post: 'Disagree with this take. PEPE will crack top 10 by market cap this cycle, not crash 🐸💎'
Created at: 2025-08-25T12:00:00Z"

Output:
{
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
    "Frog and diamond emojis indicate strong bullish sentiment",
    "USD market cap ranking context"
  ]
}

Input:
"Post: 'RT @market_news: Crypto market volatility hits new highs this week. This is exactly why I don't make predictions anymore 🤷‍♂️',
Created at: 2025-08-25T12:00:00Z"

Output:
{
  "extracted_value": null,
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
"""

base_instructions = (
    "You are an expert in cryptocurrency and general trading jargon. "
    "Your objective is to extract information from crypto-related "
    "predictions in natural language into parseable JSON data."
    "\n\n"
    "Instructions:"
    "\n\n"
    "- Dates: Any extracted date must be in the UTC ISO 8601 format"
    "- Assumptions: For each of your assumptions and normalization "
    "decisions, make a new single-phrase entry in the 'notes' list"
    "- This is social media content, beware of sarcasm and irony"
    "- When a single post contains multiple classes of predictions "
    "(e.g. a ranking and a target value) choose the boldest prediction "
    "as the class."
)

single_instructions = f"{base_instructions}\n\nExamples:\n\n{few_shot}"

batch_instructions = (
    f"{base_instructions}\n\nExamples:\n\n{few_shot}"
    "\n\nWhen you receive multiple inputs, respond with a JSON array where each element "
    "is a ParsedPrediction object matching the order of the provided posts."
)

agent = Agent(
    config.model,
    output_type=ParsedPrediction,
    instructions=single_instructions,
    model_settings=config.agent_settings,
)

batch_agent = Agent(
    config.model,
    output_type=list[ParsedPrediction],
    instructions=batch_instructions,
    model_settings=config.batch_agent_settings,
)


async def parse_prediction_single(
    item: NaturalLanguagePrediction,
) -> tuple[ParsedPrediction, RunUsage]:
    response = await agent.run(build_single_prompt(item))
    return response.output, response.usage()


async def parse_prediction_batch(
    items: list[NaturalLanguagePrediction],
) -> tuple[list[ParsedPrediction], RunUsage]:
    prompt = build_batch_prompt(items)
    response = await batch_agent.run(prompt)
    return response.output, response.usage()
