#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

def improve_temporal_patterns():
    print("=== 시간적 패턴 개선 시작 ===")
    print()
    
    # 기존 데이터 로드 (2025-09-09 기준)
    base_date = '2025-09-09'
    base_path = f'data/landing/{base_date}'
    
    # 기준 데이터 로드
    accounts_base = pd.read_csv(f'{base_path}/accounts_{base_date}.csv')
    orders_base = pd.read_csv(f'{base_path}/orders_{base_date}.csv')
    interactions_base = pd.read_csv(f'{base_path}/interactions_{base_date}.csv')
    opportunities_base = pd.read_csv(f'{base_path}/opportunities_{base_date}.csv')
    
    print(f"기준 데이터 ({base_date}):")
    print(f"  accounts: {len(accounts_base)}개")
    print(f"  orders: {len(orders_base)}개")
    print(f"  interactions: {len(interactions_base)}개")
    print(f"  opportunities: {len(opportunities_base)}개")
    print()
    
    # 개선할 날짜들
    target_dates = ['2025-09-10', '2025-09-11', '2025-09-12', '2025-09-15', '2025-09-20', '2025-09-30']
    
    for target_date in target_dates:
        print(f"--- {target_date} 데이터 개선 ---")
        
        # 날짜 계산
        base_dt = pd.to_datetime(base_date)
        target_dt = pd.to_datetime(target_date)
        days_diff = (target_dt - base_dt).days
        
        # 1. Accounts 데이터 개선 (점진적 변화)
        accounts_new = accounts_base.copy()
        
        # 일부 고객 정보 업데이트 (5-10% 확률)
        update_prob = 0.08
        for idx in accounts_new.index:
            if random.random() < update_prob:
                # 연간 검사량 약간 조정
                if 'annual_test_volume' in accounts_new.columns:
                    change = random.uniform(0.95, 1.05)
                    accounts_new.loc[idx, 'annual_test_volume'] = int(accounts_new.loc[idx, 'annual_test_volume'] * change)
        
        # updated_at 날짜 업데이트
        accounts_new['updated_at'] = target_date
        
        # 2. Orders 데이터 개선 (현실적인 증가 패턴)
        orders_new = orders_base.copy()
        
        # 새로운 주문 추가 (일별 1-3개, 주말에는 0-1개)
        is_weekend = target_dt.weekday() >= 5
        if is_weekend:
            new_orders_count = random.randint(0, 1)
        else:
            new_orders_count = random.randint(1, 3)
        
        # 기존 주문에 새로운 주문 추가
        for i in range(new_orders_count):
            # 기존 고객 중 랜덤 선택
            customer_id = random.choice(accounts_new['account_id'].tolist())
            
            # 주문 날짜 (과거 30일 내)
            order_date = target_dt - timedelta(days=random.randint(0, 30))
            
            # 주문 금액 (기존 패턴 기반)
            base_amount = random.uniform(1500, 9500)
            amount_variation = random.uniform(0.8, 1.2)
            total_amount = base_amount * amount_variation
            
            # 새로운 주문 ID
            new_order_id = orders_new['order_id'].max() + i + 1
            
            new_order = pd.DataFrame({
                'order_id': [new_order_id],
                'account_id': [customer_id],
                'order_date': [order_date.strftime('%Y-%m-%d')],
                'total_amount': [round(total_amount, 2)]
            })
            
            orders_new = pd.concat([orders_new, new_order], ignore_index=True)
        
        # 3. Interactions 데이터 개선 (업무시간 중심, 주말 패턴)
        interactions_new = interactions_base.copy()
        
        # 새로운 상호작용 추가 (일별 2-5개, 주말에는 0-2개)
        if is_weekend:
            new_interactions_count = random.randint(0, 2)
        else:
            new_interactions_count = random.randint(2, 5)
        
        for i in range(new_interactions_count):
            # 기존 고객 중 랜덤 선택
            customer_id = random.choice(accounts_new['account_id'].tolist())
            
            # 상호작용 시간 (업무시간 중심, 주말에는 더 제한적)
            if is_weekend:
                hour = random.randint(10, 16)  # 주말 오전 10시-오후 4시
            else:
                # 업무시간에 80% 확률
                if random.random() < 0.8:
                    hour = random.randint(9, 18)
                else:
                    hour = random.randint(7, 22)
            
            minute = random.randint(0, 59)
            interaction_time = target_dt.replace(hour=hour, minute=minute)
            
            # 상호작용 채널 (현실적 분포)
            channels = ['demo', 'webinar', 'visit', 'email', 'call']
            channel_weights = [0.15, 0.20, 0.25, 0.25, 0.15]  # visit, email이 더 많음
            channel = np.random.choice(channels, p=channel_weights)
            
            # 상호작용 결과 (현실적 분포)
            outcomes = ['positive', 'neutral', 'negative']
            outcome_weights = [0.4, 0.4, 0.2]  # positive와 neutral이 많음
            outcome = np.random.choice(outcomes, p=outcome_weights)
            
            # 새로운 상호작용 ID
            new_interaction_id = interactions_new['interaction_id'].max() + i + 1
            
            new_interaction = pd.DataFrame({
                'interaction_id': [new_interaction_id],
                'account_id': [customer_id],
                'contact_id': [0],
                'channel': [channel],
                'outcome': [outcome],
                'occurred_at': [interaction_time.strftime('%Y-%m-%d %H:%M:%S')]
            })
            
            interactions_new = pd.concat([interactions_new, new_interaction], ignore_index=True)
        
        # 4. Opportunities 데이터 개선 (영업 파이프라인 현실성)
        opportunities_new = opportunities_base.copy()
        
        # 새로운 기회 추가 (일별 1-2개)
        new_opportunities_count = random.randint(1, 2)
        
        for i in range(new_opportunities_count):
            # 기존 고객 중 랜덤 선택
            customer_id = random.choice(accounts_new['account_id'].tolist())
            
            # 기회 생성 날짜 (과거 60일 내)
            created_date = target_dt - timedelta(days=random.randint(0, 60))
            
            # 영업 단계 (현실적 분포)
            stages = ['MQL', 'SQL', 'POC', 'Negotiation']
            stage_weights = [0.4, 0.3, 0.2, 0.1]  # 초기 단계가 많음
            stage = np.random.choice(stages, p=stage_weights)
            
            # 예상 마감일 (30-120일 후)
            expected_close_date = target_dt + timedelta(days=random.randint(30, 120))
            
            # 예상 금액 (주문 패턴 기반)
            expected_amount = random.uniform(2000, 12000)
            
            # 유입 경로
            sources = ['Inbound', 'Outbound', 'Bid']
            source_weights = [0.5, 0.3, 0.2]
            source = np.random.choice(sources, p=source_weights)
            
            # 새로운 기회 ID
            new_opportunity_id = opportunities_new['opportunity_id'].max() + i + 1
            
            new_opportunity = pd.DataFrame({
                'opportunity_id': [new_opportunity_id],
                'account_id': [customer_id],
                'stage': [stage],
                'expected_close_date': [expected_close_date.strftime('%Y-%m-%d')],
                'amount_expected': [round(expected_amount, 2)],
                'source': [source],
                'created_at': [created_date.strftime('%Y-%m-%d')],
                'closed_at': [None]
            })
            
            opportunities_new = pd.concat([opportunities_new, new_opportunity], ignore_index=True)
        
        # 5. 데이터 저장
        target_path = f'data/landing/{target_date}'
        os.makedirs(target_path, exist_ok=True)
        
        # 모든 테이블 저장
        tables = {
            'accounts': accounts_new,
            'orders': orders_new,
            'interactions': interactions_new,
            'opportunities': opportunities_new
        }
        
        # 기존 테이블들도 복사
        other_tables = ['products', 'install_base', 'bids', 'service_tickets', 'web_events']
        for table in other_tables:
            source_file = f'{base_path}/{table}_{base_date}.csv'
            if os.path.exists(source_file):
                df = pd.read_csv(source_file)
                # 날짜 컬럼이 있다면 업데이트
                for col in df.columns:
                    if 'date' in col.lower() or 'at' in col.lower():
                        if df[col].dtype == 'object':
                            # 날짜 형식인 경우 업데이트
                            try:
                                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
                            except:
                                pass
                tables[table] = df
        
        # 파일 저장
        for table_name, df in tables.items():
            output_file = f'{target_path}/{table_name}_{target_date}.csv'
            df.to_csv(output_file, index=False)
        
        print(f"  저장 완료: {len(tables)}개 테이블")
        print(f"  accounts: {len(accounts_new)}개")
        print(f"  orders: {len(orders_new)}개 (+{len(orders_new) - len(orders_base)})")
        print(f"  interactions: {len(interactions_new)}개 (+{len(interactions_new) - len(interactions_base)})")
        print(f"  opportunities: {len(opportunities_new)}개 (+{len(opportunities_new) - len(opportunities_base)})")
        print()
    
    print("=== 시간적 패턴 개선 완료 ===")
    print("개선 사항:")
    print("1. 주문 데이터: 일정한 증가가 아닌 불규칙한 변화")
    print("2. 상호작용 데이터: 업무시간 중심, 주말 패턴 반영")
    print("3. 영업 기회: 현실적인 단계별 분포")
    print("4. 고객 데이터: 점진적 정보 업데이트")
    print("5. 주말/평일 패턴: 주말에는 활동 감소")

if __name__ == "__main__":
    improve_temporal_patterns()
