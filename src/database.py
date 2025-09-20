import duckdb
from pydantic_ai import RunUsage
from . import config


def init_db() -> None:
    """Initializes the database with the token_usage table."""
    con = duckdb.connect(config.db_file)
    con.execute("CREATE SEQUENCE IF NOT EXISTS token_usage_seq;")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS token_usage (
            id UBIGINT PRIMARY KEY DEFAULT nextval('token_usage_seq'),
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
            model_name VARCHAR,
            input_tokens UINTEGER,
            output_tokens UINTEGER,
            requests UINTEGER,
            cache_read_tokens UINTEGER,
            cache_write_tokens UINTEGER,
            batch_id UUID,
            batch_size UINTEGER,
            latency_ms DOUBLE,
            succeeded BOOLEAN
        );
        """
    )
    con.close()


def log_usage_event(
    model_name: str,
    usage: RunUsage | None,
    batch_id: str,
    batch_size: int,
    latency_ms: float,
    succeeded: bool,
) -> None:
    """Persist usage metrics for a single request/batch."""

    con = duckdb.connect(config.db_file)
    con.execute(
        """
        INSERT INTO token_usage (
            model_name,
            input_tokens,
            output_tokens,
            requests,
            cache_read_tokens,
            cache_write_tokens,
            batch_id,
            batch_size,
            latency_ms,
            succeeded
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            model_name,
            usage.input_tokens if usage else 0,
            usage.output_tokens if usage else 0,
            usage.requests if usage else 0,
            usage.cache_read_tokens if usage else 0,
            usage.cache_write_tokens if usage else 0,
            batch_id,
            batch_size,
            latency_ms,
            succeeded,
        ],
    )
    con.close()
