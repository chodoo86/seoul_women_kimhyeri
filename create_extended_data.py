#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
데이터 확장 스크립트: 2025-09-10부터 2025-09-30까지의 데이터 생성
기존 데이터를 복사하여 날짜만 변경하는 방식
"""

import os
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import shutil

# 시드 설정
np.random.seed(42)
random.seed(42)

def create_date_range():
    """2025-09-10부터 2025-09-30까지의 날짜 리스트 생성"""
    start_date = datetime(2025, 9, 10)
    end_date = datetime(2025, 9, 30)
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    return dates

def load_latest_data():
    """가장 최근 데이터 (2025-09-09) 로드"""
    latest_date = "2025-09-09"
    data = {}
    
    # 절대 경로 사용
    base_dir = os.path.dirname(__file__)
    latest_dir = os.path.join(base_dir, "data", "landing", latest_date)
    
    files = [
        'accounts', 'opportunities', 'orders', 'interactions',
        'products', 'install_base', 'bids', 'service_tickets', 'web_events'
    ]
    
    for file in files:
        try:
            filepath = os.path.join(latest_dir, f"{file}_{latest_date}.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                data[file] = df
                print(f"Loaded {file}: {len(df)} rows")
            else:
                print(f"Warning: {filepath} not found")
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    return data

def modify_data_for_date(data, date_str):
    """특정 날짜에 맞게 데이터 수정"""
    modified_data = {}
    
    for table_name, df in data.items():
        df_copy = df.copy()
        
        if table_name == 'accounts':
            # updated_at을 현재 날짜로 업데이트
            df_copy['updated_at'] = date_str
            
        elif table_name == 'opportunities':
            # 새로운 기회 추가 (5-10개)
            new_opportunities = []
            num_new = random.randint(5, 10)
            
            for i in range(num_new):
                opp_id = df_copy['opportunity_id'].max() + i + 1
                account_id = random.choice(df_copy['account_id'].unique())
                
                # 단계별 분포
                stage_weights = {'MQL': 0.17, 'SQL': 0.23, 'POC': 0.17, 'Negotiation': 0.09, 'ClosedWon': 0.17, 'ClosedLost': 0.17}
                stage = np.random.choice(list(stage_weights.keys()), p=list(stage_weights.values()))
                
                # 예상 마감일 (30-180일 후)
                close_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d')
                
                # 예상 금액
                amount = np.random.lognormal(8.5, 0.8)
                
                # 소스 분포
                source_weights = {'Bid': 0.287, 'Outbound': 0.253, 'Webinar': 0.23, 'Inbound': 0.23}
                source = np.random.choice(list(source_weights.keys()), p=list(source_weights.values()))
                
                # 생성일 (최근 30일 내)
                created_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                
                # 마감일
                closed_at = ''
                if stage in ['ClosedWon', 'ClosedLost']:
                    closed_at = (datetime.strptime(close_date, '%Y-%m-%d') - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                
                new_opp = {
                    'opportunity_id': opp_id,
                    'account_id': account_id,
                    'stage': stage,
                    'expected_close_date': close_date,
                    'amount_expected': round(amount, 2),
                    'source': source,
                    'created_at': created_date,
                    'closed_at': closed_at
                }
                new_opportunities.append(new_opp)
            
            # 새 기회 추가
            new_df = pd.DataFrame(new_opportunities)
            df_copy = pd.concat([df_copy, new_df], ignore_index=True)
            
        elif table_name == 'orders':
            # 새로운 주문 추가 (3-8개)
            new_orders = []
            num_new = random.randint(3, 8)
            
            for i in range(num_new):
                order_id = df_copy['order_id'].max() + i + 1
                account_id = random.choice(df_copy['account_id'].unique())
                
                # 주문일 (최근 30일 내)
                order_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                
                # 주문 금액
                amount = np.random.lognormal(7.5, 0.7)
                
                new_order = {
                    'order_id': order_id,
                    'account_id': account_id,
                    'order_date': order_date,
                    'total_amount': round(amount, 2)
                }
                new_orders.append(new_order)
            
            # 새 주문 추가
            new_df = pd.DataFrame(new_orders)
            df_copy = pd.concat([df_copy, new_df], ignore_index=True)
            
        elif table_name == 'interactions':
            # 새로운 상호작용 추가 (10-20개)
            new_interactions = []
            num_new = random.randint(10, 20)
            
            for i in range(num_new):
                interaction_id = df_copy['interaction_id'].max() + i + 1
                account_id = random.choice(df_copy['account_id'].unique())
                
                # 채널 분포
                channel_weights = {'webinar': 0.25, 'demo': 0.225, 'visit': 0.20, 'email': 0.20, 'call': 0.125}
                channel = np.random.choice(list(channel_weights.keys()), p=list(channel_weights.values()))
                
                # 결과 분포
                outcome_weights = {'positive': 0.4, 'neutral': 0.4, 'negative': 0.2}
                outcome = np.random.choice(list(outcome_weights.keys()), p=list(outcome_weights.values()))
                
                # 발생일시 (최근 7일 내)
                occurred_at = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d %H:%M:%S')
                
                new_interaction = {
                    'interaction_id': interaction_id,
                    'account_id': account_id,
                    'contact_id': 0,
                    'channel': channel,
                    'outcome': outcome,
                    'occurred_at': occurred_at
                }
                new_interactions.append(new_interaction)
            
            # 새 상호작용 추가
            new_df = pd.DataFrame(new_interactions)
            df_copy = pd.concat([df_copy, new_df], ignore_index=True)
            
        elif table_name == 'install_base':
            # 새로운 설치 추가 (1-3개)
            new_installs = []
            num_new = random.randint(1, 3)
            
            for i in range(num_new):
                install_id = df_copy['install_id'].max() + i + 1
                account_id = random.choice(df_copy['account_id'].unique())
                product_id = random.choice(df_copy['product_id'].unique())
                
                # 설치일 (최근 30일 내)
                install_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                
                # 보증 만료일 (1-3년 후)
                warranty_end = (datetime.strptime(install_date, '%Y-%m-%d') + timedelta(days=random.randint(365, 1095))).strftime('%Y-%m-%d')
                
                # 상태 분포
                status_weights = {'active': 0.593, 'inactive': 0.203, 'retired': 0.203}
                status = np.random.choice(list(status_weights.keys()), p=list(status_weights.values()))
                
                new_install = {
                    'install_id': install_id,
                    'account_id': account_id,
                    'product_id': product_id,
                    'install_date': install_date,
                    'warranty_end': warranty_end,
                    'status': status
                }
                new_installs.append(new_install)
            
            # 새 설치 추가
            new_df = pd.DataFrame(new_installs)
            df_copy = pd.concat([df_copy, new_df], ignore_index=True)
            
        elif table_name == 'bids':
            # 새로운 입찰 추가 (1-4개)
            new_bids = []
            num_new = random.randint(1, 4)
            
            for i in range(num_new):
                bid_id = df_copy['bid_id'].max() + i + 1
                account_id = random.choice(df_copy['account_id'].unique())
                
                # 입찰 마감일 (7-60일 후)
                bid_due_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=random.randint(7, 60))).strftime('%Y-%m-%d')
                
                # 입찰 상태 분포
                status_weights = {'won': 0.333, 'lost': 0.25, 'submitted': 0.208, 'planned': 0.208}
                bid_status = np.random.choice(list(status_weights.keys()), p=list(status_weights.values()))
                
                # 예상 금액
                est_amount = np.random.lognormal(9.0, 0.8)
                
                # 생성일 (최근 30일 내)
                created_at = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                
                new_bid = {
                    'bid_id': bid_id,
                    'account_id': account_id,
                    'bid_due_date': bid_due_date,
                    'bid_status': bid_status,
                    'est_amount': round(est_amount, 2),
                    'created_at': created_at
                }
                new_bids.append(new_bid)
            
            # 새 입찰 추가
            new_df = pd.DataFrame(new_bids)
            df_copy = pd.concat([df_copy, new_df], ignore_index=True)
            
        elif table_name == 'service_tickets':
            # 새로운 티켓 추가 (2-6개)
            new_tickets = []
            num_new = random.randint(2, 6)
            
            for i in range(num_new):
                ticket_id = df_copy['ticket_id'].max() + i + 1
                account_id = random.choice(df_copy['account_id'].unique())
                
                # 개설일 (최근 30일 내)
                opened_at = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                
                # 해결일 (개설일 + 1-14일)
                closed_at = (datetime.strptime(opened_at, '%Y-%m-%d') + timedelta(days=random.randint(1, 14))).strftime('%Y-%m-%d')
                
                # 심각도 분포
                severity_weights = {'P1': 0.091, 'P2': 0.398, 'P3': 0.511}
                severity = np.random.choice(list(severity_weights.keys()), p=list(severity_weights.values()))
                
                # 이슈 유형 분포
                issue_weights = {'Quality': 0.398, 'Training': 0.318, 'Delivery': 0.284}
                issue_type = np.random.choice(list(issue_weights.keys()), p=list(issue_weights.values()))
                
                new_ticket = {
                    'ticket_id': ticket_id,
                    'account_id': account_id,
                    'product_id': 0,
                    'opened_at': opened_at,
                    'closed_at': closed_at,
                    'severity': severity,
                    'issue_type': issue_type
                }
                new_tickets.append(new_ticket)
            
            # 새 티켓 추가
            new_df = pd.DataFrame(new_tickets)
            df_copy = pd.concat([df_copy, new_df], ignore_index=True)
            
        elif table_name == 'web_events':
            # 새로운 웹 이벤트 추가 (5-15개)
            new_events = []
            num_new = random.randint(5, 15)
            
            for i in range(num_new):
                web_event_id = df_copy['web_event_id'].max() + i + 1
                account_id = random.choice(df_copy['account_id'].unique())
                
                # 이벤트 유형
                event_types = ['pageview', 'form_submit', 'webinar_signup']
                event_type = random.choice(event_types)
                
                # 발생일시 (최근 7일 내)
                occurred_at = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d %H:%M:%S')
                
                new_event = {
                    'web_event_id': web_event_id,
                    'account_id': account_id,
                    'event_type': event_type,
                    'url': 'https://example.com',
                    'occurred_at': occurred_at
                }
                new_events.append(new_event)
            
            # 새 이벤트 추가
            new_df = pd.DataFrame(new_events)
            df_copy = pd.concat([df_copy, new_df], ignore_index=True)
        
        modified_data[table_name] = df_copy
    
    return modified_data

def save_data_to_csv(data, date_str):
    """데이터를 CSV 파일로 저장"""
    # 절대 경로 사용
    base_dir = os.path.dirname(__file__)
    date_dir = os.path.join(base_dir, "data", "landing", date_str)
    os.makedirs(date_dir, exist_ok=True)
    
    for table_name, df in data.items():
        filename = f"{table_name}_{date_str}.csv"
        filepath = os.path.join(date_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"Saved {filepath} ({len(df)} rows)")

def main():
    """메인 실행 함수"""
    print("데이터 확장 시작: 2025-09-10 ~ 2025-09-30")
    
    # 최신 데이터 로드
    print("최신 데이터 로드 중...")
    latest_data = load_latest_data()
    
    if not latest_data:
        print("❌ 최신 데이터를 로드할 수 없습니다.")
        return
    
    # 날짜 범위 생성
    dates = create_date_range()
    print(f"생성할 날짜: {len(dates)}일")
    
    # 각 날짜별로 데이터 생성 및 저장
    for i, date_str in enumerate(dates, 1):
        print(f"\n=== [{i}/{len(dates)}] {date_str} 데이터 생성 중 ===")
        
        # 데이터 수정
        modified_data = modify_data_for_date(latest_data, date_str)
        
        # CSV 파일로 저장
        save_data_to_csv(modified_data, date_str)
        
        print(f"✅ {date_str} 데이터 생성 완료")
    
    print(f"\n🎉 모든 데이터 생성 완료! ({len(dates)}일)")
    print("생성된 폴더들:")
    for date_str in dates:
        print(f"  - data/landing/{date_str}/")

if __name__ == "__main__":
    main()
