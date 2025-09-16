#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Power BI용 SQLite 데이터 연결 도우미
"""
import sqlite3
import pandas as pd
import os

def _apply_python_side_transformations(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Power Query에서 하던 경량 전처리를 Python에서 수행한다.

    - accounts: 기관규모 계산 컬럼 추가 (bed_count 기반)
    - bi_scores_daily: 스코어등급 계산 컬럼 추가 (p_win_90d 기반)
    - 날짜/시간 컬럼들은 ISO 문자열로 일관화
    """
    if table_name == 'accounts' and not df.empty:
        # 안전한 형변환 후 기관 규모 범주화
        if 'bed_count' in df.columns:
            df['bed_count'] = pd.to_numeric(df['bed_count'], errors='coerce')
            df['기관규모'] = pd.cut(
                df['bed_count'],
                bins=[-float('inf'), 49, 199, float('inf')],
                labels=['소형', '중형', '대형']
            ).astype(str)
        # 날짜/시간 열 일관화
        for col in ['created_at', 'updated_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

    if table_name == 'bi_scores_daily' and not df.empty:
        if 'p_win_90d' in df.columns:
            df['p_win_90d'] = pd.to_numeric(df['p_win_90d'], errors='coerce')
            df['스코어등급'] = pd.cut(
                df['p_win_90d'],
                bins=[-float('inf'), 0.4, 0.7, float('inf')],
                labels=['C', 'B', 'A']
            ).astype(str)
        for col in ['run_date', 't0_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')

    # 경량 타입 표준화: 날짜/시간으로 보이는 컬럼은 ISO 문자열로
    datetime_like_cols = [c for c in df.columns if c.endswith('_date') or c.endswith('_at')]
    for col in datetime_like_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

    return df


def export_for_powerbi(db_path, output_dir="powerbi_data", create_excel: bool = True, create_csv: bool = True):
    """SQLite 데이터를 Power BI에서 사용할 수 있는 형태로 내보내기.

    - CSV: 테이블별 파일 생성
    - Excel: 단일 통합 파일에 시트로 저장 (옵션)
    - Power Query 없이 바로 시각화가 가능하도록 경량 전처리 포함
    """
    
    if not os.path.exists(db_path):
        print(f"오류: 데이터베이스 파일이 존재하지 않습니다: {db_path}")
        return False
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    con = sqlite3.connect(db_path)
    
    try:
        # Power BI용 테이블들 내보내기
        tables_to_export = [
            'bi_scores_daily',
            'bi_opportunities', 
            'bi_orders',
            'accounts',
            'products',
            'interactions',
            'orders',
            'opportunities'
        ]
        
        # Excel 작성기 준비 (옵션)
        excel_path = os.path.join(output_dir, 'ivd_powerbi_data.xlsx') if create_excel else None
        excel_writer = pd.ExcelWriter(excel_path, engine='openpyxl') if create_excel else None

        for table in tables_to_export:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table}", con)
                df = _apply_python_side_transformations(table, df)
                if not df.empty:
                    if create_csv:
                        output_file = os.path.join(output_dir, f"{table}.csv")
                        df.to_csv(output_file, index=False, encoding='utf-8-sig')
                        print(f"✓ {table} → {output_file} ({len(df)} 행)")
                    if excel_writer is not None:
                        # 시트 이름은 31자 제한 대응 위해 잘라냄
                        sheet_name = table[:31]
                        df.to_excel(excel_writer, sheet_name=sheet_name, index=False)
                else:
                    print(f"⚠ {table} 테이블이 비어있습니다")
            except Exception as e:
                print(f"✗ {table} 내보내기 실패: {e}")
        
        if excel_writer is not None:
            try:
                excel_writer.close()
                print(f"✓ Excel 통합 파일 생성 → {excel_path}")
            except Exception as e:
                print(f"✗ Excel 파일 저장 실패: {e}")
        
        print(f"\n모든 데이터가 {output_dir} 폴더에 저장되었습니다.")
        if excel_path:
            print("Power BI에서 Excel 파일(시트 다중) 또는 CSV들을 바로 불러오세요.")
        else:
            print("Power BI에서 이 CSV 파일들을 불러오세요.")
        
        return True
        
    except Exception as e:
        print(f"오류: {e}")
        return False
    finally:
        con.close()

def create_powerbi_connection_string(db_path):
    """Power BI 연결 문자열 생성"""
    return f"Data Source={os.path.abspath(db_path)};Version=3;"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "build/ivd.db"
    
    print("Power BI용 데이터 내보내기 시작...")
    success = export_for_powerbi(db_path)
    
    if success:
        print("\n연결 문자열:")
        print(create_powerbi_connection_string(db_path))
    else:
        print("내보내기 실패")
        sys.exit(1)

