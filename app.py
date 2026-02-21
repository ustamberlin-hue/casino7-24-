import streamlit as st
import time

st.set_page_config(page_title="AI Namaz Hocası", page_icon="🕌")

# Tarayıcı tabanlı Yapay Zeka Seslendirme Fonksiyonu
def sesli_oku(metin):
    html_kodu = f"""
    <script>
        var msg = new SpeechSynthesisUtterance('{metin}');
        msg.lang = 'tr-TR';
        msg.rate = 0.85; 
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(html_kodu, height=0)

st.title("🕌 Yapay Zeka Sesli Namaz Hocası")
st.write("Vakti seçin ve sadece hocanın sesini takip edin.")

vakit = st.selectbox("Namaz Vakti:", ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"])

# TÜM DUALAR VE SURELER (Eksiksiz Liste)
dualar = {
    "Niyet": "Niyet ettim Allah rızası için bugünkü namazı kılmaya. Allahu Ekber.",
    "Subhaneke": "Sübhânekellâhümme ve bi hamdik ve tebârakesmük ve teâlâ ceddük ve lâ ilâhe ğayrük.",
    "Fatiha": "Elhamdülillâhi rabbilâlemîn. Errahmânirrahîm. Mâliki yevmiddîn. İyyâke na'büdü ve iyyâke nestaîn. İhdinassırâtel müstakîm. Sırâtallezîne en'amte aleyhim ğayrilmağdûbi aleyhim veleddâllîn. Amin.",
    "Sure": "Kul hüvallâhü ehad. Allâhüssamed. Lem yelid ve lem yûled. Ve lem yekün lehû küfüven ehad.",
    "Rüku": "Sübhâne rabbiyel azîm. Sübhâne rabbiyel azîm. Sübhâne rabbiyel azîm. Semi Allahu limen hamideh. Rabbena lekel hamd.",
    "Secde": "Sübhâne rabbiyel alâ. Sübhâne rabbiyel alâ. Sübhâne rabbiyel alâ.",
    "Tahiyyat": "Ettehiyyâtü lillâhi vessalevâtü vettayyibât. Esselâmü aleyke eyyühen-nebiyyü ve rahmetüllâhi ve berekâtüh. Esselâmü aleynâ ve alâ ibâdillâhis-salihîn. Eşhedü en lâ ilâhe illallâh ve eşhedü enne Muhammeden abdühû ve rasûlüh.",
    "SalliBarik": "Allahümme salli ala Muhammed. Allahümme barik ala Muhammed.",
    "Rabbena": "Rabbena atina fiddünya haseneten ve fil ahireti haseneten ve kına azabennar.",
    "Selam": "Esselâmü aleyküm ve rahmetullâh. Esselâmü aleyküm ve rahmetullâh."
}

if st.button(f"{vakit} Namazını Başlat"):
    # Her vakit için rekat sayısı
    rekat_sayilari = {"Sabah": 2, "Öğle": 4, "İkindi": 4, "Akşam": 3, "Yatsı": 4}
    toplam_rekat = rekat_sayilari[vakit]
    
    st.success(f"{vakit} namazı ({toplam_rekat} rekat) başlıyor...")

    for r in range(1, toplam_rekat + 1):
        st.subheader(f"📿 {r}. Rekat")
        
        # 1. Rekat Başlangıcı
        if r == 1:
            st.info("Niyet ve Tekbir getiriliyor...")
            sesli_oku(dualar["Niyet"])
            time.sleep(6)
            sesli_oku(dualar["Subhaneke"])
            time.sleep(7)

        # Ayakta Okuma (Kıyam)
        st.info("Fatiha ve Sure okunuyor...")
        sesli_oku(dualar["Fatiha"])
        time.sleep(18)
        sesli_oku(dualar["Sure"])
        time.sleep(10)

        # Rüku ve Secde
        st.info("Rüku ve Secde yapılıyor...")
        sesli_oku(dualar["Rüku"])
        time.sleep(10)
        sesli_oku(dualar["Secde"])
        time.sleep(12)

        # Ara ve Son Oturuşlar
        # (Öğle, İkindi, Yatsı'da 2. rekatta oturulur. Akşam'da 2. ve 3. rekatta oturulur.)
        if r == 2 or r == toplam_rekat:
            st.info("Oturuş duaları okunuyor...")
            sesli_oku(dualar["Tahiyyat"])
            time.sleep(12)
            
            # Eğer namazın en sonu ise
            if r == toplam_rekat:
                sesli_oku(dualar["SalliBarik"])
                time.sleep(12)
                sesli_oku(dualar["Rabbena"])
                time.sleep(10)
                sesli_oku(dualar["Selam"])
                st.success("Namaz bitti. Allah kabul etsin.")
    
    st.balloons()
