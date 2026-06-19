"""
DevOps PZ3 - MLOps Pipeline
Angular API Health Classifier
Kubeflow Pipelines SDK v2

Author: Budnuchenko A.V., ITSHI-23-2
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from kfp import dsl, compiler
from kfp.dsl import Output, Input, Dataset, Model, Metrics, component


@component(
    base_image="python:3.11",
    packages_to_install=["numpy==1.26.4"],
)
def load_data(dataset: Output[Dataset]):
    """Step 1: Load Angular API metrics for 7 days."""
    import json
    import numpy as np

    data = {
        'day':         [1, 2, 3, 4, 5, 6, 7],
        'requests':    [12, 18, 15, 22, 30, 28, 35],
        'errors':      [1, 0, 2, 0, 1, 3, 0],
        'response_ms': [120, 115, 130, 110, 145, 200, 105],
    }

    with open(dataset.path, 'w') as f:
        json.dump(data, f)

    print(f'[load_data] Loaded: {len(data["day"])} records')
    print(f'[load_data] Requests: {data["requests"]}')


@component(
    base_image="python:3.11",
    packages_to_install=["numpy==1.26.4"],
)
def train_model(
    dataset: Input[Dataset],
    model:   Output[Model],
    metrics: Output[Metrics],
):
    """Step 2: Compute model metrics from dataset."""
    import json
    import numpy as np

    with open(dataset.path) as f:
        data = json.load(f)

    requests = np.array(data['requests'])
    errors   = np.array(data['errors'])
    resp     = np.array(data['response_ms'])

    params = {
        'avg_requests':    float(np.mean(requests)),
        'avg_errors':      float(np.mean(errors)),
        'avg_response_ms': float(np.mean(resp)),
        'trend':           float(requests[-1] - requests[0]),
        'threshold_high':  float(np.mean(requests) * 1.2),
        'threshold_error': 2.0,
        'threshold_slow':  150.0,
    }

    with open(model.path, 'w') as f:
        json.dump(params, f)

    metrics.log_metric('avg_requests_per_day', params['avg_requests'])
    metrics.log_metric('avg_errors_per_day',   params['avg_errors'])
    metrics.log_metric('avg_response_ms',      params['avg_response_ms'])
    metrics.log_metric('load_trend',           params['trend'])

    print(f'[train_model] avg_requests={params["avg_requests"]:.2f}')
    print(f'[train_model] avg_response={params["avg_response_ms"]:.2f} ms')
    print(f'[train_model] load_trend  =+{params["trend"]:.0f}')


@component(
    base_image="python:3.11",
    packages_to_install=["numpy==1.26.4"],
)
def make_prediction(model: Input[Model]):
    """Step 3: Classify Angular REST API health status."""
    import json

    with open(model.path) as f:
        params = json.load(f)

    status  = 'HEALTHY'
    reasons = []

    if params['avg_errors'] >= params['threshold_error']:
        status = 'CRITICAL'
        reasons.append(f'High error rate: {params["avg_errors"]:.2f}/day')
    if params['avg_response_ms'] >= params['threshold_slow']:
        status = 'WARNING' if status == 'HEALTHY' else status
        reasons.append(f'Slow response: {params["avg_response_ms"]:.0f} ms')
    if params['trend'] > 15:
        status = 'WARNING' if status == 'HEALTHY' else status
        reasons.append(f'Load growth: +{params["trend"]:.0f} req/week')
    if not reasons:
        reasons.append('All metrics are normal')

    print(f'\n{"="*50}')
    print(f'  Angular REST API Status: [ {status} ]')
    for r in reasons:
        print(f'    * {r}')
    print(f'{"="*50}\n')


@dsl.pipeline(
    name='angular-api-health-pipeline',
    description='MLOps Pipeline for monitoring Angular REST API health',
)
def angular_api_pipeline():
    step1 = load_data()
    step2 = train_model(dataset=step1.outputs['dataset'])
    step3 = make_prediction(model=step2.outputs['model'])


if __name__ == '__main__':
    compiler.Compiler().compile(
        pipeline_func=angular_api_pipeline,
        package_path='mlops_pipeline.yaml',
    )
    print('Pipeline compiled: mlops_pipeline.yaml')
