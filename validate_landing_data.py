#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import os
from datetime import datetime

def validate_landing_data():
    print("=== data/landing 폴더 데이터 현실성 검증 ===")
    print()
    
    dates = ['2025-09-07', '2025-09-08', '2025-09-09', '2025-09-10', '2025-09-11', 
             '2025-09-12', '2025-09-15', '2025-09-20', '2025-09-30']
    
    for date in dates:
        print(f"--- {date} 폴더 분석 ---")
        folder_path = f'data/landing/{date}'
        
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
            print(f"CSV 파일 수: {len(files)}")
            
            # accounts.csv 분석
            accounts_file = f'{folder_path}/accounts_{date}.csv'
            if os.path.exists(accounts_file):
                try:
                    df = pd.read_csv(accounts_file)
                    print(f"accounts 행 수: {len(df)}")
                    
                    if 'created_at' in df.columns:
                        created_dates = pd.to_datetime(df['created_at']).dt.date
                        print(f"created_at 범위: {created_dates.min()} ~ {created_dates.max()}")
                    
                    if 'updated_at' in df.columns:
                        updated_dates = pd.to_datetime(df['updated_at']).dt.date
                        print(f"updated_at 범위: {updated_dates.min()} ~ {updated_dates.max()}")
                except Exception as e:
                    print(f"accounts 파일 읽기 오류: {e}")
            
            # orders.csv 분석
            orders_file = f'{folder_path}/orders_{date}.csv'
            if os.path.exists(orders_file):
                try:
                    df = pd.read_csv(orders_file)
                    print(f"orders 행 수: {len(df)}")
                    
                    if 'order_date' in df.columns:
                        order_dates = pd.to_datetime(df['order_date']).dt.date
                        print(f"order_date 범위: {order_dates.min()} ~ {order_dates.max()}")
                except Exception as e:
                    print(f"orders 파일 읽기 오류: {e}")
            
            # interactions.csv 분석
            interactions_file = f'{folder_path}/interactions_{date}.csv'
            if os.path.exists(interactions_file):
                try:
                    df = pd.read_csv(interactions_file)
                    print(f"interactions 행 수: {len(df)}")
                    
                    if 'occurred_at' in df.columns:
                        interaction_dates = pd.to_datetime(df['occurred_at']).dt.date
                        print(f"occurred_at 범위: {interaction_dates.min()} ~ {interaction_dates.max()}")
                except Exception as e:
                    print(f"interactions 파일 읽기 오류: {e}")
            
            # opportunities.csv 분석
            opportunities_file = f'{folder_path}/opportunities_{date}.csv'
            if os.path.exists(opportunities_file):
                try:
                    df = pd.read_csv(opportunities_file)
                    print(f"opportunities 행 수: {len(df)}")
                    
                    if 'created_at' in df.columns:
                        opp_created = pd.to_datetime(df['created_at']).dt.date
                        print(f"opportunities created_at 범위: {opp_created.min()} ~ {opp_created.max()}")
                except Exception as e:
                    print(f"opportunities 파일 읽기 오류: {e}")
            
            print()
        else:
            print(f"{date} 폴더가 존재하지 않음")
            print()

if __name__ == "__main__":
    validate_landing_data()
