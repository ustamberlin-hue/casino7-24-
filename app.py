import streamlit as st
import time

st.set_page_config(page_title="Hoca ile Tam Namaz", page_icon="🕌")

def hoca_seslendir(metin):
    # pitch: 0.5 ile sesi en kalın (bas) seviyeye çektim, tam bir erkek hoca sesi olur.
    html_kodu = f"""
    <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance('{metin}');
        msg.lang = 'tr-TR';
        msg.rate = 0.75; 
        msg.pitch = 0.5; 
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(html_kodu, height=0)

st.title("🕌 Sanal İmam Namaz Hocası")
st.write("Vakti seçin, niyetinizi edin ve hocanın 'Allahu Ekber' komutlarıyla hareket edin.")

vakit = st.selectbox("Namaz Vakti:", ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"])

# GERÇEK NAMAZ AKIŞI
dualar = {
    "Niyet": "Niyet ettim Allah rızası için bugünkü namazı kılmaya.",
    "Tekbir": "Allahu Ekber",
    "Subhaneke": "Sübhânekellâhümme ve bi hamdik ve tebârakesmük ve teâlâ ceddük ve lâ ilâhe ğayrük.",
    "Fatiha": "Elhamdülillâhi rabbilâlemîn. Errahmânirrahîm. Mâliki yevmiddîn. İyyâke na'büdü ve iyyâke nestaîn. İhdinassırâtel müstakîm. Sırâtallezîne en'amte aleyhim ğayrilmağdûbi aleyhim veleddâllîn. Amin.",
    "Sure1": "Bismillâhirrahmânirrahîm. Kul hüvallahü ehad. Allahüssamed. Lem yelid ve lem yüled. Ve lem yekün lehü küfüven ehad.",
    "Sure2": "Bismillâhirrahmânirrahîm. İnna a'taynakel kevser. Fesalli lirabbike venhar. İnne şânieke hüvel ebter.",
    "Rüku_Gidis": "Allahu Ekber",
    "Rüku_Tesbih": "Sübhâne rabbiyel azîm. Sübhâne rabbiyel azîm. Sübhâne rabbiyel azîm.",
    "Rüku_Donus": "Semi Allahu limen hamideh. Rabbena lekel hamd.",
    "Secde_Gidis": "Allahu Ekber",
    "Secde_Tesbih": "Sübhâne rabbiyel alâ. Sübhâne rabbiyel alâ. Sübhâne rabbiyel alâ.",
    "Secde_Kalkis": "Allahu Ekber",
    "Tahiyyat": "Ettehiyyâtü lillâhi vessalevâtü vettayyibât. Esselâmü aleyke eyyühen-nebiyyü ve rahmetüllâhi ve berekâtüh. Esselâmü aleynâ ve alâ ibâdillâhis-salihîn. Eşhedü en lâ ilâhe illallâh ve eşhedü enne Muhammeden abdühû ve rasûlüh.",
    "SalliBarik": "Allahümme salli ala Muhammed. Allahümme barik ala Muhammed.",
    "Rabbena": "Rabbena atina fiddünya haseneten ve fil ahireti haseneten ve kına azabennar.",
    "Selam": "Esselâmü aleyküm ve rahmetullâh. Esselâmü aleyküm ve rahmetullâh."
}

if st.button(f"{vakit} Namazını Başlat"):
    rekat_sayilari = {"Sabah": 2, "Öğle": 4, "İkindi": 4, "Akşam": 3, "Yatsı": 4}
    toplam = rekat_sayilari[vakit]
    
    for r in range(1, toplam + 1):
        st.subheader(f"📿 {r}. Rekat")
        
        if r == 1:
            hoca_seslendir(dualar["Niyet"])
            time.sleep(5)
            hoca_seslendir(dualar["Tekbir"])
            time.sleep(3)
            hoca_seslendir(dualar["Subhaneke"])
            time.sleep(7)

        # Ayakta Okuma
        st.info("Kıyam: Fatiha ve Sure okunuyor...")
        hoca_seslendir(dualar["Fatiha"])
        time.sleep(18)
        zamm_i_sure = dualar["Sure1"] if r % 2 != 0 else dualar["Sure2"]
        hoca_seslendir(zamm_i_sure)
        time.sleep(10)

        # RÜKU SÜRECİ
        st.warning("Rükuya gidiliyor...")
        hoca_seslendir(dualar["Rüku_Gidis"]) # Allahu Ekber
        time.sleep(2)
        hoca_seslendir(dualar["Rüku_Tesbih"])
        time.sleep(8)
        hoca_seslendir(dualar["Rüku_Donus"]) # Semi Allahu...
        time.sleep(5)

        # SECDE SÜRECİ (1. SECDE)
        st.warning("1. Secdeye gidiliyor...")
        hoca_seslendir(dualar["Secde_Gidis"]) # Allahu Ekber
        time.sleep(2)
        hoca_seslendir(dualar["Secde_Tesbih"])
        time.sleep(10)
        hoca_seslendir(dualar["Secde_Kalkis"]) # Allahu Ekber (Ara oturuş)
        time.sleep(3)

        # SECDE SÜRECİ (2. SECDE)
        st.warning("2. Secdeye gidiliyor...")
        hoca_seslendir(dualar["Secde_Gidis"]) # Allahu Ekber
        time.sleep(2)
        hoca_seslendir(dualar["Secde_Tesbih"])
        time.sleep(10)
        
        # Secdeden Kalkış
        if r < toplam:
            hoca_seslendir(dualar["Secde_Kalkis"]) # Allahu Ekber (Yeni rekata kalkış)
            st.write("--- Sonraki rekata kalkılıyor ---")
            time.sleep(4)

        # OTURUŞLAR
        if r == 2 or r == toplam:
            st.error("Oturuş...")
            hoca_seslendir(dualar["Secde_Kalkis"]) # Allahu Ekber (Oturuş için)
            time.sleep(2)
            hoca_seslendir(dualar["Tahiyyat"])
            time.sleep(12)
            
            if r == toplam:
                hoca_seslendir(dualar["SalliBarik"])
                time.sleep(12)
                hoca_seslendir(dualar["Rabbena"])
                time.sleep(10)
                hoca_seslendir(dualar["Selam"])
                st.success("Namaz bitti. Allah kabul etsin.")
    st.balloons()
