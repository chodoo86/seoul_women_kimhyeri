@echo off
chcp 65001 >nul
echo ========================================
echo IVD Lead Scoring 환경 설정 (개선된 버전)
echo ========================================
echo.

echo [1/4] Python 가상환경 확인 중...
if not exist "venv" (
    echo Python 가상환경을 생성합니다...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 오류: Python이 설치되어 있지 않거나 가상환경 생성에 실패했습니다.
        echo Python 3.8 이상을 설치해주세요.
        pause
        exit /b 1
    )
    echo ✓ 가상환경 생성 완료
) else (
    echo ✓ 가상환경이 이미 존재합니다
)

echo.
echo [2/4] 가상환경 활성화 중...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 오류: 가상환경 활성화 실패
    pause
    exit /b 1
)
echo ✓ 가상환경 활성화 완료

echo.
echo [3/4] pip 업그레이드 중... 
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo 경고: pip 업그레이드 실패 (계속 진행)
)

echo.
echo [4/4] 필요한 패키지 설치 중...
echo 미리 컴파일된 패키지를 사용하여 설치합니다...

REM 먼저 numpy를 설치 (pandas 의존성)
echo - numpy 설치 중...
python -m pip install numpy
if %errorlevel% neq 0 (
    echo 오류: numpy 설치 실패
    pause
    exit /b 1
)

REM 그 다음 pandas를 설치
echo - pandas 설치 중...
python -m pip install pandas
if %errorlevel% neq 0 (
    echo 오류: pandas 설치 실패
    pause
    exit /b 1
)

REM 나머지 패키지들을 하나씩 설치
echo - scikit-learn 설치 중...
python -m pip install scikit-learn
if %errorlevel% neq 0 (
    echo 경고: scikit-learn 설치 실패 (계속 진행)
)

echo - xgboost 설치 중...
python -m pip install xgboost
if %errorlevel% neq 0 (
    echo 경고: xgboost 설치 실패 (계속 진행)
)

echo - SQLAlchemy 설치 중...
python -m pip install SQLAlchemy
if %errorlevel% neq 0 (
    echo 경고: SQLAlchemy 설치 실패 (계속 진행)
)

echo - joblib 설치 중...
python -m pip install joblib
if %errorlevel% neq 0 (
    echo 경고: joblib 설치 실패 (계속 진행)
)

echo - matplotlib 설치 중...
python -m pip install matplotlib
if %errorlevel% neq 0 (
    echo 경고: matplotlib 설치 실패 (계속 진행)
)

echo - reportlab 설치 중...
python -m pip install reportlab
if %errorlevel% neq 0 (
    echo 경고: reportlab 설치 실패 (계속 진행)
)

echo.
echo ========================================
echo 환경 설정이 완료되었습니다!
echo ========================================
echo.
echo 설치된 패키지 확인:
python -c "import pandas, numpy, sklearn; print('✓ 핵심 패키지 설치 완료')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠ 일부 패키지 설치에 실패했을 수 있습니다.
    echo 하지만 기본 기능은 사용할 수 있습니다.
) else (
    echo ✓ 모든 핵심 패키지가 정상적으로 설치되었습니다.
)

echo.
echo 이제 다음 파일들을 실행할 수 있습니다:
echo - run_full_pipeline.bat : 전체 파이프라인 실행
echo - run_daily_scoring.bat : 일일 스코어링만 실행
echo - run_individual_steps.bat : 개별 단계 실행
echo.
pause

