#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, glob, hashlib, sqlite3, csv, sys, pathlib, datetime

def sha256sum(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def ensure_ingest_log(con):
    con.execute("""CREATE TABLE IF NOT EXISTS ingest_log(
        file_path TEXT PRIMARY KEY,
        table_name TEXT,
        row_count INTEGER,
        sha256 TEXT,
        loaded_at TEXT
    )""")

def load_csv(con, table_name, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        cols = ",".join([f'"{c}"' for c in header])
        placeholders = ",".join(["?"]*len(header))
        con.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({", ".join([c+" TEXT" for c in header])})')
        rows = [row for row in reader]
        if rows:
            # 테이블별로 다른 중복 처리 전략 사용
            if table_name in ['accounts', 'products']:
                # 마스터 테이블: INSERT OR REPLACE 사용
                try:
                    con.executemany(f'INSERT OR REPLACE INTO {table_name} ({cols}) VALUES ({placeholders})', rows)
                except sqlite3.IntegrityError as e:
                    print(f"경고: {table_name} 테이블에 중복 데이터가 있습니다. 기존 데이터를 업데이트합니다.")
                    con.execute(f'DELETE FROM {table_name}')
                    con.executemany(f'INSERT INTO {table_name} ({cols}) VALUES ({placeholders})', rows)
            else:
                # 트랜잭션 테이블: 기존 데이터 삭제 후 새로 삽입
                print(f"  {table_name} 테이블 데이터를 새로 로드합니다...")
                con.execute(f'DELETE FROM {table_name}')
                con.executemany(f'INSERT INTO {table_name} ({cols}) VALUES ({placeholders})', rows)
        return len(rows)

def run_transform(con, sql_path):
    sql = pathlib.Path(sql_path).read_text(encoding='utf-8')
    con.executescript(sql)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="SQLite DB path")
    ap.add_argument("--landing", help="landing folder path with dated CSVs")
    ap.add_argument("--transform-sql", help="Run transform.sql to build views")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    ensure_ingest_log(con)

    if args.landing:
        for day_dir in sorted(glob.glob(os.path.join(args.landing, "*"))):
            for fp in glob.glob(os.path.join(day_dir, "*.csv")):
                table_prefix = os.path.basename(fp).split("_")[0]
                table_map = {
                    "accounts": "accounts",
                    "products": "products",
                    "install": "install_base",
                    "opportunities": "opportunities",
                    "orders": "orders",
                    "interactions": "interactions",
                    "bids": "bids",
                    "service": "service_tickets",
                    "web": "web_events"
                }
                # crude mapping based on prefix
                tname = None
                for k,v in table_map.items():
                    if os.path.basename(fp).startswith(k):
                        tname = v
                        break
                if not tname:
                    continue
                sha = sha256sum(fp)
                row = con.execute("SELECT 1 FROM ingest_log WHERE file_path=? AND sha256=?", (fp,sha)).fetchone()
                if row:
                    continue
                print("Loading", fp, "→", tname)
                n = load_csv(con, tname, fp)
                con.execute("INSERT INTO ingest_log(file_path, table_name, row_count, sha256, loaded_at) VALUES (?,?,?,?,?)",
                            (fp, tname, n, sha, datetime.datetime.now(datetime.timezone.utc).isoformat()))
                con.commit()

    if args.transform_sql:
        print("Running transform:", args.transform_sql)
        run_transform(con, args.transform_sql)

    con.close()

if __name__ == "__main__":
    main()
