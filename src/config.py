from pydantic_ai.models.google import GoogleModelSettings
from pydantic_ai.models.google import GoogleModel
from . import config


db_file = "crypto_predictions.db"
model_name = "gemini-2.5-flash"

agent_settings = GoogleModelSettings(
    temperature=0.3, google_thinking_config={"thinking_budget": 500}
)

batch_agent_settings = GoogleModelSettings(
    temperature=0.3, google_thinking_config={"thinking_budget": 1000}
)

model = GoogleModel(config.model_name)
