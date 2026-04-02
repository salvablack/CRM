import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
st.set_page_config(page_title="GPS Manager", layout="wide")

DATA_FILE = Path("data.json")

# ─────────────────────────────
# DATA LAYER
# ─────────────────────────────
class DataManager:

    @staticmethod
    def load():
        if DATA_FILE.exists():
            try:
                return json.loads(DATA_FILE.read_text())
            except:
                return {"sessions": {}}
        return {"sessions": {}}

    @staticmethod
    def save(data):
        DATA_FILE.write_text(json.dumps(data, indent=2))


# ─────────────────────────────
# BUSINESS LOGIC
# ─────────────────────────────
class GPSService:

    @staticmethod
    def create_session(data, name):
        sid = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        data["sessions"][sid] = {
            "name": name,
            "created": datetime.now().isoformat(),
            "points": []
        }
        return sid

    @staticmethod
    def add_point(session, lat, lon, desc):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Coordenadas inválidas")

        session["points"].append({
            "lat": lat,
            "lon": lon,
            "desc": desc,
            "date": datetime.now().isoformat()
        })


# ─────────────────────────────
# INIT STATE
# ─────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = DataManager.load()

data = st.session_state.data

# ─────────────────────────────
# SIDEBAR
# ─────────────────────────────
st.sidebar.title("GPS Manager")

# Crear sesión
name = st.sidebar.text_input("Nueva sesión")
if st.sidebar.button("Crear"):
    if name:
        sid = GPSService.create_session(data, name)
        st.session_state.current = sid
        DataManager.save(data)
        st.rerun()

# Selección
sessions = list(data["sessions"].keys())

if sessions:
    selected = st.sidebar.selectbox(
        "Sesión",
        sessions,
        format_func=lambda x: data["sessions"][x]["name"]
    )
    st.session_state.current = selected
else:
    st.info("Crea una sesión")
    st.stop()

session = data["sessions"][st.session_state.current]

# ─────────────────────────────
# MAIN UI
# ─────────────────────────────
st.title("Gestión de Puntos GPS")
st.subheader(session["name"])

# ─── FORM ───
with st.form("point_form"):
    col1, col2 = st.columns(2)
    lat = col1.number_input("Latitud", format="%.6f")
    lon = col2.number_input("Longitud", format="%.6f")
    desc = st.text_input("Descripción")

    submitted = st.form_submit_button("Guardar punto")

    if submitted:
        try:
            GPSService.add_point(session, lat, lon, desc)
            DataManager.save(data)
            st.success("Punto guardado")
            st.rerun()
        except Exception as e:
            st.error(str(e))

# ─── TABLE ───
points = session["points"]

if points:
    st.subheader("Puntos registrados")

    st.dataframe([
        {
            "Latitud": p["lat"],
            "Longitud": p["lon"],
            "Descripción": p["desc"],
            "Fecha": p["date"]
        }
        for p in points
    ])

    # Export
    st.download_button(
        "Exportar JSON",
        data=json.dumps(points, indent=2),
        file_name="gps_data.json"
    )
else:
    st.warning("No hay puntos aún")
