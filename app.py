import streamlit as st
from datetime import datetime
import os
import pandas as pd
from openpyxl import load_workbook

st.set_page_config(page_title="Control Retornos", layout="wide")
st.title("🧾 Control de Retornos - Rio Segundo")

os.makedirs("templates", exist_ok=True)
os.makedirs("data", exist_ok=True)

menu = st.sidebar.selectbox("Menú", ["Completar Formulario", "Subir Plantillas", "Historial"])

if menu == "Subir Plantillas":
    st.header("📤 Subir Plantillas del Día")
    uploaded = st.file_uploader("Subir uno o varios Excels", 
                               type="xlsx", 
                               accept_multiple_files=True)
    
    if uploaded:
        with st.spinner("Guardando archivos..."):
            for file in uploaded:
                with open(f"templates/{file.name}", "wb") as f:
                    f.write(file.getbuffer())
                st.success(f"✅ {file.name} guardado")
        st.success(f"✅ Se guardaron {len(uploaded)} archivos correctamente")
        st.rerun()

elif menu == "Completar Formulario":
    st.header("✍️ Completar Control")
    
    files = [f for f in os.listdir("templates") if f.endswith(".xlsx")]
    if not files:
        st.warning("Sube una plantilla primero")
    else:
        selected = st.selectbox("Seleccionar archivo", files)
        
        if st.button("Cargar Formulario", type="primary"):
            st.session_state.selected_file = selected
            st.rerun()
        
        if 'selected_file' in st.session_state:
            filepath = f"templates/{st.session_state.selected_file}"
            st.title(f"🧾 {st.session_state.selected_file.replace('.xlsx', '')}")
            
            # Lectura básica
            localidad = "Rio Segundo"
            equipo = "Alessandrini / Rosso / Baldoncini"
            total_desp = 0.0
            try:
                wb = load_workbook(filepath, data_only=True)
                ws3 = wb["Hoja3"] if "Hoja3" in wb.sheetnames else wb.active
                localidad = str(ws3.cell(row=2, column=2).value or localidad)
                if "Hoja2" in wb.sheetnames:
                    ws2 = wb["Hoja2"]
                    equipo = str(ws2.cell(row=2, column=2).value or equipo)
                total_desp = float(ws3.cell(row=24, column=5).value or 0)
            except:
                pass

            st.success(f"Trabajando con: **{st.session_state.selected_file}**")

            # Formulario (mantengo lo esencial)
            st.subheader("Datos Generales")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Localidad", localidad)
                st.metric("Equipo", equipo)
                st.metric("Camión", "AD")
            with col2:
                st.metric("Fecha", datetime.today().strftime("%d-%m-%Y"))
                st.metric("Clientes", 17)
                st.metric("Total Despachado", total_desp)

            # ... (puedes agregar más campos aquí si querés)

            observaciones = st.text_area("Observaciones", height=80)
            firma = st.text_input("Firma Chofer (Nombre y Apellido)", "")

            if st.button("💾 Guardar Control", type="primary"):
                if not firma.strip():
                    st.error("Por favor ingrese la firma")
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    data = {
                        "Fecha": datetime.today().strftime("%d-%m-%Y"),
                        "Hora": datetime.today().strftime("%H:%M"),
                        "Archivo": st.session_state.selected_file,
                        "Observaciones": observaciones,
                        "Firma": firma
                    }
                    pd.DataFrame([data]).to_csv(f"data/control_{timestamp}.csv", index=False)
                    st.success("✅ Guardado!")
                    st.balloons()

else:  # Historial con descarga
    st.header("📋 Historial de Controles")
    data_files = [f for f in os.listdir("data") if f.endswith(".csv")]
    
    if data_files:
        all_data = []
        for f in sorted(data_files, reverse=True):
            df = pd.read_csv(f"data/{f}")
            all_data.append(df)
        
        if all_data:
            full_df = pd.concat(all_data, ignore_index=True)
            st.dataframe(full_df, use_container_width=True)
            
            # Botón para descargar todo
            csv = full_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Historial Completo (CSV)",
                data=csv,
                file_name=f"Historial_Retornos_{datetime.today().strftime('%d-%m-%Y')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Aún no hay controles guardados.")
