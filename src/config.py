from pydantic_ai.models.google import GoogleModelSettings
from pydantic_ai.models.google import GoogleModel
from . import config
from dotenv import load_dotenv

load_dotenv()

db_file = "crypto_predictions.db"
dataset_file = "data/annotated-dataset.json"
model_name = "gemini-2.5-flash"

agent_settings = GoogleModelSettings(
    temperature=0.3, google_thinking_config={"thinking_budget": 500}
)

batch_agent_settings = GoogleModelSettings(
    temperature=0.3, google_thinking_config={"thinking_budget": 4000}
)

model = GoogleModel(config.model_name)
