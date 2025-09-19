import duckdb
from . import config


def init_db():
    """Initializes the database and creates the token_usage table if it doesn't exist."""
    con = duckdb.connect(config.db_file)
    con.execute("CREATE SEQUENCE IF NOT EXISTS token_usage_seq;")
    con.execute("""
        CREATE TABLE IF NOT EXISTS token_usage (
            id UBIGINT PRIMARY KEY DEFAULT nextval('token_usage_seq'),
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
            model_name VARCHAR,
            input_tokens UINTEGER,
            output_tokens UINTEGER
        );
    """)
    con.close()
    print("Database initialized successfully.")


def log_token_usage(model_name: str, input_tokens: int, output_tokens: int):
    """Logs a new token usage record to the database."""
    con = duckdb.connect(config.db_file)
    con.execute(
        "INSERT INTO token_usage (model_name, input_tokens, output_tokens) VALUES (?, ?, ?)",
        [model_name, input_tokens, output_tokens],
    )
    con.close()
