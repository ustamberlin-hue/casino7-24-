import streamlit as st
import time

st.set_page_config(page_title="Sanal İmam", page_icon="🕌")

def imam_seslendir(metin):
    # pitch: 0.4 ve rate: 0.7 ile camideki hocaların o meşhur tok ve ağır sesini simüle eder.
    html_kodu = f"""
    <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance('{metin}');
        msg.lang = 'tr-TR';
        msg.rate = 0.7; 
        msg.pitch = 0.4; 
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(html_kodu, height=0)

st.title("🕌 Sanal İmam Namaz Hocası")
st.info("İmamın 'Allâhu Ekber' komutlarını duyduğunuzda hareket edin. Telefonu seccadenin önüne koyun.")

vakit = st.selectbox("Vakit Seçin:", ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"])

# TÜM DUALAR VE SURELER (Eksiksiz)
dualar = {
    "Niyet": "Niyet ettim Allah rızası için bugünkü namazı kılmaya.",
    "Tekbir": "Allâhu Ekber",
    "Subhaneke": "Sübhânekellâhümme ve bi hamdik ve tebârakesmük ve teâlâ ceddük ve lâ ilâhe ğayrük.",
    "Fatiha": "Elhamdülillâhi rabbilâlemîn. Errahmânirrahîm. Mâliki yevmiddîn. İyyâke na'büdü ve iyyâke nestaîn. İhdinassırâtel müstakîm. Sırâtallezîne en'amte aleyhim ğayrilmağdûbi aleyhim veleddâllîn. Âmîn.",
    "Sure1": "Bismillâhirrahmânirrahîm. Kul hüvallahü ehad. Allahüssamed. Lem yelid ve lem yüled. Ve lem yekün lehü küfüven ehad.",
    "Sure2": "Bismillâhirrahmânirrahîm. İnna a'taynakel kevser. Fesalli lirabbike venhar. İnne şânieke hüvel ebter.",
    "Ruku_Tesbih": "Sübhâne rabbiyel azîm. Sübhâne rabbiyel azîm. Sübhâne rabbiyel azîm.",
    "Kavme": "Semi Allâhu limen hamideh. Rabbenâ lekel hamd.",
    "Secde_Tesbih": "Sübhâne rabbiyel alâ. Sübhâne rabbiyel alâ. Sübhâne rabbiyel alâ.",
    "Tahiyyat": "Ettehiyyâtü lillâhi vessalevâtü vettayyibât. Esselâmü aleyke eyyühen-nebiyyü ve rahmetüllâhi ve berekâtüh. Esselâmü aleynâ ve alâ ibâdillâhis-salihîn. Eşhedü en lâ ilâhe illallâh ve eşhedü enne Muhammeden abdühû ve rasûlüh.",
    "SalliBarik": "Allahümme salli ala Muhammed. Allahümme barik ala Muhammed.",
    "Rabbena": "Rabbena atina fiddünya haseneten ve fil ahireti haseneten ve kına azabennar.",
    "Selam": "Esselâmü aleyküm ve rahmetullâh."
}

if st.button(f"{vakit} Namazını Başlat"):
    rekat_sayisi = {"Sabah": 2, "Öğle": 4, "İkindi": 4, "Akşam": 3, "Yatsı": 4}[vakit]
    
    for r in range(1, rekat_sayisi + 1):
        st.subheader(f"📿 {r}. Rekat")
        
        # Başlangıç
        if r == 1:
            imam_seslendir(dualar["Niyet"])
            time.sleep(5)
            imam_seslendir(dualar["Tekbir"])
            time.sleep(3)
            imam_seslendir(dualar["Subhaneke"])
            time.sleep(7)

        # Kıyam (Okuma)
        imam_seslendir(dualar["Fatiha"])
        time.sleep(18)
        zamm_i_sure = dualar["Sure1"] if r % 2 != 0 else dualar["Sure2"]
        imam_seslendir(zamm_i_sure)
        time.sleep(12)

        # RÜKÛ VE KAVME
        imam_seslendir(dualar["Tekbir"]) # Rükuya eğilirken
        time.sleep(2)
        imam_seslendir(dualar["Ruku_Tesbih"])
        time.sleep(8)
        imam_seslendir(dualar["Kavme"]) # Rükudan doğrulurken (Kavme)
        time.sleep(5)

        # SECDELER
        for s in range(1, 3):
            imam_seslendir(dualar["Tekbir"]) # Secdeye giderken
            time.sleep(2)
            imam_seslendir(dualar["Secde_Tesbih"])
            time.sleep(10)
            imam_seslendir(dualar["Tekbir"]) # Secdeden kalkarken
            time.sleep(3)

        # OTURUŞLAR
        if r == 2 or r == rekat_sayisi:
            st.write("📌 Oturuş duaları...")
            imam_seslendir(dualar["Tahiyyat"])
            time.sleep(12)
            if r == rekat_sayisi:
                imam_seslendir(dualar["SalliBarik"])
                time.sleep(12)
                imam_seslendir(dualar["Rabbena"])
                time.sleep(10)
                # Selamlar
                imam_seslendir(dualar["Selam"])
                time.sleep(4)
                imam_seslendir(dualar["Selam"])
                st.success("Namaz bitti. Allah kabul etsin.")
    st.balloons()
