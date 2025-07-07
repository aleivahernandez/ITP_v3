import streamlit as st
import pandas as pd
from PIL import Image
import os
from streamlit_extras.stylable_container import stylable_container

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

if df is None:
    st.stop()

# --- Header y Filtros ---
with stylable_container(
    key="header_container",
    css_styles="""
        {
            background-color: #0f69b4;
            border-radius: 10px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        /* Color del título y etiquetas de filtros */
        h1, .stSelectbox label {
            color: white;
        }
        /* Estilo para el botón Buscar */
        .stButton button {
            background-color: #eb3c46;
            color: white; /* Color del texto del botón */
            border-radius: 5px;
            border: none;
        }
        .stButton button:hover {
            background-color: #d4363f;
            color: white;
            border: none;
        }
        .stButton button:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        """,
):
    st.title("Brújula Tecnológica Territorial")

    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    placeholder_region = "Seleccione una Región..."
    placeholder_rubro = "Seleccione un Rubro..."

    with col1:
        regiones = [placeholder_region] + list(datos_filtros.keys())
        region_seleccionada = st.selectbox("Región", regiones)

    with col2:
        if region_seleccionada != placeholder_region:
            rubros = [placeholder_rubro] + list(datos_filtros[region_seleccionada].keys())
            rubro_seleccionado = st.selectbox("Rubro", rubros)
        else:
            rubro_seleccionado = st.selectbox("Rubro", [placeholder_rubro], disabled=True)

    with col3:
        if region_seleccionada != placeholder_region and rubro_seleccionado != placeholder_rubro:
            necesidades = datos_filtros[region_seleccionada].get(rubro_seleccionado, [])
            if necesidades:
                necesidad_seleccionada = st.selectbox("Necesidad", ["Todas"] + necesidades)
            else:
                necesidad_seleccionada = st.selectbox("Necesidad", ["No aplica"], disabled=True)
        else:
            necesidad_seleccionada = st.selectbox("Necesidad", ["No aplica"], disabled=True)

    with col4:
        st.write("")
        st.write("")
        disable_search = region_seleccionada == placeholder_region or rubro_seleccionado == placeholder_rubro
        buscar = st.button("Buscar", use_container_width=True, disabled=disable_search)


# --- Lógica de Búsqueda y Visualización ---
if 'buscar' in locals() and buscar:
    try:
        # 1. Filtrado inicial de datos
        resultados = df[(df['Región'] == region_seleccionada) & (df['Rubro'] == rubro_seleccionado)]
        
        if 'necesidad_seleccionada' in locals() and necesidad_seleccionada not in ["Todas", "No aplica"]:
            resultados = resultados[resultados['Necesidad'] == necesidad_seleccionada]

        # 2. Lógica para ordenar por disponibilidad de imagen
        if not resultados.empty:
            resultados['tiene_imagen'] = resultados['Publication Number'].apply(
                lambda pub_num: os.path.exists(os.path.join('images', f"{pub_num}.png"))
            )
            resultados = resultados.sort_values(by='tiene_imagen', ascending=False).drop(columns=['tiene_imagen'])

        st.markdown("---")

        if not resultados.empty:
            st.subheader(f"Resultados de la búsqueda: {len(resultados)} patentes encontradas")

            for index, row in resultados.iterrows():
                with stylable_container(
                    key=f"card_{row['Publication Number']}",
                    css_styles="""
                        {
                            border: 1px solid #e6e6e6;
                            border-radius: 10px;
                            padding: 1.5rem;
                            margin-bottom: 1rem;
                            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
                        }
                        """,
                ):
                    col_img, col_info = st.columns([1, 4])
                    with col_img:
                        ruta_imagen = os.path.join('images', f"{row['Publication Number']}.png")
                        if os.path.exists(ruta_imagen):
                            st.image(Image.open(ruta_imagen), use_container_width=True)
                        else:
                            st.image(os.path.join('images', 'no image.png'), use_container_width=True)

                    with col_info:
                        st.markdown(f"**{row['Title (Original language)']}**")
                        st.write(f"**Solicitante:** {row['Assignee - DWPI']}")
                        st.write(f"**País:** {row['Publication Country Code']}")
                        st.info("**Estado en Chile:** Dominio Público en Chile")
        else:
            st.warning("No se encontraron resultados para los filtros seleccionados.")

    except KeyError as e:
        st.error(f"Error de columna: No se pudo encontrar la columna {e}. Revisa 'datos.xlsx'.")
