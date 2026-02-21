import streamlit as st
import time

st.set_page_config(page_title="Makamlı Namaz Hocası", page_icon="🕌")

def hoca_seslendir(metin):
    # Ses tonu ve hızı dinlediğin hocaya benzetildi (Ağır ve Vakur)
    html_kodu = f"""
    <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance('{metin}');
        msg.lang = 'tr-TR';
        msg.rate = 0.65; 
        msg.pitch = 0.9; 
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(html_kodu, height=0)

st.title("🕌 Sanal İmam (Makamlı Okuyuş)")
st.info("📍 KONUM bilgisini takip edin ve hocanın komutuyla hareket edin.")

vakit = st.selectbox("Vakit Seçin:", ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"])

# MAKAMA UYGUN FONETİK ARAPÇA (Ses dosyasındaki ritimle)
dualar = {
    "Niyet": "Niyet ettim Allah rızası için namaz kılmaya.",
    "Tekbir": "Allâââhu Ekber",
    "Subhaneke": "Sübhâânekellââ hümme ve bi hamdik. Ve tebââ rakesmük. Ve teââ lâ ceddük. Ve lââ ilââhe ğayrük.",
    "Fatiha": "Elhamdülillââhi rabbil ââlemîîn. Errahmâânirrahîîm. Mââliki yevmiddîîn. İyyââke na'büdü ve iyyââke nestaîîn. İhdinassırââtel müstakîîm. Sırââtallezîîne en'amte aleyhim. Ğayril mağdûûbi aleyhim veleddââââllîîn. Âââmîîn.",
    "Sure1": "Bismillââhir rahmâânir rahîîm. Kul hüvallââhu ehad. Allââhüs samed. Lem yelid ve lem yüüled. Ve lem yekün lehüü küfüven ehad.",
    "Ruku_Gidis": "Allahu Ekber rükûya.",
    "Ruku_Tesbih": "Sübhââne rabbiyel azîîm. Sübhââne rabbiyel azîîm. Sübhââne rabbiyel azîîm.",
    "Kavme": "Semi Allââhu limen hamideh. Rabbenââ lekel hamd. Doğrulun.",
    "Secde_Gidis": "Allahu Ekber secdeye.",
    "Secde_Tesbih": "Sübhââne rabbiyel alââ. Sübhââne rabbiyel alââ. Sübhâne rabbiyel alââ.",
    "Tahiyyat": "Ettehiyyââtü lillââhi vessalevââtü vettayyibâât. Esselââmu aleyke eyyühen nebiyyü ve rahmetüllââhi ve berekââtüh. Esselââmu aleynââ ve alââ ibââdillâhis sââlihîîn. Eşhedü en lââ ilââhe illallââh. Ve eşhedü enne Muhammeden abdühüü ve rasûûlüh.",
    "SalliBarik": "Allââhümme salli alââ Muhammed. Allââhümme bâârik alââ Muhammed.",
    "Rabbena": "Rabbenââ ââti nââ fiddünyââ haseneten ve fil ââhireti haseneten ve kınââ azââ bennââr.",
    "Selam": "Esselââmu aleyküm ve rahmetullââhh."
}

if st.button("Namazı Başlat"):
    rekatlar = {"Sabah": 2, "Öğle": 4, "İkindi": 4, "Akşam": 3, "Yatsı": 4}[vakit]
    
    for r in range(1, rekatlar + 1):
        st.markdown(f"### 📍 KONUM: {r}. Rekat - AYAKTA")
        if r == 1:
            hoca_seslendir(dualar["Niyet"])
            time.sleep(5)
            hoca_seslendir(dualar["Tekbir"])
            time.sleep(4)
            hoca_seslendir(dualar["Subhaneke"])
            time.sleep(10)

        hoca_seslendir(dualar["Fatiha"])
        time.sleep(22) # Ağır okuma süresi
        hoca_seslendir(dualar["Sure1"])
        time.sleep(12)

        # RÜKÛ VE KAVME
        st.markdown("### 📍 KONUM: RÜKÛ")
        hoca_seslendir(dualar["Ruku_Gidis"])
        time.sleep(3)
        hoca_seslendir(dualar["Ruku_Tesbih"])
        time.sleep(10)
        
        st.markdown("### 📍 KONUM: DOĞRUL (KAVME)")
        hoca_seslendir(dualar["Kavme"])
        time.sleep(6)

        # SECDE
        for s in range(1, 3):
            st.markdown(f"### 📍 KONUM: {s}. SECDE")
            hoca_seslendir(dualar["Secde_Gidis"])
            time.sleep(3)
            hoca_seslendir(dualar["Secde_Tesbih"])
            time.sleep(12)
            hoca_seslendir(dualar["Tekbir"]) # Kalkış
            time.sleep(4)

        # OTURUŞ
        if r == 2 or r == rekatlar:
            st.markdown("### 📍 KONUM: OTURUŞ")
            hoca_seslendir(dualar["Tahiyyat"])
            time.sleep(15)
            if r == rekatlar:
                hoca_seslendir(dualar["SalliBarik"])
                time.sleep(15)
                hoca_seslendir(dualar["Rabbena"])
                time.sleep(12)
                st.markdown("### 📍 KONUM: SELAM")
                hoca_seslendir(dualar["Selam"])
                time.sleep(5)
                hoca_seslendir(dualar["Selam"])

    st.balloons()
