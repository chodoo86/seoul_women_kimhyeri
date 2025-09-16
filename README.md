# IVD Lead Scoring (Portfolio Demo)

A runnable, self-contained demo for **B2B lead scoring + funnel dashboard** in the **IVD (In-Vitro Diagnostics)** space.

## Quickstart (no external DB needed: uses SQLite)
```bash
# 1) Create Python env (recommended) and install deps
pip install -r requirements.txt

# 2) Create SQLite DB and tables
python -c "import sqlite3, os; os.makedirs('build', exist_ok=True); sqlite3.connect('build/ivd.db').close()"
python - <<'PY'
import sqlite3, pathlib
sql = pathlib.Path('sql/ddl.sql').read_text(encoding='utf-8')
con = sqlite3.connect('build/ivd.db')
con.executescript(sql)
con.close()
PY

# 3) Ingest sample CSVs from data/landing into DB
python src/pipelines/ingest.py --db build/ivd.db --landing data/landing

# 4) Transform (create feature views)
python src/pipelines/ingest.py --db build/ivd.db --transform-sql sql/transform.sql

# 5) Retrain (one-time) and then daily scoring
python src/pipelines/score.py --db build/ivd.db --mode retrain
python src/pipelines/score.py --db build/ivd.db --mode score

# 6) (Optional) Export BI tables to CSV for Power BI Desktop
python src/pipelines/score.py --db build/ivd.db --mode export
```

### Power BI
- Connect to `build/ivd.db` via ODBC/SQLite connector and use tables prefixed with **bi_*** (e.g., `bi_scores_daily`, `bi_opportunities`, `bi_orders`).
- A placeholder `powerbi/ivd_funnel.pbix` is included (empty shell); build visuals using the layout described in README and docs/case_study.pdf.

### Automation idea
- **Daily:** run `ingest` → `transform` → `score`.
- **Weekly/conditional:** run `retrain` if drift/performance triggers fire (simple logic included).

---

## Folder
- `sql/ddl.sql`: tables for SQLite; `sql/transform.sql`: feature prep view
- `src/pipelines/ingest.py`: CSV → DB + transform runner
- `src/pipelines/score.py`: retrain/score/export (XGBoost + logistic regression fallback)
- `data/landing/`: dated folders with synthetic CSVs
- `docs/`: case study PDF and a simple architecture diagram

Good luck and have fun!
