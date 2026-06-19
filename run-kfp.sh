#!/bin/bash
# =============================================================
# DevOps PZ3 — MLOps Pipeline
# Angular API Health Classifier
# Автор: Будниченко А.В., ІТШІ-23-2
# =============================================================

set -e

echo "========================================================"
echo "  DevOps PZ3 — Angular API MLOps Pipeline"
echo "========================================================"
echo ""

# 1. Install dependencies
echo "[1/4] Встановлення залежностей..."
pip install -r requirements.txt -q
echo "  OK: kfp==2.15.0, numpy==1.26.4"
echo ""

# 2. Local test run
echo "[2/4] Локальний тест pipeline..."
python run-pipeline.py
echo ""

# 3. Compile pipeline YAML
echo "[3/4] Компіляція Kubeflow Pipeline у YAML..."
python pipeline.py
echo "  OK: mlops_pipeline.yaml"
echo ""

# 4. Deploy Kubernetes Job
echo "[4/4] Розгортання Kubernetes Job..."
kubectl apply -f mlops-job.yaml
echo ""

echo "Статус Job:"
kubectl get jobs
echo ""
echo "Статус Pods:"
kubectl get pods
echo ""

echo "========================================================"
echo "  Pipeline успішно розгорнуто!"
echo "  Перегляд логів:"
echo "  kubectl logs -l app=mlops-pipeline --tail=50"
echo "========================================================"
