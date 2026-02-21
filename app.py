import streamlit as st
import time

st.set_page_config(page_title="Hoca ile Tam Namaz", page_icon="🕌")

def hoca_seslendir(metin):
    # pitch: 0.6 ve rate: 0.8 ile sesi olabildiğince kalın ve hoca edasında erkek sesi yapar
    html_kodu = f"""
    <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance('{metin}');
        msg.lang = 'tr-TR';
        msg.rate = 0.8; 
        msg.pitch = 0.6; 
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(html_kodu, height=0)

st.title("🕌 Sanal Erkek Namaz Hocası")
st.write("Vakti seçin, telefonu seccadenin önüne koyun ve sadece hocayı takip edin.")

vakit = st.selectbox("Hangi Namazı Kılacaksınız?", ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"])

# GERÇEK NAMAZ SURE VE DUALARI
dualar = {
    "Niyet": "Niyet ettim Allah rızası için bugünkü namazı kılmaya. Allahu Ekber.",
    "Subhaneke": "Sübhânekellâhümme ve bi hamdik ve tebârakesmük ve teâlâ ceddük ve lâ ilâhe ğayrük.",
    "Fatiha": "Elhamdülillâhi rabbilâlemîn. Errahmânirrahîm. Mâliki yevmiddîn. İyyâke na'büdü ve iyyâke nestaîn. İhdinassırâtel müstakîm. Sırâtallezîne en'amte aleyhim ğayrilmağdûbi aleyhim veleddâllîn. Amin.",
    "Fil": "Elem tera keyfe feale rabbüke biashâbil fîl. Elem yec’al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bihicâratin min siccîl. Fecealehüm keasfin me’kûl.",
    "Kureys": "Liî lâfi kurayş. Îlâfihim rihleteşşitâi vessayf. Felya'büdû rabbe hâzelbeyt. Ellezî et'amehüm min cû'in ve âmenehüm min havf.",
    "Maun": "Eraeytellezî yükezzibü biddîn. Fezâlikellezî yedü'ulyetîm. Ve lâ yehuddu alâ taâmil miskîn. Feveylün lilmusallîn. Ellezîne hüm an salâtihim sâhûn. Ellezîne hüm yürâûn. Ve yemneûnel mâûn.",
    "Kevser": "İnnâ a'taynâkel kevser. Fesalli lirabbike venhar. İnne şânieke hüvel ebter.",
    "Rüku": "Sübhâne rabbiyel azîm. Sübhâne rabbiyel azîm. Sübhâne rabbiyel azîm. Semi Allahu limen hamideh. Rabbena lekel hamd.",
    "Secde": "Sübhâne rabbiyel alâ. Sübhâne rabbiyel alâ. Sübhâne rabbiyel alâ.",
    "Tahiyyat": "Ettehiyyâtü lillâhi vessalevâtü vettayyibât. Esselâmü aleyke eyyühen-nebiyyü ve rahmetüllâhi ve berekâtüh. Esselâmü aleynâ ve alâ ibâdillâhis-salihîn. Eşhedü en lâ ilâhe illallâh ve eşhedü enne Muhammeden abdühû ve rasûlüh.",
    "SalliBarik": "Allahümme salli ala Muhammed. Allahümme barik ala Muhammed.",
    "Rabbena": "Rabbena atina fiddünya haseneten ve fil ahireti haseneten ve kına azabennar.",
    "Selam": "Esselâmü aleyküm ve rahmetullâh. Esselâmü aleyküm ve rahmetullâh."
}

# Sure Sıralaması (Rekatlara göre farklı sure okumak için)
sure_listesi = ["Fil", "Kureys", "Maun", "Kevser"]

if st.button(f"{vakit} Namazını Başlat"):
    # Rekat sayıları: Sabah (2), Öğle (4), İkindi (4), Akşam (3), Yatsı (4)
    rekat_plani = {"Sabah": 2, "Öğle": 4, "İkindi": 4, "Akşam": 3, "Yatsı": 4}
    toplam = rekat_plani[vakit]
    
    for r in range(1, toplam + 1):
        st.subheader(f"📿 {r}. Rekat")
        
        # 1. Rekatta Niyet ve Subhaneke
        if r == 1:
            hoca_seslendir(dualar["Niyet"])
            time.sleep(6)
            hoca_seslendir(dualar["Subhaneke"])
            time.sleep(7)

        # Her rekatta Fatiha
        hoca_seslendir(dualar["Fatiha"])
        time.sleep(18)
        
        # Zamm-ı Sure (Farz namazın ilk 2 rekatında, sünnetlerin her rekatında okunur)
        # Burada her rekat için farklı bir sure seçiyoruz
        secilen_sure = sure_listesi[r-1] if r <= 4 else "Kevser"
        hoca_seslendir(dualar[secilen_sure])
        time.sleep(10)

        # Rüku ve Secde (Tesbihatlar dahil)
        st.info("Rüku ve Secde yapılıyor...")
        hoca_seslendir(dualar["Rüku"])
        time.sleep(12)
        hoca_seslendir(dualar["Secde"])
        time.sleep(15)

        # Oturuş Mantığı
        # 2. rekatta (Ara oturuş) veya en son rekatta (Son oturuş)
        if r == 2 or r == toplam:
            st.warning("Oturuş ve Dualar...")
            hoca_seslendir(dualar["Tahiyyat"])
            time.sleep(12)
            
            if r == toplam:
                hoca_seslendir(dualar["SalliBarik"])
                time.sleep(12)
                hoca_seslendir(dualar["Rabbena"])
                time.sleep(10)
                hoca_seslendir(dualar["Selam"])
                st.success("Namazınız bitti. Allah kabul etsin.")
    st.balloons()
