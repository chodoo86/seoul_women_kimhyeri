@echo off
chcp 65001 >nul
echo ========================================
echo IVD Lead Scoring 전체 파이프라인 실행
echo ========================================
echo.

REM 가상환경 활성화
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo 오류: 가상환경이 설정되지 않았습니다.
    echo 먼저 setup_environment.bat을 실행해주세요.
    pause
    exit /b 1
)

echo [1/6] 데이터베이스 생성 중...
python -c "import sqlite3, os; os.makedirs('build', exist_ok=True); sqlite3.connect('build/ivd.db').close()"
if %errorlevel% neq 0 (
    echo 오류: 데이터베이스 파일 생성 실패
    pause
    exit /b 1
)

python -c "import sqlite3, pathlib; sql = pathlib.Path('sql/ddl.sql').read_text(encoding='utf-8'); con = sqlite3.connect('build/ivd.db'); con.executescript(sql); con.close()"
if %errorlevel% neq 0 (
    echo 오류: 데이터베이스 테이블 생성 실패
    pause
    exit /b 1
)
echo ✓ 데이터베이스 생성 완료

echo.
echo [2/6] 데이터 수집 중...
python src/pipelines/ingest.py --db build/ivd.db --landing data/landing
if %errorlevel% neq 0 (
    echo 오류: 데이터 수집 실패
    echo data/landing 폴더에 CSV 파일들이 있는지 확인해주세요.
    pause
    exit /b 1
)
echo ✓ 데이터 수집 완료

echo.
echo [3/6] 특성 생성 중...
python src/pipelines/ingest.py --db build/ivd.db --transform-sql sql/transform.sql
if %errorlevel% neq 0 (
    echo 오류: 특성 생성 실패
    echo sql/transform.sql 파일을 확인해주세요.
    pause
    exit /b 1
)
echo ✓ 특성 생성 완료

echo.
echo [4/6] 모델 재훈련 중...
python src/pipelines/score.py --db build/ivd.db --mode retrain
if %errorlevel% neq 0 (
    echo 오류: 모델 재훈련 실패
    echo 필요한 패키지가 설치되어 있는지 확인해주세요.
    pause
    exit /b 1
)
echo ✓ 모델 재훈련 완료

echo.
echo [5/6] 일일 스코어링 중...
python src/pipelines/score.py --db build/ivd.db --mode score
if %errorlevel% neq 0 (
    echo 오류: 스코어링 실패
    pause
    exit /b 1
)
echo ✓ 일일 스코어링 완료

echo.
echo [6/6] BI 데이터 내보내기 중...
python -c "from src.utils.powerbi_connector import export_for_powerbi; export_for_powerbi('build/ivd.db', output_dir='power_data', create_excel=True, create_csv=False)" 
if %errorlevel% neq 0 (
    echo 오류: 내보내기 실패
    pause
    exit /b 1
)
echo ✓ BI 데이터 내보내기 완료

echo.
echo ========================================
echo 모든 파이프라인이 성공적으로 완료되었습니다!
echo ========================================
echo.
echo 생성된 파일들:
echo - build/ivd.db (SQLite 데이터베이스)
echo - exports/ (Power BI용 CSV 파일들)
echo - src/models/ (훈련된 ML 모델들)
echo.
echo Power BI에서 build/ivd.db에 연결하여 대시보드를 확인하세요.
echo.
echo 다음 단계:
echo 1. Power BI Desktop 실행
echo 2. "데이터 가져오기" → "SQL Server" 선택
echo 3. "고급 옵션" → "SQL 문"에 "SELECT * FROM bi_scores_daily" 입력
echo 4. build/ivd.db 파일 경로를 데이터 소스로 설정
echo.
pause

