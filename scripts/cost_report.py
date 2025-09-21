from dataclasses import dataclass

import duckdb

from src import config


INPUT_RATE = 0.3 / 1_000_000
OUTPUT_RATE = 2.5 / 1_000_000

QUERY = f"""
SELECT
    model_name,
    batch_size,
    COUNT(*) AS request_count,
    AVG(CAST(succeeded AS DOUBLE)) AS success_rate,
    AVG(latency_ms) / 1000.0 AS latency_mean,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY latency_ms) / 1000.0 AS latency_p50,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) / 1000.0 AS latency_p95,
    AVG(input_tokens) AS input_tokens_mean,
    AVG(input_tokens * {INPUT_RATE}) AS input_cost_mean,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY input_tokens * {INPUT_RATE}) AS input_cost_p50,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY input_tokens * {INPUT_RATE}) AS input_cost_p95,
    AVG(output_tokens) AS output_tokens_mean,
    AVG(output_tokens * {OUTPUT_RATE}) AS output_cost_mean,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY output_tokens * {OUTPUT_RATE}) AS output_cost_p50,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY output_tokens * {OUTPUT_RATE}) AS output_cost_p95
FROM token_usage
GROUP BY 1, 2
ORDER BY 1, 2
"""


@dataclass
class ReportRow:
    model_name: str | None
    batch_size: int | None
    request_count: int
    success_rate: float | None
    latency_mean: float | None
    latency_p50: float | None
    latency_p95: float | None
    input_tokens_mean: float | None
    input_cost_mean: float | None
    input_cost_p50: float | None
    input_cost_p95: float | None
    output_tokens_mean: float | None
    output_cost_mean: float | None
    output_cost_p50: float | None
    output_cost_p95: float | None


def fetch_rows() -> list[ReportRow]:
    connection = duckdb.connect(config.db_file, read_only=True)
    try:
        result = connection.execute(QUERY)
        rows = result.fetchall()
    finally:
        connection.close()

    return [ReportRow(*row) for row in rows]


def format_number(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def format_percentage(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.1f}%"


def print_report(rows: list[ReportRow]) -> None:
    headers = [
        "model",
        "batch",
        "requests",
        "success",
        "lat_mean_s",
        "lat_p50_s",
        "lat_p95_s",
        "in_tokens",
        "in_cost_mean",
        "in_cost_p50",
        "in_cost_p95",
        "out_tokens",
        "out_cost_mean",
        "out_cost_p50",
        "out_cost_p95",
    ]

    table: list[list[str]] = []
    for row in rows:
        table.append(
            [
                row.model_name or "-",
                str(row.batch_size) if row.batch_size is not None else "-",
                str(row.request_count),
                format_percentage(row.success_rate),
                format_number(row.latency_mean),
                format_number(row.latency_p50),
                format_number(row.latency_p95),
                format_number(row.input_tokens_mean, digits=1),
                format_number(row.input_cost_mean, digits=4),
                format_number(row.input_cost_p50, digits=4),
                format_number(row.input_cost_p95, digits=4),
                format_number(row.output_tokens_mean, digits=1),
                format_number(row.output_cost_mean, digits=4),
                format_number(row.output_cost_p50, digits=4),
                format_number(row.output_cost_p95, digits=4),
            ]
        )

    widths = [len(header) for header in headers]
    for row in table:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    def format_row(cells: list[str]) -> str:
        return "  ".join(cell.rjust(widths[idx]) for idx, cell in enumerate(cells))

    print(format_row(headers))
    print(format_row(["-" * w for w in widths]))
    for row in table:
        print(format_row(row))


def main() -> None:
    rows = fetch_rows()
    print_report(rows)


if __name__ == "__main__":
    main()
