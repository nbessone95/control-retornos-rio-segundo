import streamlit as st
from datetime import datetime
import os
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Control Retornos", layout="wide")
st.title("🧾 Control de Retornos - Rio Segundo")
st.caption("Equipo: Alessandrini / Rosso / Baldoncini")

os.makedirs("templates", exist_ok=True)
os.makedirs("completed", exist_ok=True)
os.makedirs("data", exist_ok=True)   # Nueva carpeta para guardar datos

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
            
            # Datos generales
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.date_input("Fecha", datetime.today())
                camion = st.selectbox("Camión", ["AD", "Otro"])
                clientes = st.number_input("Cantidad de Clientes", value=17)
            with col2:
                total_vacios = st.number_input("Total Vacíos", value=295)
                pallets = st.number_input("Pallets", value=0)
                chapas = st.number_input("Chapas", value=0)

            st.subheader("Retornos por Envase")
            c1, c2 = st.columns(2)
            with c1:
                r2500 = st.number_input("Retorno 2500", value=0)
                r2000 = st.number_input("Retorno 2000", value=0)
            with c2:
                r1250 = st.number_input("Retorno 1250", value=0)

            st.subheader("Mercadería (Hoja 2)")
            d1, d2 = st.columns(2)
            with d1:
                dev_2500 = st.number_input("Devuelta 2500", value=0)
                falt_2500 = st.number_input("Faltante 2500", value=0)
            with d2:
                venta_envases = st.number_input("Venta de Envases", value=0)
                merc_rota = st.number_input("Mercadería Rota", value=0)

            observaciones = st.text_area("Observaciones", height=80)

            st.subheader("Firma Digital")
            from streamlit_drawable_canvas import st_canvas
            canvas = st_canvas(height=250, width=700, stroke_width=4, stroke_color="#000000", 
                             background_color="#ffffff", key="canvas")

            if st.button("💾 Guardar Control Completo", type="primary"):
                if canvas.image_data is not None:
                    # Guardar firma
                    img = Image.fromarray(canvas.image_data.astype("uint8"))
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    firma_path = f"completed/firma_{timestamp}.png"
                    img.save(firma_path)

                    # Guardar datos en CSV
                    data = {
                        "Fecha": fecha,
                        "Camion": camion,
                        "Archivo": st.session_state.selected_file,
                        "Clientes": clientes,
                        "Total_Vacios": total_vacios,
                        "Retorno_2500": r2500,
                        "Retorno_2000": r2000,
                        "Retorno_1250": r1250,
                        "Pallets": pallets,
                        "Chapas": chapas,
                        "Devuelta_2500": dev_2500,
                        "Faltante_2500": falt_2500,
                        "Venta_Envases": venta_envases,
                        "Merc_Rota": merc_rota,
                        "Observaciones": observaciones,
                        "Firma": firma_path
                    }
                    df = pd.DataFrame([data])
                    df.to_csv(f"data/control_{timestamp}.csv", index=False)

                    st.success("✅ ¡Control guardado correctamente!")
                    st.image(firma_path, caption="Firma")
                    st.balloons()
                else:
                    st.error("Por favor hacé tu firma")

else:  # Historial
    st.header("📋 Historial de Controles")
    
    data_files = [f for f in os.listdir("data") if f.endswith(".csv")]
    
    if data_files:
        for file in sorted(data_files, reverse=True):
            df = pd.read_csv(f"data/{file}")
            st.subheader(f"📅 {df['Fecha'].iloc[0]} - {df['Camion'].iloc[0]}")
            st.write(df.drop(columns=["Firma"]).iloc[0])
            st.image(f"completed/{os.path.basename(df['Firma'].iloc[0])}", width=400)
            st.divider()
    else:
        st.info("Aún no hay controles guardados. Completá uno primero.")
