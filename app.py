import streamlit as st

st.set_page_config(page_title="Sanal Namaz Hocası", page_icon="🕌", layout="centered")

st.title("🕌 Sanal Namaz Hocası")
st.write("Vakti seçin ve Hocayı tam ekran izleyerek namazınızı kılın.")

# 5 Vakit Seçimi
vakit = st.selectbox("Namaz Vakti Seçin:", ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"])

# GERÇEK NAMAZ EĞİTİM VİDEOLARI (Her vakit için ayrı tam video)
# Bu videolar niyetten selama kadar her şeyi içerir.
namaz_videolari = {
    "Sabah": "https://www.youtube.com/watch?v=kYv_86t06tI",
    "Öğle": "https://www.youtube.com/watch?v=S-t14Xunp80",
    "İkindi": "https://www.youtube.com/watch?v=9S_9xI9-6vU",
    "Akşam": "https://www.youtube.com/watch?v=7uK3F8LgUf8",
    "Yatsı": "https://www.youtube.com/watch?v=n-W2m-tX6yM"
}

if st.button(f"{vakit} Namazını Başlat"):
    st.success(f"{vakit} namazı rehberliği yüklendi. Lütfen hocayı takip edin.")
    
    # YouTube videosunu doğrudan gömüyoruz (Bu yöntem siyah ekran sorununu çözer)
    st.video(namaz_videolari[vakit])
    
    st.info("💡 İpucu: Videoyu tam ekran yapıp sesini açarak seccadenin önüne koyabilirsiniz.")
    st.balloons()
