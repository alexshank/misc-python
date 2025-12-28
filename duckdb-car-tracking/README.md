# DuckDB Car Tracking

Vehicle fuel and mileage data analysis with DuckDB.

## Install

```bash
uv venv
source .venv/bin/activate
uv sync

# or, one-liner
uv venv && source .venv/bin/activate && uv sync
```

## Run

> Uses `vehicle-log-sample.csv` synthetic data.

```bash
python3 main.py

# or, write to file
python3 main.py > output.txt
```

