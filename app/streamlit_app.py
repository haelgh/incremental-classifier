import streamlit as st
import boto3
import json
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
    0: {"label": "Світ та Політика", "color": "#1f77b4", "icon": "🌍", "template": {"uk": "Вітаємо! Дякуємо за ваш запит щодо міжнародних новин...", "en": "Hello! Thank you for your inquiry regarding international news..."}},
    1: {"label": "Спорт", "color": "#2ca02c", "icon": "🏆", "template": {"uk": "Спортивний відділ отримав ваше повідомлення...", "en": "Sports department has received your message..."}},
    2: {"label": "Бізнес та Фінанси", "color": "#ff7f0e", "icon": "💼", "template": {"uk": "Ваш запит щодо фінансових питань передано аналітикам...", "en": "Your inquiry regarding financial matters has been forwarded..."}},
    3: {"label": "IT та Інновації", "color": "#9467bd", "icon": "⚡", "template": {"uk": "Вітаємо у майбутньому! Ваш запит щодо STEM/Tech передано...", "en": "Welcome to the future! Your STEM/Tech inquiry has been routed..."}},
    4: {"label": "Кризова підтримка (Агресія)", "color": "#d62728", "icon": "🚨", "template": {"uk": "Ми бачимо, що ви незадоволені. Передаємо ваш запит старшому менеджеру.", "en": "We understand your frustration. Your ticket has been escalated."}},
    5: {"label": "Позитивний відгук", "color": "#e377c2", "icon": "✨", "template": {"uk": "Дякуємо за теплі слова! Нам дуже приємно...", "en": "Thank you for your kind words! We are thrilled..."}},
    6: {"label": "Пропозиції та Оптимізм", "color": "#bcbd22", "icon": "💡", "template": {"uk": "Дякуємо за вашу ідею! Ми розглянемо її на найближчій нараді.", "en": "Thank you for your idea! We will review it shortly."}},
    7: {"label": "Критичні ситуації (Сум)", "color": "#7f7f7f", "icon": "📉", "template": {"uk": "Нам шкода, що так сталося. Давайте знайдемо вихід разом.", "en": "We are sorry this happened. Let's find a solution together."}}
}

@st.cache_resource
def get_sagemaker_client():
    return boto3.client(
        'sagemaker-runtime',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_REGION"]
    )

col1, col2 = st.columns([2, 1])

with col1:
    st.title("📨 Smart Desk: AI Маршрутизація")
    st.markdown("Система розпізнає 8 категорій текстів (новини та емоції) на базі моделі RoBERTa.")
    st.divider()

    text_input = st.text_area("Вхідне повідомлення:", height=150)

    if st.button("Проаналізувати", type="primary", use_container_width=True):
        if not text_input.strip():
            st.warning("Поле вводу порожнє.")
        else:
            with st.spinner("Звернення до AWS SageMaker..."):
                try:
                    client = get_sagemaker_client()
                    lang = detect_language(text_input)
                    payload = json.dumps({"text": text_input})
                    
                    response = client.invoke_endpoint(
                        EndpointName=st.secrets["SAGEMAKER_ENDPOINT_NAME"],
                        ContentType='application/json',
                        Body=payload
                    )
                    
                    result_str = response['Body'].read().decode('utf-8').strip()
                    clean_result = re.sub(r'[\[\]"]', '', result_str)
                    class_id = int(float(clean_result))
                    
                    ui_info = CLASS_UI.get(class_id)
                    if ui_info:
                        st.success("Успішно оброблено!")
                        st.markdown(f"""
                        <div style="padding: 15px; border-radius: 10px; border-left: 5px solid {ui_info['color']}; background-color: rgba(255,255,255,0.05); margin-bottom: 20px;">
                            <h3 style="color: {ui_info['color']}; margin: 0;">{ui_info['icon']} {ui_info['label']}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.code(ui_info["template"][lang], language="markdown")
                        
                        st.session_state.history.append({
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "text": text_input,
                            "result": ui_info['label'],
                            "icon": ui_info['icon'],
                            "color": ui_info['color']
                        })
                except Exception as e:
                    st.error(f"Помилка AWS: {str(e)}")

with col2:
    st.header("📋 Історія")
    if not st.session_state.history:
        st.info("Черга порожня.")
    else:
        for item in reversed(st.session_state.history):
            st.markdown(f"**{item['time']}** | <span style='color:{item['color']}'>{item['icon']} {item['result']}</span>", unsafe_allow_html=True)
            st.caption(f"«{item['text'][:60]}...»")
            st.divider()