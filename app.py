import streamlit as st

st.set_page_config(page_title="Gerçek Bebek Giydirme", page_icon="🧸", layout="centered")

# CSS ile Görselliği Güzelleştirme
st.markdown("""
    <style>
    .main { background-color: #fff5f8; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #ffb6c1; color: white; border: none; }
    .stButton>button:hover { background-color: #ff69b4; color: white; }
    .bebek-container { position: relative; width: 300px; height: 450px; margin: auto; background: white; border-radius: 20px; border: 5px solid #ffb6c1; overflow: hidden; display: flex; justify-content: center; align-items: center; }
    .katman { position: absolute; width: 250px; transition: all 0.3s; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎀 Benim Tatlı Bebeğim")
st.write("Aşağıdaki gardıroptan kıyafet seç, bebeğin üzerinde görsün!")

# --- DURUM YÖNETİMİ ---
if 'ust_resim' not in st.session_state: st.session_state.ust_resim = ""
if 'alt_resim' not in st.session_state: st.session_state.alt_resim = ""
if 'aksesuar_resim' not in st.session_state: st.session_state.aksesuar_resim = ""

# --- OYUN ALANI ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("👶 Manken")
    
    # Gerçek Bebek ve Kıyafet Katmanları (Emoji ve Görsel Temsili)
    # Not: Gerçek PNG linkleri eklenerek daha da güzelleştirilebilir.
    bebek_html = f"""
    <div class="bebek-container">
        <img src="https://cdn-icons-png.flaticon.com/512/3069/3069172.png" class="katman" style="z-index: 1;"> <div style="position: absolute; z-index: 5; font-size: 80px; top: 180px;">{st.session_state.ust_resim}</div>
        <div style="position: absolute; z-index: 4; font-size: 80px; top: 250px;">{st.session_state.alt_resim}</div>
        <div style="position: absolute; z-index: 6; font-size: 60px; top: 60px;">{st.session_state.aksesuar_resim}</div>
    </div>
    """
    st.components.v1.html(bebek_html, height=460)

with col2:
    st.subheader("👗 Gardırop")
    
    with st.expander("👕 Üstler", expanded=True):
        u1, u2 = st.columns(2)
        if u1.button("💖 Pembe"): st.session_state.ust_resim = "👚"
        if u2.button("💙 Mavi"): st.session_state.ust_resim = "👕"
        if u1.button("🐥 Ördek"): st.session_state.ust_resim = "🐤"
        if u2.button("🦁 Aslan"): st.session_state.ust_resim = "🦁"

    with st.expander("👖 Altlar"):
        a1, a2 = st.columns(2)
        if a1.button("👖 Kot"): st.session_state.alt_resim = "👖"
        if a2.button("👗 Etek"): st.session_state.alt_resim = "👗"
        if a1.button("🩳 Şort"): st.session_state.alt_resim = "🩳"
        if a2.button("🌸 Çiçekli"): st.session_state.alt_resim = "🌺"

    with st.expander("🎩 Aksesuar"):
        ak1, ak2 = st.columns(2)
        if ak1.button("👑 Taç"): st.session_state.aksesuar_resim = "👑"
        if ak2.button("👒 Şapka"): st.session_state.aksesuar_resim = "👒"
        if ak1.button("🕶️ Gözlük"): st.session_state.aksesuar_resim = "🕶️"
        if ak2.button("🎀 Toka"): st.session_state.aksesuar_resim = "🎀"

if st.button("♻️ Bebeği Soy / Sıfırla"):
    st.session_state.ust_resim = ""
    st.session_state.alt_resim = ""
    st.session_state.aksesuar_resim = ""
    st.rerun()
