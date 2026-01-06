import streamlit as st
import google.generativeai as genai
import os

# Sayfa Ayarları
st.set_page_config(page_title="FLL Kural Asistanı", page_icon="🤖")

# Başlık
st.title("🤖 FLL Submerged - Kural Asistanı")
st.write("FLL kuralları ve görevleri hakkında sorularınızı sorun.")

# 1. API KEY AYARI (Güvenlik için Secrets'tan çekeceğiz)
# GitHub'a asla açık API Key yüklemeyin!
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("API Key bulunamadı! Lütfen Streamlit Secrets ayarlarını yapın.")
    st.stop()

# 2. MODEL VE TALİMATLAR
# Buraya AI Studio'daki "System Instruction" metnini yapıştırın.
# Eğer PDF kullandıysan, PDF içeriğini metne döküp buraya eklemek en garanti yoldur.
SYSTEM_PROMPT = """
Sen uzman bir FIRST LEGO League (FLL) Başhakemisin. 
Soruları yanıtlarken FLL Robot Oyunu kural kitapçığını referans al.
Daima nazik ve öğretici ol. Cevaplarında kural maddelerini (R12, M04 gibi) belirt.
"""

# Modeli Başlat
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# 3. SOHBET GEÇMİŞİ YÖNETİMİ
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana çiz
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
        message_placeholder = st.empty()
        full_response = ""
        
        # Sohbet geçmişini modele gönder
        chat = model.start_chat(history=[
            {"role": m["role"], "parts": [m["content"]]} 
            for m in st.session_state.messages[:-1]
        ])
        
        response = chat.send_message(prompt, stream=True)
        
        # Akışkan (streaming) cevap efekti
        for chunk in response:
            full_response += chunk.text
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "model", "content": full_response})
