import streamlit as st
import boto3
import json
import re
from datetime import datetime
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Smart Desk | Continual Learning", page_icon="📨", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

def detect_language(text):
    if re.search('[а-яА-ЯіїєґІЇЄҐ]', text):
        return "uk"
    return "en"

CLASS_UI = {
    0: {
        "label": "Глобальні події / Політика", "color": "#1f77b4", "icon": "🌍", 
        "routing": "PR-відділ / Моніторинг", "action": "Аналіз репутаційних ризиків. Відповідь не потребується, зберегти для звіту.",
        "template": {"uk": "Запит стосується загальних новин. Пряма відповідь не передбачена регламентом.", "en": "Information regarding global events. No direct response required by protocol."}
    },
    1: {
        "label": "Спортивні події", "color": "#2ca02c", "icon": "🏆", 
        "routing": "Відділ спонсорства та івентів", "action": "Перевірити наявність запитів на партнерство. Передати маркетологам.",
        "template": {"uk": "Вітаємо! Ваш запит щодо спортивних ініціатив передано до профільного відділу.", "en": "Hello! Your message regarding sports initiatives has been forwarded to the relevant department."}
    },
    2: {
        "label": "Комерція та Фінанси", "color": "#ff7f0e", "icon": "💼", 
        "routing": "B2B Sales / Бухгалтерія", "action": "Високий пріоритет. Залучити фінансового консультанта для підготовки комерційної пропозиції.",
        "template": {"uk": "Доброго дня. Дякуємо за звернення. Ваш запит передано фінансовому спеціалісту, який зв'яжеться з вами найближчим часом.", "en": "Good day. Your financial/commercial inquiry has been routed to our B2B specialist."}
    },
    3: {
        "label": "Технології та Інновації", "color": "#9467bd", "icon": "⚡", 
        "routing": "IT Департамент", "action": "Технічний аналіз або розгляд пропозицій щодо співпраці у сфері STEM.",
        "template": {"uk": "Вітаємо! Ваш запит на технічну або інноваційну тематику зареєстровано в IT-відділі.", "en": "Hello! Your tech-related inquiry has been registered with our IT department."}
    },
    4: {
        "label": "Кризова ситуація / Агресія", "color": "#d62728", "icon": "🚨", 
        "routing": "Escalation Team (Менеджери)", "action": "КРИТИЧНО (SLA < 15 хв). Негайна ескалація. Зв'язатися з клієнтом особисто для нейтралізації конфлікту.",
        "template": {"uk": "Шановний(а) клієнте. Ми фіксуємо ваше невдоволення. Керівництво вже розглядає вашу ситуацію для негайного вирішення.", "en": "Dear Customer. We acknowledge your severe frustration. Management is reviewing your case immediately."}
    },
    5: {
        "label": "Позитивний фідбек / Лояльність", "color": "#e377c2", "icon": "✨", 
        "routing": "Відділ маркетингу", "action": "Низький пріоритет. Надіслати автоматичну подяку. Розглянути можливість використання для PR.",
        "template": {"uk": "Дякуємо за ваш позитивний настрій та довіру до нас! Ми працюємо саме для таких моментів.", "en": "Thank you for your positive energy and trust in us! This makes our day."}
    },
    6: {
        "label": "Пропозиції та Ідеї (Оптимізм)", "color": "#bcbd22", "icon": "💡", 
        "routing": "Product Managers (R&D)", "action": "Проаналізувати ідею клієнта. Додати в беклог, якщо пропозиція конструктивна.",
        "template": {"uk": "Дякуємо за вашу ідею! Ми передали її команді розробників для розгляду в наступних оновленнях.", "en": "Thank you for your suggestion! We have forwarded your idea to our product team."}
    },
    7: {
        "label": "Сум / Проблемна ситуація", "color": "#7f7f7f", "icon": "📉", 
        "routing": "Служба турботи (Емпатійна підтримка)", "action": "Середній пріоритет. Проявити максимальну емпатію. Запропонувати компенсацію або допомогу.",
        "template": {"uk": "Нам дуже прикро, що у вас склалася така ситуація. Розкажіть детальніше, і ми зробимо все можливе, щоб допомогти.", "en": "We are truly sorry to hear you are going through this. Please let us know how we can support you."}
    }
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
            lang = detect_language(text_input)
            
            if lang == "uk":
                with st.spinner("Переклад на зрозумілу для нейромережі мову..."):
                    try:
                        text_to_analyze = GoogleTranslator(source='uk', target='en').translate(text_input)
                        st.caption(f"🔧 Внутрішній переклад для AWS: *«{text_to_analyze}»*")
                    except Exception as e:
                        st.error("Помилка перекладу. Спробуйте ще раз.")
                        text_to_analyze = text_input 
            else:
                text_to_analyze = text_input

            with st.spinner("Звернення до AWS SageMaker..."):
                try:
                    client = get_sagemaker_client()
                    
                    payload = json.dumps({"text": text_to_analyze})
                    
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
                        st.success("Текст успішно проаналізовано!")
                        
                        st.markdown(f"""
                        <div style="padding: 15px; border-radius: 10px; border-left: 5px solid {ui_info['color']}; background-color: rgba(255,255,255,0.05); margin-bottom: 20px;">
                            <h3 style="color: {ui_info['color']}; margin: 0;">{ui_info['icon']} {ui_info['label']}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("### 📊 Системна маршрутизація")
                        st.info(f"**Департамент:** {ui_info['routing']}")
                        st.warning(f"**Рекомендована дія для оператора:** {ui_info['action']}")
                        
                        st.markdown("### 📝 Чорновик відповіді (Draft)")
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