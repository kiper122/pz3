@echo off
chcp 65001 >nul 2>&1
:: DevOps PZ3 - MLOps Pipeline (Windows)
:: Angular API Health Classifier

set PYTHON=C:\Users\49160\AppData\Local\Python\bin\python.exe

echo ========================================================
echo   DevOps PZ3 - Angular API MLOps Pipeline
echo ========================================================
echo.

echo [1/4] Installing dependencies...
"%PYTHON%" -m pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)
echo   OK: kfp, numpy installed
echo.

echo [2/4] Local pipeline test...
"%PYTHON%" run-pipeline.py
if %errorlevel% neq 0 (
    echo ERROR: run-pipeline.py failed
    pause
    exit /b 1
)
echo.

echo [3/4] Compiling Kubeflow Pipeline to YAML...
"%PYTHON%" pipeline.py
if %errorlevel% neq 0 (
    echo ERROR: pipeline.py compilation failed
    pause
    exit /b 1
)
echo   OK: mlops_pipeline.yaml
echo.

echo [4/4] Deploying Kubernetes Job...
kubectl apply -f mlops-job.yaml
echo.

echo Job status:
kubectl get jobs
echo.
echo Pods status:
kubectl get pods
echo.

echo ========================================================
echo   Pipeline deployed successfully!
echo   Logs: kubectl logs -l app=mlops-pipeline --tail=50
echo ========================================================
pause
