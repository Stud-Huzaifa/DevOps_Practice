# GameScope AI

GameScope AI is a web-based machine learning system that predicts game success level, profit potential, and market trend alignment from Steam-like metadata.

## Key capabilities

- Success class prediction (`High`, `Medium`, `Low`)
- Profit potential estimation (USD, model-derived)
- Trend alignment and risk analysis
- Opportunity and recommendation engine
- Advanced game-themed interactive UI for what-if simulation

## Repository standards

- Code style consistency via `.editorconfig`
- Contribution guidance in `CONTRIBUTING.md`
- Version history in `CHANGELOG.md`
- License included (`MIT`)
- Runtime artifacts and local files excluded by `.gitignore`

## Project layout

- `data/steam_top_games_2026.csv`: source dataset
- `src/gamescope_ai/features.py`: preprocessing + feature engineering + target engineering
- `src/gamescope_ai/train.py`: model training, model selection, and evaluation pipeline
- `src/gamescope_ai/predictor.py`: inference + recommendations engine
- `train_model.py`: entrypoint for training
- `GameScope_AI/app.py`: Streamlit web app
- `artifacts/`: generated models and metadata (local; not committed)

## Quickstart

```bash
python -m pip install -r requirements.txt
python train_model.py
streamlit run GameScope_AI/app.py
```

Open: `http://localhost:8501`

## Deploy on Render (recommended)

This repository includes a production Docker setup (`Dockerfile`) for stable deployment.

1. Push latest code to GitHub.
2. In Render, create a new **Web Service** from your GitHub repo.
3. Configure:
   - Environment: `Docker`
   - Root directory: `GameScope AI`
   - Plan: `Free` (or higher)
4. Deploy. Render will run:
   - `streamlit run GameScope_AI/app.py --server.address=0.0.0.0 --server.port=$PORT`

Notes:
- Model artifacts are auto-generated on first run if missing.
- First boot may take longer due to package install + model training.

## Modeling approach

- **Feature engineering**:
  - Game age
  - Review ratio
  - Estimated revenue
  - Genre / tag / category counts
  - Platform coverage
  - Log-transformed engagement signals
- **Success score**:
  - Weighted score from owners, review ratio, engagement, CCU, estimated revenue
  - Converted to success classes by quantile bins
- **Model selection**:
  - Candidate classifiers: Random Forest, Extra Trees
  - Candidate regressors: Random Forest, Extra Trees
  - Auto-select best classifier by balanced accuracy
  - Auto-select best regressor by R2
- **Text encoding**:
  - TF-IDF on genres, tags, categories, short description

## Operational notes

- Profit is estimated from data-driven patterns and should be treated as directional guidance, not guaranteed outcome.
- To improve accuracy further, add stronger external features (wishlist count, follower growth, regional pricing, release window competition).
