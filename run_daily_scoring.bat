@echo off
chcp 65001 >nul
echo ========================================
echo IVD 일일 스코어링 실행
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

REM 데이터베이스 존재 확인
if not exist "build/ivd.db" (
    echo 오류: 데이터베이스가 존재하지 않습니다.
    echo 먼저 run_full_pipeline.bat을 실행하여 초기 설정을 완료해주세요.
    pause
    exit /b 1
)

echo [1/4] 데이터 수집 중...
python src/pipelines/ingest.py --db build/ivd.db --landing data/landing
if %errorlevel% neq 0 (
    echo 오류: 데이터 수집 실패
    echo data/landing 폴더에 새로운 CSV 파일들이 있는지 확인해주세요.
    pause
    exit /b 1
)
echo ✓ 데이터 수집 완료

echo.
echo [2/4] 특성 생성 중...
python src/pipelines/ingest.py --db build/ivd.db --transform-sql sql/transform.sql
if %errorlevel% neq 0 (
    echo 오류: 특성 생성 실패
    pause
    exit /b 1
)
echo ✓ 특성 생성 완료

echo.
echo [3/4] 일일 스코어링 중...
python src/pipelines/score.py --db build/ivd.db --mode score
if %errorlevel% neq 0 (
    echo 오류: 스코어링 실패
    pause
    exit /b 1
)
echo ✓ 일일 스코어링 완료

echo.
echo [4/4] BI 데이터 내보내기 중...
python src/pipelines/score.py --db build/ivd.db --mode export
if %errorlevel% neq 0 (
    echo 오류: 내보내기 실패
    pause
    exit /b 1
)
echo ✓ BI 데이터 내보내기 완료

echo.
echo ========================================
echo 일일 스코어링이 완료되었습니다!
echo ========================================
echo.
echo 업데이트된 파일들:
echo - build/ivd.db (최신 스코어 포함)
echo - exports/ (최신 Power BI용 CSV 파일들)
echo.
echo Power BI 대시보드가 자동으로 새 데이터를 반영합니다.
echo.
pause

