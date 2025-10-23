#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
간단한 데이터 생성 스크립트: 2025-09-13 ~ 2025-09-30
"""

import os
from datetime import datetime, timedelta

# 생성할 날짜 리스트
dates = []
for day in range(13, 31):  # 13일부터 30일까지
    dates.append(f"2025-09-{day:02d}")

# 기본 템플릿 (2025-09-15 데이터 참고)
base_dir = os.path.dirname(os.path.abspath(__file__))

for date_str in dates:
    print(f"생성 중: {date_str}")
    
    # 날짜 폴더 생성
    date_dir = os.path.join(base_dir, "data", "landing", date_str)
    os.makedirs(date_dir, exist_ok=True)
    
    # 날짜에서 일(day) 추출
    day_num = int(date_str.split('-')[2])
    
    # accounts.csv
    with open(os.path.join(date_dir, f"accounts_{date_str}.csv"), 'w', encoding='utf-8') as f:
        f.write("account_id,account_name,account_type,bed_count,annual_test_volume,city,state_region,country,ownership_type,created_at,updated_at\n")
        for i in [1,6,37,46,14,55,34,49,13,58,47,51,32,4,53,18,9,7,41,5,44,20,35,59,26,57,16,28,10,31,27,17,25,56,12,33,54,42,38,30,45,2,22,3,48,40,36,24]:
            f.write(f"{i},기관_{i:03d},검사실,260,167028,Incheon,Gyeonggi,Korea,민영,2023-09-14,{date_str}\n")
    
    # opportunities.csv
    with open(os.path.join(date_dir, f"opportunities_{date_str}.csv"), 'w', encoding='utf-8') as f:
        f.write("opportunity_id,account_id,stage,expected_close_date,amount_expected,source,created_at,closed_at\n")
        base_opp_id = 77 + (day_num - 10) * 5
        for i in range(5):
            opp_id = base_opp_id + i
            account_id = [1,6,37,46,14][i]
            stage = ['MQL','SQL','POC','Negotiation','ClosedWon'][i]
            amount = 25000 + i * 1000
            f.write(f"{opp_id},{account_id},{stage},2025-12-{10+i:02d},{amount}.00,Bid,{date_str},\n")
    
    # orders.csv
    with open(os.path.join(date_dir, f"orders_{date_str}.csv"), 'w', encoding='utf-8') as f:
        f.write("order_id,account_id,order_date,total_amount\n")
        base_order_id = 281 + (day_num - 10) * 5
        for i in range(5):
            order_id = base_order_id + i
            account_id = [1,6,37,46,14][i]
            amount = 5500 + i * 100
            f.write(f"{order_id},{account_id},{date_str},{amount}.00\n")
    
    # products.csv (변경 없음)
    with open(os.path.join(date_dir, f"products_{date_str}.csv"), 'w', encoding='utf-8') as f:
        f.write("product_id,product_name,product_type,brand,requires_install,list_price\n")
        f.write("10,BioCore Control Z,Reagent,BioCore,0,660\n")
        f.write("12,MedLabs Analyzer B,Analyzer,MedLabs,1,69684\n")
        f.write("1,AlphaDx Analyzer A,Analyzer,AlphaDx,1,69039\n")
        f.write("14,MedLabs Reagent Y,Reagent,MedLabs,0,647\n")
        f.write("6,BioCore Analyzer A,Analyzer,BioCore,1,46870\n")
        f.write("9,BioCore Reagent Y,Reagent,BioCore,0,218\n")
        f.write("3,AlphaDx Reagent X,Reagent,AlphaDx,0,466\n")
        f.write("2,AlphaDx Analyzer B,Analyzer,AlphaDx,1,44224\n")
        f.write("15,MedLabs Control Z,Reagent,MedLabs,0,797\n")
        f.write("5,AlphaDx Control Z,Reagent,AlphaDx,0,606\n")
        f.write("8,BioCore Reagent X,Reagent,BioCore,0,771\n")
        f.write("11,MedLabs Analyzer A,Analyzer,MedLabs,1,60335\n")
    
    # interactions.csv
    with open(os.path.join(date_dir, f"interactions_{date_str}.csv"), 'w', encoding='utf-8') as f:
        f.write("interaction_id,account_id,contact_id,channel,outcome,occurred_at\n")
        base_int_id = 1 + (day_num - 10) * 5
        channels = ['demo','webinar','visit','email','call']
        outcomes = ['positive','neutral','positive','negative','positive']
        for i in range(5):
            int_id = base_int_id + i
            account_id = [1,6,37,46,14][i]
            f.write(f"{int_id},{account_id},0,{channels[i]},{outcomes[i]},{date_str} {10+i}:00:00\n")
    
    # install_base.csv
    with open(os.path.join(date_dir, f"install_base_{date_str}.csv"), 'w', encoding='utf-8') as f:
        f.write("install_id,account_id,product_id,install_date,warranty_end,status\n")
        base_install_id = 1 + (day_num - 10) * 3
        for i in range(3):
            install_id = base_install_id + i
            account_id = [1,6,37][i]
            product_id = i + 1
            warranty_date = datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=365)
            f.write(f"{install_id},{account_id},{product_id},{date_str},{warranty_date.strftime('%Y-%m-%d')},active\n")
    
    # bids.csv
    with open(os.path.join(date_dir, f"bids_{date_str}.csv"), 'w', encoding='utf-8') as f:
        f.write("bid_id,account_id,bid_due_date,bid_status,est_amount,created_at\n")
        base_bid_id = 1 + (day_num - 10) * 2
        for i in range(2):
            bid_id = base_bid_id + i
            account_id = [1,6][i]
            due_date = datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=30+i*5)
            amount = 30000 + i * 1000
            f.write(f"{bid_id},{account_id},{due_date.strftime('%Y-%m-%d')},submitted,{amount}.00,{date_str}\n")
    
    # service_tickets.csv
    with open(os.path.join(date_dir, f"service_tickets_{date_str}.csv"), 'w', encoding='utf-8') as f:
        f.write("ticket_id,account_id,product_id,opened_at,closed_at,severity,issue_type\n")
        base_ticket_id = 1 + (day_num - 10) * 2
        for i in range(2):
            ticket_id = base_ticket_id + i
            account_id = [1,6][i]
            closed_date = datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=2+i)
            severity = ['P2','P3'][i]
            issue_type = ['Quality','Training'][i]
            f.write(f"{ticket_id},{account_id},0,{date_str},{closed_date.strftime('%Y-%m-%d')},{severity},{issue_type}\n")
    
    # web_events.csv
    with open(os.path.join(date_dir, f"web_events_{date_str}.csv"), 'w', encoding='utf-8') as f:
        f.write("web_event_id,account_id,event_type,url,occurred_at\n")
        base_event_id = 1 + (day_num - 10) * 2
        for i in range(2):
            event_id = base_event_id + i
            account_id = [1,6][i]
            event_type = ['pageview','form_submit'][i]
            f.write(f"{event_id},{account_id},{event_type},https://example.com,{date_str} {10+i*4}:00:00\n")

print(f"\n✅ 모든 데이터 생성 완료! ({len(dates)}일)")
print("생성된 폴더들:")
for date_str in dates:
    print(f"  - data/landing/{date_str}/")

