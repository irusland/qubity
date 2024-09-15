# Candle Data Processing Benchmark

This project benchmarks two different candle data processors: a **Lazy Native Python Processor** and a **Pandas DataFrame Processor**. The goal is to compare their performance in aggregating large datasets of trading data into candlestick data structures.

## Table of Contents

- [Overview](#overview)
- [Processors](#processors)
  - [LazyCandleProcessor](#lazycandleprocessor)
  - [PandasCandleProcessor](#pandascandleprocessor)
- [Loaders](#loaders)
  - [Clients](#clients)
  - [Models](#models)
- [Experiment Instructions](#experiment-instructions)
- [Results](#results)
- [Author](#author)

## Overview

In financial data analysis, candlestick data is crucial for visualizing price movements over time. Aggregating raw trade data into candlesticks can be computationally intensive, especially with large datasets. This project compares two approaches to processing this data:

1. **Lazy Native Python Processor**: Utilizes Python's built-in data structures and generators for on-the-fly computation without loading all data into memory.
2. **Pandas DataFrame Processor**: Uses Pandas for data manipulation and aggregation, leveraging vectorized operations for performance.

## Processors

### LazyCandleProcessor

The `LazyCandleProcessor` processes data using native Python constructs. It iterates over the data lazily, computing aggregates as needed without loading the entire dataset into memory.

- **Advantages**:
  - Minimal memory usage.
  - Excellent performance with large datasets.
- **Internals**:
  - Located at [`data_processors/lazy.py`](data_processors/lazy.py).

### PandasCandleProcessor

The `PandasCandleProcessor` leverages Pandas DataFrames for data manipulation. It converts data into DataFrames and uses resampling and aggregation functions to compute candlestick data.

- **Advantages**:
  - Concise and expressive code.
  - Utilizes Pandas' optimized routines.
- **Internals**:
  - Located at [`data_processors/pandas_dataframe.py`](data_processors/pandas_dataframe.py).

## Loaders

Data is loaded from various sources representing different market data aspects.

### Clients

The clients are responsible for fetching data from various APIs or data sources.

- **Internals**:
  - Located at [`data_loaders/clients.py`](data_loaders/clients.py).

### Models

The models define the data structures used throughout the project.

- **Trade Model**:
  - Located at [`data_loaders/models/trade.py`](data_loaders/models/trade.py).
- **Open Interest Model**:
  - Located at [`data_loaders/models/open_interest.py`](data_loaders/models/open_interest.py).
- **Funding Rate Model**:
  - Located at [`data_loaders/models/funding_rate.py`](data_loaders/models/funding_rate.py).
- **Time Data Model**:
  - Located at [`data_loaders/models/timedata.py`](data_loaders/models/timedata.py).

## Experiment Instructions

To run the benchmark experiment comparing the two processors, follow these steps:


3. **Run the Experiment**:

   Using Docker Compose:

   ```bash
   docker-compose up
   ```

   Or, if you prefer to run without Docker:

   Install Dependencies

   This project uses [Poetry](https://python-poetry.org/) for dependency management.

   ```bash
   poetry install
   ```

   ```bash
   poetry run python experiment.py
   ```

   The `experiment.py` script orchestrates the benchmarking process.


## Results

After running the experiment, you should see output similar to the following:

```
Processing SpotClient: 100%|█████████▉| 3599002/3600000 [00:00<00:00, 29031449.26s/s]
Processing PerpClient: 100%|█████████▉| 3599975/3600000 [00:00<00:00, 29274069.77s/s]
Processing OpenInterestClient: 100%|██████████| 3600000/3600000 [00:00<00:00, 20798201652.89s/s]
Processing FundingRateClient: 100%|██████████| 3600000/3600000 [00:00<00:00, 48087561783.44s/s]
PandasCandleProcessor: mean 0:00:00.594170 (from 4 experiments [0:00:00.589267, 0:00:00.597463, 0:00:00.585400, 0:00:00.604549])
LazyCandleProcessor: mean 0:00:00.000005 (from 4 experiments [0:00:00.000004, 0:00:00.000004, 0:00:00.000005, 0:00:00.000007])
Best processor: LazyCandleProcessor with mean 0:00:00.000005 increase in performance x118834.00
```

### Interpretation

- **PandasCandleProcessor** took approximately 0.594 seconds on average.
- **LazyCandleProcessor** took approximately 0.000005 seconds on average.
- The **LazyCandleProcessor** was significantly faster, with an increase in performance of approximately **118,834 times** compared to the Pandas processor.

## Author

This project was developed by Ruslan Sirazhetdinov ([@irusland](https://github.com/irusland)).

---
