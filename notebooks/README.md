# Notebooks

Exploratory analysis, risk-scoring validation, and model prototyping.

Conventions:

- Name notebooks `NN-topic.ipynb` (e.g. `01-eda-risk-scoring.ipynb`).
- Notebooks read from `data/` and write to `models/`; they don't write
  anything else the rest of the project depends on — scoring logic itself
  lives in `backend/app/risk/`, not inline in a notebook.
- Unlike a typical scratch-notebook convention, **outputs are committed** for
  this project: it's a portfolio piece, and GitHub renders the charts
  (radar plots, risk breakdowns, SHAP plots) inline without anyone needing to
  run the notebook. Re-run and re-save before committing if the underlying
  data or logic changes, so committed outputs stay accurate.

Run against the backend environment:

```bash
cd backend
uv run jupyter lab
```

Or re-execute headlessly (used to verify the notebook after edits):

```bash
cd backend
uv run jupyter nbconvert --to notebook --execute --inplace ../notebooks/01-eda-risk-scoring.ipynb
```
