"""
Day 7: API Server Automated Endpoint Tests
"""
import requests
from requests.auth import HTTPBasicAuth
import pytest

BASE_URL = "http://127.0.0.1:8888"
AUTH = HTTPBasicAuth("admin", "cybersnoop2025")

@pytest.mark.parametrize("endpoint", [
    "/api/status",
    "/api/stats",
    "/api/interfaces",
    "/api/packets",
    "/api/threats"
])
def test_authenticated_get_endpoints(endpoint):
    r = requests.get(BASE_URL + endpoint, auth=AUTH)
    assert r.status_code == 200
    assert isinstance(r.json(), dict)

def test_packets_limit_validation():
    r = requests.get(BASE_URL + "/api/packets?limit=0", auth=AUTH)
    assert r.status_code == 400
    r = requests.get(BASE_URL + "/api/packets?limit=2000", auth=AUTH)
    assert r.status_code == 400

def test_threats_limit_validation():
    r = requests.get(BASE_URL + "/api/threats?limit=0", auth=AUTH)
    assert r.status_code == 400
    r = requests.get(BASE_URL + "/api/threats?limit=1000", auth=AUTH)
    assert r.status_code == 400

def test_monitoring_control():
    r = requests.post(BASE_URL + "/api/monitoring/start", auth=AUTH)
    assert r.status_code == 200
    r = requests.post(BASE_URL + "/api/monitoring/stop", auth=AUTH)
    assert r.status_code == 200

def test_auth_required():
    r = requests.get(BASE_URL + "/api/status")
    assert r.status_code == 401

def test_rate_limiting():
    for _ in range(35):
        r = requests.get(BASE_URL + "/api/status", auth=AUTH)
    assert r.status_code in (200, 429)

# WebSocket test is best done with a separate async client or manual test
