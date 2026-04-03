# EvidenceAtlas

EvidenceAtlas builds a review-level network of shared primary studies across 501 Cochrane reviews. It merges overlap structure with quality, fragility, audit, and oracle-risk annotations, then exports the network used by the dashboard and manuscript.

## Inputs

- `C:\Users\user\OneDrive - NHS\Documents\Pairwise70\data`
- `C:\OverlapDetector\data\output\overlap_pairs.csv`
- `C:\MetaAudit\results\dashboard_data.json`
- `C:\FragilityAtlas\data\output\fragility_atlas_results.csv`
- `C:\EvidenceQuality\data\reviews_compact.json`
- Optional: `C:\Models\EvidenceOracle\results\predictions.csv`

## Repository Layout

- `assemble_network.py`: network assembly pipeline
- `data/network.json`: exported network data
- `dashboard.html`: interactive D3 dashboard artifact
- `paper/manuscript.md`: manuscript draft
- `tests/test_atlas.py`: test suite

## Run

```powershell
python assemble_network.py
python assemble_network.py --max-reviews 100 --min-overlap 1
```

## Validate

```powershell
python -m pytest -q
```

## Current Outputs

- `data/network.json` is the canonical export used by the dashboard and tests
- `dashboard.html` is the browser-facing artifact for interactive network inspection

## Notes

- Oracle predictions are optional. If `C:\Models\EvidenceOracle\results\predictions.csv` is missing, `oracle_risk` is left null.
- `results/` is currently unused by the assembler; the network export lives under `data/`.
