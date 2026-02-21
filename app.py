import streamlit as st
import time

st.set_page_config(page_title="Sesli Namaz Hocası", page_icon="🕌")

st.title("🕌 Tam Sesli Namaz Hocası")
st.write("Vakti seçin ve sadece hocanın sesli dualarını takip edin.")

# 5 Vakit Seçimi
vakit = st.selectbox("Namaz Vakti Seçin:", ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"])

# DUA VE SURE SES LİNKLERİ
# Namazda okunan tüm duaların ses dosyaları
DUALAR = {
    "Tekbir": "https://www.namazzamani.net/sesli/tekbir.mp3",
    "Sübhaneke": "https://www.namazzamani.net/sesli/subhaneke.mp3",
    "Fatiha": "https://www.namazzamani.net/sesli/fatiha.mp3",
    "Sure": "https://www.namazzamani.net/sesli/ihlas.mp3", # Örnek: İhlas suresi
    "Rüku": "https://www.namazzamani.net/sesli/ruku_tesbih.mp3",
    "Secde": "https://www.namazzamani.net/sesli/secde_tesbih.mp3",
    "Tahiyyat": "https://www.namazzamani.net/sesli/ettehiyyatu.mp3",
    "SalliBarik": "https://www.namazzamani.net/sesli/sallibarik.mp3",
    "Rabbena": "https://www.namazzamani.net/sesli/rabbena.mp3",
    "Selam": "https://www.namazzamani.net/sesli/selam.mp3"
}

# Namaz Akış Mantığı (Rekat sayıları ve okunacaklar)
def namaz_kil(vakit_adi, rekat_sayisi):
    for rekat in range(1, rekat_sayisi + 1):
        st.subheader(f"📿 {rekat}. Rekat")
        
        # 1. Başlangıç (Sadece 1. Rekatta)
        if rekat == 1:
            st.write("Niyet ve Tekbir...")
            st.audio(DUALAR["Tekbir"], autoplay=True)
            time.sleep(3)
            st.audio(DUALAR["Sübhaneke"], autoplay=True)
            time.sleep(5)
            
        # 2. Ayakta Okuma
        st.write("Fatiha ve Sure okunuyor...")
        st.audio(DUALAR["Fatiha"], autoplay=True)
        time.sleep(15)
        st.audio(DUALAR["Sure"], autoplay=True)
        time.sleep(10)
        
        # 3. Rüku ve Secde
        st.write("Rüku...")
        st.audio(DUALAR["Rüku"], autoplay=True)
        time.sleep(7)
        st.write("Secde...")
        st.audio(DUALAR["Secde"], autoplay=True)
        time.sleep(10)
        
        # 4. Oturuş (Son rekatta veya her 2 rekatta bir)
        if rekat == rekat_sayisi or rekat % 2 == 0:
            st.write("Oturuş ve Dualar...")
            st.audio(DUALAR["Tahiyyat"], autoplay=True)
            time.sleep(10)
            if rekat == rekat_sayisi:
                st.audio(DUALAR["SalliBarik"], autoplay=True)
                time.sleep(10)
                st.audio(DUALAR["Rabbena"], autoplay=True)
                time.sleep(10)
                st.audio(DUALAR["Selam"], autoplay=True)
                st.success("Namaz Tamamlandı.")

if st.button(f"{vakit} Namazını Başlat"):
    plan = {"Sabah": 2, "Öğle": 4, "İkindi": 4, "Akşam": 3, "Yatsı": 4}
    namaz_kil(vakit, plan[vakit])
    st.balloons()
