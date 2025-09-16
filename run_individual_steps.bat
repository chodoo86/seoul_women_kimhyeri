@echo off
chcp 65001 >nul
echo ========================================
echo IVD Lead Scoring 개별 단계 실행
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

:menu
echo.
echo 실행할 단계를 선택하세요:
echo.
echo 1. 데이터베이스 생성
echo 2. 데이터 수집
echo 3. 특성 생성
echo 4. 모델 재훈련
echo 5. 일일 스코어링
echo 6. BI 데이터 내보내기
echo 7. 전체 파이프라인 실행
echo 8. 종료
echo.
set /p choice="선택 (1-8): "

if "%choice%"=="1" goto step1
if "%choice%"=="2" goto step2
if "%choice%"=="3" goto step3
if "%choice%"=="4" goto step4
if "%choice%"=="5" goto step5
if "%choice%"=="6" goto step6
if "%choice%"=="7" goto step7
if "%choice%"=="8" goto end
echo 잘못된 선택입니다. 다시 선택해주세요.
goto menu

:step1
echo.
echo [1/1] 데이터베이스 생성 중...
python -c "import sqlite3, os; os.makedirs('build', exist_ok=True); sqlite3.connect('build/ivd.db').close()"
if %errorlevel% neq 0 (
    echo 오류: 데이터베이스 파일 생성 실패
    goto menu
)

python -c "import sqlite3, pathlib; sql = pathlib.Path('sql/ddl.sql').read_text(encoding='utf-8'); con = sqlite3.connect('build/ivd.db'); con.executescript(sql); con.close()"
if %errorlevel% neq 0 (
    echo 오류: 데이터베이스 테이블 생성 실패
    goto menu
)
echo ✓ 데이터베이스 생성 완료
goto menu

:step2
echo.
echo [1/1] 데이터 수집 중...
if not exist "data/landing" (
    echo 오류: data/landing 폴더가 존재하지 않습니다.
    goto menu
)
python src/pipelines/ingest.py --db build/ivd.db --landing data/landing
if %errorlevel% neq 0 (
    echo 오류: 데이터 수집 실패
    goto menu
)
echo ✓ 데이터 수집 완료
goto menu

:step3
echo.
echo [1/1] 특성 생성 중...
if not exist "build/ivd.db" (
    echo 오류: 데이터베이스가 존재하지 않습니다. 먼저 단계 1을 실행해주세요.
    goto menu
)
python src/pipelines/ingest.py --db build/ivd.db --transform-sql sql/transform.sql
if %errorlevel% neq 0 (
    echo 오류: 특성 생성 실패
    goto menu
)
echo ✓ 특성 생성 완료
goto menu

:step4
echo.
echo [1/1] 모델 재훈련 중...
if not exist "build/ivd.db" (
    echo 오류: 데이터베이스가 존재하지 않습니다. 먼저 단계 1-3을 실행해주세요.
    goto menu
)
python src/pipelines/score.py --db build/ivd.db --mode retrain
if %errorlevel% neq 0 (
    echo 오류: 모델 재훈련 실패
    goto menu
)
echo ✓ 모델 재훈련 완료
goto menu

:step5
echo.
echo [1/1] 일일 스코어링 중...
if not exist "build/ivd.db" (
    echo 오류: 데이터베이스가 존재하지 않습니다. 먼저 단계 1-4를 실행해주세요.
    goto menu
)
python src/pipelines/score.py --db build/ivd.db --mode score
if %errorlevel% neq 0 (
    echo 오류: 스코어링 실패
    goto menu
)
echo ✓ 일일 스코어링 완료
goto menu

:step6
echo.
echo [1/1] BI 데이터 내보내기 중...
if not exist "build/ivd.db" (
    echo 오류: 데이터베이스가 존재하지 않습니다. 먼저 단계 1-5를 실행해주세요.
    goto menu
)
python src/pipelines/score.py --db build/ivd.db --mode export
if %errorlevel% neq 0 (
    echo 오류: 내보내기 실패
    goto menu
)
echo ✓ BI 데이터 내보내기 완료
goto menu

:step7
echo.
echo 전체 파이프라인을 실행합니다...
call run_full_pipeline.bat
goto menu

:end
echo.
echo 프로그램을 종료합니다.
pause

