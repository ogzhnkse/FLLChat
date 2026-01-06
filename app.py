import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="FLL Asistanı", page_icon="🤖")
st.title("🤖 FLL Submerged - Kural Asistanı")

# 1. API KEY
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API Key hatası! Secrets ayarlarını kontrol et.")
    st.stop()

# 2. MODEL SEÇİMİ (EN GARANTİ YÖNTEM: 'gemini-pro')
# 1.5-flash bazen bölge veya hesap türü nedeniyle görünmeyebilir.
# 'gemini-pro' ise herkese açıktır.
model_name = "gemini-pro"

# System Prompt'u eski modelde doğrudan mesaj geçmişine ekleyeceğiz
SYSTEM_PROMPT = "Sen uzman bir FLL Başhakemisin. Soruları FLL Robot Oyunu kurallarına göre cevapla."

model = genai.GenerativeModel(model_name)

# 3. SOHBET GEÇMİŞİ
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Botun kimliğini en başa 'gizli' bir mesaj olarak ekliyoruz
    st.session_state.messages.append({"role": "user", "content": SYSTEM_PROMPT})
    st.session_state.messages.append({"role": "model", "content": "Anlaşıldı, FLL kurallarına göre yardımcı olmaya hazırım."})

# Mesajları ekrana yaz (System prompt'u gizlemek için 2. mesajdan başlıyoruz)
for message in st.session_state.messages[2:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. KULLANICI GİRİŞİ
if prompt := st.chat_input("Sorunuzu sorun..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Sohbeti başlat
            chat = model.start_chat(history=[
                {"role": m["role"], "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ])
            
            response = chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "model", "content": response.text})
            
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
            st.warning("Eğer '404' hatası devam ediyorsa, API Key'inizi yeniden oluşturmayı deneyin.")
