## Bid Price Prediction for Real-Time Bidding (RTB) [ADvantage]

This repository contains all code, data preprocessing scripts and documentation needed to reproduce our LightGBM-based system that predicts optimal bid prices in a real-time advertising exchange, meeting a strict 5 ms inference budget.

### 1. Project Overview

Advertisers compete in RTB auctions by submitting bid prices for each ad impression.
Our goal: **predict a competitive yet cost-efficient bid price from the historical logs of impressions, clicks and conversions**.
Key deliverables:

- Cleaned \& merged dataset (imp, clk, conv logs) with engineered features.
- Trained LightGBM regressor optimized for speed (≤5 ms), memory (≤512 MB) and accuracy (RMSE ≈ 37.8).
- Command-line interface to score new bid requests.


### 2. Folder Structure

```
.
├── data/                 # Raw & processed datasets (not tracked in git-lfs)
├── notebooks/            # Exploratory & feature-engineering notebooks
├── src/
│   ├── preprocessing.py  # Cleaning, merging, feature-engineering pipeline
│   ├── train.py          # Model training & hyper-parameter search
│   ├── infer.py          # Fast inference entry-point (≤5 ms)
│   └── utils.py          # Shared helpers
├── requirements.txt
├── main.py               # CLI wrapper: python3.9 main.py <input.txt> <output.txt>
└── README.md             # You are here
```


### 3. Quick Start

1. Create and activate a Python 3.9 virtual environment
```bash
python3.9 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\Activate.ps1     # Windows PowerShell
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the end-to-end pipeline on the sample dataset
```bash
# Train model (writes model.pkl under models/)
python src/train.py --config configs/default.yaml

# Predict bid prices
python3.9 main.py sample_input.txt sample_output.txt
```

Input format (`sample_input.txt`)

```
BidId PayingPrice
100234	12.5
…
```

Output format (`sample_output.txt`)

```
BidId BidPrice
100234	14.9
…
```


### 4. Data Pipeline

| Step | Description |
| :-- | :-- |
| Merge logs | Combine impression, click and conversion logs on `BidID`. |
| Missing values | <0.1% NaN replaced with column medians. |
| Feature engineering | Scores, composite keys (`CreativeID + AdvertiserID`), CTR, CVR, etc. |
| Encoding | Label-encode categorical IDs; LightGBM handles remaining categories natively. |
| Split | 80% train / 20% test with K-fold CV inside training script. |

### 5. Modeling

- Candidates: XGBoost, Random Forest, LightGBM.
- **Chosen model: LightGBM** for native categorical support, lower memory and 2.2 ms average inference latency.
- Best hyper-parameters (GridSearch):
    - learning_rate = 0.2 -  feature_fraction = 0.9 -  max_depth = 7 -  num_leaves = 20

| Metric | Value |
| :-- | :-- |
| RMSE | 37.82 |
| MAE | 22 |
| Avg inference time | 2.2 ms |
| Memory footprint | 112 MB |

### 6. How to Re-Train with New Data

```bash
python src/preprocessing.py --raw_dir data/raw --out_dir data/processed
python src/train.py --config configs/my_experiment.yaml
```

### 7. Known Limitations \& Future Work

- RMSE still higher than ideal; aim for <15 via additional features (e.g., time-of-day interactions).
- Investigate neural nets to classify click/conversion propensity tiers and adjust bid multipliers.
- Dynamic feature weights for the composite score instead of linear addition.
