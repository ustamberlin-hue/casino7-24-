import streamlit as st
import time

# Sayfa tasarımı
st.set_page_config(page_title="Sanal Namaz Hocası", page_icon="🕌", layout="wide")

st.title("🕌 5 Vakit Sanal Namaz Hocası")
st.write("Vakti seçin, 'Namazı Başlat' butonuna basın ve Hocayı takip edin.")

# 5 Vakit Seçimi
vakit = st.selectbox("Kılmak istediğiniz namazı seçin:", 
                     ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"])

# Namazların Rekat Yapısı
rekatlar = {
    "Sabah": ["Sünnet (2 rekat)", "Farz (2 rekat)"],
    "Öğle": ["İlk Sünnet (4)", "Farz (4)", "Son Sünnet (2)"],
    "İkindi": ["Sünnet (4)", "Farz (4)"],
    "Akşam": ["Farz (3)", "Sünnet (2)"],
    "Yatsı": ["İlk Sünnet (4)", "Farz (4)", "Son Sünnet (2)", "Vitir (3)"]
}

# --- MEDYA LİNKLERİ ---
# Not: Buradaki linkleri gerçek namaz videoları ve sesleri ile güncelleyebilirsin.
# Mevcut linkler sistemin çalışmasını test etmen içindir.
HOCA_VIDEO = "https://www.w3schools.com/html/mov_bbb.mp4" 
HOCA_SES = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

if st.button(f"{vakit} Namazını Başlat"):
    st.success(f"{vakit} namazı rehberliği başladı. Allah kabul etsin.")
    
    for bolum in rekatlar[vakit]:
        st.header(f"📿 Bölüm: {bolum}")
        
        # Temel Namaz Akışı (Hoca bu sırayla hareket eder)
        akis = ["Niyet ve Tekbir", "Kıyam (Fatiha ve Sure)", "Rüku", "Secde", "Tahiyyat (Oturuş)"]
        
        for adim in akis:
            st.subheader(f"📍 Şu an: {adim}")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.video(HOCA_VIDEO) # Hoca hareketi
            with col2:
                st.audio(HOCA_SES, autoplay=True) # Hoca sesi
                st.write(f"Lütfen hoca ile birlikte {adim} yapın.")
            
            # Senin hareketleri tamamlaman için bekleme süresi
            time.sleep(10) 
            st.divider()

    st.balloons()
    st.success(f"{vakit} namazı tamamlandı!")
