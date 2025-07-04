import streamlit as st
import pandas as pd
from PIL import Image
import os

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Brújula Tecnológica Territorial",
    layout="wide"
)

# --- Datos para los filtros ---
datos_filtros = {
    "Coquimbo": {
        "Agroindustria Competitiva e Hídricamente Eficiente": [],
        "Energías Renovables y Gestión Hídrica Integrada": [],
        "Minería Sustentable y de Alto Valor": [],
        "Pesca y Acuicultura Sostenible y Diversificada": [],
        "Turismo de Intereses Especiales": [],
        "Salud y Bienestar": [],
    },
    "Maule": {
        "Agroindustria y alimentación avanzada": ["Calidad de la Miel", "Envasado de Cárnicos"],
        "Bienestar, calidad de vida y cohesión social": [],
        "Biosalud": [],
        "Región Sustentable y Resiliente": [],
        "Turismo de intereses especiales": [],
    },
    "Los Lagos": {
        "Acuicultura Sostenible y de Alto Valor": [],
        "Energías Renovables": [],
        "Industria Forestal y de la Madera con Valor Agregado": [],
        "Producción Silvoagropecuaria Adaptativa y Resiliente": [],
        "Salud y Bienestar": [],
        "Turismo de Naturaleza y Aventura con Identidad": [],
    }
}

# --- Carga de Datos ---
@st.cache_data
def cargar_datos(filepath):
    try:
        return pd.read_excel(filepath)
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo '{filepath}'. Asegúrate de que está en el repositorio.")
        return None

df = cargar_datos("datos.xlsx")

# --- Header y Filtros ---
st.title("Brújula Tecnológica Territorial")

# --- SECCIÓN DE DIAGNÓSTICO ---
# Mostramos los nombres de las columnas leídas del Excel si el DataFrame se cargó.
if df is not None:
    st.info("Diagnóstico: Nombres de columnas leídos desde 'datos.xlsx'")
    st.write(df.columns.tolist())
else:
    st.stop() # Detiene la ejecución si el archivo no se pudo cargar.
# --------------------------------

col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    regiones = list(datos_filtros.keys())
    region_seleccionada = st.selectbox("Región", regiones)

with col2:
    rubros = list(datos_filtros[region_seleccionada].keys())
    rubro_seleccionado = st.selectbox("Rubro", rubros)

with col3:
    necesidades = datos_filtros[region_seleccionada][rubro_seleccionado]
    if necesidades:
        necesidad_seleccionada = st.selectbox("Necesidad", necesidades)
    else:
        necesidad_seleccionada = st.selectbox("Necesidad", ["No aplica"], disabled=True)

with col4:
    st.write("")
    st.write("")
    buscar = st.button("Buscar", use_container_width=True)


# --- Lógica de Búsqueda y Visualización ---
if buscar:
    try:
        # Filtrado inicial por región y rubro.
        resultados = df[(df['Región'] == region_seleccionada) & (df['Rubro'] == rubro_seleccionado)]

        if necesidades and necesidad_seleccionada != "No aplica":
            resultados = resultados[resultados['Necesidad'] == necesidad_seleccionada]

        st.markdown("---") 

        if not resultados.empty:
            st.subheader(f"Resultados de la búsqueda: {len(resultados)} patentes encontradas")

            for index, row in resultados.iterrows():
                st.markdown("---")
                col_img, col_info = st.columns([1, 4])

                with col_img:
                    ruta_imagen = os.path.join('images', f"{row['Publication Number']}.png")
                    if os.path.exists(ruta_imagen):
                        imagen = Image.open(ruta_imagen)
                        st.image(imagen, use_column_width=True)
                    else:
                        st.warning(f"No se encontró: {ruta_imagen}")

                with col_info:
                    st.markdown(f"**{row['Title (Original language)']}**")
                    st.write(f"**Solicitante:** {row['Assignee - DWPI']}")
                    st.write(f"**País:** {row['Publication Country Code']}")
                    st.info("**Estado en Chile:** Dominio Público en Chile")
        else:
            st.warning("No se encontraron resultados para los filtros seleccionados.")
            
    except KeyError as e:
        st.error(f"Error de columna: No se pudo encontrar la columna {e} en el archivo Excel. Por favor, revisa que los nombres de las columnas en 'datos.xlsx' coincidan con los esperados.")
