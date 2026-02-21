import streamlit as st
import random

# Sayfa Ayarları
st.set_page_config(page_title="Almanca Öğren", page_icon="🇩🇪")

# CSS ile Görünümü Güzelleştirme
st.markdown("""
    <style>
    .main { text-align: center; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FFCC00; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇩🇪 Almanca A1-A2 Kelime Kartları")

# Kelime Havuzu
if 'words' not in st.session_state:
    st.session_state.words = [
        {"de": "Der Apfel", "tr": "Elma", "level": "A1"},
        {"de": "Das Haus", "tr": "Ev", "level": "A1"},
        {"de": "Entscheiden", "tr": "Karar vermek", "level": "A2"},
        {"de": "Die Umwelt", "tr": "Çevre", "level": "A2"},
        {"de": "Günstig", "tr": "Uygun / Ucuz", "level": "A1"},
        {"de": "Vielleicht", "tr": "Belki", "level": "A2"},
        {"de": "Frühstücken", "tr": "Kahvaltı yapmak", "level": "A1"},
        {"de": "Der Unterschied", "tr": "Fark", "level": "A2"}
    ]

if 'current_word' not in st.session_state:
    st.session_state.current_word = random.choice(st.session_state.words)
    st.session_state.show_answer = False

# Kelime Kartı Arayüzü
st.info(f"Seviye: {st.session_state.current_word['level']}")
st.markdown(f"## {st.session_state.current_word['de']}")

if st.button("Cevabı Göster"):
    st.session_state.show_answer = True

if st.session_state.show_answer:
    st.success(f"Türkçesi: **{st.session_state.current_word['tr']}**")

if st.button("Sıradaki Kelime ➡️"):
    st.session_state.current_word = random.choice(st.session_state.words)
    st.session_state.show_answer = False
    st.rerun()
