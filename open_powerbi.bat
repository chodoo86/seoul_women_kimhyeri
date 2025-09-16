@echo off
chcp 65001 >nul
echo ========================================
echo Power BI용 데이터 내보내기
echo ========================================
echo.

REM 가상환경 활성화
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo 오류: 가상환경이 설정되지 않았습니다.
    pause
    exit /b 1
)

REM 데이터베이스 존재 확인
if not exist "build\ivd.db" (
    echo 오류: build\ivd.db 파일이 존재하지 않습니다.
    echo 먼저 run_full_pipeline.bat을 실행해주세요.
    pause
    exit /b 1
)

echo Power BI용 데이터를 내보내는 중...
python src/utils/powerbi_connector.py build/ivd.db

if %errorlevel% neq 0 (
    echo 오류: 데이터 내보내기 실패
    pause
    exit /b 1
)

echo.
echo ========================================
echo Power BI용 데이터 내보내기 완료!
echo ========================================
echo.
echo 생성된 파일들:
echo - powerbi_data\bi_scores_daily.csv
echo - powerbi_data\bi_opportunities.csv
echo - powerbi_data\bi_orders.csv
echo - powerbi_data\accounts.csv
echo - powerbi_data\products.csv
echo - powerbi_data\interactions.csv
echo - powerbi_data\orders.csv
echo - powerbi_data\opportunities.csv
echo.
echo Power BI에서 이 파일들을 불러오세요:
echo 1. Power BI Desktop 실행
echo 2. "데이터 가져오기" → "텍스트/CSV" 선택
echo 3. powerbi_data 폴더의 원하는 CSV 파일 선택
echo 4. "로드" 클릭
echo.

REM powerbi_data 폴더 열기
start "" "powerbi_data"

pause
