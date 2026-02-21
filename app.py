import streamlit as st
import random

# Uygulama Başlığı
st.title("🇩🇪 Almanca A1-A2 Kelime Öğrenme")

# Kelime Veritabanı (Örnektir, listeyi büyütebilirsiniz)
if 'words' not in st.session_state:
    st.session_state.words = [
        {"de": "Der Apfel", "tr": "Elma", "level": "A1"},
        {"de": "Laufen", "tr": "Koşmak / Yürümek", "level": "A1"},
        {"de": "Entscheiden", "tr": "Karar vermek", "level": "A2"},
        {"de": "Die Umwelt", "tr": "Çevre", "level": "A2"},
        {"de": "Günstig", "tr": "Uygun / Ucuz", "level": "A1"},
        {"de": "Vielleicht", "tr": "Belki", "level": "A2"}
    ]

# Mevcut kelimeyi hafızada tutmak için session_state kullanıyoruz
if 'current_word' not in st.session_state:
    st.session_state.current_word = random.choice(st.session_state.words)
    st.session_state.show_answer = False

# Arayüz Düzeni
st.subheader(f"Seviye: {st.session_state.current_word['level']}")
st.info(f"Bu kelimenin anlamı nedir? **{st.session_state.current_word['de']}**")

if st.button("Cevabı Göster"):
    st.session_state.show_answer = True

if st.session_state.show_answer:
    st.success(f"Türkçesi: **{st.session_state.current_word['tr']}**")

if st.button("Yeni Kelime Getir"):
    st.session_state.current_word = random.choice(st.session_state.words)
    st.session_state.show_answer = False
    st.rerun()

# İstatistikler
st.sidebar.write(f"Toplam Kelime Sayısı: {len(st.session_state.words)}")
