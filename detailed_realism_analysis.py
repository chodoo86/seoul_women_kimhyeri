#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def detailed_realism_analysis():
    print("=== 추가 현실성 분석 ===")
    print()
    
    # 1. 주문 금액 분포 현실성
    print("1. 주문 금액 분포 현실성:")
    df = pd.read_csv('data/landing/2025-09-30/orders_2025-09-30.csv')
    print(f"평균 주문 금액: {df['total_amount'].mean():.2f}")
    print(f"중간값: {df['total_amount'].median():.2f}")
    print(f"최소값: {df['total_amount'].min():.2f}")
    print(f"최대값: {df['total_amount'].max():.2f}")
    print(f"표준편차: {df['total_amount'].std():.2f}")
    
    # 주문 금액 분포의 현실성 평가
    if 1000 <= df['total_amount'].mean() <= 10000:
        print("[OK] 주문 금액이 현실적 범위 (1,000-10,000)")
    else:
        print("[X] 주문 금액이 비현실적 범위")
    
    print()
    
    # 2. 고객 규모별 분포
    print("2. 고객 규모별 분포:")
    accounts = pd.read_csv('data/landing/2025-09-30/accounts_2025-09-30.csv')
    account_types = accounts['account_type'].value_counts()
    for account_type, count in account_types.items():
        pct = (count / len(accounts)) * 100
        print(f"{account_type}: {count}개 ({pct:.1f}%)")
    
    # 기관 유형 분포의 현실성 평가
    if len(account_types) >= 3 and all(count > 0 for count in account_types.values):
        print("[OK] 다양한 기관 유형이 현실적으로 분포")
    else:
        print("[X] 기관 유형 분포가 비현실적")
    
    print()
    
    # 3. 상호작용 시간 패턴
    print("3. 상호작용 시간 패턴:")
    interactions = pd.read_csv('data/landing/2025-09-30/interactions_2025-09-30.csv')
    interactions['hour'] = pd.to_datetime(interactions['occurred_at']).dt.hour
    hour_dist = interactions['hour'].value_counts().sort_index()
    
    print("시간대별 상호작용:")
    for hour, count in hour_dist.items():
        print(f"  {hour:02d}시: {count}개")
    
    # 업무시간 상호작용 비율 확인
    business_hours = interactions[(interactions['hour'] >= 9) & (interactions['hour'] <= 18)]
    business_ratio = len(business_hours) / len(interactions) * 100
    print(f"업무시간(9-18시) 상호작용 비율: {business_ratio:.1f}%")
    
    if business_ratio >= 60:
        print("[OK] 업무시간에 상호작용이 집중됨 (현실적)")
    else:
        print("[X] 업무시간 외 상호작용이 과도함 (비현실적)")
    
    print()
    
    # 4. 고객별 활동 패턴
    print("4. 고객별 활동 패턴:")
    
    # 고객별 주문 수 분포
    customer_orders = df.groupby('account_id').size()
    print(f"주문한 고객 수: {len(customer_orders)}")
    print(f"평균 주문 수: {customer_orders.mean():.2f}")
    print(f"주문 수 분포:")
    print(f"  1회: {len(customer_orders[customer_orders == 1])}명")
    print(f"  2-3회: {len(customer_orders[(customer_orders >= 2) & (customer_orders <= 3)])}명")
    print(f"  4회 이상: {len(customer_orders[customer_orders >= 4])}명")
    
    # 고객별 상호작용 수 분포
    customer_interactions = interactions.groupby('account_id').size()
    print(f"상호작용한 고객 수: {len(customer_interactions)}")
    print(f"평균 상호작용 수: {customer_interactions.mean():.2f}")
    
    print()
    
    # 5. 데이터 일관성 검증
    print("5. 데이터 일관성 검증:")
    
    # 고객 ID 일관성
    account_ids = set(accounts['account_id'].unique())
    order_account_ids = set(df['account_id'].unique())
    interaction_account_ids = set(interactions['account_id'].unique())
    
    print(f"accounts 고객 수: {len(account_ids)}")
    print(f"orders 고객 수: {len(order_account_ids)}")
    print(f"interactions 고객 수: {len(interaction_account_ids)}")
    
    # 외래키 일관성 확인
    if order_account_ids.issubset(account_ids):
        print("[OK] orders의 account_id가 accounts에 존재")
    else:
        print("[X] orders에 존재하지 않는 account_id 발견")
    
    if interaction_account_ids.issubset(account_ids):
        print("[OK] interactions의 account_id가 accounts에 존재")
    else:
        print("[X] interactions에 존재하지 않는 account_id 발견")
    
    print()
    
    # 6. 비즈니스 로직 현실성
    print("6. 비즈니스 로직 현실성:")
    
    # 상호작용 후 주문 패턴
    print("상호작용-주문 연관성:")
    interaction_dates = pd.to_datetime(interactions['occurred_at']).dt.date
    order_dates = pd.to_datetime(df['order_date']).dt.date
    
    # 상호작용 후 30일 내 주문이 발생한 고객
    recent_interactions = interactions[pd.to_datetime(interactions['occurred_at']).dt.date >= pd.to_datetime('2025-09-01').date()]
    recent_orders = df[pd.to_datetime(df['order_date']).dt.date >= pd.to_datetime('2025-09-01').date()]
    
    interaction_customers = set(recent_interactions['account_id'].unique())
    order_customers = set(recent_orders['account_id'].unique())
    
    overlap = len(interaction_customers.intersection(order_customers))
    print(f"상호작용한 고객 중 주문한 고객: {overlap}명")
    print(f"상호작용-주문 전환율: {overlap/len(interaction_customers)*100:.1f}%")
    
    if overlap > 0:
        print("[OK] 상호작용과 주문 간 연관성 존재")
    else:
        print("[X] 상호작용과 주문 간 연관성 부족")
    
    print()
    
    # 7. 종합 현실성 평가
    print("7. 종합 현실성 평가:")
    
    realism_issues = []
    
    # 주문 금액 현실성
    if not (1000 <= df['total_amount'].mean() <= 10000):
        realism_issues.append("주문 금액이 비현실적")
    
    # 업무시간 상호작용
    if business_ratio < 60:
        realism_issues.append("업무시간 외 상호작용 과다")
    
    # 데이터 일관성
    if not (order_account_ids.issubset(account_ids) and interaction_account_ids.issubset(account_ids)):
        realism_issues.append("데이터 일관성 문제")
    
    # 상호작용-주문 연관성
    if overlap == 0:
        realism_issues.append("상호작용-주문 연관성 부족")
    
    if len(realism_issues) == 0:
        print("[우수] 현실적인 합성 데이터")
    elif len(realism_issues) <= 2:
        print("[양호] 대체로 현실적인 합성 데이터")
        print("개선 사항:")
        for issue in realism_issues:
            print(f"  - {issue}")
    else:
        print("[개선필요] 현실성이 부족한 합성 데이터")
        print("주요 문제점:")
        for issue in realism_issues:
            print(f"  - {issue}")

if __name__ == "__main__":
    detailed_realism_analysis()
