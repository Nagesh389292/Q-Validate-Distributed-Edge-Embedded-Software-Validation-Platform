from fastapi.testclient import TestClient
from qvalidate.api.main import app

client = TestClient(app)

def test_test_impact_analysis_endpoint():
    # Submit git diff with MemoryManager.cpp
    req_payload = {"changed_files": ["src/MemoryManager.cpp", "include/Memory.hpp"]}
    res = client.post("/api/v1/regressions/impact-analysis", json=req_payload)
    assert res.status_code == 200
    data = res.json()
    assert "COMP-MEM" in data["impacted_component_ids"]
    assert data["selected_test_count"] >= 1
    
    test_ids = [t["test_id"] for t in data["selected_tests"]]
    assert "MEM-003" in test_ids
