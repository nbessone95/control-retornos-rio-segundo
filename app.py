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
            if st.button("Cargar y Leer Datos del Excel", type="primary"):
                st.session_state.selected_file = selected
                st.rerun()

        if st.session_state.selected_file:
            filepath = f"templates/{st.session_state.selected_file}"
            st.success(f"Editando: **{st.session_state.selected_file}**")
            
            # Lectura automática del Excel
            try:
                wb = load_workbook(filepath, data_only=True)
                ws = wb["Hoja3"] if "Hoja3" in wb.sheetnames else wb.active
                
                # Leer despachos según tu archivo
                despacho_2500 = ws.cell(row=5, column=1).value or 0
                despacho_2000 = ws.cell(row=8, column=1).value or 0
                despacho_1250 = ws.cell(row=11, column=1).value or 0
                
                st.subheader("📦 Datos de Despacho (leídos del Excel)")
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Despacho 2500", despacho_2500)
                    st.metric("Despacho 200
