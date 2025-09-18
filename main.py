from fastapi import FastAPI

app = FastAPI()


@app.post("/parse_prediction")
def parse_prediction(input):
    pass
