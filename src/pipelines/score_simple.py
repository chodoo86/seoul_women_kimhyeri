#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
간단한 휴리스틱 기반 스코어링 파이프라인
ML 모델 대신 비즈니스 로직을 사용하여 안정적으로 작동합니다.
"""
import argparse, sqlite3, os, sys, datetime
import pandas as pd
import numpy as np

def fetch_all_data(con):
    """모든 필요한 데이터를 가져옵니다."""
    print("=== 데이터 수집 중 ===")
    
    # 기본 테이블들
    accounts = pd.read_sql_query("SELECT * FROM accounts", con)
    opportunities = pd.read_sql_query("SELECT * FROM opportunities", con)
    orders = pd.read_sql_query("SELECT * FROM orders", con)
    interactions = pd.read_sql_query("SELECT * FROM interactions", con)
    products = pd.read_sql_query("SELECT * FROM products", con)
    
    print(f"  - accounts: {len(accounts)}행 (중복 제거 전)")
    print(f"  - opportunities: {len(opportunities)}행")
    print(f"  - orders: {len(orders)}행")
    print(f"  - interactions: {len(interactions)}행")
    print(f"  - products: {len(products)}행")
    
    # accounts 중복 제거 (최신 데이터만 유지)
    if not accounts.empty:
        print("  - accounts 중복 제거 중...")
        # updated_at 컬럼이 있는지 확인
        if 'updated_at' in accounts.columns:
            # updated_at 기준으로 최신 데이터만 유지
            accounts['updated_at'] = pd.to_datetime(accounts['updated_at'], errors='coerce')
            accounts_clean = accounts.sort_values('updated_at').drop_duplicates(subset=['account_id'], keep='last')
        else:
            # updated_at이 없으면 created_at 기준
            if 'created_at' in accounts.columns:
                accounts['created_at'] = pd.to_datetime(accounts['created_at'], errors='coerce')
                accounts_clean = accounts.sort_values('created_at').drop_duplicates(subset=['account_id'], keep='last')
            else:
                # 둘 다 없으면 첫 번째 데이터만 유지
                accounts_clean = accounts.drop_duplicates(subset=['account_id'], keep='first')
        
        print(f"  - accounts: {len(accounts_clean)}행 (중복 제거 후)")
        accounts = accounts_clean
    
    return accounts, opportunities, orders, interactions, products

def calculate_heuristic_scores(accounts, opportunities, orders, interactions):
    """휴리스틱 방식으로 스코어를 계산합니다."""
    print("=== 휴리스틱 스코어 계산 중 ===")
    
    scores_data = []
    today = datetime.date.today()
    
    for _, account in accounts.iterrows():
        account_id = account['account_id']
        
        # 1. 최근 90일 상호작용 수
        cutoff_90d = today - datetime.timedelta(days=90)
        recent_interactions = interactions[
            (interactions['account_id'] == account_id) &
            (pd.to_datetime(interactions['occurred_at']).dt.date >= cutoff_90d)
        ]
        interaction_count = len(recent_interactions)
        
        # 2. 최근 180일 주문 금액
        cutoff_180d = today - datetime.timedelta(days=180)
        recent_orders = orders[
            (orders['account_id'] == account_id) &
            (pd.to_datetime(orders['order_date']).dt.date >= cutoff_180d)
        ]
        if not recent_orders.empty:
            # total_amount를 숫자로 변환
            amounts = pd.to_numeric(recent_orders['total_amount'], errors='coerce').fillna(0)
            order_amount = amounts.sum()
        else:
            order_amount = 0
        
        # 3. 기관 규모
        bed_count = account.get('bed_count', 0)
        if pd.isna(bed_count) or bed_count == '':
            bed_count = 0
        else:
            bed_count = pd.to_numeric(bed_count, errors='coerce')
            if pd.isna(bed_count):
                bed_count = 0
        
        # 4. 연간 검사량
        annual_volume = account.get('annual_test_volume', 0)
        if pd.isna(annual_volume) or annual_volume == '':
            annual_volume = 0
        else:
            annual_volume = pd.to_numeric(annual_volume, errors='coerce')
            if pd.isna(annual_volume):
                annual_volume = 0
        
        # 5. 휴리스틱 스코어 계산
        # 상호작용 점수 (0-0.3)
        interaction_score = min(interaction_count / 10, 0.3)
        
        # 주문 점수 (0-0.3)
        order_score = min(order_amount / 50000, 0.3)
        
        # 기관 규모 점수 (0-0.2)
        if bed_count >= 200:
            size_score = 0.2
        elif bed_count >= 50:
            size_score = 0.1
        else:
            size_score = 0.05
        
        # 연간 검사량 점수 (0-0.2)
        volume_score = min(annual_volume / 10000, 0.2)
        
        # 최종 확률 (0.1 ~ 0.9)
        p_win_90d = min(max(0.1 + interaction_score + order_score + size_score + volume_score, 0.1), 0.9)
        
        # 예상 거래금액
        expected_amount = max(annual_volume * 0.001, 1000)  # 최소 1000
        
        # 기대가치
        margin = 8000.0
        contact_cost = 120.0
        expected_value = p_win_90d * margin - contact_cost
        
        # 우선순위 (확률 0.5 이상)
        is_priority = 1 if p_win_90d >= 0.5 else 0
        
        # 스코어 등급
        if p_win_90d >= 0.7:
            score_grade = 'A'
        elif p_win_90d >= 0.4:
            score_grade = 'B'
        else:
            score_grade = 'C'
        
        scores_data.append({
            'run_date': today.isoformat(),
            'account_id': account_id,
            't0_date': today.isoformat(),
            'p_win_90d': p_win_90d,
            'expected_amount_180d': expected_amount,
            'expected_value': expected_value,
            'is_priority': is_priority
        })
    
    scores_df = pd.DataFrame(scores_data)
    print(f"  - {len(scores_df)}개 계정 스코어링 완료")
    
    return scores_df

def update_bi_tables(con, opportunities, orders):
    """BI 테이블을 업데이트합니다."""
    print("=== BI 테이블 업데이트 중 ===")
    
    # 기존 데이터 삭제
    con.execute("DELETE FROM bi_opportunities")
    con.execute("DELETE FROM bi_orders")
    
    # 새 데이터 삽입
    opportunities.to_sql("bi_opportunities", con, if_exists="append", index=False)
    orders.to_sql("bi_orders", con, if_exists="append", index=False)
    
    con.commit()
    print("  - bi_opportunities 업데이트 완료")
    print("  - bi_orders 업데이트 완료")

def export_powerbi_excel(con, output_path, accounts_clean=None):
    """Power BI용 Excel 파일을 생성합니다."""
    print(f"=== Power BI Excel 파일 생성: {output_path} ===")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 테이블 이름들
    table_names = [
        'bi_scores_daily', 'accounts', 'bi_opportunities', 'bi_orders',
        'interactions', 'opportunities', 'orders', 'products'
    ]
    
    tables = {}
    
    # 각 테이블에서 데이터 가져오기
    for name in table_names:
        try:
            if name == 'accounts' and accounts_clean is not None:
                # accounts는 중복 제거된 데이터 사용
                tables[name] = accounts_clean.copy()
            else:
                tables[name] = pd.read_sql_query(f"SELECT * FROM {name}", con)
            print(f"  - {name}: {len(tables[name])}행")
        except Exception as e:
            print(f"  - {name}: 오류 - {e}")
            tables[name] = pd.DataFrame()
    
    # 데이터 타입 정리
    tables = _clean_data_types(tables)
    
    # Excel 파일 생성
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for name in table_names:
            if not tables[name].empty:
                tables[name].to_excel(writer, sheet_name=name, index=False)
                print(f"  OK {name}: {len(tables[name])}행 내보내기 완료")
            else:
                print(f"  NO {name}: 내보낼 데이터 없음")
    
    print(f"SUCCESS: Excel 파일 생성 완료: {output_path}")

def _clean_data_types(tables):
    """데이터 타입을 정리합니다."""
    cleaned = dict(tables)
    
    # accounts: 날짜, 숫자, 기관규모
    if 'accounts' in cleaned and not cleaned['accounts'].empty:
        df = cleaned['accounts'].copy()
        
        # 날짜 컬럼 처리
        for col in ['created_at', 'updated_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 숫자 컬럼 처리
        for col in ['bed_count', 'annual_test_volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 기관규모 계산
        if 'bed_count' in df.columns:
            def get_size_category(bed_count):
                if pd.isna(bed_count):
                    return '소형'
                if bed_count >= 200:
                    return '대형'
                elif bed_count >= 50:
                    return '중형'
                else:
                    return '소형'
            df['기관규모'] = df['bed_count'].apply(get_size_category)
        
        cleaned['accounts'] = df
    
    # bi_scores_daily: 날짜, 숫자
    if 'bi_scores_daily' in cleaned and not cleaned['bi_scores_daily'].empty:
        df = cleaned['bi_scores_daily'].copy()
        
        # 날짜 컬럼 처리
        for col in ['run_date', 't0_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
        
        # 숫자 컬럼 처리
        for col in ['p_win_90d', 'expected_amount_180d', 'expected_value']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        cleaned['bi_scores_daily'] = df
    
    # orders: 날짜, 숫자
    if 'orders' in cleaned and not cleaned['orders'].empty:
        df = cleaned['orders'].copy()
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        if 'total_amount' in df.columns:
            df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
        cleaned['orders'] = df
    
    # interactions: 날짜
    if 'interactions' in cleaned and not cleaned['interactions'].empty:
        df = cleaned['interactions'].copy()
        if 'occurred_at' in df.columns:
            df['occurred_at'] = pd.to_datetime(df['occurred_at'], errors='coerce')
        cleaned['interactions'] = df
    
    # opportunities: 날짜, 숫자
    if 'opportunities' in cleaned and not cleaned['opportunities'].empty:
        df = cleaned['opportunities'].copy()
        for col in ['expected_close_date', 'created_at', 'closed_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        if 'amount_expected' in df.columns:
            df['amount_expected'] = pd.to_numeric(df['amount_expected'], errors='coerce')
        cleaned['opportunities'] = df
    
    # products: 숫자
    if 'products' in cleaned and not cleaned['products'].empty:
        df = cleaned['products'].copy()
        if 'requires_install' in df.columns:
            df['requires_install'] = pd.to_numeric(df['requires_install'], errors='coerce').fillna(0).astype(int)
        if 'list_price' in df.columns:
            df['list_price'] = pd.to_numeric(df['list_price'], errors='coerce')
        cleaned['products'] = df
    
    # bi_orders, bi_opportunities: 기본 테이블과 동일한 타입 적용
    if 'bi_orders' in cleaned and 'orders' in cleaned:
        cleaned['bi_orders'] = cleaned['orders'].copy()
    if 'bi_opportunities' in cleaned and 'opportunities' in cleaned:
        cleaned['bi_opportunities'] = cleaned['opportunities'].copy()
    
    return cleaned

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--mode", choices=["score","export"], default="score")
    args = ap.parse_args()

    print(f"=== 간단한 휴리스틱 파이프라인 시작 ({args.mode} 모드) ===")
    
    con = sqlite3.connect(args.db)
    
    try:
        # 모든 데이터 가져오기
        accounts, opportunities, orders, interactions, products = fetch_all_data(con)
        
        if args.mode == "score":
            print("=== 스코어링 모드 ===")
            
            # 기존 스코어 삭제
            con.execute("DELETE FROM bi_scores_daily")
            
            # 휴리스틱 스코어 계산
            scores_df = calculate_heuristic_scores(accounts, opportunities, orders, interactions)
            
            # 스코어를 DB에 저장
            scores_df.to_sql("bi_scores_daily", con, if_exists="append", index=False)
            print(f"SUCCESS: {len(scores_df)}개 계정 스코어링 완료")
            
            # BI 테이블 업데이트
            update_bi_tables(con, opportunities, orders)
            
            # 통계 출력
            print("\n=== 스코어 분포 ===")
            # 스코어 등급별 분포 계산
            a_count = len(scores_df[scores_df['p_win_90d'] >= 0.7])
            b_count = len(scores_df[(scores_df['p_win_90d'] >= 0.4) & (scores_df['p_win_90d'] < 0.7)])
            c_count = len(scores_df[scores_df['p_win_90d'] < 0.4])
            print(f"  - A등급: {a_count}개")
            print(f"  - B등급: {b_count}개")
            print(f"  - C등급: {c_count}개")
            print(f"  - 우선순위 고객: {len(scores_df[scores_df['is_priority']==1])}개")
            
        elif args.mode == "export":
            print("=== 내보내기 모드 ===")
            
            # 스코어링 먼저 실행
            con.execute("DELETE FROM bi_scores_daily")
            scores_df = calculate_heuristic_scores(accounts, opportunities, orders, interactions)
            scores_df.to_sql("bi_scores_daily", con, if_exists="append", index=False)
            
            # BI 테이블 업데이트
            update_bi_tables(con, opportunities, orders)
            
            # Excel 파일 생성 (중복 제거된 accounts 전달)
            output_path = os.path.join("powerbi_data", "ivd_powerbi_data.xlsx")
            export_powerbi_excel(con, output_path, accounts_clean=accounts)
    
    except Exception as e:
        print(f"Error occurred: {e}")
        raise
    
    finally:
        con.close()
    
    print("=== 파이프라인 완료 ===")

if __name__ == "__main__":
    main()
