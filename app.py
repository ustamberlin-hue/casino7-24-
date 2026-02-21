import streamlit as st
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="Sanal Namaz Hocası", page_icon="🕌", layout="wide")

st.title("🕌 5 Vakit Sanal Namaz Hocası")
st.write("Telefonu sabitleyin, sesini açın ve Hocayı takip edin.")

# 5 Vakit Seçimi
vakit = st.sidebar.selectbox("Kılmak istediğiniz namazı seçin:", 
                     ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"])

# --- MEDYA HAVUZU (Hoca Buradan Besleniyor) ---
# Buradaki linkler internetteki hazır namaz eğitim videolarından çekilir.
MEDYA = {
    "Kıyam": {"video": "https://www.w3schools.com/html/mov_bbb.mp4", "ses": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"},
    "Rüku": {"video": "https://www.w3schools.com/html/mov_bbb.mp4", "ses": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"},
    "Secde": {"video": "https://www.w3schools.com/html/mov_bbb.mp4", "ses": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"}
}

if st.button(f"{vakit} Namazını Başlat"):
    st.success(f"{vakit} namazı kılınışı başlıyor... Lütfen niyet edin.")
    
    # Namaz Akış Döngüsü
    akis = ["Kıyam", "Rüku", "Secde", "Secde", "Kıyam"] # Örnek 1 rekat
    
    for adim in akis:
        st.subheader(f"📍 Bölüm: {adim}")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.video(MEDYA[adim]["video"]) # Hocanın görseli
        with col2:
            st.audio(MEDYA[adim]["ses"], autoplay=True) # Hocanın sesi
            st.write(f"Hoca şimdi {adim} halini gösteriyor.")
        
        time.sleep(8) # Senin yetişmen için bekleme süresi
        st.divider()

    st.balloons()
    st.success("Namaz bitti. Allah kabul etsin!")
