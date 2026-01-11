from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, CLASS_NAMES

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code in [200, 404] 

def test_class_names_structure():
    assert len(CLASS_NAMES) > 0
    assert isinstance(CLASS_NAMES, dict)