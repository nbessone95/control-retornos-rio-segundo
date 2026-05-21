import streamlit as st
from datetime import datetime
import os
from PIL import Image

st.set_page_config(page_title="Control Retornos", layout="wide")
st.title("🧾 Control de Retornos - Rio Segundo")
st.caption("Equipo: Alessandrini / Rosso / Baldoncini")

os.makedirs("templates", exist_ok=True)
os.makedirs("completed", exist_ok=True)

menu = st.sidebar.selectbox("Menú", ["Completar Formulario", "Subir Plantillas", "Historial"])

if menu == "Subir Plantillas":
    st.header("📤 Subir Plantillas del Día")
    uploaded = st.file_uploader("Subir uno o varios Excels", type="xlsx", accept_multiple_files=True)
    if uploaded:
        for file in uploaded:
            with open(f"templates/{file.name}", "wb") as f:
                f.write(file.getbuffer())
            st.success(f"✅ {file.name} guardado")

elif menu == "Completar Formulario":
    st.header("✍️ Completar Control Completo")
    
    files = [f for f in os.listdir("templates") if f.endswith(".xlsx")]
    
    if not files:
        st.warning("No hay plantillas. Sube una primero.")
    else:
        if 'selected_file' not in st.session_state:
            st.session_state.selected_file = None
            
        col_select, col_btn = st.columns([3,1])
        with col_select:
            selected = st.selectbox("Seleccionar archivo", files, 
                                  index=files.index(st.session_state.selected_file) if st.session_state.selected_file in files else 0)
        
        with col_btn:
            if st.button("Cargar Formulario", type="primary"):
                st.session_state.selected_file = selected
                st.rerun()

        if st.session_state.selected_file:
            st.success(f"Editando: **{st.session_state.selected_file}**")
            
            # HOJA 3 - ENVASES
            st.subheader("📦 1. Retornos de Envases")
            c1, c2, c3 = st.columns(3)
            with c1:
                r2500 = st.number_input("Retorno 2500", value=0)
                r2000 = st.number_input("Retorno 2000", value=0)
            with c2:
                r1250 = st.number_input("Retorno 1250", value=0)
                pallets = st.number_input("Pallets", value=0)
            with c3:
                chapas = st.number_input("Chapas", value=0)
                clientes = st.number_input("Cantidad de Clientes", value=17)
            
            total_vacios = st.number_input("Total Vacíos", value=295)

            # HOJA 2 - MERCADERÍAS
            st.subheader("📋 2. Retornos de Mercaderías (Hoja 2)")
            st.write("**Mercadería Devuelta**")
            d1, d2 = st.columns(2)
            with d1:
                dev_2500 = st.number_input("Devuelta 2500", value=0)
                dev_2000 = st.number_input("Devuelta 2000", value=0)
            with d2:
                dev_1250 = st.number_input("Devuelta 1250", value=0)
                dev_otras = st.number_input("Otras devueltas", value=0)

            st.write("**Mercadería Faltante**")
            f1, f2 = st.columns(2)
            with f1:
                falt_2500 = st.number_input("Faltante 2500", value=0)
                falt_2000 = st.number_input("Faltante 2000", value=0)
            with f2:
                falt_1250 = st.number_input("Faltante 1250", value=0)
                falt_otras = st.number_input("Otras faltantes", value=0)

            venta_envases = st.number_input("Venta de Envases (unidades)", value=0)
            merc_rota = st.number_input("Mercadería Rota", value=0)
            
            observaciones = st.text_area("Observaciones Generales", height=100)

            # FIRMA
            st.subheader("✍️ Firma Digital")
            from streamlit_drawable_canvas import st_canvas
            canvas = st_canvas(
                height=280,
                width=700,
                stroke_width=4,
                stroke_color="#000000",
                background_color="#ffffff",
                key="canvas",
            )

            if st.button("💾 Guardar Control Completo", type="primary"):
                if canvas.image_data is not None:
                    img = Image.fromarray(canvas.image_data.astype("uint8"))
                    firma_path = f"completed/firma_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
                    img.save(firma_path)
                    st.success("✅ ¡Control guardado correctamente!")
                    st.image(firma_path, caption="Firma guardada")
                    st.balloons()
                else:
                    st.error("Por favor realizá tu firma digital")

else:
    st.header("📋 Historial")
    completed = os.listdir("completed")
    if completed:
        for f in sorted(completed, reverse=True):
            st.write(f"📄 {f}")
    else:
        st.info("Aún no hay controles completados.")
