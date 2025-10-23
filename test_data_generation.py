#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
데이터 생성 테스트 스크립트
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 시드 설정
np.random.seed(42)
random.seed(42)

def create_test_data():
    """테스트용 간단한 데이터 생성"""
    
    # 2025-09-10 데이터 생성
    date_str = "2025-09-10"
    
    # accounts 데이터 (기존 패턴 유지)
    accounts_data = {
        'account_id': [1, 2, 3, 4, 5],
        'account_name': ['기관_001', '기관_002', '기관_003', '기관_004', '기관_005'],
        'account_type': ['검사실', '의원', '병원', '검진센터', '검사실'],
        'bed_count': [260, 150, 300, 80, 200],
        'annual_test_volume': [167028, 120000, 180000, 80000, 150000],
        'city': ['Incheon', 'Seoul', 'Busan', 'Seongnam', 'Daegu'],
        'state_region': ['Gyeonggi', 'Seoul', 'Busan', 'Seoul', 'Daegu'],
        'country': ['Korea', 'Korea', 'Korea', 'Korea', 'Korea'],
        'ownership_type': ['민영', '민영', '공공', '민영', '공공'],
        'created_at': ['2023-09-14', '2022-01-15', '2021-03-20', '2024-05-10', '2023-11-30'],
        'updated_at': [date_str, date_str, date_str, date_str, date_str]
    }
    
    # opportunities 데이터 (새로운 기회 추가)
    opportunities_data = {
        'opportunity_id': [1, 2, 3, 4, 5],
        'account_id': [1, 2, 3, 4, 5],
        'stage': ['MQL', 'SQL', 'POC', 'Negotiation', 'ClosedWon'],
        'expected_close_date': ['2025-12-10', '2025-11-15', '2025-10-30', '2025-10-15', '2025-09-20'],
        'amount_expected': [25000.0, 18000.0, 32000.0, 15000.0, 28000.0],
        'source': ['Bid', 'Outbound', 'Webinar', 'Inbound', 'Bid'],
        'created_at': ['2025-08-10', '2025-08-15', '2025-08-20', '2025-08-25', '2025-08-30'],
        'closed_at': ['', '', '', '', '2025-09-15']
    }
    
    # orders 데이터 (새로운 주문 추가)
    orders_data = {
        'order_id': [1, 2, 3, 4, 5],
        'account_id': [1, 2, 3, 4, 5],
        'order_date': ['2025-09-05', '2025-09-08', '2025-09-09', '2025-09-10', '2025-09-10'],
        'total_amount': [5500.0, 7200.0, 4800.0, 6200.0, 8900.0]
    }
    
    # interactions 데이터 (새로운 상호작용 추가)
    interactions_data = {
        'interaction_id': [1, 2, 3, 4, 5],
        'account_id': [1, 2, 3, 4, 5],
        'contact_id': [0, 0, 0, 0, 0],
        'channel': ['demo', 'webinar', 'visit', 'email', 'call'],
        'outcome': ['positive', 'neutral', 'positive', 'negative', 'positive'],
        'occurred_at': ['2025-09-10 10:30:00', '2025-09-10 14:15:00', '2025-09-10 16:45:00', '2025-09-10 09:20:00', '2025-09-10 11:10:00']
    }
    
    # products 데이터 (변경 없음)
    products_data = {
        'product_id': [1, 2, 3, 4, 5],
        'product_name': ['AlphaDx Analyzer A', 'BioCore Reagent B', 'MedLabs Control C', 'AlphaDx Reagent D', 'BioCore Analyzer E'],
        'product_type': ['Analyzer', 'Reagent', 'Control', 'Reagent', 'Analyzer'],
        'brand': ['AlphaDx', 'BioCore', 'MedLabs', 'AlphaDx', 'BioCore'],
        'requires_install': [1, 0, 0, 0, 1],
        'list_price': [50000.0, 500.0, 600.0, 400.0, 45000.0]
    }
    
    # install_base 데이터 (새로운 설치 추가)
    install_base_data = {
        'install_id': [1, 2, 3, 4, 5],
        'account_id': [1, 2, 3, 4, 5],
        'product_id': [1, 2, 3, 4, 5],
        'install_date': ['2025-09-05', '2025-09-08', '2025-09-09', '2025-09-10', '2025-09-10'],
        'warranty_end': ['2026-09-05', '2026-09-08', '2026-09-09', '2026-09-10', '2026-09-10'],
        'status': ['active', 'active', 'inactive', 'active', 'active']
    }
    
    # bids 데이터 (새로운 입찰 추가)
    bids_data = {
        'bid_id': [1, 2, 3, 4, 5],
        'account_id': [1, 2, 3, 4, 5],
        'bid_due_date': ['2025-10-10', '2025-10-15', '2025-10-20', '2025-10-25', '2025-10-30'],
        'bid_status': ['submitted', 'planned', 'won', 'lost', 'submitted'],
        'est_amount': [30000.0, 25000.0, 35000.0, 20000.0, 28000.0],
        'created_at': ['2025-09-05', '2025-09-08', '2025-09-09', '2025-09-10', '2025-09-10']
    }
    
    # service_tickets 데이터 (새로운 티켓 추가)
    service_tickets_data = {
        'ticket_id': [1, 2, 3, 4, 5],
        'account_id': [1, 2, 3, 4, 5],
        'product_id': [0, 0, 0, 0, 0],
        'opened_at': ['2025-09-05', '2025-09-08', '2025-09-09', '2025-09-10', '2025-09-10'],
        'closed_at': ['2025-09-07', '2025-09-10', '2025-09-11', '2025-09-12', '2025-09-13'],
        'severity': ['P2', 'P3', 'P1', 'P2', 'P3'],
        'issue_type': ['Quality', 'Training', 'Delivery', 'Quality', 'Training']
    }
    
    # web_events 데이터 (새로운 웹 이벤트 추가)
    web_events_data = {
        'web_event_id': [1, 2, 3, 4, 5],
        'account_id': [1, 2, 3, 4, 5],
        'event_type': ['pageview', 'form_submit', 'webinar_signup', 'pageview', 'form_submit'],
        'url': ['https://example.com', 'https://example.com', 'https://example.com', 'https://example.com', 'https://example.com'],
        'occurred_at': ['2025-09-10 09:00:00', '2025-09-10 10:30:00', '2025-09-10 14:15:00', '2025-09-10 16:45:00', '2025-09-10 18:20:00']
    }
    
    # 데이터프레임 생성
    dataframes = {
        'accounts': pd.DataFrame(accounts_data),
        'opportunities': pd.DataFrame(opportunities_data),
        'orders': pd.DataFrame(orders_data),
        'interactions': pd.DataFrame(interactions_data),
        'products': pd.DataFrame(products_data),
        'install_base': pd.DataFrame(install_base_data),
        'bids': pd.DataFrame(bids_data),
        'service_tickets': pd.DataFrame(service_tickets_data),
        'web_events': pd.DataFrame(web_events_data)
    }
    
    return dataframes, date_str

def save_test_data(dataframes, date_str):
    """테스트 데이터를 CSV 파일로 저장"""
    # 절대 경로 사용
    base_dir = os.path.dirname(__file__)
    date_dir = os.path.join(base_dir, "data", "landing", date_str)
    os.makedirs(date_dir, exist_ok=True)
    
    for table_name, df in dataframes.items():
        filename = f"{table_name}_{date_str}.csv"
        filepath = os.path.join(date_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"Saved {filepath}")

def main():
    """메인 실행 함수"""
    print("테스트 데이터 생성 시작...")
    
    # 테스트 데이터 생성
    dataframes, date_str = create_test_data()
    
    # CSV 파일로 저장
    save_test_data(dataframes, date_str)
    
    print(f"✅ 테스트 데이터 생성 완료! ({date_str})")
    print(f"생성된 폴더: data/landing/{date_str}/")

if __name__ == "__main__":
    main()
