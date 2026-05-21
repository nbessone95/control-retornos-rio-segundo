import streamlit as st
from datetime import datetime
import os
import pandas as pd
from PIL import Image
from openpyxl import load_workbook

st.set_page_config(page_title="Control Retornos", layout="wide")
st.title("🧾 Control de Retornos - Rio Segundo")
st.caption("Equipo: Alessandrini / Rosso / Baldoncini")

os.makedirs("templates", exist_ok=True)
os.makedirs("completed", exist_ok=True)
os.makedirs("data", exist_ok=True)

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
    st.header("✍️ Completar Control")
    
    files = [f for f in os.listdir("templates") if f.endswith(".xlsx")]
    
    if not files:
        st.warning("No hay plantillas. Sube una primero.")
    else:
        if 'selected_file' not in st.session_state:
            st.session_state.selected_file = None
            
        col_select, col_btn = st.columns([3,1])
        with col_select:
            selected = st.selectbox("Seleccionar archivo a completar", files, 
                                  index=files.index(st.session_state.selected_file) if st.session_state.selected_file in files else 0)
        
        with col_btn:
            if st.button("Cargar y Leer Datos del Excel", type="primary"):
                st.session_state.selected_file = selected
                st.rerun()
        
        if st.session_state.selected_file:
            filepath = f"templates/{st.session_state.selected_file}"
            st.success(f"Trabajando con: **{st.session_state.selected_file}**")
            
            # Lectura de datos del Excel
            d2500 = d2000 = d1250 = 0
            try:
                wb = load_workbook(filepath, data_only=True)
                ws = wb["Hoja3"] if "Hoja3" in wb.sheetnames else wb.active
                d2500 = ws.cell(row=5, column=1).value or 0
                d2000 = ws.cell(row=8, column=1).value or 0
                d1250 = ws.cell(row=11, column=1).value or 0
            except:
                pass

            # ==================== HOJA 1 - SOLO LECTURA ====================
            st.subheader("📦 1. CONTROL DE RETORNOS DE ENVASES")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Datos Generales (no modificables)**")
                st.metric("Localidad", "Rio Segundo")
                st.metric("Equipo", "Alessandrini / Rosso / Baldoncini")
                st.metric("Camión", "AD")
                st.date_input("Fecha", datetime.today(), disabled=True)
            
            with col2:
                st.write("**Despachos (Columna A)**")
                st.metric("Despacho 2500", d2500)
                st.metric("Despacho 2000", d2000)
                st.metric("Despacho 1250", d1250)

            st.subheader("Cambios / Despachos Detallados")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Cambio 2500", 0, delta="no modificable")
                st.metric("Cambio 2000", 0, delta="no modificable")
                st.metric("Cambio 1250", 0, delta="no modificable")
            with c2:
                st.metric("Cambio 354", 0, delta="no modificable")
                st.metric("Cambio 220", 0, delta="no modificable")
            with c3:
                st.metric("Cambio Monster 473", 0, delta="no modificable")

            st.subheader("Retornos (Completar)")
            r1, r2, r3 = st.columns(3)
            with r1:
                ret_2500 = st.number_input("Retorno 2500", value=0)
                ret_2000 = st.number_input("Retorno 2000", value=0)
            with r2:
                ret_1250 = st.number_input("Retorno 1250", value=0)
                clientes = st.number_input("Cantidad de Clientes", value=17)
            with r3:
                pallets = st.number_input("Pallets", value=0)
                chapas = st.number_input("Chapas", value=0)

            total_vacios = st.number_input("**TOTAL VACÍOS RETORNADOS**", value=0)

            # ==================== HOJA 2 ====================
            st.subheader("📋 2. Retornos Llenos y Cambios")
            st.write("**Retornos Llenos**")
            rl1, rl2 = st.columns(2)
            with rl1:
                lleno_2500 = st.number_input("Retorno Lleno 2500", value=0)
                lleno_2000 = st.number_input("Retorno Lleno 2000", value=0)
            with rl2:
                lleno_1250 = st.number_input("Retorno Lleno 1250", value=0)

            st.write("**Cambios**")
            ch1, ch2, ch3 = st.columns(3)
            with ch1:
                cam_2500 = st.number_input("Cambio 2500", value=0)
                cam_2000 = st.number_input("Cambio 2000", value=0)
            with ch2:
                cam_1250 = st.number_input("Cambio 1250", value=0)
                cam_354 = st.number_input("Cambio 354", value=0)
            with ch3:
                cam_220 = st.number_input("Cambio 220", value=0)
                cam_473 = st.number_input("Cambio 473 (Monster)", value=0)

            merc_rota = st.number_input("Mercadería Rota", value=0)
            observaciones = st.text_area("Observaciones", height=100)

            # Firma
            st.subheader("✍️ Firma Digital")
            from streamlit_drawable_canvas import st_canvas
            canvas = st_canvas(height=280, width=700, stroke_width=4, stroke_color="#000000", 
                             background_color="#ffffff", key="canvas")

            if st.button("💾 Guardar Control Completo", type="primary"):
                if canvas.image_data is not None:
                    img = Image.fromarray(canvas.image_data.astype("uint8"))
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    firma_path = f"completed/firma_{timestamp}.png"
                    img.save(firma_path)
                    
                    data = {**{k:v for k,v in locals().items() if k.startswith(('ret_','lleno_','cam_','pallets','chapas','clientes','total','merc'))}, 
                           "Fecha": datetime.today().strftime("%Y-%m-%d"),
                           "Archivo": st.session_state.selected_file}
                    pd.DataFrame([data]).to_csv(f"data/control_{timestamp}.csv", index=False)

                    st.success("✅ ¡Control guardado correctamente!")
                    st.image(firma_path, caption="Firma guardada")
                    st.balloons()
                else
