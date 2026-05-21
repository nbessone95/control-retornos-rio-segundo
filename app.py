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
            
            # ==================== LECTURA COLUMNA B (Hoja 1) ====================
            col_b_2500 = col_b_2000 = col_b_1250 = 0
            try:
                wb = load_workbook(filepath, data_only=True)
                ws = wb["Hoja3"] if "Hoja3" in wb.sheetnames else wb.active
                
                col_b_2500 = ws.cell(row=5, column=2).value or 0   # Columna B
                col_b_2000 = ws.cell(row=8, column=2).value or 0
                col_b_1250 = ws.cell(row=11, column=2).value or 0
            except:
                st.warning("No se pudieron leer los datos de la columna B.")

            # ==================== HOJA 1 ====================
            st.subheader("📦 1. CONTROL DE RETORNOS DE ENVASES")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write("**DATOS COLUMNA B (Excel)**")
                st.metric("2500", col_b_2500)
                st.metric("2000", col_b_2000)
                st.metric("1250", col_b_1250)
            
            with col2:
                st.write("**RETORNOS (completar)**")
                c1, c2, c3 = st.columns(3)
                with c1:
                    ret_2500 = st.number_input("Retorno 2500", value=0)
                    ret_2000 = st.number_input("Retorno 2000", value=0)
                with c2:
                    ret_1250 = st.number_input("Retorno 1250", value=0)
                    pallets = st.number_input("Pallets", value=0)
                with c3:
                    chapas = st.number_input("Chapas", value=0)
                    clientes = st.number_input("Cantidad de Clientes", value=17)

            total_vacios = st.number_input("**TOTAL VACÍOS RETORNADOS**", value=0)

            # ==================== HOJA 2 - SOLO RETORNOS LLENOS ====================
            st.subheader("📋 2. Retornos Llenos")
            st.write("**Completar manualmente:**")
            rl1, rl2 = st.columns(2)
            with rl1:
                lleno_2500 = st.number_input("Retorno Lleno 2500", value=0)
                lleno_2000 = st.number_input("Retorno Lleno 2000", value=0)
            with rl2:
                lleno_1250 = st.number_input("Retorno Lleno 1250", value=0)
                venta_envases = st.number_input("Venta de Envases", value=0)

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
                    
                    data = {
                        "Fecha": datetime.today().strftime("%Y-%m-%d"),
                        "Archivo": st.session_state.selected_file,
                        "ColB_2500": col_b_2500,
                        "ColB_2000": col_b_2000,
                        "ColB_1250": col_b_1250,
                        "Retorno_2500": ret_2500,
                        "Retorno_2000": ret_2000,
                        "Retorno_1250": ret_1250,
                        "Pallets": pallets,
                        "Chapas": chapas,
                        "Clientes": clientes,
                        "Total_Vacios": total_vacios,
                        "Lleno_2500": lleno_2500,
                        "Lleno_2000": lleno_2000,
                        "Lleno_1250": lleno_1250,
                        "Venta_Envases": venta_envases,
                        "Merc_Rota": merc_rota,
                        "Observaciones": observaciones
                    }
                    pd.DataFrame([data]).to_csv(f"data/control_{timestamp}.csv", index=False)

                    st.success("✅ ¡Control guardado correctamente!")
                    st.image(firma_path, caption="Firma guardada")
                    st.balloons()
                else:
                    st.error("Por favor realizá tu firma digital")

else:
    st.header("📋 Historial")
    data_files = [f for f in os.listdir("data") if f.endswith(".csv")]
    if data_files:
        for file in sorted(data_files, reverse=True):
            df = pd.read_csv(f"data/{file}")
            st.subheader(f"📅 {df['Fecha'].iloc[0]}")
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no hay controles guardados.")
