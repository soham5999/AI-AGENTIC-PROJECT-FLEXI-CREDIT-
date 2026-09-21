import httpx

def run_tests():
    client = httpx.Client(base_url='http://127.0.0.1:8000/api')

    # 1. Health check
    h = client.get('/health').json()
    assert h['status'] == 'online', 'Health check failed'
    print('[PASS] Health Check:', h['status'])

    # 2. Vehicles
    v = client.get('/vehicles').json()
    assert len(v) > 0, 'No vehicles found'
    print('[PASS] Vehicles List:', len(v), 'vehicle(s) found')

    # 3. Predict
    pred = client.post('/predict', json={
        'vehicle_age': 3, 'odometer_km': 62450, 'days_since_service': 195,
        'battery_voltage': 11.9, 'engine_temp': 99, 'brake_wear_pct': 78,
        'tire_pressure_avg': 30, 'oil_life_pct': 22, 'vehicle_id': 'v-camry-01'
    }).json()
    assert 'probability' in pred and 'riskLevel' in pred, 'Predict failed'
    print(f"[PASS] Prediction: {pred['probability']}% Risk: {pred['riskLevel']} Req: {pred['maintenanceRequired']}")

    # 4. Agent Analyze
    agent = client.post('/agent/analyze', json={
        'query': 'Perform complete maintenance diagnostic for my vehicle',
        'vehicle_id': 'v-camry-01'
    }).json()
    assert len(agent['executionSteps']) >= 5, 'Agent steps failed'
    assert len(agent['recommendations']) > 0, 'Agent recommendations failed'
    print(f"[PASS] Agent Execution Steps: {len(agent['executionSteps'])}, Mode: {agent['agentMode']}")
    print(f"[PASS] Agent Recommendations Count: {len(agent['recommendations'])}")

    # 5. Maintenance
    m_records = client.get('/maintenance/v-camry-01').json()
    m_before = len(m_records)
    new_m = client.post('/maintenance', json={
        'vehicle_id': 'v-camry-01', 'date': '2026-03-21', 'mileage': 62500,
        'service_type': 'Brake Pad Replacement Test', 'cost': 210.0, 'notes': 'Test log entry'
    }).json()
    m_after = len(client.get('/maintenance/v-camry-01').json())
    assert m_after == m_before + 1, 'Maintenance add failed'
    print(f"[PASS] Maintenance Added, new count: {m_after}")

    # Clean up test log
    client.delete(f"/maintenance/{new_m['id']}")
    m_final = len(client.get('/maintenance/v-camry-01').json())
    assert m_final == m_before, 'Maintenance delete failed'
    print('[PASS] Maintenance Deleted cleanly')

    # 6. Model Performance
    perf = client.get('/model/performance').json()
    assert perf['accuracy'] > 80, 'Model accuracy low'
    print(f"[PASS] Model Accuracy: {perf['accuracy']}%, F1: {perf['f1Score']}%")
    print(f"[PASS] Top Feature: {perf['featureImportances'][0]['feature']} ({perf['featureImportances'][0]['importance']}%)")

    # 7. Dataset Summary
    ds = client.get('/dataset/current').json()
    assert ds['totalRecords'] > 0, 'Dataset empty'
    print(f"[PASS] Dataset Records: {ds['totalRecords']}, Features: {ds['totalFeatures']}")

    print('\n=================================================')
    print('ALL 7 AUTOMATED ENDPOINT VERIFICATIONS PASSED 100%!')
    print('=================================================')

if __name__ == '__main__':
    run_tests()
