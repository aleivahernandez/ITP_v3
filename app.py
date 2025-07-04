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
    """Carga los datos desde un archivo Excel."""
    try:
        return pd.read_excel(filepath)
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo '{filepath}'. Asegúrate de que está en el repositorio.")
        return None

df = cargar_datos("datos.xlsx")

# Detiene la ejecución si el archivo no se pudo cargar.
if df is None:
    st.stop()

# --- CSS Personalizado para el Header ---
st.markdown("""
<style>
    /* Contenedor principal del header */
    .header-container {
        background-color: #0f69b4;
        padding: 2rem 2rem 1rem 2rem; /* Acolchado: arriba, derecha, abajo, izquierda */
        border-radius: 10px;
        margin-bottom: 2rem; /* Espacio debajo del header */
    }
    /* Estilo para el título dentro del header */
    .header-container h1 {
        color: white;
    }
    /* Estilo para las etiquetas de los filtros */
    .header-container .stSelectbox label {
        color: white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# --- Header y Filtros ---
# Usamos un markdown para abrir un div y aplicarle nuestra clase CSS
st.markdown('<div class="header-container">', unsafe_allow_html=True)

st.title("Brújula Tecnológica Territorial")

# Creamos columnas para distribuir los filtros y el botón horizontalmente.
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    regiones = list(datos_filtros.keys())
    region_seleccionada = st.selectbox("Región", regiones, label_visibility="visible")

with col2:
    rubros = list(datos_filtros[region_seleccionada].keys())
    rubro_seleccionado = st.selectbox("Rubro", rubros, label_visibility="visible")

with col3:
    necesidades = datos_filtros[region_seleccionada][rubro_seleccionado]
    if necesidades:
        necesidad_seleccionada = st.selectbox("Necesidad", necesidades, label_visibility="visible")
    else:
        necesidad_seleccionada = st.selectbox("Necesidad", ["No aplica"], disabled=True, label_visibility="visible")

with col4:
    st.write("") # Espaciador para alinear verticalmente
    st.write("") # Espaciador para alinear verticalmente
    buscar = st.button("Buscar", use_container_width=True)

# Cerramos el div del header
st.markdown('</div>', unsafe_allow_html=True)


# --- Lógica de Búsqueda y Visualización de Resultados ---
if buscar:
    try:
        # Filtrado inicial por región y rubro.
        resultados = df[(df['Región'] == region_seleccionada) & (df['Rubro'] == rubro_seleccionado)]

        # Si hay necesidades y se seleccionó una, se aplica el filtro adicional.
        if necesidades and necesidad_seleccionada != "No aplica":
            resultados = resultados[resultados['Necesidad'] == necesidad_seleccionada]

        st.markdown("---")

        if not resultados.empty:
            st.subheader(f"Resultados de la búsqueda: {len(resultados)} patentes encontradas")

            # Iteramos sobre cada fila del DataFrame de resultados para mostrar las tarjetas.
            for index, row in resultados.iterrows():
                st.markdown("---") # Separador para cada tarjeta
                col_img, col_info = st.columns([1, 4]) # Proporción 20% para imagen, 80% para info

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
        st.error(f"Error de columna: No se pudo encontrar la columna {e}. Revisa que los nombres en 'datos.xlsx' sean correctos.")
