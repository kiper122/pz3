"""
Local MLOps Pipeline runner (no Kubeflow cluster needed).
For testing and demonstration purposes.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
import numpy as np

def load_data():
    print("=" * 55)
    print("  STEP 1: load_data - Angular API data loading")
    print("=" * 55)
    data = {
        "day": [1, 2, 3, 4, 5, 6, 7],
        "requests": [12, 18, 15, 22, 30, 28, 35],
        "errors": [1, 0, 2, 0, 1, 3, 0],
        "response_ms": [120, 115, 130, 110, 145, 200, 105],
    }
    print(f"  Loaded: {len(data['day'])} records (7 days)")
    print(f"  Requests:     {data['requests']}")
    print(f"  Errors:       {data['errors']}")
    print(f"  Response(ms): {data['response_ms']}")
    return data

def train_model(data):
    print("\n" + "=" * 55)
    print("  STEP 2: train_model - Computing model metrics")
    print("=" * 55)
    requests = np.array(data["requests"])
    errors   = np.array(data["errors"])
    resp     = np.array(data["response_ms"])

    params = {
        "avg_requests":    float(np.mean(requests)),
        "avg_errors":      float(np.mean(errors)),
        "avg_response_ms": float(np.mean(resp)),
        "trend":           float(requests[-1] - requests[0]),
    }

    print(f"  avg_requests/day : {params['avg_requests']:.2f}")
    print(f"  avg_errors/day   : {params['avg_errors']:.2f}")
    print(f"  avg_response_ms  : {params['avg_response_ms']:.2f}")
    print(f"  load_trend (+7d) : +{params['trend']:.0f}")
    return params

def make_prediction(params):
    print("\n" + "=" * 55)
    print("  STEP 3: make_prediction - API status forecast")
    print("=" * 55)

    status  = "HEALTHY"
    reasons = []

    if params["avg_errors"] >= 2.0:
        status = "CRITICAL"
        reasons.append(f"High error rate: {params['avg_errors']:.2f}/day")
    if params["avg_response_ms"] >= 150.0:
        status = "WARNING" if status == "HEALTHY" else status
        reasons.append(f"Slow response: {params['avg_response_ms']:.0f} ms")
    if params["trend"] > 15:
        status = "WARNING" if status == "HEALTHY" else status
        reasons.append(f"Load growth: +{params['trend']:.0f} req/week")
    if not reasons:
        reasons.append("All metrics are normal")

    print(f"\n  >>> Angular REST API Status: [ {status} ]")
    for r in reasons:
        print(f"      * {r}")
    print(f"\n  PIPELINE RESULT: {status}")
    print("=" * 55)
    return status

if __name__ == "__main__":
    print("\n  Angular API Health MLOps Pipeline")
    print("  DevOps PZ3 - Budnuchenko A.V., ITSHI-23-2\n")
    data   = load_data()
    params = train_model(data)
    result = make_prediction(params)
    print(f"\n  Pipeline finished. Result: {result}\n")
