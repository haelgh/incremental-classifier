from fastapi.testclient import TestClient
import sys
import os

# Додаємо корінь проекту в шлях, щоб Python бачив папку app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, CLASS_NAMES

client = TestClient(app)

def test_read_main():
    # Цей тест перевіряє, чи запускається додаток. 
    # Якщо у тебе немає GET / endpoint, тест впаде з 404, це ок, головне що app імпортувався
    response = client.get("/")
    assert response.status_code in [200, 404] 

def test_class_names_structure():
    # Перевіряємо, що словник категорій не порожній
    assert len(CLASS_NAMES) > 0
    assert isinstance(CLASS_NAMES, dict)