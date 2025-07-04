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
# Diccionario para manejar la lógica de los filtros anidados.
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
# Usamos un bloque try-except para manejar el error si el archivo no se encuentra.
@st.cache_data
def cargar_datos(filepath):
    """Carga los datos desde un archivo Excel."""
    try:
        # Asegúrate de que el archivo 'datos.xlsx' esté en la raíz de tu repositorio
        return pd.read_excel(filepath)
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo '{filepath}'. Asegúrate de que el archivo está en el repositorio de GitHub.")
        return pd.DataFrame() # Retorna un DataFrame vacío para evitar más errores.

df = cargar_datos("datos.xlsx")

# --- Header y Filtros ---
st.title("Brújula Tecnológica Territorial")

# Creamos columnas para distribuir los filtros y el botón horizontalmente.
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    regiones = list(datos_filtros.keys())
    region_seleccionada = st.selectbox("Región", regiones)

with col2:
    rubros = list(datos_filtros[region_seleccionada].keys())
    rubro_seleccionado = st.selectbox("Rubro", rubros)

with col3:
    # Las necesidades dependen de la región y rubro seleccionados.
    necesidades = datos_filtros[region_seleccionada][rubro_seleccionado]
    # Si no hay necesidades, el selectbox se deshabilita para evitar confusiones.
    if necesidades:
        necesidad_seleccionada = st.selectbox("Necesidad", necesidades)
    else:
        # Mostramos un selectbox deshabilitado con un mensaje.
        necesidad_seleccionada = st.selectbox("Necesidad", ["No aplica"], disabled=True)


with col4:
    # Se necesita un espacio vertical para alinear el botón con los filtros.
    st.write("")
    st.write("")
    buscar = st.button("Buscar", use_container_width=True)


# --- Lógica de Búsqueda y Visualización ---
if buscar:
    # Filtrado inicial por región y rubro.
    resultados = df[(df['Región'] == region_seleccionada) & (df['Rubro'] == rubro_seleccionado)]

    # Si hay necesidades y se seleccionó una, se aplica el filtro adicional.
    if necesidades and necesidad_seleccionada != "No aplica":
        resultados = resultados[resultados['Necesidad'] == necesidad_seleccionada]

    st.markdown("---") # Línea separadora

    if not resultados.empty:
        st.subheader(f"Resultados de la búsqueda: {len(resultados)} patentes encontradas")

        # Iteramos sobre cada fila del DataFrame de resultados para mostrar las tarjetas.
        for index, row in resultados.iterrows():
            st.markdown("---") # Separador para cada tarjeta
            # Creamos dos columnas para la tarjeta: imagen a la izquierda, texto a la derecha.
            col_img, col_info = st.columns([1, 4]) # Proporción 20% para la imagen, 80% para la info

            with col_img:
                # La ruta a la imagen debe incluir la carpeta 'images'
                ruta_imagen = os.path.join('images', f"{row['Publication Number']}.png")
                # Verificamos si la imagen existe antes de intentar mostrarla.
                if os.path.exists(ruta_imagen):
                    imagen = Image.open(ruta_imagen)
                    st.image(imagen, use_column_width=True)
                else:
                    st.warning(f"No se encontró: {ruta_imagen}")

            with col_info:
                # LÍNEA CORREGIDA:
                st.markdown(f"**{row['Title (Original language)']}**")
                st.write(f"**Solicitante:** {row['Assignee - DWPI']}")
                st.write(f"**País:** {row['Publication Country Code']}")
                st.info("**Estado en Chile:** Dominio Público en Chile") # Usamos st.info para destacar.
    else:
        st.warning("No se encontraron resultados para los filtros seleccionados.")
