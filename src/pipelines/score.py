#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, sqlite3, os, sys, datetime
import pandas as pd
import numpy as np

# Try to import ML; fall back to simple rule-based if missing
ML_AVAILABLE = True
try:
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression, LinearRegression
    from sklearn.metrics import roc_auc_score
    import joblib
except Exception as e:
    ML_AVAILABLE = False

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_DIR = os.path.abspath(MODEL_DIR)
os.makedirs(MODEL_DIR, exist_ok=True)

def fetch_features(con):
    # read feature_view
    df = pd.read_sql_query("SELECT * FROM feature_view", con, parse_dates=['t0_date'])
    # For labels, build a synthetic y_close_90d and y_amount_180d using heuristics on orders/opps
    # Note: for demo, we'll use orders within 90/180 days relative to now (approximation).
    t0 = pd.Timestamp(datetime.datetime.utcnow().date())
    orders = pd.read_sql_query("SELECT account_id, order_date, total_amount FROM orders", con, parse_dates=['order_date'])
    if not orders.empty:
        orders['days_ago'] = (t0 - orders['order_date']).dt.days
        agg90 = orders[orders['days_ago']<=90].groupby('account_id')['total_amount'].sum().rename('amt90')
        agg180 = orders[orders['days_ago']<=180].groupby('account_id')['total_amount'].sum().rename('amt180')
    else:
        agg90 = pd.Series(dtype=float); agg180 = pd.Series(dtype=float)
    df = df.merge(agg90, left_on='account_id', right_index=True, how='left')
    df = df.merge(agg180, left_on='account_id', right_index=True, how='left')
    df['amt90'] = df['amt90'].fillna(0.0); df['amt180'] = df['amt180'].fillna(0.0)
    df['y_close_90d'] = (df['amt90'] > 0).astype(int)
    df['y_amount_180d'] = df['amt180']
    return df

def train_models(df):
    if not ML_AVAILABLE:
        print("ML libraries not available; skipping train.")
        return None, None

    y_cls = df['y_close_90d'].astype(int)
    y_reg = df['y_amount_180d'].astype(float)
    X = df.drop(columns=['y_close_90d','y_amount_180d','t0_date','account_id','amt90','amt180'])

    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in X.columns if c not in num_cols]

    pre = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), num_cols),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("ohe", OneHotEncoder(handle_unknown="ignore"))]), cat_cols)
    ])

    clf = Pipeline([("prep", pre), ("clf", LogisticRegression(max_iter=1000))])
    reg = Pipeline([("prep", pre), ("reg", LinearRegression())])

    Xtr, Xte, ytr, yte = train_test_split(X, y_cls, test_size=0.25, stratify=y_cls, random_state=42)
    clf.fit(Xtr, ytr)
    proba = clf.predict_proba(Xte)[:,1]
    try:
        auc = roc_auc_score(yte, proba)
    except Exception:
        auc = float('nan')
    print(f"[Retrain] Validation AUC: {auc:.3f}")

    # Regressor
    reg.fit(X, y_reg)

    import joblib
    joblib.dump(clf, os.path.join(MODEL_DIR, "lead_model.joblib"))
    joblib.dump(reg, os.path.join(MODEL_DIR, "amount_model.joblib"))
    print("Saved models to", MODEL_DIR)

def score_today(con, export=False):
    # Load or fallback
    model_path = os.path.join(MODEL_DIR, "lead_model.joblib")
    amount_path = os.path.join(MODEL_DIR, "amount_model.joblib")
    have_models = os.path.exists(model_path) and os.path.exists(amount_path)
    df = fetch_features(con)
    X = df.drop(columns=['y_close_90d','y_amount_180d','t0_date','account_id','amt90','amt180'])

    if ML_AVAILABLE and have_models:
        import joblib
        clf = joblib.load(model_path)
        reg = joblib.load(amount_path)
        p = clf.predict_proba(X)[:,1]
        amt = reg.predict(X)
    else:
        # Simple heuristic fallback
        p = (0.05 + 0.4*(df['interactions_90d']>3).astype(float) + 0.3*(df['orders_cnt_180d']>0).astype(float)).clip(0,1).values
        amt = (df['monetary_180d']*0.6 + (df['install_equipment_count_active']*2000)).values

    margin = 8000.0
    contact_cost = 120.0
    ev = p*margin - contact_cost
    is_priority = (p >= 0.5).astype(int)

    out = pd.DataFrame({
        "run_date": [datetime.date.today().isoformat()]*len(df),
        "account_id": df['account_id'].values,
        "t0_date": df['t0_date'].dt.date.astype(str).values,
        "p_win_90d": p,
        "expected_amount_180d": amt,
        "expected_value": ev,
        "is_priority": is_priority
    })
    out.to_sql("bi_scores_daily", con, if_exists="append", index=False)
    print(f"Scored {len(out)} accounts → bi_scores_daily")

    # Legacy CSV export removed in favor of single Excel export handled separately
    if export:
        print("Skipping legacy CSV export; Excel export is handled by export_powerbi_excel().")

def maybe_update_bi_tables(con):
    # mirror latest opportunities/orders into bi_* for convenience
    con.execute("DELETE FROM bi_opportunities")
    con.execute("INSERT INTO bi_opportunities SELECT * FROM opportunities")
    con.execute("DELETE FROM bi_orders")
    con.execute("INSERT INTO bi_orders SELECT * FROM orders")
    con.commit()

def _coerce_types_and_compute_columns(tables: dict) -> dict:
    """Apply Power BI-side cleaning/modeling in Python so PBIX can load directly.

    Expected keys present in tables dict: accounts, bi_scores_daily, opportunities, orders,
    interactions, products, bi_opportunities, bi_orders
    """
    cleaned = dict(tables)

    # accounts: dates, ints, and size bucket (기관규모)
    if 'accounts' in cleaned:
        df = cleaned['accounts'].copy()
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        if 'updated_at' in df.columns:
            df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')
        for col in ['bed_count','annual_test_volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        if 'bed_count' in df.columns:
            def bucket(b):
                if pd.isna(b):
                    return np.nan
                if b >= 200:
                    return '대형'
                if b >= 50:
                    return '중형'
                return '소형'
            df['기관규모'] = df['bed_count'].apply(bucket)
        cleaned['accounts'] = df

    # bi_scores_daily: dates, decimals, score grade (스코어등급)
    if 'bi_scores_daily' in cleaned:
        df = cleaned['bi_scores_daily'].copy()
        for col in ['run_date','t0_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
        for col in ['p_win_90d','expected_amount_180d','expected_value']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        if 'p_win_90d' in df.columns:
            def grade(p):
                if pd.isna(p):
                    return np.nan
                if p >= 0.7:
                    return 'A'
                if p >= 0.4:
                    return 'B'
                return 'C'
            df['스코어등급'] = df['p_win_90d'].apply(grade)
        cleaned['bi_scores_daily'] = df

    # orders: date, numeric
    if 'orders' in cleaned:
        df = cleaned['orders'].copy()
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        if 'total_amount' in df.columns:
            df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
        cleaned['orders'] = df

    # interactions: datetime
    if 'interactions' in cleaned:
        df = cleaned['interactions'].copy()
        if 'occurred_at' in df.columns:
            df['occurred_at'] = pd.to_datetime(df['occurred_at'], errors='coerce')
        cleaned['interactions'] = df

    # opportunities: dates, numeric where applicable
    if 'opportunities' in cleaned:
        df = cleaned['opportunities'].copy()
        for col in ['expected_close_date','created_at','closed_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        if 'amount_expected' in df.columns:
            df['amount_expected'] = pd.to_numeric(df['amount_expected'], errors='coerce')
        cleaned['opportunities'] = df

    # products: requires_install to integer/bool-ish, list_price numeric
    if 'products' in cleaned:
        df = cleaned['products'].copy()
        if 'requires_install' in df.columns:
            df['requires_install'] = pd.to_numeric(df['requires_install'], errors='coerce').fillna(0).astype(int)
        if 'list_price' in df.columns:
            df['list_price'] = pd.to_numeric(df['list_price'], errors='coerce')
        cleaned['products'] = df

    # bi_opportunities, bi_orders: mirror tables can inherit types from base if needed
    if 'bi_orders' in cleaned and 'orders' in cleaned:
        # Ensure numeric/date formatting similar to orders
        df = cleaned['bi_orders'].copy()
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        if 'total_amount' in df.columns:
            df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
        cleaned['bi_orders'] = df
    if 'bi_opportunities' in cleaned and 'opportunities' in cleaned:
        df = cleaned['bi_opportunities'].copy()
        for col in ['expected_close_date','created_at','closed_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        if 'amount_expected' in df.columns:
            df['amount_expected'] = pd.to_numeric(df['amount_expected'], errors='coerce')
        cleaned['bi_opportunities'] = df

    return cleaned

def export_powerbi_excel(con, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Pull raw tables from SQLite
    table_names = [
        'bi_scores_daily', 'accounts', 'bi_opportunities', 'bi_orders',
        'interactions', 'opportunities', 'orders', 'products'
    ]
    tables = {}
    for name in table_names:
        try:
            tables[name] = pd.read_sql_query(f"SELECT * FROM {name}", con)
        except Exception:
            tables[name] = pd.DataFrame()

    # Apply cleaning/modeling
    tables = _coerce_types_and_compute_columns(tables)

    # Write to a single Excel with 8 sheets
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for name in table_names:
            tables[name].to_excel(writer, sheet_name=name, index=False)
    print(f"Exported Excel with {len(table_names)} sheets → {output_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--mode", choices=["retrain","score","export"], default="score")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    # Ensure feature view exists
    try:
        con.execute("SELECT 1 FROM feature_view LIMIT 1").fetchone()
    except Exception:
        # Try to build it
        sql = open("sql/transform.sql", "r", encoding="utf-8").read()
        con.executescript(sql)

    if args.mode == "retrain":
        df = fetch_features(con)
        train_models(df)
        maybe_update_bi_tables(con)
    elif args.mode == "score":
        score_today(con, export=False)
        maybe_update_bi_tables(con)
    elif args.mode == "export":
        # Ensure latest scores exist, then export a single Excel workbook for Power BI
        score_today(con, export=False)
        maybe_update_bi_tables(con)
        export_powerbi_excel(con, os.path.join("powerbi_data", "ivd_powerbi_data.xlsx"))

    con.close()

if __name__ == "__main__":
    main()
