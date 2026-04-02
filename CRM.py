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
#  CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GPS Tracker",
    page_icon="📍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = Path(os.path.expanduser("~")) / "gps_tracker_data.json"


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"points": [], "routes": []}


def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
#  TEMA — Negro + Teal + Verde (igual a capturas)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');

* { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, .block-container {
    background-color: #1a1a1a !important;
    color: #ffffff !important;
    font-family: 'Roboto', sans-serif !important;
    padding-top: 0 !important;
}

[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] { background: #111 !important; }
[data-testid="stSidebarNav"] { display: none; }

.block-container {
    max-width: 480px !important;
    padding: 0 12px 100px 12px !important;
    margin: 0 auto !important;
}

/* Ocultar decoraciones innecesarias */
footer { display: none !important; }
#MainMenu { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Títulos ── */
h1, h2, h3 {
    font-family: 'Roboto', sans-serif !important;
    color: #ffffff !important;
}

/* ── Botón grande TEAL (Capturar Punto) ── */
.btn-teal {
    display: block;
    background: #1a8fa0;
    border-radius: 16px;
    padding: 28px 20px;
    text-align: center;
    cursor: pointer;
    margin-bottom: 12px;
    border: none;
    width: 100%;
    transition: opacity .2s;
}
.btn-teal:hover { opacity: .9; }
.btn-teal .icon { font-size: 2rem; margin-bottom: 6px; }
.btn-teal .label { font-size: 1.25rem; font-weight: 700; color: #fff; display: block; }
.btn-teal .sublabel { font-size: .85rem; color: rgba(255,255,255,.75); display: block; margin-top: 2px; }

/* ── Botón grande VERDE (Iniciar Tracking) ── */
.btn-green {
    display: block;
    background: #2ecc71;
    border-radius: 16px;
    padding: 28px 20px;
    text-align: center;
    cursor: pointer;
    margin-bottom: 12px;
    border: none;
    width: 100%;
    transition: opacity .2s;
}
.btn-green:hover { opacity: .9; }
.btn-green .icon { font-size: 2rem; margin-bottom: 6px; }
.btn-green .label { font-size: 1.25rem; font-weight: 700; color: #fff; display: block; }
.btn-green .sublabel { font-size: .85rem; color: rgba(255,255,255,.75); display: block; margin-top: 2px; }

/* ── Card oscura ── */
.dark-card {
    background: #2a2a2a;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 12px;
}

/* ── GPS status bar ── */
.gps-bar {
    background: #2a2a2a;
    border-radius: 12px;
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    font-weight: 500;
    font-size: .95rem;
}
.gps-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.gps-dot-on  { background: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
.gps-dot-off { background: #e74c3c; }
.gps-dot-search { background: #f39c12; box-shadow: 0 0 8px #f39c12; }

/* ── Stats ── */
.stats-card {
    background: #2a2a2a;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.stats-title { font-weight: 700; font-size: 1rem; margin-bottom: 12px; color: #fff; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; text-align: center; }
.stat-val { font-size: 1.8rem; font-weight: 900; }
.stat-lbl { font-size: .72rem; color: #aaa; margin-top: 2px; }
.color-teal { color: #1ab8d0; }
.color-green { color: #2ecc71; }
.color-yellow { color: #f1c40f; }

/* ── Nav link cards ── */
.nav-card {
    background: #2a2a2a;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 500;
    font-size: 1rem;
    cursor: pointer;
}
.nav-card .left { display: flex; align-items: center; gap: 12px; }
.nav-card .arrow { color: #555; font-size: 1.2rem; }

/* ── Streamlit buttons override → invisible, we use HTML ── */
div[data-testid="stButton"] > button {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    color: transparent !important;
    font-size: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}

/* ── Page title bar ── */
.page-title {
    font-size: 1.6rem; font-weight: 900; color: #fff;
    padding: 18px 0 6px 0; margin-bottom: 4px;
}
.page-subtitle { font-size: .82rem; color: #888; margin-bottom: 16px; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #2a2a2a !important;
    border: 1px solid #3a3a3a !important;
    color: #fff !important;
    border-radius: 10px !important;
    font-family: 'Roboto', sans-serif !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label,
.stDateInput label, .stTimeInput label {
    color: #aaa !important; font-size: .82rem !important;
}
.stDateInput > div > div > input, .stTimeInput > div > div > input {
    background: #2a2a2a !important; border: 1px solid #3a3a3a !important;
    color: #fff !important; border-radius: 10px !important;
}

/* ── Real action buttons ── */
.action-btn {
    width: 100%; padding: 15px; border: none; border-radius: 12px;
    font-family: 'Roboto', sans-serif; font-weight: 700; font-size: 1rem;
    cursor: pointer; transition: opacity .2s; display: flex;
    align-items: center; justify-content: center; gap: 8px; margin-bottom: 10px;
}
.action-btn-teal { background: #1a8fa0; color: #fff; }
.action-btn-green { background: #2ecc71; color: #fff; }
.action-btn-red   { background: #e74c3c; color: #fff; }
.action-btn:hover { opacity: .88; }

/* ── Data card (Visualización) ── */
.data-card {
    background: #1a8fa0;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
    color: #fff;
}
.data-card-route {
    background: #27ae60;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
    color: #fff;
}
.data-card h3 { font-size: 1.1rem; font-weight: 700; margin-bottom: 2px; color: #fff; }
.data-card .dc-type { font-size: .8rem; opacity: .8; margin-bottom: 14px; }
.data-card-route h3 { font-size: 1.1rem; font-weight: 700; margin-bottom: 2px; color: #fff; }
.data-card-route .dc-type { font-size: .8rem; opacity: .8; margin-bottom: 14px; }
.dc-sep { border: none; border-top: 1px solid rgba(255,255,255,.2); margin: 10px 0; }
.dc-lbl { font-size: .75rem; opacity: .75; margin-bottom: 2px; }
.dc-val { font-size: .95rem; font-weight: 500; margin-bottom: 10px; }

/* ── Download buttons ── */
.stDownloadButton > button {
    border-radius: 12px !important;
    font-family: 'Roboto', sans-serif !important;
    font-weight: 700 !important;
    font-size: .95rem !important;
    padding: 14px !important;
    border: none !important;
    width: 100% !important;
    transition: opacity .2s !important;
}
div[data-testid="column"]:nth-child(1) .stDownloadButton > button {
    background: #1a8fa0 !important; color: #fff !important;
}
div[data-testid="column"]:nth-child(2) .stDownloadButton > button {
    background: #2ecc71 !important; color: #fff !important;
}

/* ── Back button ── */
.back-btn {
    color: #1ab8d0; font-weight: 500; font-size: .95rem;
    cursor: pointer; display: inline-flex; align-items: center;
    gap: 5px; padding: 8px 0; margin-bottom: 10px; background: none; border: none;
}

/* ── Bottom Nav ── */
.bottom-nav {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: #222; border-top: 1px solid #333;
    display: flex; z-index: 999; padding-bottom: env(safe-area-inset-bottom);
}
.bnav-item {
    flex: 1; padding: 12px 4px; text-align: center;
    cursor: pointer; font-size: .65rem; color: #666;
    display: flex; flex-direction: column; align-items: center; gap: 3px;
}
.bnav-item.active { color: #1ab8d0; }
.bnav-icon { font-size: 1.4rem; }

/* ── Metric ── */
[data-testid="stMetricValue"] {
    font-family: 'Roboto', sans-serif !important;
    font-weight: 900 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { display: none !important; }

/* ── GPS Component iframe border ── */
iframe { border: none !important; }

/* ── Remove extra spacing ── */
.stMarkdown { margin: 0 !important; }
div[data-testid="stVerticalBlock"] > div { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def points_to_csv(items):
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=["n","tipo","titulo","descripcion","latitud","longitud","altitud","precision_m","fecha"])
    w.writeheader()
    for i, p in enumerate(items, 1):
        w.writerow({"n": i, "tipo": p.get("tipo","punto"),
                    "titulo": p.get("title",""), "descripcion": p.get("desc",""),
                    "latitud": p["lat"], "longitud": p["lon"],
                    "altitud": p.get("alt", 0), "precision_m": p.get("acc",""),
                    "fecha": p.get("date","")})
    return out.getvalue()


def build_kml(items):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
             '  <n>GPS Tracker Export</n>',
             '  <Style id="ps"><IconStyle><color>ff00aaff</color><scale>1.2</scale>'
             '<Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon>'
             '</IconStyle></Style>',
             '  <Style id="ls"><LineStyle><color>ff2ecc71</color><width>4</width></LineStyle></Style>']

    # puntos individuales
    indep = [p for p in items if p.get("tipo") == "punto"]
    for i, p in enumerate(indep, 1):
        lines += ['  <Placemark>',
                  f'    <n>{p.get("title", f"Punto {i}")}</n>',
                  f'    <description>{p.get("desc","")}\nFecha: {p.get("date","")}\nPrecision: {p.get("acc","")}m</description>',
                  '    <styleUrl>#ps</styleUrl>',
                  f'    <Point><coordinates>{p["lon"]},{p["lat"]},{p.get("alt",0)}</coordinates></Point>',
                  '  </Placemark>']

    # rutas
    rutas = {}
    for p in items:
        if p.get("tipo") == "ruta":
            rn = p.get("route_name","Ruta")
            rutas.setdefault(rn, []).append(p)

    for rname, rpts in rutas.items():
        for i, p in enumerate(rpts, 1):
            lines += ['  <Placemark>',
                      f'    <n>{rname} #{i}</n>',
                      f'    <description>{p.get("desc","")}</description>',
                      '    <styleUrl>#ps</styleUrl>',
                      f'    <Point><coordinates>{p["lon"]},{p["lat"]},{p.get("alt",0)}</coordinates></Point>',
                      '  </Placemark>']
        if len(rpts) >= 2:
            coords = " ".join(f'{p["lon"]},{p["lat"]},{p.get("alt",0)}' for p in rpts)
            lines += ['  <Placemark>', f'    <n>{rname} — Recorrido</n>',
                      '    <styleUrl>#ls</styleUrl>',
                      '    <LineString><tessellate>1</tessellate>',
                      f'      <coordinates>{coords}</coordinates>',
                      '    </LineString>', '  </Placemark>']
    lines += ['</Document></kml>']
    return "\n".join(lines)


def build_kmz(items):
    kml = build_kml(items)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("doc.kml", kml)
    return buf.getvalue()


def build_map_html(items):
    if not items:
        return ""
    clat = sum(p["lat"] for p in items) / len(items)
    clon = sum(p["lon"] for p in items) / len(items)
    markers = ""
    for i, p in enumerate(items, 1):
        col = "#2ecc71" if p.get("tipo") == "ruta" else "#1ab8d0"
        popup = f"{i}. {p.get('title','')}<br>{p.get('desc','')}<br>{p.get('date','')}"
        markers += f"""
L.circleMarker([{p['lat']},{p['lon']}],{{
    radius:9,color:'{col}',fillColor:'{col}',fillOpacity:.9,weight:2
}}).addTo(map).bindPopup(`{popup}`);
L.marker([{p['lat']},{p['lon']}],{{
    icon:L.divIcon({{className:'',html:`<div style='color:#fff;font-size:10px;font-weight:bold;
    background:{col};border-radius:50%;width:18px;height:18px;display:flex;align-items:center;
    justify-content:center;font-family:Roboto,sans-serif;margin-left:-9px;margin-top:-9px'>{i}</div>`,iconSize:[0,0]}})
}}).addTo(map);
"""
    # líneas de rutas
    rutas = {}
    for p in items:
        if p.get("tipo") == "ruta":
            rutas.setdefault(p.get("route_name","Ruta"), []).append(p)
    poly = ""
    for rpts in rutas.values():
        if len(rpts) >= 2:
            coords = ",".join(f"[{p['lat']},{p['lon']}]" for p in rpts)
            poly += f"L.polyline([{coords}],{{color:'#2ecc71',weight:3,opacity:.8}}).addTo(map);\n"

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>body{{margin:0;background:#1a1a1a;}}#map{{height:100vh;}}</style>
</head><body><div id="map"></div><script>
var map=L.map('map').setView([{clat},{clon}],15);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
  {{attribution:'© OSM',maxZoom:19}}).addTo(map);
{markers}{poly}
</script></body></html>"""


# ─────────────────────────────────────────────
#  GPS COMPONENT
# ─────────────────────────────────────────────
GPS_HTML = """
<div style="font-family:'Roboto',sans-serif;">

  <!-- Status bar -->
  <div id="gps-bar" style="background:#2a2a2a;border-radius:12px;padding:14px 18px;
    display:flex;align-items:center;gap:10px;margin-bottom:12px;">
    <div id="dot" style="width:10px;height:10px;border-radius:50%;background:#f39c12;
      box-shadow:0 0 8px #f39c12;flex-shrink:0;animation:blink 1s infinite;"></div>
    <span id="status-txt" style="color:#fff;font-weight:500;font-size:.9rem;">
      Buscando señal GPS...</span>
  </div>

  <!-- Coords grid -->
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:10px;">
    <div style="background:#2a2a2a;border-radius:10px;padding:12px;text-align:center;">
      <div style="font-size:.62rem;color:#888;text-transform:uppercase;margin-bottom:4px;">Latitud</div>
      <div id="vlat" style="font-size:.82rem;color:#1ab8d0;font-weight:700;">—</div>
    </div>
    <div style="background:#2a2a2a;border-radius:10px;padding:12px;text-align:center;">
      <div style="font-size:.62rem;color:#888;text-transform:uppercase;margin-bottom:4px;">Longitud</div>
      <div id="vlon" style="font-size:.82rem;color:#1ab8d0;font-weight:700;">—</div>
    </div>
    <div style="background:#2a2a2a;border-radius:10px;padding:12px;text-align:center;">
      <div style="font-size:.62rem;color:#888;text-transform:uppercase;margin-bottom:4px;">Altitud</div>
      <div id="valt" style="font-size:.82rem;color:#1ab8d0;font-weight:700;">—</div>
    </div>
  </div>

  <!-- Accuracy -->
  <div style="background:#2a2a2a;border-radius:10px;padding:12px;margin-bottom:14px;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
      <span style="font-size:.72rem;color:#888;">Precisión GPS</span>
      <span id="vacc" style="font-size:.8rem;color:#1ab8d0;font-weight:700;">—</span>
    </div>
    <div style="background:#1a1a1a;border-radius:4px;height:5px;">
      <div id="accbar" style="height:100%;border-radius:4px;background:#f39c12;width:5%;transition:width .5s;"></div>
    </div>
  </div>

  <!-- Capture button -->
  <button id="capbtn" onclick="doCapture()" disabled style="
    width:100%;padding:16px;background:#1a8fa0;color:#fff;border:none;
    border-radius:12px;font-family:'Roboto',sans-serif;font-weight:700;
    font-size:1rem;cursor:pointer;opacity:.4;transition:all .2s;
    display:flex;align-items:center;justify-content:center;gap:8px;">
    📍 Capturar Ubicación GPS
  </button>

  <div id="errmsg" style="display:none;margin-top:10px;background:rgba(231,76,60,.12);
    border:1px solid rgba(231,76,60,.3);border-radius:10px;padding:12px;
    color:#e74c3c;font-size:.8rem;"></div>
</div>

<style>
  @keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}
  @keyframes gpson{0%{box-shadow:0 0 0 0 rgba(46,204,113,.5)}
    70%{box-shadow:0 0 0 10px rgba(46,204,113,0)}100%{box-shadow:0 0 0 0 rgba(46,204,113,0)}}
</style>

<script>
var cur = null;

function setStatus(txt, color, anim) {
  document.getElementById('status-txt').textContent = txt;
  document.getElementById('status-txt').style.color = color;
  var d = document.getElementById('dot');
  d.style.background = color;
  d.style.boxShadow = '0 0 8px ' + color;
  d.style.animation = anim || '';
}

if (!navigator.geolocation) {
  var el = document.getElementById('errmsg');
  el.style.display = 'block';
  el.textContent = '⚠️ Tu navegador no soporta GPS. Usa Chrome en Android.';
  setStatus('GPS no disponible', '#e74c3c', '');
} else {
  navigator.geolocation.watchPosition(
    function(pos) {
      var c = pos.coords;
      cur = {
        lat: c.latitude, lon: c.longitude,
        alt: c.altitude !== null ? parseFloat(c.altitude.toFixed(1)) : 0,
        acc: Math.round(c.accuracy)
      };
      document.getElementById('vlat').textContent = c.latitude.toFixed(7);
      document.getElementById('vlon').textContent = c.longitude.toFixed(7);
      document.getElementById('valt').textContent = c.altitude !== null
        ? c.altitude.toFixed(1) + ' m' : 'N/D';
      document.getElementById('vacc').textContent = '±' + Math.round(c.accuracy) + ' m';
      var pct = Math.max(5, Math.min(100, 100 - (c.accuracy / 50 * 100)));
      var bc  = c.accuracy < 10 ? '#2ecc71' : c.accuracy < 30 ? '#f39c12' : '#e74c3c';
      document.getElementById('accbar').style.width = pct + '%';
      document.getElementById('accbar').style.background = bc;
      var btn = document.getElementById('capbtn');
      btn.disabled = false; btn.style.opacity = '1';
      btn.style.background = '#1a8fa0';
      setStatus('GPS Conectado · ±' + Math.round(c.accuracy) + ' m', '#2ecc71', 'gpson 1.5s infinite');
      document.getElementById('errmsg').style.display = 'none';
    },
    function(err) {
      var msgs = {
        1: 'Permiso denegado. Ve a Ajustes del navegador → Permisos → Ubicación.',
        2: 'GPS no disponible. Activa el GPS y sal al exterior.',
        3: 'Tiempo agotado. Verifica que el GPS esté activado en el teléfono.'
      };
      var el = document.getElementById('errmsg');
      el.style.display = 'block';
      el.textContent = '⚠️ ' + (msgs[err.code] || err.message);
      setStatus('Error de GPS', '#e74c3c', '');
    },
    { enableHighAccuracy: true, maximumAge: 5000, timeout: 20000 }
  );
}

function doCapture() {
  if (!cur) return;
  var base = window.parent.location.href.split('?')[0];
  window.parent.location.href = base
    + '?glat=' + cur.lat
    + '&glon=' + cur.lon
    + '&galt=' + cur.alt
    + '&gacc=' + cur.acc;
}
</script>
"""


# ─────────────────────────────────────────────
#  ESTADO
# ─────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "page" not in st.session_state:
    st.session_state.page = "home"
if "capture_mode" not in st.session_state:
    st.session_state.capture_mode = None   # "punto" o "ruta"
if "active_route" not in st.session_state:
    st.session_state.active_route = None   # nombre de ruta activa
if "tracking_on" not in st.session_state:
    st.session_state.tracking_on = False

data = st.session_state.data


def save():
    save_data(data)


def go(page):
    st.session_state.page = page
    st.rerun()


# ── Leer GPS desde query params ──
qp = st.query_params
if "glat" in qp:
    try:
        st.session_state["gps_lat"] = float(qp["glat"])
        st.session_state["gps_lon"] = float(qp["glon"])
        st.session_state["gps_alt"] = float(qp.get("galt", 0))
        st.session_state["gps_acc"] = float(qp.get("gacc", 0))
        # Si venía de captura, ir a la página correcta
        if st.session_state.capture_mode:
            pass  # ya está en la página correcta
    except Exception:
        pass

gps_lat = st.session_state.get("gps_lat")
gps_lon = st.session_state.get("gps_lon")
gps_alt = st.session_state.get("gps_alt", 0.0)
gps_acc = st.session_state.get("gps_acc")

# ── Calcular estadísticas ──
all_items = data.get("points", [])
n_puntos = len([p for p in all_items if p.get("tipo") == "punto"])
n_rutas  = len(set(p.get("route_name","") for p in all_items if p.get("tipo") == "ruta"))
n_total  = len(all_items)


# ─────────────────────────────────────────────────────────────────────────────
#  PÁGINA: HOME
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "home":

    st.markdown('<div class="page-subtitle" style="color:#aaa;font-size:.85rem;'
                'padding-top:16px;">Registra tus puntos y rutas</div>', unsafe_allow_html=True)

    # GPS bar (solo visual)
    gps_connected = gps_lat is not None
    dot_cls = "gps-dot-on" if gps_connected else "gps-dot-search"
    gps_txt = f"GPS Conectado — {gps_lat:.5f}, {gps_lon:.5f}" if gps_connected else "GPS — Abre 📍 Capturar para activar"
    st.markdown(f"""
<div class="gps-bar">
  <div class="gps-dot {dot_cls}"></div>
  <span style="font-size:.88rem;">{gps_txt}</span>
</div>
""", unsafe_allow_html=True)

    # Botón CAPTURAR PUNTO
    st.markdown("""
<div class="btn-teal" onclick="">
  <div class="icon">📍</div>
  <span class="label">Capturar Punto</span>
  <span class="sublabel">Punto independiente</span>
</div>
""", unsafe_allow_html=True)
    if st.button("__capturar_punto__", key="btn_cap"):
        st.session_state.capture_mode = "punto"
        go("capturar")
    # Overlay invisible encima del card HTML
    st.markdown("""<style>
div[data-testid="stButton"]:has(button[kind="secondary"]:first-child) {
  margin-top: -100px; opacity: 0; height: 100px;
}
</style>""", unsafe_allow_html=True)

    # Usamos columnas para los dos botones grandes
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📍 Capturar\nPunto", use_container_width=True, key="h_cap"):
            st.session_state.capture_mode = "punto"
            go("capturar")
    with col2:
        label = "⏹ Detener\nTracking" if st.session_state.tracking_on else "🔀 Iniciar\nTracking"
        if st.button(label, use_container_width=True, key="h_track"):
            if not st.session_state.tracking_on:
                st.session_state.tracking_on = True
                st.session_state.active_route = f"Ruta_{datetime.now().strftime('%d%m%Y_%H%M')}"
                st.session_state.capture_mode = "ruta"
                go("capturar")
            else:
                st.session_state.tracking_on = False
                st.session_state.active_route = None
                st.session_state.capture_mode = None
                st.rerun()

    # Redefinir los botones de Streamlit con el estilo correcto
    st.markdown("""
<style>
/* Botón izquierdo = teal */
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) button {
    background: #1a8fa0 !important; color: #fff !important;
    border-radius: 16px !important; padding: 28px 10px !important;
    font-size: 1rem !important; font-weight: 700 !important;
    white-space: pre-line !important; height: auto !important; min-height: 90px;
}
/* Botón derecho = verde */
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) button {
    background: #2ecc71 !important; color: #fff !important;
    border-radius: 16px !important; padding: 28px 10px !important;
    font-size: 1rem !important; font-weight: 700 !important;
    white-space: pre-line !important; height: auto !important; min-height: 90px;
}
div[data-testid="stHorizontalBlock"] button:hover { opacity: .88 !important; }
</style>
""", unsafe_allow_html=True)

    # Tracking activo banner
    if st.session_state.tracking_on and st.session_state.active_route:
        ruta_pts = [p for p in all_items if p.get("route_name") == st.session_state.active_route]
        st.markdown(f"""
<div style="background:#27ae60;border-radius:12px;padding:12px 16px;
  margin:8px 0;display:flex;align-items:center;gap:10px;">
  <div style="width:8px;height:8px;border-radius:50%;background:#fff;
    animation:blink 1s infinite;flex-shrink:0;"></div>
  <div>
    <div style="font-weight:700;font-size:.9rem;color:#fff;">Tracking activo</div>
    <div style="font-size:.75rem;color:rgba(255,255,255,.8);">
      {st.session_state.active_route} · {len(ruta_pts)} pt(s) registrado(s)</div>
  </div>
  <style>@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.2}}}}</style>
</div>
""", unsafe_allow_html=True)

    # Estadísticas
    st.markdown(f"""
<div class="stats-card">
  <div class="stats-title">Estadísticas</div>
  <div class="stats-grid">
    <div>
      <div class="stat-val color-teal">{n_total}</div>
      <div class="stat-lbl">Total de datos</div>
    </div>
    <div>
      <div class="stat-val color-green">{n_puntos}</div>
      <div class="stat-lbl">Puntos</div>
    </div>
    <div>
      <div class="stat-val color-yellow">{n_rutas}</div>
      <div class="stat-lbl">Rutas</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Nav cards
    col_m, col_d = st.columns(2)
    with col_m:
        if st.button("🗺️  Ver en Mapas  ›", use_container_width=True, key="h_map"):
            go("mapa")
    with col_d:
        if st.button("☰  Ver Todos los Datos  ›", use_container_width=True, key="h_data"):
            go("datos")

    st.markdown("""
<style>
/* Nav cards style */
div[data-testid="stHorizontalBlock"]:last-of-type button {
    background: #2a2a2a !important; color: #fff !important;
    border: none !important; border-radius: 14px !important;
    padding: 18px 14px !important; font-size: .9rem !important;
    font-weight: 500 !important; text-align: left !important;
    height: auto !important;
}
div[data-testid="stHorizontalBlock"]:last-of-type button:hover {
    background: #333 !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PÁGINA: CAPTURAR
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "capturar":

    modo = st.session_state.capture_mode or "punto"
    es_ruta = modo == "ruta"

    if st.button("← Volver", key="back_cap"):
        go("home")

    titulo_pag = "Registrar Ruta" if es_ruta else "Capturar Punto"
    sub_pag    = f"Ruta: {st.session_state.active_route}" if es_ruta else "Punto independiente"
    st.markdown(f'<div class="page-title">{titulo_pag}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{sub_pag}</div>', unsafe_allow_html=True)

    # Widget GPS
    st.components.v1.html(GPS_HTML, height=300, scrolling=False)

    # Mostrar coords capturadas
    if gps_lat is not None:
        st.markdown(f"""
<div style="background:#1a8fa0;border-radius:12px;padding:14px 16px;margin:8px 0;color:#fff;">
  <div style="font-weight:700;margin-bottom:6px;">✅ Ubicación capturada</div>
  <div style="font-size:.85rem;opacity:.9;">
    {gps_lat:.7f}, {gps_lon:.7f}<br>
    Altitud: {gps_alt} m &nbsp;·&nbsp; Precisión: ±{gps_acc} m
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="background:#2a2a2a;border-radius:12px;padding:14px 16px;margin:8px 0;
  color:#aaa;font-size:.85rem;">
  ⏳ Presiona <b style='color:#fff'>"📍 Capturar Ubicación GPS"</b> arriba para obtener tu posición.
</div>
""", unsafe_allow_html=True)

    # Formulario
    st.markdown("---")
    title = st.text_input("Título", placeholder="Ej: Casa / Vértice NW / Inicio ruta")
    desc  = st.text_area("Descripción", placeholder="Notas del campo...", height=80)
    col1, col2 = st.columns(2)
    with col1:
        date_val = st.date_input("Fecha", value=datetime.today())
    with col2:
        time_val = st.time_input("Hora", value=datetime.now().time())

    # Distancia si es ruta activa
    if es_ruta and st.session_state.active_route and gps_lat is not None:
        ruta_pts = [p for p in all_items if p.get("route_name") == st.session_state.active_route]
        if ruta_pts:
            last = ruta_pts[-1]
            dist = haversine(last["lat"], last["lon"], gps_lat, gps_lon)
            st.markdown(f"""
<div style="background:#2a2a2a;border-radius:10px;padding:12px;
  color:#2ecc71;font-size:.85rem;margin:6px 0;">
  📏 Distancia al punto anterior: <b>{dist:.1f} m</b>
</div>
""", unsafe_allow_html=True)

    btn_lbl = "✅ Guardar Punto de Ruta" if es_ruta else "✅ Guardar Punto GPS"
    btn_col = "#2ecc71" if es_ruta else "#1a8fa0"

    st.markdown(f"""<style>
div[data-testid="stButton"]:last-of-type button {{
    background: {btn_col} !important; color: #fff !important;
    border-radius: 12px !important; padding: 15px !important;
    font-size: 1rem !important; font-weight: 700 !important;
    height: auto !important;
}}
</style>""", unsafe_allow_html=True)

    if gps_lat is None:
        st.button(btn_lbl, disabled=True, use_container_width=True)
    else:
        if st.button(btn_lbl, use_container_width=True, key="save_point"):
            new_p = {
                "tipo": modo,
                "title": title.strip() or (f"Punto {n_total+1}" if not es_ruta else f"PT {n_total+1}"),
                "desc": desc.strip(),
                "lat": gps_lat, "lon": gps_lon,
                "alt": gps_alt, "acc": gps_acc,
                "date": f"{date_val} {time_val}",
                "route_name": st.session_state.active_route if es_ruta else None,
            }
            data["points"].append(new_p)
            save()
            # Limpiar GPS capturado
            st.query_params.clear()
            for k in ["gps_lat","gps_lon","gps_alt","gps_acc"]:
                st.session_state.pop(k, None)
            st.success(f"✅ Guardado: {new_p['title']}")
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  PÁGINA: MAPA
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "mapa":

    if st.button("← Volver", key="back_map"):
        go("home")

    st.markdown('<div class="page-title">Ver en Mapas</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{n_total} elemento(s)</div>', unsafe_allow_html=True)

    if not all_items:
        st.markdown("""
<div style="background:#2a2a2a;border-radius:14px;padding:30px;
  text-align:center;color:#888;">
  Aún no hay datos registrados.<br>Captura tu primer punto desde Home.
</div>
""", unsafe_allow_html=True)
    else:
        st.components.v1.html(build_map_html(all_items), height=420, scrolling=False)


# ─────────────────────────────────────────────────────────────────────────────
#  PÁGINA: VER TODOS LOS DATOS
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "datos":

    if st.button("← Volver", key="back_dat"):
        go("home")

    st.markdown('<div class="page-title">Visualización en Mapas</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{n_total} elemento(s)</div>', unsafe_allow_html=True)

    if not all_items:
        st.markdown("""
<div style="background:#2a2a2a;border-radius:14px;padding:30px;
  text-align:center;color:#888;">
  No hay datos aún.
</div>
""", unsafe_allow_html=True)
    else:
        # Listar puntos y rutas
        for i, p in enumerate(all_items):
            es_ruta = p.get("tipo") == "ruta"
            card_cls = "data-card-route" if es_ruta else "data-card"
            tipo_txt = f"Ruta: {p.get('route_name','')}" if es_ruta else "Punto independiente"
            col_card, col_del = st.columns([5, 1])
            with col_card:
                gmaps = f"https://maps.google.com/?q={p['lat']},{p['lon']}"
                st.markdown(f"""
<div class="{card_cls}">
  <h3>{p.get('title','Sin título')}</h3>
  <div class="dc-type">{tipo_txt}</div>
  <hr class="dc-sep"/>
  <div class="dc-lbl">Descripción</div>
  <div class="dc-val">{p.get('desc','—')}</div>
  <div class="dc-lbl">Coordenadas</div>
  <div class="dc-val">{p['lat']:.6f}, {p['lon']:.6f}</div>
  <div class="dc-lbl">Altitud</div>
  <div class="dc-val">{p.get('alt',0)} m</div>
  <div class="dc-lbl">Precisión</div>
  <div class="dc-val">±{p.get('acc','?')} m</div>
  <div class="dc-lbl">Fecha</div>
  <div class="dc-val">{p.get('date','')}</div>
  <a href="{gmaps}" target="_blank" style="display:inline-flex;align-items:center;gap:6px;
    color:#fff;text-decoration:none;font-weight:600;font-size:.88rem;
    background:rgba(255,255,255,.15);border-radius:8px;padding:8px 14px;margin-top:6px;">
    ↗ Ver en Google Maps
  </a>
</div>
""", unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️", key=f"del_{i}", help="Eliminar"):
                    data["points"].pop(i)
                    save()
                    st.rerun()

    # Exportar
    if all_items:
        st.markdown("---")
        st.markdown('<div style="font-weight:700;font-size:1rem;margin-bottom:10px;">Exportar Datos</div>',
                    unsafe_allow_html=True)
        fname = f"gps_{datetime.now().strftime('%Y%m%d')}"
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button("⬇ CSV",
                data=points_to_csv(all_items).encode("utf-8"),
                file_name=fname+".csv", mime="text/csv",
                use_container_width=True)
        with col_b:
            st.download_button("⬇ KMZ",
                data=build_kmz(all_items),
                file_name=fname+".kmz",
                mime="application/vnd.google-earth.kmz",
                use_container_width=True)
        col_c, col_d = st.columns(2)
        with col_c:
            st.download_button("⬇ KML",
                data=build_kml(all_items).encode("utf-8"),
                file_name=fname+".kml",
                mime="application/vnd.google-earth.kml+xml",
                use_container_width=True)
        with col_d:
            st.download_button("⬇ JSON",
                data=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name=f"gps_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True)

        st.markdown("""<style>
/* CSV button teal */
section[data-testid="stMain"] div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) .stDownloadButton button {
    background: #1a8fa0 !important; color: #fff !important;
    border-radius: 12px !important; padding: 14px !important;
    font-weight: 700 !important; font-size: .95rem !important; border: none !important;
}
/* KMZ button green */
section[data-testid="stMain"] div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) .stDownloadButton button {
    background: #2ecc71 !important; color: #fff !important;
    border-radius: 12px !important; padding: 14px !important;
    font-weight: 700 !important; font-size: .95rem !important; border: none !important;
}
</style>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  BOTTOM NAV (siempre visible)
# ─────────────────────────────────────────────
page = st.session_state.page
nav_html = f"""
<div class="bottom-nav">
  <div class="bnav-item {'active' if page=='home' else ''}"
    onclick="window.location.href='?nav=home'">
    <div class="bnav-icon">🏠</div>
    <div>Home</div>
  </div>
  <div class="bnav-item {'active' if page=='capturar' else ''}"
    onclick="window.location.href='?nav=cap'">
    <div class="bnav-icon">📍</div>
    <div>Capturar</div>
  </div>
  <div class="bnav-item {'active' if page=='mapa' else ''}"
    onclick="window.location.href='?nav=map'">
    <div class="bnav-icon">🗺️</div>
    <div>Mapa</div>
  </div>
  <div class="bnav-item {'active' if page=='datos' else ''}"
    onclick="window.location.href='?nav=dat'">
    <div class="bnav-icon">☰</div>
    <div>Datos</div>
  </div>
</div>
"""
st.markdown(nav_html, unsafe_allow_html=True)

# Manejar nav desde bottom bar
if "nav" in qp:
    nav_map = {"home":"home","cap":"capturar","map":"mapa","dat":"datos"}
    dest = nav_map.get(qp["nav"])
    if dest and dest != st.session_state.page:
        st.query_params.clear()
        st.session_state.page = dest
        st.rerun()

