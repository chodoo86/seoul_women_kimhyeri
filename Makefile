
.PHONY: db ingest transform retrain score export

db:
	@mkdir -p build
	@python -c "import sqlite3, os; os.makedirs('build', exist_ok=True); sqlite3.connect('build/ivd.db').close()"
	@python - <<'PY'\
import sqlite3, pathlib; \
sql = pathlib.Path('sql/ddl.sql').read_text(encoding='utf-8'); \
con = sqlite3.connect('build/ivd.db'); \
con.executescript(sql); \
con.close(); \
PY

ingest:
	@python src/pipelines/ingest.py --db build/ivd.db --landing data/landing

transform:
	@python src/pipelines/ingest.py --db build/ivd.db --transform-sql sql/transform.sql

retrain:
	@python src/pipelines/score.py --db build/ivd.db --mode retrain

score:
	@python src/pipelines/score.py --db build/ivd.db --mode score

export:
	@python src/pipelines/score.py --db build/ivd.db --mode export
