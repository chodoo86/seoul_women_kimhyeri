#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as np

def analyze_data_realism():
    print("=== 합성 데이터의 현실성 분석 ===")
    print()
    
    dates = ['2025-09-07', '2025-09-08', '2025-09-09', '2025-09-10', '2025-09-11', 
             '2025-09-12', '2025-09-15', '2025-09-20', '2025-09-30']
    
    # 1. 데이터 일관성 분석
    print("1. 데이터 일관성 분석")
    print("-" * 50)
    
    accounts_data = {}
    for date in dates:
        file_path = f'data/landing/{date}/accounts_{date}.csv'
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            accounts_data[date] = df
    
    # accounts 데이터의 일관성 확인
    print("Accounts 데이터 일관성:")
    base_columns = ['account_id', 'account_name', 'account_type', 'bed_count', 'annual_test_volume']
    for col in base_columns:
        values = {}
        for date, df in accounts_data.items():
            if col in df.columns:
                values[date] = df[col].tolist()
        
        # 모든 날짜에서 동일한지 확인
        if len(set(str(v) for v in values.values())) == 1:
            print(f"  [OK] {col}: 모든 날짜에서 동일 (일관성 있음)")
        else:
            print(f"  [X] {col}: 날짜별로 다름 (일관성 없음)")
    
    print()
    
    # 2. 시간적 패턴 분석
    print("2. 시간적 패턴 분석")
    print("-" * 50)
    
    # Orders 데이터의 시간적 패턴
    print("Orders 데이터 패턴:")
    for date in dates:
        file_path = f'data/landing/{date}/orders_{date}.csv'
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if 'order_date' in df.columns:
                order_dates = pd.to_datetime(df['order_date']).dt.date
                recent_orders = order_dates[order_dates >= pd.to_datetime(date).date()]
                print(f"  {date}: 총 {len(df)}개 주문, 최근 주문 {len(recent_orders)}개")
    
    print()
    
    # 3. 데이터 증가 패턴 분석
    print("3. 데이터 증가 패턴 분석")
    print("-" * 50)
    
    # 각 날짜별 데이터 양 추이
    data_counts = {}
    for date in dates:
        file_path = f'data/landing/{date}/orders_{date}.csv'
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            data_counts[date] = len(df)
    
    print("Orders 데이터 증가 패턴:")
    prev_count = None
    for date, count in data_counts.items():
        if prev_count is not None:
            change = count - prev_count
            change_pct = (change / prev_count) * 100 if prev_count > 0 else 0
            print(f"  {date}: {count}개 (변화: {change:+d}, {change_pct:+.1f}%)")
        else:
            print(f"  {date}: {count}개 (기준)")
        prev_count = count
    
    print()
    
    # 4. 비즈니스 로직 현실성 분석
    print("4. 비즈니스 로직 현실성 분석")
    print("-" * 50)
    
    # 최신 날짜 데이터로 분석
    latest_date = '2025-09-30'
    accounts_file = f'data/landing/{latest_date}/accounts_{latest_date}.csv'
    orders_file = f'data/landing/{latest_date}/orders_{latest_date}.csv'
    interactions_file = f'data/landing/{latest_date}/interactions_{latest_date}.csv'
    
    if all(os.path.exists(f) for f in [accounts_file, orders_file, interactions_file]):
        accounts_df = pd.read_csv(accounts_file)
        orders_df = pd.read_csv(orders_file)
        interactions_df = pd.read_csv(interactions_file)
        
        # 고객별 주문 패턴 분석
        print("고객별 주문 패턴:")
        customer_orders = orders_df.groupby('account_id').size()
        print(f"  주문한 고객 수: {len(customer_orders)}")
        print(f"  평균 주문 수: {customer_orders.mean():.2f}")
        print(f"  최대 주문 수: {customer_orders.max()}")
        
        # 고객별 상호작용 패턴 분석
        print("\n고객별 상호작용 패턴:")
        customer_interactions = interactions_df.groupby('account_id').size()
        print(f"  상호작용한 고객 수: {len(customer_interactions)}")
        print(f"  평균 상호작용 수: {customer_interactions.mean():.2f}")
        print(f"  최대 상호작용 수: {customer_interactions.max()}")
        
        # 상호작용 채널 분포
        if 'channel' in interactions_df.columns:
            print("\n상호작용 채널 분포:")
            channel_dist = interactions_df['channel'].value_counts()
            for channel, count in channel_dist.items():
                pct = (count / len(interactions_df)) * 100
                print(f"  {channel}: {count}개 ({pct:.1f}%)")
        
        # 상호작용 결과 분포
        if 'outcome' in interactions_df.columns:
            print("\n상호작용 결과 분포:")
            outcome_dist = interactions_df['outcome'].value_counts()
            for outcome, count in outcome_dist.items():
                pct = (count / len(interactions_df)) * 100
                print(f"  {outcome}: {count}개 ({pct:.1f}%)")
    
    print()
    
    # 5. 데이터 품질 평가
    print("5. 데이터 품질 평가")
    print("-" * 50)
    
    # 결측값 분석
    latest_files = {
        'accounts': f'data/landing/{latest_date}/accounts_{latest_date}.csv',
        'orders': f'data/landing/{latest_date}/orders_{latest_date}.csv',
        'interactions': f'data/landing/{latest_date}/interactions_{latest_date}.csv',
        'opportunities': f'data/landing/{latest_date}/opportunities_{latest_date}.csv'
    }
    
    for name, file_path in latest_files.items():
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            missing_data = df.isnull().sum()
            total_missing = missing_data.sum()
            print(f"{name}:")
            print(f"  총 행 수: {len(df)}")
            print(f"  결측값: {total_missing}개")
            if total_missing > 0:
                for col, missing in missing_data.items():
                    if missing > 0:
                        pct = (missing / len(df)) * 100
                        print(f"    {col}: {missing}개 ({pct:.1f}%)")
            else:
                print("  [OK] 결측값 없음")
    
    print()
    
    # 6. 현실성 종합 평가
    print("6. 현실성 종합 평가")
    print("-" * 50)
    
    realism_score = 0
    max_score = 0
    
    # 데이터 일관성 (20점)
    max_score += 20
    if all(len(set(str(accounts_data[date][col].tolist()) for date in accounts_data.keys())) == 1 
           for col in ['account_id', 'account_name', 'account_type']):
        realism_score += 20
        print("[OK] 데이터 일관성: 20/20 (고객 기본 정보는 일관성 있음)")
    else:
        print("[X] 데이터 일관성: 0/20")
    
    # 시간적 패턴 (20점)
    max_score += 20
    if data_counts['2025-09-30'] > data_counts['2025-09-07']:
        realism_score += 15
        print("[OK] 시간적 패턴: 15/20 (데이터가 시간에 따라 증가)")
    else:
        print("[X] 시간적 패턴: 0/20")
    
    # 비즈니스 로직 (30점)
    max_score += 30
    if len(customer_orders) > 0 and len(customer_interactions) > 0:
        realism_score += 25
        print("[OK] 비즈니스 로직: 25/30 (고객-주문-상호작용 관계가 존재)")
    else:
        print("[X] 비즈니스 로직: 0/30")
    
    # 데이터 품질 (20점)
    max_score += 20
    if total_missing == 0:
        realism_score += 20
        print("[OK] 데이터 품질: 20/20 (결측값 없음)")
    else:
        print(f"[X] 데이터 품질: 10/20 (일부 결측값 존재)")
        realism_score += 10
    
    # 다양성 (10점)
    max_score += 10
    if 'channel' in interactions_df.columns and len(interactions_df['channel'].unique()) > 2:
        realism_score += 10
        print("[OK] 다양성: 10/10 (다양한 상호작용 채널)")
    else:
        print("[X] 다양성: 5/10")
        realism_score += 5
    
    print(f"\n=== 종합 현실성 점수: {realism_score}/{max_score} ({realism_score/max_score*100:.1f}%) ===")
    
    if realism_score >= max_score * 0.8:
        print("[우수] 매우 현실적인 합성 데이터")
    elif realism_score >= max_score * 0.6:
        print("[양호] 어느 정도 현실적인 합성 데이터")
    else:
        print("[개선필요] 현실성이 부족한 합성 데이터")

if __name__ == "__main__":
    analyze_data_realism()
