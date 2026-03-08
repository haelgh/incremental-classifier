import streamlit as st
import requests
import re
from datetime import datetime

st.set_page_config(page_title="Smart Desk | Continual Learning", page_icon="📨", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

def detect_language(text):
    if re.search('[а-яА-ЯіїєґІЇЄҐ]', text):
        return "uk"
    return "en"

CLASS_UI = {
    0: {"label": "Світ та Політика", "color": "#1f77b4", "icon": "🌍", "template": {
        "uk": "Вітаємо! Дякуємо за ваш запит щодо міжнародних новин...", "en": "Hello! Thank you for your inquiry regarding international news..."}},
    1: {"label": "Спорт", "color": "#2ca02c", "icon": "🏆", "template": {
        "uk": "Спортивний відділ отримав ваше повідомлення...", "en": "Sports department has received your message..."}},
    2: {"label": "Бізнес та Фінанси", "color": "#ff7f0e", "icon": "💼", "template": {
        "uk": "Ваш запит щодо фінансових питань передано аналітикам...", "en": "Your inquiry regarding financial matters has been forwarded..."}},
    3: {"label": "IT та Інновації", "color": "#9467bd", "icon": "⚡", "template": {
        "uk": "Вітаємо у майбутньому! Ваш запит щодо STEM/Tech передано...", "en": "Welcome to the future! Your STEM/Tech inquiry has been routed..."}},
    4: {"label": "Кризова підтримка (Агресія)", "color": "#d62728", "icon": "🚨", "template": {
        "uk": "Ми бачимо, що ви незадоволені. Передаємо ваш запит старшому менеджеру для негайного вирішення.", 
        "en": "We understand your frustration. Your ticket has been escalated to a senior manager for immediate resolution."}},
    5: {"label": "Позитивний відгук", "color": "#e377c2", "icon": "✨", "template": {
        "uk": "Дякуємо за теплі слова! Нам дуже приємно...", "en": "Thank you for your kind words! We are thrilled..."}},
    6: {"label": "Пропозиції та Оптимізм", "color": "#bcbd22", "icon": "💡", "template": {
        "uk": "Дякуємо за вашу ідею! Ми розглянемо її на найближчій нараді.", "en": "Thank you for your idea! We will review it shortly."}},
    7: {"label": "Критичні ситуації (Сум)", "color": "#7f7f7f", "icon": "📉", "template": {
        "uk": "Нам шкода, що так сталося. Давайте знайдемо вихід разом.", "en": "We are sorry this happened. Let's find a solution together."}}
}

col1, col2 = st.columns([2, 1])

with col1:
    st.title("📨 Smart Desk. Класифікатор текстів")
    st.markdown("Система на базі Continual Learning ШІ. Автоматично класифікує вхідні листи (EN/UK) та підбирає оптимальний шаблон відповіді мовою клієнта.")
    st.divider()

    text_input = st.text_area("Вхідне повідомлення (від клієнта або з моніторингу):", height=150, placeholder="Введіть текст скарги, комерційного запиту або відгуку (англійською або українською)...")

    if st.button("Проаналізувати та підібрати відповідь", type="primary", use_container_width=True):
        if not text_input.strip():
            st.warning("Поле вводу порожнє.")
        else:
            with st.spinner("Звернення до ML-ядра на AWS SageMaker..."):
                try:

                    lang = detect_language(text_input)
                    
                    response = requests.post("http://127.0.0.1:8000/predict", json={"text": text_input})
                    if response.status_code == 200:
                        data = response.json()
                        if "error" in data:
                            st.error(f"Помилка моделі: {data['error']}")
                        else:
                            class_id = data.get("predicted_class_id")
                            
                            ui_info = CLASS_UI.get(class_id)
                            if ui_info:
                                label = ui_info["label"]
                                color = ui_info["color"]
                                icon = ui_info["icon"]
                                template = ui_info["template"][lang]
                            else:
                                label = "Невідомо"
                                color = "gray"
                                icon = "❓"
                                template = "Відповідь потребує ручного втручання оператора."

                            st.success("Лист успішно оброблено!")
                            
                            st.markdown(f"""
                            <div style="padding: 15px; border-radius: 10px; border-left: 5px solid {color}; background-color: rgba(255,255,255,0.05); margin-bottom: 20px;">
                                <h3 style="color: {color}; margin: 0;">{icon} Департамент: {label}</h3>
                                <p style="color: gray; margin: 5px 0 0 0; font-size: 0.9em;">Визначена мова: <b>{lang.upper()}</b></p>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown("#### 📝 Проєкт відповіді (Draft):")
                            edited_template = st.text_area("Відредагуйте текст за потреби:", value=template, height=150)
                            st.caption("👇 Натисніть іконку копіювання у правому верхньому куточку рамки, щоб скопіювати текст:")
                            st.code(edited_template, language="markdown")

                            st.session_state.history.append({
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "text": text_input,
                                "result": label,
                                "icon": icon,
                                "color": color,
                                "lang": lang.upper()
                            })
                    else:
                        st.error(f"HTTP Помилка: {response.status_code}")
                except Exception as e:
                    st.error("Помилка з'єднання з API. Переконайтеся, що бекенд працює.")

with col2:
    st.header("📋 Історія маршрутизації")
    st.markdown("Останні оброблені тикети:")
    
    if not st.session_state.history:
        st.info("Черга порожня.")
    else:
        for item in reversed(st.session_state.history):
            st.markdown(f"**{item['time']}** | <span style='color:{item['color']}'>{item['icon']} {item['result']}</span> [{item['lang']}]", unsafe_allow_html=True)
            st.caption(f"Вхідний текст: «{item['text'][:60]}...»")
            st.divider()