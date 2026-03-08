import subprocess
import sys
import time

def main():
    print("🚀 Запуск системи Smart Desk...")
    
    print("⏳ Піднімаємо FastAPI бекенд (порт 8000)...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)
    
    print("⏳ Піднімаємо Streamlit фронтенд...")
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app/frontend.py"]
    )
    
    print("✅ Усі сервери запущені! Для виходу натисніть Ctrl+C в цьому терміналі.")
    
    try:
        frontend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Отримано сигнал зупинки. Гасимо сервери...")
        backend.terminate()
        frontend.terminate()
        print("✅ Система успішно зупинена.")

if __name__ == "__main__":
    main()