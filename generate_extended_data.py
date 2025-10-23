#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
데이터 확장 스크립트: 2025-09-10부터 2025-09-30까지의 데이터 생성
기존 패턴을 분석하여 일관성 있는 데이터를 생성합니다.
"""

import os
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import csv

# 시드 설정 (재현 가능한 결과를 위해)
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

def load_sample_data():
    """기존 샘플 데이터 로드"""
    sample_data = {}
    sample_files = [
        'accounts.csv', 'opportunities.csv', 'orders.csv', 'interactions.csv',
        'products.csv', 'install_base.csv', 'bids.csv', 'service_tickets.csv', 'web_events.csv'
    ]
    
    for file in sample_files:
        try:
            # 절대 경로 사용
            file_path = os.path.join(os.path.dirname(__file__), 'data', 'samples', file)
            df = pd.read_csv(file_path)
            sample_data[file.replace('.csv', '')] = df
        except Exception as e:
            print(f"Warning: Could not load {file}: {e}")
    
    return sample_data

def generate_accounts_data(sample_data, date_str):
    """accounts 데이터 생성"""
    if 'accounts' not in sample_data:
        return None
    
    df = sample_data['accounts'].copy()
    # updated_at을 현재 날짜로 업데이트
    df['updated_at'] = date_str
    return df

def generate_opportunities_data(sample_data, date_str):
    """opportunities 데이터 생성 (새로운 기회 추가)"""
    if 'opportunities' not in sample_data:
        return None
    
    df = sample_data['opportunities'].copy()
    
    # 새로운 기회 생성 (5-10개)
    new_opportunities = []
    num_new = random.randint(5, 10)
    
    for i in range(num_new):
        opp_id = df['opportunity_id'].max() + i + 1
        account_id = random.choice(df['account_id'].unique())
        
        # 단계별 분포 (기존 패턴 유지)
        stage_weights = {'MQL': 0.17, 'SQL': 0.23, 'POC': 0.17, 'Negotiation': 0.09, 'ClosedWon': 0.17, 'ClosedLost': 0.17}
        stage = np.random.choice(list(stage_weights.keys()), p=list(stage_weights.values()))
        
        # 예상 마감일 (30-180일 후)
        close_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d')
        
        # 예상 금액 (기존 분포 유지)
        amount = np.random.lognormal(8.5, 0.8)  # 평균 약 20,000원
        
        # 소스 분포 (기존 패턴 유지)
        source_weights = {'Bid': 0.287, 'Outbound': 0.253, 'Webinar': 0.23, 'Inbound': 0.23}
        source = np.random.choice(list(source_weights.keys()), p=list(source_weights.values()))
        
        # 생성일 (최근 30일 내)
        created_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        
        # 마감일 (ClosedWon/ClosedLost인 경우)
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
    
    # 기존 데이터와 새 데이터 합치기
    new_df = pd.DataFrame(new_opportunities)
    result_df = pd.concat([df, new_df], ignore_index=True)
    return result_df

def generate_orders_data(sample_data, date_str):
    """orders 데이터 생성 (새로운 주문 추가)"""
    if 'orders' not in sample_data:
        return None
    
    df = sample_data['orders'].copy()
    
    # 새로운 주문 생성 (3-8개)
    new_orders = []
    num_new = random.randint(3, 8)
    
    for i in range(num_new):
        order_id = df['order_id'].max() + i + 1
        account_id = random.choice(df['account_id'].unique())
        
        # 주문일 (최근 30일 내)
        order_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        
        # 주문 금액 (기존 분포 유지)
        amount = np.random.lognormal(7.5, 0.7)  # 평균 약 5,500원
        
        new_order = {
            'order_id': order_id,
            'account_id': account_id,
            'order_date': order_date,
            'total_amount': round(amount, 2)
        }
        new_orders.append(new_order)
    
    # 기존 데이터와 새 데이터 합치기
    new_df = pd.DataFrame(new_orders)
    result_df = pd.concat([df, new_df], ignore_index=True)
    return result_df

def generate_interactions_data(sample_data, date_str):
    """interactions 데이터 생성 (새로운 상호작용 추가)"""
    if 'interactions' not in sample_data:
        return None
    
    df = sample_data['interactions'].copy()
    
    # 새로운 상호작용 생성 (10-20개)
    new_interactions = []
    num_new = random.randint(10, 20)
    
    for i in range(num_new):
        interaction_id = df['interaction_id'].max() + i + 1
        account_id = random.choice(df['account_id'].unique())
        
        # 채널 분포 (기존 패턴 유지)
        channel_weights = {'webinar': 0.25, 'demo': 0.225, 'visit': 0.20, 'email': 0.20, 'call': 0.125}
        channel = np.random.choice(list(channel_weights.keys()), p=list(channel_weights.values()))
        
        # 결과 분포 (기존 패턴 유지)
        outcome_weights = {'positive': 0.4, 'neutral': 0.4, 'negative': 0.2}
        outcome = np.random.choice(list(outcome_weights.keys()), p=list(outcome_weights.values()))
        
        # 발생일시 (최근 7일 내)
        occurred_at = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d %H:%M:%S')
        
        new_interaction = {
            'interaction_id': interaction_id,
            'account_id': account_id,
            'contact_id': 0,  # 기존 패턴 유지
            'channel': channel,
            'outcome': outcome,
            'occurred_at': occurred_at
        }
        new_interactions.append(new_interaction)
    
    # 기존 데이터와 새 데이터 합치기
    new_df = pd.DataFrame(new_interactions)
    result_df = pd.concat([df, new_df], ignore_index=True)
    return result_df

def generate_products_data(sample_data, date_str):
    """products 데이터 생성 (변경 없음)"""
    if 'products' not in sample_data:
        return None
    return sample_data['products'].copy()

def generate_install_base_data(sample_data, date_str):
    """install_base 데이터 생성 (새로운 설치 추가)"""
    if 'install_base' not in sample_data:
        return None
    
    df = sample_data['install_base'].copy()
    
    # 새로운 설치 생성 (1-3개)
    new_installs = []
    num_new = random.randint(1, 3)
    
    for i in range(num_new):
        install_id = df['install_id'].max() + i + 1
        account_id = random.choice(df['account_id'].unique())
        product_id = random.choice(df['product_id'].unique())
        
        # 설치일 (최근 30일 내)
        install_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        
        # 보증 만료일 (1-3년 후)
        warranty_end = (datetime.strptime(install_date, '%Y-%m-%d') + timedelta(days=random.randint(365, 1095))).strftime('%Y-%m-%d')
        
        # 상태 분포 (기존 패턴 유지)
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
    
    # 기존 데이터와 새 데이터 합치기
    new_df = pd.DataFrame(new_installs)
    result_df = pd.concat([df, new_df], ignore_index=True)
    return result_df

def generate_bids_data(sample_data, date_str):
    """bids 데이터 생성 (새로운 입찰 추가)"""
    if 'bids' not in sample_data:
        return None
    
    df = sample_data['bids'].copy()
    
    # 새로운 입찰 생성 (1-4개)
    new_bids = []
    num_new = random.randint(1, 4)
    
    for i in range(num_new):
        bid_id = df['bid_id'].max() + i + 1
        account_id = random.choice(df['account_id'].unique())
        
        # 입찰 마감일 (7-60일 후)
        bid_due_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=random.randint(7, 60))).strftime('%Y-%m-%d')
        
        # 입찰 상태 분포 (기존 패턴 유지)
        status_weights = {'won': 0.333, 'lost': 0.25, 'submitted': 0.208, 'planned': 0.208}
        bid_status = np.random.choice(list(status_weights.keys()), p=list(status_weights.values()))
        
        # 예상 금액 (기존 분포 유지)
        est_amount = np.random.lognormal(9.0, 0.8)  # 평균 약 20,000원
        
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
    
    # 기존 데이터와 새 데이터 합치기
    new_df = pd.DataFrame(new_bids)
    result_df = pd.concat([df, new_df], ignore_index=True)
    return result_df

def generate_service_tickets_data(sample_data, date_str):
    """service_tickets 데이터 생성 (새로운 티켓 추가)"""
    if 'service_tickets' not in sample_data:
        return None
    
    df = sample_data['service_tickets'].copy()
    
    # 새로운 티켓 생성 (2-6개)
    new_tickets = []
    num_new = random.randint(2, 6)
    
    for i in range(num_new):
        ticket_id = df['ticket_id'].max() + i + 1
        account_id = random.choice(df['account_id'].unique())
        
        # 개설일 (최근 30일 내)
        opened_at = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        
        # 해결일 (개설일 + 1-14일)
        closed_at = (datetime.strptime(opened_at, '%Y-%m-%d') + timedelta(days=random.randint(1, 14))).strftime('%Y-%m-%d')
        
        # 심각도 분포 (기존 패턴 유지)
        severity_weights = {'P1': 0.091, 'P2': 0.398, 'P3': 0.511}
        severity = np.random.choice(list(severity_weights.keys()), p=list(severity_weights.values()))
        
        # 이슈 유형 분포 (기존 패턴 유지)
        issue_weights = {'Quality': 0.398, 'Training': 0.318, 'Delivery': 0.284}
        issue_type = np.random.choice(list(issue_weights.keys()), p=list(issue_weights.values()))
        
        new_ticket = {
            'ticket_id': ticket_id,
            'account_id': account_id,
            'product_id': 0,  # 기존 패턴 유지
            'opened_at': opened_at,
            'closed_at': closed_at,
            'severity': severity,
            'issue_type': issue_type
        }
        new_tickets.append(new_ticket)
    
    # 기존 데이터와 새 데이터 합치기
    new_df = pd.DataFrame(new_tickets)
    result_df = pd.concat([df, new_df], ignore_index=True)
    return result_df

def generate_web_events_data(sample_data, date_str):
    """web_events 데이터 생성 (새로운 웹 이벤트 추가)"""
    if 'web_events' not in sample_data:
        return None
    
    df = sample_data['web_events'].copy()
    
    # 새로운 웹 이벤트 생성 (5-15개)
    new_events = []
    num_new = random.randint(5, 15)
    
    for i in range(num_new):
        web_event_id = df['web_event_id'].max() + i + 1
        account_id = random.choice(df['account_id'].unique())
        
        # 이벤트 유형 (기존 패턴 유지)
        event_types = ['pageview', 'form_submit', 'webinar_signup']
        event_type = random.choice(event_types)
        
        # 발생일시 (최근 7일 내)
        occurred_at = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d %H:%M:%S')
        
        new_event = {
            'web_event_id': web_event_id,
            'account_id': account_id,
            'event_type': event_type,
            'url': 'https://example.com',  # 기존 패턴 유지
            'occurred_at': occurred_at
        }
        new_events.append(new_event)
    
    # 기존 데이터와 새 데이터 합치기
    new_df = pd.DataFrame(new_events)
    result_df = pd.concat([df, new_df], ignore_index=True)
    return result_df

def generate_data_for_date(sample_data, date_str):
    """특정 날짜에 대한 모든 데이터 생성"""
    data_generators = {
        'accounts': generate_accounts_data,
        'opportunities': generate_opportunities_data,
        'orders': generate_orders_data,
        'interactions': generate_interactions_data,
        'products': generate_products_data,
        'install_base': generate_install_base_data,
        'bids': generate_bids_data,
        'service_tickets': generate_service_tickets_data,
        'web_events': generate_web_events_data
    }
    
    generated_data = {}
    for table_name, generator_func in data_generators.items():
        try:
            generated_data[table_name] = generator_func(sample_data, date_str)
            print(f"Generated {table_name} data for {date_str}")
        except Exception as e:
            print(f"Error generating {table_name} data for {date_str}: {e}")
    
    return generated_data

def save_data_to_csv(generated_data, date_str):
    """생성된 데이터를 CSV 파일로 저장"""
    # 절대 경로 사용
    base_dir = os.path.dirname(__file__)
    date_dir = os.path.join(base_dir, "data", "landing", date_str)
    os.makedirs(date_dir, exist_ok=True)
    
    for table_name, df in generated_data.items():
        if df is not None:
            filename = f"{table_name}_{date_str}.csv"
            filepath = os.path.join(date_dir, filename)
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"Saved {filepath}")

def main():
    """메인 실행 함수"""
    print("데이터 확장 시작: 2025-09-10 ~ 2025-09-30")
    
    # 샘플 데이터 로드
    print("샘플 데이터 로드 중...")
    sample_data = load_sample_data()
    
    # 날짜 범위 생성
    dates = create_date_range()
    print(f"생성할 날짜: {len(dates)}일")
    
    # 각 날짜별로 데이터 생성 및 저장
    for date_str in dates:
        print(f"\n=== {date_str} 데이터 생성 중 ===")
        
        # 데이터 생성
        generated_data = generate_data_for_date(sample_data, date_str)
        
        # CSV 파일로 저장
        save_data_to_csv(generated_data, date_str)
        
        print(f"{date_str} 데이터 생성 완료")
    
    print(f"\n✅ 모든 데이터 생성 완료! ({len(dates)}일)")
    print("생성된 폴더들:")
    for date_str in dates:
        print(f"  - data/landing/{date_str}/")

if __name__ == "__main__":
    main()
