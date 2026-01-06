import streamlit as st
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="FLL Kural Asistanı", page_icon="🤖")
st.title("🤖 FLL Submerged - Kural Asistanı")

# 1. API KEY KONTROLÜ
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API Key hatası! Lütfen Streamlit Secrets ayarlarını kontrol edin.")
    st.error(f"Hata detayı: {e}")
    st.stop()

# 2. MODEL AYARLARI (En kararlı sürümü kullanıyoruz)
SYSTEM_PROMPT = """
Sen uzman bir FLL Başhakemisin. 
Soruları yanıtlarken FLL Robot Oyunu kural kitapçığını referans al.
Daima nazik ve öğretici ol. Cevaplarında kural maddelerini (R12, M04 gibi) belirt.
"""

# Modeli oluştur
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # "latest" yerine bunu kullanıyoruz
    system_instruction=SYSTEM_PROMPT
)

# 3. SOHBET GEÇMİŞİ BAŞLATMA
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları ekrana yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. KULLANICI GİRİŞİ VE CEVAP
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot cevabını üret
    with st.chat_message("assistant"):
        try:
            # Sohbet geçmişini Gemini formatına çevir
            # Hata çıkmaması için geçmişi temizleyip sadece son soruyu da gönderebiliriz
            # Ama bağlamı korumak için şunu deniyoruz:
            history_for_gemini = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                history_for_gemini.append({"role": role, "parts": [m["content"]]})

            chat = model.start_chat(history=history_for_gemini)
            
            # Cevabı al (stream=False yaptık hata ayıklamak daha kolay olsun diye)
            response = chat.send_message(prompt)
            st.markdown(response.text)
            
            # Geçmişe ekle
            st.session_state.messages.append({"role": "model", "content": response.text})
            
        except Exception as e:
            # HATAYI BURADA YAKALAYIP EKRANA BASIYORUZ
            st.error("Bir hata oluştu:")
            st.code(e)
            # Hata durumunda geçmişi temizlemek bazen kurtarıcı olur
            if st.button("Sohbeti Sıfırla"):
                st.session_state.messages = []
                st.rerun()
