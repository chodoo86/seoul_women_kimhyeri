#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IVD Lead Scoring 데이터 시각화 분석 스크립트
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
import matplotlib.font_manager as fm
import os
import matplotlib

# Windows에서 사용 가능한 한글 폰트 찾기
def find_korean_font():
    """사용 가능한 한글 폰트 찾기"""
    # Windows 기본 한글 폰트들 (우선순위 순)
    font_list = [
        'Malgun Gothic',  # Windows 10/11 기본 한글 폰트
        'Microsoft YaHei',  # 중국어이지만 한글 지원
        'SimHei',  # 중국어이지만 한글 지원
        'Arial Unicode MS',  # 유니코드 지원
        'DejaVu Sans'  # 기본 폰트
    ]
    
    # 시스템에 설치된 폰트 목록 가져오기
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    for font in font_list:
        if font in available_fonts:
            return font
    
    # 폰트를 찾지 못한 경우 기본 폰트 사용
    return 'DejaVu Sans'

# 한글 폰트 설정
korean_font = find_korean_font()
plt.rcParams['font.family'] = korean_font
plt.rcParams['axes.unicode_minus'] = False

# matplotlib 캐시 클리어 (옵션)
try:
    matplotlib.font_manager._rebuild()
except AttributeError:
    # _rebuild 메서드가 없는 경우 무시
    pass

# 인코딩 설정
os.environ['PYTHONIOENCODING'] = 'utf-8'

print(f"사용 중인 폰트: {korean_font}")

# 폰트 테스트
try:
    fig, ax = plt.subplots(figsize=(1, 1))
    ax.text(0.5, 0.5, '한글 테스트', ha='center', va='center')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.close(fig)
    print("한글 폰트 테스트 성공")
except Exception as e:
    print(f"한글 폰트 테스트 실패: {e}")

def load_data():
    """데이터 로드"""
    data = {}
    
    # CSV 파일들 로드
    files = {
        'accounts': 'data/samples/accounts.csv',
        'opportunities': 'data/samples/opportunities.csv',
        'orders': 'data/samples/orders.csv',
        'interactions': 'data/samples/interactions.csv',
        'products': 'data/samples/products.csv',
        'install_base': 'data/samples/install_base.csv',
        'bids': 'data/samples/bids.csv',
        'service_tickets': 'data/samples/service_tickets.csv',
        'web_events': 'data/samples/web_events.csv'
    }
    
    for name, file_path in files.items():
        try:
            data[name] = pd.read_csv(file_path)
            print(f"[OK] {name}: {len(data[name])} rows loaded")
        except Exception as e:
            print(f"[ERROR] {name}: Error loading - {e}")
    
    return data

def analyze_accounts(data):
    """고객 기관 분석"""
    df = data['accounts']
    
    # 1. 기관 유형별 분포
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 3, 1)
    account_type_counts = df['account_type'].value_counts()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    plt.pie(account_type_counts.values, labels=account_type_counts.index, autopct='%1.1f%%', colors=colors)
    plt.title('기관 유형별 분포', fontsize=14, fontweight='bold')
    
    # 2. 지역별 분포
    plt.subplot(2, 3, 2)
    city_counts = df['city'].value_counts().head(8)
    plt.bar(range(len(city_counts)), city_counts.values, color='#FF9F43')
    plt.xticks(range(len(city_counts)), city_counts.index, rotation=45)
    plt.title('주요 도시별 기관 수', fontsize=14, fontweight='bold')
    plt.ylabel('기관 수')
    
    # 3. 병상 수 분포
    plt.subplot(2, 3, 3)
    plt.hist(df['bed_count'], bins=20, color='#6C5CE7', alpha=0.7, edgecolor='black')
    plt.title('병상 수 분포', fontsize=14, fontweight='bold')
    plt.xlabel('병상 수')
    plt.ylabel('빈도')
    
    # 4. 연간 검사량 분포
    plt.subplot(2, 3, 4)
    plt.hist(df['annual_test_volume'], bins=20, color='#00B894', alpha=0.7, edgecolor='black')
    plt.title('연간 검사량 분포', fontsize=14, fontweight='bold')
    plt.xlabel('연간 검사량')
    plt.ylabel('빈도')
    
    # 5. 소유 형태별 분포
    plt.subplot(2, 3, 5)
    ownership_counts = df['ownership_type'].value_counts()
    plt.pie(ownership_counts.values, labels=ownership_counts.index, autopct='%1.1f%%', 
            colors=['#FF7675', '#74B9FF'])
    plt.title('소유 형태별 분포', fontsize=14, fontweight='bold')
    
    # 6. 기관 유형별 평균 병상 수
    plt.subplot(2, 3, 6)
    type_bed_avg = df.groupby('account_type')['bed_count'].mean()
    plt.bar(range(len(type_bed_avg)), type_bed_avg.values, color='#A29BFE')
    plt.xticks(range(len(type_bed_avg)), type_bed_avg.index, rotation=45)
    plt.title('기관 유형별 평균 병상 수', fontsize=14, fontweight='bold')
    plt.ylabel('평균 병상 수')
    
    plt.tight_layout()
    plt.savefig('account_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def analyze_opportunities(data):
    """영업 기회 분석"""
    df = data['opportunities']
    
    # 날짜 컬럼 변환
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['expected_close_date'] = pd.to_datetime(df['expected_close_date'])
    
    plt.figure(figsize=(15, 10))
    
    # 1. 영업 단계별 분포
    plt.subplot(2, 3, 1)
    stage_counts = df['stage'].value_counts()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FDCB6E', '#E17055']
    plt.pie(stage_counts.values, labels=stage_counts.index, autopct='%1.1f%%', colors=colors)
    plt.title('영업 단계별 분포', fontsize=14, fontweight='bold')
    
    # 2. 유입 경로별 분포
    plt.subplot(2, 3, 2)
    source_counts = df['source'].value_counts()
    plt.bar(range(len(source_counts)), source_counts.values, color='#00B894')
    plt.xticks(range(len(source_counts)), source_counts.index, rotation=45)
    plt.title('유입 경로별 분포', fontsize=14, fontweight='bold')
    plt.ylabel('기회 수')
    
    # 3. 예상 거래금액 분포
    plt.subplot(2, 3, 3)
    plt.hist(df['amount_expected'], bins=20, color='#6C5CE7', alpha=0.7, edgecolor='black')
    plt.title('예상 거래금액 분포', fontsize=14, fontweight='bold')
    plt.xlabel('예상 거래금액')
    plt.ylabel('빈도')
    
    # 4. 월별 기회 생성 추이
    plt.subplot(2, 3, 4)
    df['created_month'] = df['created_at'].dt.to_period('M')
    monthly_opps = df['created_month'].value_counts().sort_index()
    plt.plot(range(len(monthly_opps)), monthly_opps.values, marker='o', color='#E17055', linewidth=2)
    plt.title('월별 기회 생성 추이', fontsize=14, fontweight='bold')
    plt.xlabel('월')
    plt.ylabel('기회 수')
    plt.xticks(range(len(monthly_opps)), [str(x) for x in monthly_opps.index], rotation=45)
    
    # 5. 유입 경로별 평균 금액
    plt.subplot(2, 3, 5)
    source_amount = df.groupby('source')['amount_expected'].mean()
    plt.bar(range(len(source_amount)), source_amount.values, color='#A29BFE')
    plt.xticks(range(len(source_amount)), source_amount.index, rotation=45)
    plt.title('유입 경로별 평균 금액', fontsize=14, fontweight='bold')
    plt.ylabel('평균 금액')
    
    # 6. 영업 단계별 평균 금액
    plt.subplot(2, 3, 6)
    stage_amount = df.groupby('stage')['amount_expected'].mean()
    plt.bar(range(len(stage_amount)), stage_amount.values, color='#FD79A8')
    plt.xticks(range(len(stage_amount)), stage_amount.index, rotation=45)
    plt.title('영업 단계별 평균 금액', fontsize=14, fontweight='bold')
    plt.ylabel('평균 금액')
    
    plt.tight_layout()
    plt.savefig('opportunity_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def analyze_interactions(data):
    """고객 상호작용 분석"""
    df = data['interactions']
    
    # 날짜 컬럼 변환
    df['occurred_at'] = pd.to_datetime(df['occurred_at'])
    
    plt.figure(figsize=(15, 10))
    
    # 1. 채널별 상호작용 분포
    plt.subplot(2, 3, 1)
    channel_counts = df['channel'].value_counts()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FDCB6E']
    plt.pie(channel_counts.values, labels=channel_counts.index, autopct='%1.1f%%', colors=colors)
    plt.title('채널별 상호작용 분포', fontsize=14, fontweight='bold')
    
    # 2. 상호작용 결과 분포
    plt.subplot(2, 3, 2)
    outcome_counts = df['outcome'].value_counts()
    colors = ['#00B894', '#FDCB6E', '#E17055']
    plt.pie(outcome_counts.values, labels=outcome_counts.index, autopct='%1.1f%%', colors=colors)
    plt.title('상호작용 결과 분포', fontsize=14, fontweight='bold')
    
    # 3. 월별 상호작용 추이
    plt.subplot(2, 3, 3)
    df['occurred_month'] = df['occurred_at'].dt.to_period('M')
    monthly_interactions = df['occurred_month'].value_counts().sort_index()
    plt.plot(range(len(monthly_interactions)), monthly_interactions.values, marker='o', color='#6C5CE7', linewidth=2)
    plt.title('월별 상호작용 추이', fontsize=14, fontweight='bold')
    plt.xlabel('월')
    plt.ylabel('상호작용 수')
    plt.xticks(range(len(monthly_interactions)), [str(x) for x in monthly_interactions.index], rotation=45)
    
    # 4. 채널별 결과 분석
    plt.subplot(2, 3, 4)
    channel_outcome = pd.crosstab(df['channel'], df['outcome'])
    channel_outcome.plot(kind='bar', stacked=True, color=['#00B894', '#FDCB6E', '#E17055'])
    plt.title('채널별 상호작용 결과', fontsize=14, fontweight='bold')
    plt.xlabel('채널')
    plt.ylabel('상호작용 수')
    plt.legend(title='결과')
    plt.xticks(rotation=45)
    
    # 5. 고객별 상호작용 수 분포
    plt.subplot(2, 3, 5)
    customer_interactions = df['account_id'].value_counts()
    plt.hist(customer_interactions.values, bins=20, color='#A29BFE', alpha=0.7, edgecolor='black')
    plt.title('고객별 상호작용 수 분포', fontsize=14, fontweight='bold')
    plt.xlabel('상호작용 수')
    plt.ylabel('고객 수')
    
    # 6. 시간대별 상호작용 패턴
    plt.subplot(2, 3, 6)
    df['hour'] = df['occurred_at'].dt.hour
    hourly_interactions = df['hour'].value_counts().sort_index()
    plt.plot(hourly_interactions.index, hourly_interactions.values, marker='o', color='#E17055', linewidth=2)
    plt.title('시간대별 상호작용 패턴', fontsize=14, fontweight='bold')
    plt.xlabel('시간')
    plt.ylabel('상호작용 수')
    
    plt.tight_layout()
    plt.savefig('interaction_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def analyze_orders(data):
    """주문 패턴 분석"""
    df = data['orders']
    
    # 날짜 컬럼 변환
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    plt.figure(figsize=(15, 10))
    
    # 1. 월별 주문 추이
    plt.subplot(2, 3, 1)
    df['order_month'] = df['order_date'].dt.to_period('M')
    monthly_orders = df['order_month'].value_counts().sort_index()
    plt.plot(range(len(monthly_orders)), monthly_orders.values, marker='o', color='#00B894', linewidth=2)
    plt.title('월별 주문 추이', fontsize=14, fontweight='bold')
    plt.xlabel('월')
    plt.ylabel('주문 수')
    plt.xticks(range(len(monthly_orders)), [str(x) for x in monthly_orders.index], rotation=45)
    
    # 2. 주문 금액 분포
    plt.subplot(2, 3, 2)
    plt.hist(df['total_amount'], bins=20, color='#6C5CE7', alpha=0.7, edgecolor='black')
    plt.title('주문 금액 분포', fontsize=14, fontweight='bold')
    plt.xlabel('주문 금액')
    plt.ylabel('빈도')
    
    # 3. 고객별 주문 수 분포
    plt.subplot(2, 3, 3)
    customer_orders = df['account_id'].value_counts()
    plt.hist(customer_orders.values, bins=20, color='#FF9F43', alpha=0.7, edgecolor='black')
    plt.title('고객별 주문 수 분포', fontsize=14, fontweight='bold')
    plt.xlabel('주문 수')
    plt.ylabel('고객 수')
    
    # 4. 고객별 총 주문 금액
    plt.subplot(2, 3, 4)
    customer_amount = df.groupby('account_id')['total_amount'].sum().sort_values(ascending=False).head(10)
    plt.bar(range(len(customer_amount)), customer_amount.values, color='#E17055')
    plt.title('상위 10개 고객별 총 주문 금액', fontsize=14, fontweight='bold')
    plt.xlabel('고객 순위')
    plt.ylabel('총 주문 금액')
    
    # 5. 주문 금액별 구간 분포
    plt.subplot(2, 3, 5)
    amount_bins = [0, 2000, 5000, 10000, 20000, float('inf')]
    amount_labels = ['0-2K', '2K-5K', '5K-10K', '10K-20K', '20K+']
    df['amount_range'] = pd.cut(df['total_amount'], bins=amount_bins, labels=amount_labels)
    amount_range_counts = df['amount_range'].value_counts()
    plt.pie(amount_range_counts.values, labels=amount_range_counts.index, autopct='%1.1f%%')
    plt.title('주문 금액 구간별 분포', fontsize=14, fontweight='bold')
    
    # 6. 월별 평균 주문 금액
    plt.subplot(2, 3, 6)
    monthly_avg_amount = df.groupby('order_month')['total_amount'].mean()
    plt.plot(range(len(monthly_avg_amount)), monthly_avg_amount.values, marker='o', color='#A29BFE', linewidth=2)
    plt.title('월별 평균 주문 금액', fontsize=14, fontweight='bold')
    plt.xlabel('월')
    plt.ylabel('평균 주문 금액')
    plt.xticks(range(len(monthly_avg_amount)), [str(x) for x in monthly_avg_amount.index], rotation=45)
    
    plt.tight_layout()
    plt.savefig('order_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def analyze_products(data):
    """제품 분석"""
    df = data['products']
    
    plt.figure(figsize=(15, 8))
    
    # 1. 브랜드별 제품 분포
    plt.subplot(2, 3, 1)
    brand_counts = df['brand'].value_counts()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    plt.pie(brand_counts.values, labels=brand_counts.index, autopct='%1.1f%%', colors=colors)
    plt.title('브랜드별 제품 분포', fontsize=14, fontweight='bold')
    
    # 2. 제품 유형별 분포
    plt.subplot(2, 3, 2)
    type_counts = df['product_type'].value_counts()
    colors = ['#96CEB4', '#FDCB6E']
    plt.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', colors=colors)
    plt.title('제품 유형별 분포', fontsize=14, fontweight='bold')
    
    # 3. 제품 가격 분포
    plt.subplot(2, 3, 3)
    plt.hist(df['list_price'], bins=15, color='#6C5CE7', alpha=0.7, edgecolor='black')
    plt.title('제품 가격 분포', fontsize=14, fontweight='bold')
    plt.xlabel('가격')
    plt.ylabel('빈도')
    
    # 4. 브랜드별 평균 가격
    plt.subplot(2, 3, 4)
    brand_price = df.groupby('brand')['list_price'].mean()
    plt.bar(range(len(brand_price)), brand_price.values, color='#00B894')
    plt.xticks(range(len(brand_price)), brand_price.index, rotation=45)
    plt.title('브랜드별 평균 가격', fontsize=14, fontweight='bold')
    plt.ylabel('평균 가격')
    
    # 5. 제품 유형별 가격 비교
    plt.subplot(2, 3, 5)
    type_price = df.groupby('product_type')['list_price'].mean()
    plt.bar(range(len(type_price)), type_price.values, color='#E17055')
    plt.xticks(range(len(type_price)), type_price.index, rotation=45)
    plt.title('제품 유형별 평균 가격', fontsize=14, fontweight='bold')
    plt.ylabel('평균 가격')
    
    # 6. 설치 필요 제품 비율
    plt.subplot(2, 3, 6)
    install_counts = df['requires_install'].value_counts()
    labels = ['설치 불필요', '설치 필요']
    colors = ['#A29BFE', '#FD79A8']
    plt.pie(install_counts.values, labels=labels, autopct='%1.1f%%', colors=colors)
    plt.title('설치 필요 제품 비율', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('product_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_summary_report(data):
    """요약 보고서 생성"""
    print("=" * 60)
    print("IVD Lead Scoring 데이터 분석 요약 보고서")
    print("=" * 60)
    
    # 기본 통계
    print(f"\n데이터 규모:")
    for name, df in data.items():
        print(f"  - {name}: {len(df):,} rows")
    
    # 고객 기관 요약
    accounts = data['accounts']
    print(f"\n고객 기관 요약:")
    print(f"  - 총 기관 수: {len(accounts):,}개")
    print(f"  - 평균 병상 수: {accounts['bed_count'].mean():.0f}개")
    print(f"  - 평균 연간 검사량: {accounts['annual_test_volume'].mean():,.0f}건")
    print(f"  - 주요 기관 유형: {accounts['account_type'].mode()[0]} ({accounts['account_type'].value_counts().iloc[0]}개)")
    
    # 영업 기회 요약
    opportunities = data['opportunities']
    print(f"\n영업 기회 요약:")
    print(f"  - 총 기회 수: {len(opportunities):,}개")
    print(f"  - 평균 예상 금액: {opportunities['amount_expected'].mean():,.0f}원")
    print(f"  - 성사율: {len(opportunities[opportunities['stage'] == 'ClosedWon']) / len(opportunities) * 100:.1f}%")
    print(f"  - 주요 유입 경로: {opportunities['source'].mode()[0]} ({opportunities['source'].value_counts().iloc[0]}개)")
    
    # 상호작용 요약
    interactions = data['interactions']
    print(f"\n고객 상호작용 요약:")
    print(f"  - 총 상호작용 수: {len(interactions):,}개")
    print(f"  - 평균 상호작용 수: {len(interactions) / len(accounts):.1f}회/고객")
    print(f"  - 긍정적 반응 비율: {len(interactions[interactions['outcome'] == 'positive']) / len(interactions) * 100:.1f}%")
    print(f"  - 주요 채널: {interactions['channel'].mode()[0]} ({interactions['channel'].value_counts().iloc[0]}개)")
    
    # 주문 요약
    orders = data['orders']
    print(f"\n주문 요약:")
    print(f"  - 총 주문 수: {len(orders):,}개")
    print(f"  - 평균 주문 금액: {orders['total_amount'].mean():,.0f}원")
    print(f"  - 총 매출: {orders['total_amount'].sum():,.0f}원")
    print(f"  - 평균 주문 수: {len(orders) / len(accounts):.1f}회/고객")
    
    print("\n" + "=" * 60)

def main():
    """메인 실행 함수"""
    print("IVD Lead Scoring 데이터 분석 시작...")
    
    # 데이터 로드
    data = load_data()
    
    if not data:
        print("데이터 로드 실패")
        return
    
    # 분석 실행
    print("\n고객 기관 분석 중...")
    analyze_accounts(data)
    
    print("영업 기회 분석 중...")
    analyze_opportunities(data)
    
    print("고객 상호작용 분석 중...")
    analyze_interactions(data)
    
    print("주문 패턴 분석 중...")
    analyze_orders(data)
    
    print("제품 분석 중...")
    analyze_products(data)
    
    # 요약 보고서 생성
    generate_summary_report(data)
    
    print("\n분석 완료! 그래프가 저장되었습니다.")

if __name__ == "__main__":
    main()
