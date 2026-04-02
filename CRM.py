import streamlit as st
import json
import csv
import io
import math
from datetime import datetime
from pathlib import Path

st.set_page_config(layout="wide", page_title="GPS Tracker PRO")

DATA_FILE = Path("gps_data.json")

# ─────────────────────────────
# DATA
# ─────────────────────────────
def load():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"sessions": {}, "current": None}

def save(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))

if "data" not in st.session_state:
    st.session_state.data = load()

data = st.session_state.data

# ─────────────────────────────
# GPS JS
# ─────────────────────────────
gps_html = """
<script>
function getLocation(){
    navigator.geolocation.getCurrentPosition(function(pos){
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        const url = new URL(window.location);
        url.searchParams.set("lat", lat);
        url.searchParams.set("lon", lon);
        window.location.href = url;
    });
}
</script>
<button onclick="getLocation()">📍 Usar mi GPS</button>
"""

params = st.query_params

lat_q = params.get("lat")
lon_q = params.get("lon")

# ─────────────────────────────
# SIDEBAR
# ─────────────────────────────
st.sidebar.title("Sesiones")

name = st.sidebar.text_input("Nueva sesión")

if st.sidebar.button("Crear"):
    if name:
        sid = f"{name}_{datetime.now().strftime('%H%M%S')}"
        data["sessions"][sid] = {"name": name, "points": []}
        data["current"] = sid
        save(data)
        st.rerun()

sessions = list(data["sessions"].keys())

if not sessions:
    st.warning("Crea una sesión")
    st.stop()

current = st.sidebar.selectbox(
    "Seleccionar",
    sessions,
    format_func=lambda x: data["sessions"][x]["name"]
)

data["current"] = current
session = data["sessions"][current]

# ─────────────────────────────
# MAIN
# ─────────────────────────────
st.title("GPS Tracker")

tab1, tab2, tab3 = st.tabs(["📍 Captura", "🗺️ Mapa", "📤 Exportar"])

# ─────────────────────────────
# TAB 1
# ─────────────────────────────
with tab1:

    st.components.v1.html(gps_html, height=80)

    lat = float(lat_q) if lat_q else 0.0
    lon = float(lon_q) if lon_q else 0.0

    st.write("Lat:", lat, "Lon:", lon)

    desc = st.text_input("Descripción")

    if st.button("Guardar punto"):
        if lat != 0 and lon != 0:
            session["points"].append({
                "lat": lat,
                "lon": lon,
                "desc": desc,
                "time": datetime.now().isoformat()
            })
            save(data)
            st.success("Guardado")
            st.query_params.clear()
            st.rerun()
        else:
            st.error("Primero obtén GPS")

    st.write(session["points"])

# ─────────────────────────────
# TAB 2 MAPA
# ─────────────────────────────
with tab2:
    if session["points"]:
        import pandas as pd

        df = pd.DataFrame(session["points"])
        st.map(df.rename(columns={"lat": "latitude", "lon": "longitude"}))
    else:
        st.info("Sin puntos")

# ─────────────────────────────
# EXPORT
# ─────────────────────────────
with tab3:

    if session["points"]:

        # CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["lat","lon","desc","time"])
        writer.writeheader()
        writer.writerows(session["points"])

        st.download_button("CSV", output.getvalue(), "data.csv")

        # JSON
        st.download_button(
            "JSON",
            json.dumps(session["points"], indent=2),
            "data.json"
        )
