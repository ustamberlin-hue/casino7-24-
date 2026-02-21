import streamlit as st

st.set_page_config(page_title="Manken Giydirme", page_icon="💃", layout="wide")

st.title("💃 Profesyonel Manken Giydirme")
st.write("Kıyafetleri mankenin üzerine sürükle ve kendi stilini yarat!")

# HTML ve JavaScript ile Sürükle-Bırak Sistemi
drag_drop_html = """
<style>
    .game-container { display: flex; gap: 50px; justify-content: center; background: #f9f9f9; padding: 20px; border-radius: 15px; }
    .wardrobe { width: 200px; border: 2px dashed #ccc; padding: 10px; display: flex; flex-direction: column; gap: 10px; }
    .model-area { position: relative; width: 300px; height: 500px; border: 2px solid #333; background: #fff url('https://cdn-icons-png.flaticon.com/512/65/65581.png') no-repeat center; background-size: contain; }
    .item { width: 80px; cursor: move; border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); }
    .dropped-item { position: absolute; cursor: move; }
</style>

<div class="game-container">
    <div class="wardrobe" id="wardrobe" ondrop="drop(event)" ondragover="allowDrop(event)">
        <h3>Gardırop</h3>
        <img id="dress1" src="https://cdn-icons-png.flaticon.com/512/2357/2357127.png" draggable="true" ondragstart="drag(event)" class="item" alt="Elbise">
        <img id="hat1" src="https://cdn-icons-png.flaticon.com/512/1039/1039755.png" draggable="true" ondragstart="drag(event)" class="item" alt="Şapka">
        <img id="shoes1" src="https://cdn-icons-png.flaticon.com/512/2872/2872620.png" draggable="true" ondragstart="drag(event)" class="item" alt="Ayakkabı">
    </div>

    <div class="model-area" id="model" ondrop="drop(event)" ondragover="allowDrop(event)">
        <h3 style="text-align:center; color: #888;">Manken</h3>
    </div>
</div>

<script>
    function allowDrop(ev) {
        ev.preventDefault();
    }

    function drag(ev) {
        ev.dataTransfer.setData("text", ev.target.id);
    }

    function drop(ev) {
        ev.preventDefault();
        var data = ev.dataTransfer.getData("text");
        var draggedElement = document.getElementById(data);
        
        // Eğer mankenin üzerine bırakılırsa pozisyonu ayarla
        if (ev.target.id === "model") {
            ev.target.appendChild(draggedElement);
            draggedElement.style.position = "absolute";
            draggedElement.style.left = (ev.offsetX - 40) + "px";
            draggedElement.style.top = (ev.offsetY - 20) + "px";
        } else if (ev.target.id === "wardrobe") {
            ev.target.appendChild(draggedElement);
            draggedElement.style.position = "static";
        }
    }
</script>
"""

# HTML kodunu Streamlit'e bas
st.components.v1.html(drag_drop_html, height=600)

st.divider()
st.info("💡 **Nasıl Oynanır?** Soldaki kıyafetleri farenle tut, mankenin üzerine istediğin yere bırak. Beğenmezsen geri gardıroba sürükle!")
