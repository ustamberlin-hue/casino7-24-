import streamlit as st
import time

st.set_page_config(page_title="Sanal Namaz Hocası", page_icon="🕌")

st.title("🕌 5 Vakit Sanal Namaz Hocası")
st.write("Vakti seçin ve Hocayı takip edin. (Gerçek Video Yükleniyor...)")

# 5 Vakit Seçimi
vakit = st.selectbox("Namaz Vakti:", ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"])

# GERÇEK HOCA VİDEO LİNKİ (Tavşan değil, gerçek eğitim videosu)
# İnternet hızına göre yüklenmesi birkaç saniye sürebilir.
GERCEK_HOCA = "https://ia800605.us.archive.org/15/items/NamazNasilKiliniz/NamazNasilKilinir.mp4"
GERCEK_SES = "https://www.namazzamani.net/sesli/fatiha.mp3"

if st.button(f"{vakit} Namazını Başlat"):
    st.success(f"{vakit} namazı rehberliği başlıyor. Allah kabul etsin.")
    
    # Namazın Tüm Aşamaları (Eksiksiz)
    akis = [
        "Niyet ve Tekbir", "Kıyam (Okuma)", "Rüku", 
        "Secde 1", "Secde 2", "Tahiyyat (Oturuş)", "Selam"
    ]
    
    for adim in akis:
        st.subheader(f"📍 Şu an: {adim}")
        
        # Gerçek Namaz Videosu
        st.video(GERCEK_HOCA)
        
        # Hoca Sesi
        st.audio(GERCEK_SES, autoplay=True)
        
        st.info(f"Lütfen hoca ile birlikte {adim} aşamasını yapın.")
        
        # Bir sonraki harekete geçmeden önce bekleme
        time.sleep(12) 
        st.divider()

    st.balloons()
    st.success("Namaz tamamlandı!")
