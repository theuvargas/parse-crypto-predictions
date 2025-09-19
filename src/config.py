from pydantic_ai import ModelSettings


db_file = "crypto_predictions.db"
provider = "google-gla"
model_name = "gemini-2.5-flash"
model_settings = ModelSettings(temperature=0.3)
