import streamlit as st
import time

st.set_page_config(page_title="Namaz Rehberi", page_icon="🕌")

def hoca_seslendir(metin):
    # rate: 0.9 (Daha akıcı ve hızlı), pitch: 1.2 (Net kadın sesi)
    html_kodu = f"""
    <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance('{metin}');
        msg.lang = 'tr-TR';
        msg.rate = 0.9; 
        msg.pitch = 1.2; 
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(html_kodu, height=0)

st.title("🕌 Akıcı Namaz Rehberi")
st.write("📍 **KONUM** bilgisini takip ederek hareketlerinizi yapın.")

vakit = st.selectbox("Vakit Seçin:", ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"])

# AKICI ARAPÇA OKUNUŞLAR (Fonetik İyileştirme)
dualar = {
    "Niyet": "Niyet ettim Allah rızası için namaz kılmaya.",
    "Tekbir": "Allahu Ekber",
    "Subhaneke": "Sübhanekellahümme ve bihamdik. Ve tebarekesmük. Ve teala ceddük. Ve lailahe gayrük.",
    "Fatiha": "Elhamdülillahi rabbil alemin. Errahmanirrahim. Maliki yevmiddin. İyyake nabüdü ve iyyake nestain. İhdinassıratel müstakim. Sıratallezine enamte aleyhim. Gayril magdubi aleyhim veleddallin. Amin.",
    "Sure1": "Bismillahir rahmanir rahim. Kul hüvallahü ehad. Allahüssamed. Lem yelid ve lem yüled. Ve lem yekün lehü küfüven ehad.",
    "Ruku_Tesbih": "Sübhane rabbiyel azim. Sübhane rabbiyel azim. Sübhane rabbiyel azim.",
    "Kavme": "Semi Allahü limen hamideh. Rabbena lekel hamd.",
    "Secde_Tesbih": "Sübhane rabbiyel ala. Sübhane rabbiyel ala. Sübhane rabbiyel ala.",
    "Tahiyyat": "Ettehiyyatü lillahi vessalevatü vettayyibat. Esselamü aleyke eyyühen nebiyyü ve rahmetüllahi ve berekatüh. Esselamü aleyna ve ala ibadillahis salihin. Eşhedü en la ilahe illallah. Ve eşhedü enne Muhammeden abdühü ve rasulüh.",
    "SalliBarik": "Allahümme salli ala Muhammed. Allahümme barik ala Muhammed.",
    "Rabbena": "Rabbena atina fiddünya haseneten ve fil ahireti haseneten ve kına azabennar.",
    "Selam": "Esselamü aleyküm ve rahmetullah."
}

if st.button("Namazı Başlat"):
    rekatlar = {"Sabah": 2, "Öğle": 4, "İkindi": 4, "Akşam": 3, "Yatsı": 4}[vakit]
    
    for r in range(1, rekatlar + 1):
        # KONUM GÖSTERGELERİ
        st.info(f"📍 **KONUM: {r}. Rekat - AYAKTA**")
        if r == 1:
            hoca_seslendir(dualar["Niyet"])
            time.sleep(4)
            hoca_seslendir(dualar["Tekbir"])
            time.sleep(2)
            hoca_seslendir(dualar["Subhaneke"])
            time.sleep(6)

        hoca_seslendir(dualar["Fatiha"])
        time.sleep(15)
        hoca_seslendir(dualar["Sure1"])
        time.sleep(8)

        # RÜKÛ VE DOĞRULMA
        st.warning("📍 **KONUM: RÜKÛ**")
        hoca_seslendir(dualar["Tekbir"])
        time.sleep(2)
        hoca_seslendir(dualar["Ruku_Tesbih"])
        time.sleep(6)
        
        st.success("📍 **KONUM: DOĞRUL (KAVME)**")
        hoca_seslendir(dualar["Kavme"])
        time.sleep(4)

        # SECDE
        for s in range(1, 3):
            st.error(f"📍 **KONUM: {s}. SECDE**")
            hoca_seslendir(dualar["Tekbir"])
            time.sleep(2)
            hoca_seslendir(dualar["Secde_Tesbih"])
            time.sleep(8)
            hoca_seslendir(dualar["Tekbir"]) 
            time.sleep(3)

        # OTURUŞ
        if r == 2 or r == rekatlar:
            st.markdown("### 📍 **KONUM: OTURUŞ**")
            hoca_seslendir(dualar["Tahiyyat"])
            time.sleep(10)
            if r == rekatlar:
                hoca_seslendir(dualar["SalliBarik"])
                time.sleep(10)
                hoca_seslendir(dualar["Rabbena"])
                time.sleep(8)
                st.success("📍 **KONUM: SELAM**")
                hoca_seslendir(dualar["Selam"])
                time.sleep(3)
                hoca_seslendir(dualar["Selam"])

    st.balloons()
