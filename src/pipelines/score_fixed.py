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
    """피처 뷰에서 데이터를 가져옵니다."""
    # read feature_view
    df = pd.read_sql_query("SELECT * FROM feature_view", con, parse_dates=['t0_date'])
    
    # For labels, build a synthetic y_close_90d and y_amount_180d using heuristics on orders/opps
    t0 = pd.Timestamp(datetime.datetime.now(datetime.timezone.utc).date())
    orders = pd.read_sql_query("SELECT account_id, order_date, total_amount FROM orders", con, parse_dates=['order_date'])
    
    if not orders.empty:
        orders['days_ago'] = (t0 - orders['order_date']).dt.days
        agg90 = orders[orders['days_ago']<=90].groupby('account_id')['total_amount'].sum().rename('amt90')
        agg180 = orders[orders['days_ago']<=180].groupby('account_id')['total_amount'].sum().rename('amt180')
    else:
        agg90 = pd.Series(dtype=float)
        agg180 = pd.Series(dtype=float)
    
    df = df.merge(agg90, left_on='account_id', right_index=True, how='left')
    df = df.merge(agg180, left_on='account_id', right_index=True, how='left')
    df['amt90'] = df['amt90'].fillna(0.0)
    df['amt180'] = df['amt180'].fillna(0.0)
    
    # 데이터 타입 변환
    df['amt90'] = pd.to_numeric(df['amt90'], errors='coerce').fillna(0.0)
    df['amt180'] = pd.to_numeric(df['amt180'], errors='coerce').fillna(0.0)
    df['y_close_90d'] = (df['amt90'] > 0).astype(int)
    df['y_amount_180d'] = df['amt180']
    
    return df

def train_models(df):
    """모델을 훈련합니다."""
    if not ML_AVAILABLE:
        print("ML libraries not available; skipping train.")
        return None, None

    print(f"Training with {len(df)} samples and {len(df.columns)} features")
    
    y_cls = df['y_close_90d'].astype(int)
    y_reg = df['y_amount_180d'].astype(float)
    X = df.drop(columns=['y_close_90d','y_amount_180d','t0_date','account_id','amt90','amt180'])

    print(f"Feature columns: {list(X.columns)}")
    print(f"Number of features: {len(X.columns)}")

    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in X.columns if c not in num_cols]

    print(f"Numeric columns: {num_cols}")
    print(f"Categorical columns: {cat_cols}")

    pre = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), num_cols),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("ohe", OneHotEncoder(handle_unknown="ignore"))]), cat_cols)
    ])

    clf = Pipeline([("prep", pre), ("clf", LogisticRegression(max_iter=1000))])
    reg = Pipeline([("prep", pre), ("reg", LinearRegression())])

    # 데이터가 충분한지 확인
    if len(df) < 10:
        print("Not enough data for training, using heuristic approach")
        return None, None

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

    # 모델 저장
    joblib.dump(clf, os.path.join(MODEL_DIR, "lead_model.joblib"))
    joblib.dump(reg, os.path.join(MODEL_DIR, "amount_model.joblib"))
    print("Saved models to", MODEL_DIR)
    
    return clf, reg

def score_today(con, export=False):
    """오늘의 스코어를 계산합니다."""
    print("=== Starting scoring process ===")
    
    # Load or fallback
    model_path = os.path.join(MODEL_DIR, "lead_model.joblib")
    amount_path = os.path.join(MODEL_DIR, "amount_model.joblib")
    have_models = os.path.exists(model_path) and os.path.exists(amount_path)
    
    print(f"Model files exist: {have_models}")
    
    df = fetch_features(con)
    print(f"Fetched {len(df)} accounts for scoring")
    
    # 기존 스코어 삭제
    con.execute("DELETE FROM bi_scores_daily")
    
    if ML_AVAILABLE and have_models:
        try:
            import joblib
            clf = joblib.load(model_path)
            reg = joblib.load(amount_path)
            
            # 피처 준비
            X = df.drop(columns=['y_close_90d','y_amount_180d','t0_date','account_id','amt90','amt180'])
            print(f"Features for scoring: {len(X.columns)}")
            
            # 예측
            p = clf.predict_proba(X)[:,1]
            amt = reg.predict(X)
            print("Used ML models for scoring")
            
        except Exception as e:
            print(f"ML model failed: {e}")
            print("Falling back to heuristic approach")
            p, amt = _heuristic_scoring(df)
    else:
        print("Using heuristic approach")
        p, amt = _heuristic_scoring(df)

    # 비즈니스 로직
    margin = 8000.0
    contact_cost = 120.0
    ev = p*margin - contact_cost
    is_priority = (p >= 0.5).astype(int)

    # 스코어 등급 계산
    def get_score_grade(prob):
        if prob >= 0.7:
            return 'A'
        elif prob >= 0.4:
            return 'B'
        else:
            return 'C'
    
    score_grades = [get_score_grade(prob) for prob in p]

    out = pd.DataFrame({
        "run_date": [datetime.date.today().isoformat()]*len(df),
        "account_id": df['account_id'].values,
        "t0_date": df['t0_date'].dt.date.astype(str).values,
        "p_win_90d": p,
        "expected_amount_180d": amt,
        "expected_value": ev,
        "is_priority": is_priority,
        "스코어등급": score_grades
    })
    
    out.to_sql("bi_scores_daily", con, if_exists="append", index=False)
    print(f"Scored {len(out)} accounts → bi_scores_daily")
    
    # 통계 출력
    print(f"Score distribution:")
    print(f"  - A grade: {len(out[out['스코어등급']=='A'])} accounts")
    print(f"  - B grade: {len(out[out['스코어등급']=='B'])} accounts") 
    print(f"  - C grade: {len(out[out['스코어등급']=='C'])} accounts")
    print(f"  - Priority: {len(out[out['is_priority']==1])} accounts")

    if export:
        print("Export mode - Excel will be generated separately")

def _heuristic_scoring(df):
    """휴리스틱 방식으로 스코어를 계산합니다."""
    print("Using heuristic scoring approach")
    
    # 기본 확률
    p = np.full(len(df), 0.1)
    
    # 상호작용 기반 점수
    if 'interactions_90d' in df.columns:
        p += 0.3 * (df['interactions_90d'] > 3).astype(float)
    
    # 주문 기반 점수  
    if 'orders_cnt_180d' in df.columns:
        p += 0.2 * (df['orders_cnt_180d'] > 0).astype(float)
    
    # 기관 규모 기반 점수
    if 'bed_count' in df.columns:
        p += 0.1 * (df['bed_count'] > 100).astype(float)
    
    # 확률 범위 제한
    p = np.clip(p, 0.05, 0.95)
    
    # 예상 금액 계산
    if 'monetary_180d' in df.columns:
        amt = df['monetary_180d'] * 0.6
    else:
        amt = np.full(len(df), 1000.0)  # 기본값
    
    return p, amt

def maybe_update_bi_tables(con):
    """BI 테이블을 업데이트합니다."""
    print("Updating BI tables...")
    
    # mirror latest opportunities/orders into bi_* for convenience
    con.execute("DELETE FROM bi_opportunities")
    con.execute("INSERT INTO bi_opportunities SELECT * FROM opportunities")
    con.execute("DELETE FROM bi_orders")
    con.execute("INSERT INTO bi_orders SELECT * FROM orders")
    con.commit()
    print("BI tables updated")

def _coerce_types_and_compute_columns(tables: dict) -> dict:
    """Power BI용 데이터 타입 변환 및 계산 컬럼 추가."""
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
    """Power BI용 Excel 파일을 생성합니다."""
    print(f"=== Exporting Power BI Excel to {output_path} ===")
    
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
            print(f"  - {name}: {len(tables[name])} rows")
        except Exception as e:
            print(f"  - {name}: Error - {e}")
            tables[name] = pd.DataFrame()

    # Apply cleaning/modeling
    tables = _coerce_types_and_compute_columns(tables)

    # Write to a single Excel with 8 sheets
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for name in table_names:
            if not tables[name].empty:
                tables[name].to_excel(writer, sheet_name=name, index=False)
                print(f"  ✓ {name}: {len(tables[name])} rows exported")
            else:
                print(f"  ✗ {name}: No data to export")
    
    print(f"✅ Exported Excel with {len(table_names)} sheets → {output_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--mode", choices=["retrain","score","export"], default="score")
    args = ap.parse_args()

    print(f"=== Starting {args.mode} mode ===")
    
    con = sqlite3.connect(args.db)
    
    # Ensure feature view exists
    try:
        con.execute("SELECT 1 FROM feature_view LIMIT 1").fetchone()
        print("Feature view exists")
    except Exception:
        print("Creating feature view...")
        sql = open("sql/transform.sql", "r", encoding="utf-8").read()
        con.executescript(sql)

    if args.mode == "retrain":
        print("=== Retrain Mode ===")
        df = fetch_features(con)
        train_models(df)
        maybe_update_bi_tables(con)
        
    elif args.mode == "score":
        print("=== Score Mode ===")
        score_today(con, export=False)
        maybe_update_bi_tables(con)
        
    elif args.mode == "export":
        print("=== Export Mode ===")
        # Ensure latest scores exist, then export a single Excel workbook for Power BI
        score_today(con, export=False)
        maybe_update_bi_tables(con)
        export_powerbi_excel(con, os.path.join("powerbi_data", "ivd_powerbi_data.xlsx"))

    con.close()
    print("=== Process completed ===")

if __name__ == "__main__":
    main()

