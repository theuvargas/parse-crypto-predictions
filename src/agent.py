from pydantic_ai import Agent
from dotenv import load_dotenv
from .models import ParsedPrediction

load_dotenv()

instructions = (
    "Your objective is to extract information from crypto-related "
    "predictions in natural language into parseable JSON data.\n\n"
    "Instructions:\n\n"
    "- Dates: Any extracted date must be in the UTC ISO4601 format"
    "- Assumptions: For each of your assumptions and nomalization "
    "decisions, should make a new single-phrase entry in the 'notes'"
    "list.\n\n"
)

agent = Agent(
    "google-gla:gemini-2.5-flash-lite",
    output_type=ParsedPrediction,
    instructions=instructions,
)
