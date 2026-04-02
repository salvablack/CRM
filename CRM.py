import streamlit as st
import json
import csv
import os
import zipfile
import io
import math
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
#  CONFIG & PERSISTENCE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GPS Field Tracker",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Archivo temporal persistente en el dispositivo
DATA_FILE = Path(os.path.expanduser("~")) / "gps_tracker_data.json"


def load_data() -> dict:
    """Carga datos desde archivo local persistente."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"sessions": {}, "current_session": None}


def save_data(data: dict):
    """Guarda datos en archivo local persistente."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
#  ESTILOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg: #0b0f1a;
    --surface: #111827;
    --surface2: #1a2235;
    --accent: #00e5a0;
    --accent2: #0099ff;
    --warn: #ff6b35;
    --text: #e8edf5;
    --muted: #7a8599;
    --border: rgba(255,255,255,0.07);
    --radius: 12px;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,229,160,0.35) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
}

.stRadio > div {
    gap: 0.5rem;
}

.stRadio label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}

.metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
}

.point-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
}

.point-card.tracking {
    border-left-color: var(--accent2);
}

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.badge-track { background: rgba(0,153,255,0.15); color: var(--accent2); border: 1px solid rgba(0,153,255,0.3); }
.badge-point { background: rgba(0,229,160,0.12); color: var(--accent); border: 1px solid rgba(0,229,160,0.3); }
.badge-count { background: rgba(255,255,255,0.07); color: var(--muted); border: 1px solid var(--border); }

.header-band {
    background: linear-gradient(135deg, #0b1628 0%, #0d1f3c 50%, #0b1628 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.coord-display {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: var(--accent);
    background: rgba(0,229,160,0.06);
    padding: 2px 8px;
    border-radius: 4px;
}

.file-indicator {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    background: var(--surface2);
    padding: 4px 10px;
    border-radius: 6px;
    border: 1px solid var(--border);
}

.stDownloadButton > button {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.82rem !important;
}

.stDownloadButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    color: var(--accent) !important;
}

.delete-btn > button {
    background: rgba(255,107,53,0.15) !important;
    color: var(--warn) !important;
    border: 1px solid rgba(255,107,53,0.3) !important;
    font-size: 0.75rem !important;
    padding: 0.25rem 0.6rem !important;
}

.warning-box {
    background: rgba(255,107,53,0.08);
    border: 1px solid rgba(255,107,53,0.25);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: var(--warn);
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2) -> float:
    """Distancia en metros entre dos coordenadas."""
    R = 6371000
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(Δλ/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def points_to_csv(points: list) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["seq", "title", "description", "latitude", "longitude", "altitude", "date", "mode"])
    writer.writeheader()
    for i, p in enumerate(points, 1):
        writer.writerow({
            "seq": i,
            "title": p.get("title", ""),
            "description": p.get("description", ""),
            "latitude": p["lat"],
            "longitude": p["lon"],
            "altitude": p.get("alt", 0),
            "date": p.get("date", ""),
            "mode": p.get("mode", "point"),
        })
    return output.getvalue()


def points_to_kml(session_name: str, points: list, mode: str) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<kml xmlns="http://www.opengis.net/kml/2.2">',
             '<Document>',
             f'  <name>{session_name}</name>',
             '  <Style id="trackStyle"><LineStyle><color>ff00aaff</color><width>3</width></LineStyle></Style>',
             '  <Style id="pointStyle"><IconStyle><color>ff00e5a0</color><scale>1.2</scale></IconStyle></Style>',
             ]
    for i, p in enumerate(points, 1):
        lines += [
            '  <Placemark>',
            f'    <name>{p.get("title", f"Punto {i}")}</name>',
            f'    <description>{p.get("description","")}\n📅 {p.get("date","")}</description>',
            '    <styleUrl>#pointStyle</styleUrl>',
            '    <Point>',
            f'      <coordinates>{p["lon"]},{p["lat"]},{p.get("alt",0)}</coordinates>',
            '    </Point>',
            '  </Placemark>',
        ]
    if mode == "tracking" and len(points) >= 2:
        coords = " ".join(f'{p["lon"]},{p["lat"]},{p.get("alt",0)}' for p in points)
        lines += [
            '  <Placemark>',
            f'    <name>{session_name} — Track</name>',
            '    <styleUrl>#trackStyle</styleUrl>',
            '    <LineString><tessellate>1</tessellate>',
            f'      <coordinates>{coords}</coordinates>',
            '    </LineString>',
            '  </Placemark>',
        ]
    lines += ['</Document>', '</kml>']
    return "\n".join(lines)


def build_kmz(session_name: str, points: list, mode: str) -> bytes:
    kml_content = points_to_kml(session_name, points, mode)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("doc.kml", kml_content)
    return buf.getvalue()


def build_map_html(points: list, mode: str) -> str:
    if not points:
        return "<p>Sin puntos</p>"
    center_lat = sum(p["lat"] for p in points) / len(points)
    center_lon = sum(p["lon"] for p in points) / len(points)
    markers_js = ""
    for i, p in enumerate(points, 1):
        color = "blue" if mode == "tracking" else "green"
        popup = f"{i}. {p.get('title','Sin título')}<br>{p.get('description','')}<br>{p.get('date','')}"
        markers_js += f"""
        L.circleMarker([{p['lat']}, {p['lon']}], {{
            radius: 8, color: '{"#0099ff" if mode=="tracking" else "#00e5a0"}',
            fillColor: '{"#0099ff" if mode=="tracking" else "#00e5a0"}', fillOpacity: 0.8
        }}).addTo(map).bindPopup(`{popup}`);
        L.tooltip({{permanent: true, direction: 'top', className: 'lbl'}})
         .setContent('{i}').addTo(map).setLatLng([{p['lat']}, {p['lon']}]);
"""
    polyline_js = ""
    if mode == "tracking" and len(points) >= 2:
        coords = ", ".join(f"[{p['lat']}, {p['lon']}]" for p in points)
        polyline_js = f"L.polyline([{coords}], {{color: '#0099ff', weight: 3, opacity: 0.8}}).addTo(map);"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  body {{ margin:0; background:#0b0f1a; font-family: monospace; }}
  #map {{ height:100vh; }}
  .lbl {{ background:transparent; border:none; box-shadow:none; color:#fff; font-size:11px; font-weight:bold; }}
</style>
</head>
<body>
<div id="map"></div>
<script>
  var map = L.map('map').setView([{center_lat}, {center_lon}], 14);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
    {{attribution:'© OpenStreetMap'}}).addTo(map);
  {markers_js}
  {polyline_js}
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
#  ESTADO & CARGA
# ─────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


def save():
    save_data(data)


# ─────────────────────────────────────────────
#  SIDEBAR — Sesiones
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛰️ GPS Field Tracker")
    st.markdown(f'<div class="file-indicator">💾 {DATA_FILE}</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("### 📁 Sesiones")

    # Crear nueva sesión
    with st.expander("➕ Nueva sesión"):
        new_name = st.text_input("Nombre de sesión", key="new_session_name")
        new_mode = st.radio("Modo", ["Puntos independientes", "Tracking (secuencia)"], key="new_mode")
        if st.button("Crear sesión"):
            if new_name.strip():
                sid = f"{new_name.strip()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                data["sessions"][sid] = {
                    "name": new_name.strip(),
                    "mode": "tracking" if "Tracking" in new_mode else "point",
                    "created": datetime.now().isoformat(),
                    "points": []
                }
                data["current_session"] = sid
                save()
                st.success("✅ Sesión creada")
                st.rerun()
            else:
                st.warning("Ingresa un nombre")

    # Seleccionar sesión
    session_ids = list(data["sessions"].keys())
    session_names = [f'{data["sessions"][s]["name"]} ({data["sessions"][s]["mode"]})' for s in session_ids]

    if session_ids:
        cur_index = 0
        if data["current_session"] in session_ids:
            cur_index = session_ids.index(data["current_session"])
        selected_label = st.selectbox("Sesión activa", session_names, index=cur_index, key="session_select")
        selected_sid = session_ids[session_names.index(selected_label)]
        if selected_sid != data["current_session"]:
            data["current_session"] = selected_sid
            save()
            st.rerun()
    else:
        st.info("Crea tu primera sesión ↑")
        selected_sid = None

    # Eliminar sesión
    if selected_sid:
        st.divider()
        with st.expander("🗑️ Eliminar sesión actual"):
            if st.button("⚠️ Confirmar eliminación", type="secondary"):
                del data["sessions"][selected_sid]
                data["current_session"] = list(data["sessions"].keys())[-1] if data["sessions"] else None
                save()
                st.rerun()


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
if not selected_sid or selected_sid not in data["sessions"]:
    st.markdown("## 🛰️ GPS Field Tracker")
    st.info("Crea una sesión desde el menú lateral para comenzar.")
    st.stop()

session = data["sessions"][selected_sid]
points = session["points"]
mode = session["mode"]

# Header
mode_badge = "tracking" if mode == "tracking" else "point"
badge_class = "badge-track" if mode == "tracking" else "badge-point"
badge_label = "TRACKING" if mode == "tracking" else "PUNTOS"

st.markdown(f"""
<div class="header-band">
  <div>
    <div style="font-size:0.75rem; color:#7a8599; font-family:'Space Mono',monospace; text-transform:uppercase; letter-spacing:2px; margin-bottom:4px;">Sesión activa</div>
    <div style="font-size:1.6rem; font-weight:800;">{session['name']}</div>
    <div style="margin-top:6px; display:flex; gap:8px; align-items:center;">
      <span class="badge {badge_class}">{badge_label}</span>
      <span class="badge badge-count">{len(points)} punto{'s' if len(points)!=1 else ''}</span>
      <span style="color:#7a8599; font-family:'Space Mono',monospace; font-size:0.72rem;">Creada: {session.get('created','')[:16]}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Tabs ───
tab_add, tab_view, tab_map, tab_export = st.tabs([
    "📍 Agregar punto", "📋 Ver puntos", "🗺️ Ver en mapa", "📤 Exportar"
])


# ─────────────────────────────────────────────
# TAB 1: AGREGAR PUNTO
# ─────────────────────────────────────────────
with tab_add:
    st.markdown("### Registrar nuevo punto GPS")

    col_a, col_b = st.columns(2)
    with col_a:
        title = st.text_input("📌 Título del punto", placeholder="Ej: Entrada del sitio")
    with col_b:
        date_val = st.date_input("📅 Fecha", value=datetime.today())

    description = st.text_area("📝 Descripción", placeholder="Notas, observaciones, condiciones del terreno...", height=90)

    col1, col2, col3 = st.columns(3)
    with col1:
        lat = st.number_input("🌐 Latitud", value=0.0, format="%.7f", step=0.0000001)
    with col2:
        lon = st.number_input("🌐 Longitud", value=0.0, format="%.7f", step=0.0000001)
    with col3:
        alt = st.number_input("⛰️ Altitud (m)", value=0.0, format="%.1f")

    st.markdown("**💡 Ingresa las coordenadas desde tu GPS / app de maps**")

    time_val = st.time_input("⏰ Hora", value=datetime.now().time())

    if mode == "tracking" and len(points) > 0:
        last = points[-1]
        dist = haversine(last["lat"], last["lon"], lat, lon)
        st.markdown(f'<div class="metric-card">📏 Distancia al punto anterior: <span style="color:#0099ff;font-family:Space Mono,monospace;font-weight:700;">{dist:.1f} m</span></div>', unsafe_allow_html=True)

    if st.button("✅ Guardar punto GPS", use_container_width=True):
        if lat == 0.0 and lon == 0.0:
            st.markdown('<div class="warning-box">⚠️ Las coordenadas parecen ser 0,0 — verifica la latitud y longitud.</div>', unsafe_allow_html=True)
        else:
            new_point = {
                "title": title.strip() or f"Punto {len(points)+1}",
                "description": description.strip(),
                "lat": lat,
                "lon": lon,
                "alt": alt,
                "date": f"{date_val} {time_val}",
                "mode": mode,
            }
            session["points"].append(new_point)
            save()
            st.success(f"✅ Punto #{len(session['points'])} guardado correctamente")
            st.rerun()


# ─────────────────────────────────────────────
# TAB 2: VER PUNTOS
# ─────────────────────────────────────────────
with tab_view:
    if not points:
        st.info("Aún no hay puntos en esta sesión. Ve a **Agregar punto** para comenzar.")
    else:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total puntos", len(points))
        if mode == "tracking" and len(points) >= 2:
            total_dist = sum(
                haversine(points[i]["lat"], points[i]["lon"], points[i+1]["lat"], points[i+1]["lon"])
                for i in range(len(points)-1)
            )
            col_m2.metric("Distancia total", f"{total_dist:.0f} m")
            col_m3.metric("Distancia km", f"{total_dist/1000:.3f} km")
        else:
            col_m2.metric("Modo", "Puntos independientes")

        st.markdown("---")

        for i, p in enumerate(points):
            card_class = "point-card tracking" if mode == "tracking" else "point-card"
            seq_label = f"#{i+1}" if mode == "tracking" else "●"
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"""
                <div class="{card_class}">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-weight:700;font-size:0.95rem;color:#e8edf5;">{seq_label} {p.get('title','Sin título')}</span>
                    <span style="color:#7a8599;font-size:0.72rem;">{p.get('date','')}</span>
                  </div>
                  <div style="color:#7a8599;margin-bottom:6px;font-size:0.8rem;">{p.get('description','') or '—'}</div>
                  <span class="coord-display">LAT {p['lat']:.7f}</span>&nbsp;
                  <span class="coord-display">LON {p['lon']:.7f}</span>&nbsp;
                  <span class="coord-display">ALT {p.get('alt',0):.1f}m</span>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                with st.container():
                    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{i}_{selected_sid}", help="Eliminar punto"):
                        session["points"].pop(i)
                        save()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TAB 3: MAPA
# ─────────────────────────────────────────────
with tab_map:
    if not points:
        st.info("Agrega puntos para visualizarlos en el mapa.")
    else:
        map_html = build_map_html(points, mode)
        st.components.v1.html(map_html, height=520, scrolling=False)
        st.markdown(f"📍 Mostrando **{len(points)} punto(s)** en modo **{mode}**")


# ─────────────────────────────────────────────
# TAB 4: EXPORTAR
# ─────────────────────────────────────────────
with tab_export:
    if not points:
        st.info("No hay puntos para exportar.")
    else:
        st.markdown("### Exportar datos")
        st.markdown(f"Sesión: **{session['name']}** — {len(points)} punto(s) — Modo: **{mode}**")

        st.divider()

        col_e1, col_e2, col_e3 = st.columns(3)

        # CSV
        with col_e1:
            st.markdown("#### 📊 CSV")
            st.markdown("Compatible con Excel, QGIS, Google Sheets.")
            csv_data = points_to_csv(points)
            fname_csv = f"{session['name'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv"
            st.download_button(
                "⬇️ Descargar CSV",
                data=csv_data.encode("utf-8"),
                file_name=fname_csv,
                mime="text/csv",
                use_container_width=True,
            )

        # KMZ
        with col_e2:
            st.markdown("#### 🗺️ KMZ")
            st.markdown("Compatible con Google Earth, Maps, QGIS.")
            kmz_data = build_kmz(session["name"], points, mode)
            fname_kmz = f"{session['name'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.kmz"
            st.download_button(
                "⬇️ Descargar KMZ",
                data=kmz_data,
                file_name=fname_kmz,
                mime="application/vnd.google-earth.kmz",
                use_container_width=True,
            )

        # KML
        with col_e3:
            st.markdown("#### 📌 KML")
            st.markdown("Formato abierto para SIG y mapas.")
            kml_data = points_to_kml(session["name"], points, mode)
            fname_kml = f"{session['name'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.kml"
            st.download_button(
                "⬇️ Descargar KML",
                data=kml_data.encode("utf-8"),
                file_name=fname_kml,
                mime="application/vnd.google-earth.kml+xml",
                use_container_width=True,
            )

        st.divider()

        # JSON backup completo
        st.markdown("#### 💾 Respaldo completo (JSON)")
        st.markdown("Exporta **todas las sesiones** como respaldo del archivo local.")
        json_backup = json.dumps(data, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️ Descargar respaldo JSON",
            data=json_backup.encode("utf-8"),
            file_name=f"gps_tracker_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=False,
        )

        st.markdown("---")
        st.markdown(f'<div class="file-indicator">💾 Datos guardados localmente en: {DATA_FILE}</div>', unsafe_allow_html=True)
