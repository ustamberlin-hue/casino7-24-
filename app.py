import streamlit as st

st.set_page_config(page_title="Bebek Giydirmece", page_icon="👶")

st.title("🎀 Sevimli Bebek Giydirme Oyunu")
st.write("Bebeğin için en güzel kıyafetleri seç ve stilini yarat!")

# --- OYUN ALANI (Sütunlar) ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🗄️ Gardırop")
    
    # Bebek Seçimi
    bebek = st.radio("Bir bebek seç:", ["🍼 Minik Ali", "🎀 Pamuk Ayşe", "🧸 Yumuşak Kerem"])
    
    # Kıyafet Seçenekleri
    sapka = st.selectbox("Şapka Seç:", ["Yok", "Mavi Bere", "Pembe Toka", "Güneş Şapkası", "Panda Başlığı"])
    ust = st.selectbox("Üst Giyim:", ["Tişört", "Kazak", "Pijama Üstü", "Süper Kahraman Kostümü"])
    alt = st.selectbox("Alt Giyim:", ["Pantolon", "Etek", "Şort", "Tulum"])
    ayakkabı = st.selectbox("Ayakkabı:", ["Patik", "Spor Ayakkabı", "Sandalet", "Yürüyüş Botu"])
    aksesuar = st.multiselect("Ekstralar:", ["Emzik", "Çıngırak", "Gözlük", "Oyuncak Ayı"])

with col2:
    st.header("👶 Stil Notu")
    
    # Seçimlere göre dinamik bir sonuç ekranı
    st.write(f"### Şu an giydirilen: **{bebek}**")
    
    # Kombin Özeti
    st.success(f"🎨 **Kombin Özeti:**")
    st.write(f"🤠 **Başta:** {sapka}")
    st.write(f"👕 **Gövdede:** {ust}")
    st.write(f"👖 **Bacaklarda:** {alt}")
    st.write(f"👟 **Ayaklarda:** {ayakkabı}")
    
    if aksesuar:
        st.write(f"✨ **Aksesuarlar:** {', '.join(aksesuar)}")

    # Eğlenceli bir buton
    if st.button("📸 Fotoğraf Çek (Kombini Onayla)"):
        st.balloons()
        st.write(f"✨ Harika! **{bebek}** bugün çok şık görünüyor!")

# Alt kısımda görsel bir dokunuş
st.divider()
st.info("İpucu: Farklı aksesuarları aynı anda seçerek bebeğini daha süslü yapabilirsin!")
