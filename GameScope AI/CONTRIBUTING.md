# Contributing Guide

Thanks for contributing to GameScope AI.

## Development setup

1. Install dependencies:
   - `python -m pip install -r requirements.txt`
2. Train/update models:
   - `python train_model.py`
3. Run app:
   - `streamlit run app.py`

## Contribution standards

- Keep changes focused and small when possible.
- Add clear naming and concise comments for non-obvious logic.
- Preserve model reproducibility (`random_state` required in training code).
- Do not commit local artifacts (`artifacts/`) or environment files.

## Validation checklist

- Run app locally and test one prediction scenario.
- Re-train model if training or feature code changed.
- Ensure no linter/syntax issues in edited files.

## Pull request guidance

- Use a descriptive title.
- Explain why the change is needed.
- Include test steps and expected behavior.
