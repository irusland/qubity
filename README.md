# Candle Data Processing Benchmark

This project benchmarks two different candle data processors: a **Lazy Native Python Processor** and a **Pandas DataFrame Processor**. The goal is to compare their performance in aggregating large datasets of trading data into candlestick data structures.

## Table of Contents

- [Overview](#overview)
- [Data loading](#data-loading)
- [Experiment Instructions](#experiment-instructions)
- [Results](#results)
- [Processors](#processors)
  - [LazyCandleProcessor](#lazycandleprocessor)
  - [PandasCandleProcessor](#pandascandleprocessor)
- [Loaders](#loaders)
  - [Clients](#clients)
  - [Models](#models)
- [Author](#author)

## Overview

In financial data analysis, candlestick data is crucial for visualizing price movements over time. Aggregating raw trade data into candlesticks can be computationally intensive, especially with large datasets. This project compares two approaches to processing this data:

1. **Lazy Native Python Processor**: Utilizes Python's built-in data structures and generators for on-the-fly computation without loading all data into memory.
2. **Pandas DataFrame Processor**: Uses Pandas for data manipulation and aggregation, leveraging vectorized operations for performance.


## Data loading

Run [`data_loaders/models/timedata.py`](data_processors/lazy.py) to get [`processed_data/result_lazy.csv`](processed_data/result_lazy.csv)
that looks like this:

```
timestamp,open_spot,open_perp,high_spot,high_perp,low_spot,low_perp,close_spot,close_perp,volume_total,volume_spot,volume_perp,buy_volume_total,buy_volume_spot,buy_volume_perp,sell_volume_total,sell_volume_spot,sell_volume_perp,trades_total,trades_spot,trades_perp,buy_trades_total,buy_trades_spot,buy_trades_perp,sell_trades_total,sell_trades_spot,sell_trades_perp,open_interest,funding_rate
2024-09-12 07:00:00+00:00,57948.0,57920.1,58054.0,58025.9,57938.17,57909.2,58038.0,58015.2,797.3490799999998,127.29607999999999,670.0529999999999,493.23056,89.96755999999999,403.26300000000003,304.11852,37.32852,266.78999999999996,7075,3615,3460,4113,2031,2082,2962,1584,1378,87691.653,
2024-09-12 07:05:00+00:00,58038.0,58015.2,58061.1,58046.7,57876.0,57842.0,57915.31,57882.6,654.47375,30.87775,623.596,296.66839,8.98939,287.679,357.80536,21.88836,335.91700000000003,6095,2494,3601,2381,893,1488,3714,1601,2113,87775.688,
2024-09-12 07:10:00+00:00,57915.31,57882.6,57980.0,57955.1,57901.99,57872.0,57951.21,57916.1,235.23425000000003,15.16525,220.06900000000002,146.17958000000002,9.970580000000002,136.209,89.05466999999999,5.1946699999999995,83.85999999999999,4518,2332,2186,2625,1376,1249,1893,956,937,87808.426,
...
```


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


## Author

This project was developed by Ruslan Sirazhetdinov ([@irusland](https://github.com/irusland)).

---
