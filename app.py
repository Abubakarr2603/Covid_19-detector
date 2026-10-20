import streamlit as st
import streamlit.components.v1 as components
import requests

st.set_page_config(page_title="COVID-19 Diagnostic Portal", page_icon="🩺", layout="wide")

API_URL = "http://127.0.0.1:8000/predict"
COLORS = {"idle": "#3DD9EB", "normal": "#2EF2A0", "covid": "#FF4D5E"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=DM+Sans:wght@400;500;600&display=swap');

html, body, .stApp, button, input { font-family: 'DM Sans', sans-serif; }
.stApp {
  background:
    radial-gradient(55% 45% at 78% 28%, rgba(__RGB__, .24), transparent 70%),
    radial-gradient(45% 40% at 8% 95%, rgba(90, 100, 255, .14), transparent 70%),
    #060A12;
  color: #E8EEF9;
}
[data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer { display: none !important; }
.block-container { max-width: 1240px; padding-top: 3rem; padding-bottom: 2rem; }

.hero-title {
  font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700;
  font-size: clamp(2.2rem, 4.4vw, 3.6rem); line-height: 1.05; letter-spacing: -0.03em;
  color: #F4F7FD; max-width: 14ch;
}
.hero-sub { color: #8B97AE; font-size: 1.05rem; margin: 1rem 0 2rem; max-width: 46ch; }

[data-testid="stColumn"], [data-testid="column"] {
  background: rgba(255, 255, 255, .035);
  border: 1px solid rgba(255, 255, 255, .08);
  border-radius: 28px; padding: 1.6rem; backdrop-filter: blur(14px);
}
.panel-title { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 600; font-size: 1.15rem; color: #F4F7FD; }

[data-testid="stWidgetLabel"] p { color: #8B97AE; font-size: .9rem; }
[data-testid="stFileUploaderDropzone"] {
  background: rgba(255, 255, 255, .03); border: 1.5px dashed rgba(255, 255, 255, .2); border-radius: 18px;
}
[data-testid="stFileUploaderDropzone"] button { border-radius: 999px; }
[data-testid="stImage"] img { border-radius: 16px; border: 1px solid rgba(255, 255, 255, .1); }

div.stButton > button {
  background: #E8EEF9; border: 0; border-radius: 999px; padding: .65rem 1.7rem; font-weight: 600;
  transition: box-shadow .2s, transform .2s;
}
div.stButton > button p { color: #06101C; }
div.stButton > button:hover { background: #fff; box-shadow: 0 0 28px rgba(__RGB__, .55); transform: translateY(-1px); }

.result {
  display: flex; gap: 1rem; align-items: center; margin-top: 1.2rem; padding: 1.1rem 1.3rem;
  border-radius: 20px; border: 1px solid rgba(__RGB__, .5); background: rgba(__RGB__, .1);
}
.result .dot { width: 14px; height: 14px; flex: none; border-radius: 50%; background: __ACCENT__; box-shadow: 0 0 18px __ACCENT__; }
.result .t { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.3rem; color: #F4F7FD; }
.result .s { color: #9AA7BF; font-size: .92rem; margin-top: .15rem; }
[data-testid="stCaptionContainer"] { color: #6F7B92; }
[data-stale="true"], [data-stale="true"] * { opacity: 1 !important; transition: none !important; }
</style>
"""

def run_scan():
    """Runs as a button callback, so the result is saved before the page reruns."""
    f = st.session_state.get("xray")
    if f is None:
        return
    try:
        files = {"file": (f.name, f.getvalue(), f.type)}
        response = requests.post(API_URL, files=files, timeout=30)
        if response.status_code == 200:
            prediction = response.json().get("prediction", "")
            st.session_state.result = {"covid": "COVID" in prediction}
            st.session_state.error = None
        else:
            st.session_state.error = "API error: the image could not be processed."
    except Exception as e:
        st.session_state.error = f"Could not connect to the FastAPI backend: {e}"


st.session_state.setdefault("result", None)
st.session_state.setdefault("error", None)

# Work out the state BEFORE drawing anything, so the page styling is identical on every
# rerun. (Re-creating the style block at the end of the script is what made the screen blink.)
current = st.session_state.get("xray")
name = current.name if current else None
if st.session_state.get("last_file") != name:  # file removed or replaced
    st.session_state.result = None
    st.session_state.error = None
    st.session_state.last_file = name

res = st.session_state.result
state = "idle" if res is None else ("covid" if res["covid"] else "normal")
accent = COLORS[state]
rgb = ",".join(str(int(accent[i:i + 2], 16)) for i in (1, 3, 5))

st.markdown(CSS.replace("__RGB__", rgb).replace("__ACCENT__", accent), unsafe_allow_html=True)

st.markdown(
    '<div class="hero-title">COVID-19 chest X-ray screening</div>'
    '<div class="hero-sub">Upload a scan and the XGBoost model classifies it in seconds.</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 1.15], gap="large")

with col1:
    uploaded_file = st.file_uploader("Chest X-ray (PNG or JPG)", type=["png", "jpg", "jpeg"], key="xray")

    if uploaded_file is not None:
        st.image(uploaded_file, width=300)
        st.button("Run diagnostic scan", on_click=run_scan)

    if st.session_state.error:
        st.error(st.session_state.error)

    title, sub = {
        "idle": ("Waiting for a scan", "Upload an X-ray, then run the scan to see the result."),
        "normal": ("Normal", "The model found no COVID-19 pattern in this X-ray."),
        "covid": ("COVID-19 detected", "The model found a COVID-19 pattern in this X-ray. Confirm it with a clinician."),
    }[state]
    st.markdown(
        f'<div class="result"><div class="dot"></div><div><div class="t">{title}</div>'
        f'<div class="s">{sub}</div></div></div>',
        unsafe_allow_html=True,
    )

THREEJS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
  html, body { margin: 0; background: transparent; overflow: hidden; }
  #c { width: 100%; height: 450px; cursor: grab; }
  #c:active { cursor: grabbing; }
  #c canvas { animation: fadein .8s ease; }
  @keyframes fadein { from { opacity: 0; } to { opacity: 1; } }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
<div id="c"></div>
<script>
const container = document.getElementById('c');
let W = container.clientWidth, H = container.clientHeight;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 100);
camera.position.set(0, 0.2, 11.5);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(W, H);
container.appendChild(renderer.domElement);

const COLOR = new THREE.Color("__COLOR__");
const LIGHT = COLOR.clone().lerp(new THREE.Color(0xffffff), 0.6);

scene.add(new THREE.AmbientLight(0xffffff, 0.55));
const key = new THREE.DirectionalLight(0xffffff, 0.9); key.position.set(3, 4, 6); scene.add(key);
const rim = new THREE.PointLight(COLOR, 1.4, 40); rim.position.set(-5, 2, -5); scene.add(rim);

const root = new THREE.Group();
root.position.y = -0.8;
scene.add(root);
const lungs = new THREE.Group();
lungs.position.y = -0.2;
root.add(lungs);

// ---------- Materials ----------
const lungMat = new THREE.MeshPhongMaterial({
  color: COLOR, transparent: true, opacity: 0.28, shininess: 90,
  side: THREE.DoubleSide, depthWrite: false
});
const lungWire = new THREE.MeshBasicMaterial({ color: COLOR, wireframe: true, transparent: true, opacity: 0.09 });
const airMat = new THREE.MeshBasicMaterial({ color: LIGHT, side: THREE.DoubleSide });
const boneMat = new THREE.MeshBasicMaterial({ color: 0xDDE8F5, transparent: true, opacity: 0.22 });
const muscleMat = new THREE.MeshPhongMaterial({
  color: COLOR, transparent: true, opacity: 0.35, side: THREE.DoubleSide, shininess: 40
});

// ---------- Lung shape: deformed sphere ----------
// side = -1 -> right lung (screen left), +1 -> left lung (screen right, has cardiac notch)
function lungGeometry(side) {
  const g = new THREE.SphereGeometry(1, 56, 44);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    let x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const t = (y + 1) / 2;                       // 0 = base, 1 = apex
    const widen = 0.72 + 0.4 * (1 - t);          // narrow apex, wide base
    x *= widen; z *= widen;
    if (x * side < 0) x *= 0.42;                 // flatten inner (medial) face
    if (y < -0.78) {                             // flat, slightly concave base
      y = -0.78 + (y + 0.78) * 0.25;
      y += 0.12 * (1 - (x * x + z * z));
    }
    if (side > 0 && x * side < 0 && z > 0) {     // cardiac notch on the left lung
      x += side * 0.3 * Math.exp(-Math.pow((y + 0.35) / 0.38, 2)) * z;
    }
    p.setXYZ(i, x * 0.95 + side * 0.75, y * 2.0, z * 0.75);
  }
  g.computeVertexNormals();
  return g;
}
[-1, 1].forEach(side => {
  const geo = lungGeometry(side);
  lungs.add(new THREE.Mesh(geo, lungMat));
  lungs.add(new THREE.Mesh(geo, lungWire));
});

// ---------- Airways ----------
function tube(a, b, r0, r1, mat) {
  const dir = new THREE.Vector3().subVectors(b, a);
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r1, r0, dir.length(), 8, 1, true), mat);
  m.position.copy(a).addScaledVector(dir, 0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
  return m;
}

// Trachea with cartilage rings
root.add(tube(new THREE.Vector3(0, 3.2, 0), new THREE.Vector3(0, 1.0, 0), 0.19, 0.19,
  new THREE.MeshPhongMaterial({ color: LIGHT, transparent: true, opacity: 0.35, side: THREE.DoubleSide })));
const ringGeo = new THREE.TorusGeometry(0.2, 0.022, 6, 24);
for (let i = 0; i < 15; i++) {
  const ring = new THREE.Mesh(ringGeo, airMat);
  ring.rotation.x = Math.PI / 2;
  ring.position.set(0, 1.1 + i * 0.14, 0);
  root.add(ring);
}
// Larynx
const larynx = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.26, 0.55, 14), muscleMat);
larynx.position.set(0, 3.5, 0);
root.add(larynx);

// Bronchial tree (seeded so it looks the same every run)
let seed = 11;
const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };

function insideLung(pt, side) {
  const dx = (pt.x - side * 0.85) / 0.85, dy = (pt.y + 0.1) / 1.6, dz = pt.z / 0.5;
  return dx * dx + dy * dy + dz * dz < 1;
}

function branch(start, dir, len, r, depth, side) {
  const end = start.clone().addScaledVector(dir, len);
  if (!insideLung(end, side)) return;
  lungs.add(tube(start, end, r, r * 0.78, airMat));
  if (depth <= 0) return;
  const axis = new THREE.Vector3(rnd() - 0.5, rnd() - 0.5, (rnd() - 0.5) * 0.8).cross(dir).normalize();
  [1, -1].forEach(sign => {
    const d = dir.clone().applyAxisAngle(axis, sign * (0.45 + rnd() * 0.35));
    d.x += side * 0.12; d.y -= 0.08;           // drift outward and down
    branch(end, d.normalize(), len * (0.74 + rnd() * 0.08), r * 0.74, depth - 1, side);
  });
}

[-1, 1].forEach(side => {
  const carina = new THREE.Vector3(0, 1.0, 0);
  const hilum = new THREE.Vector3(side * 0.75, 0.5, 0);
  root.add(tube(carina, hilum, 0.14, 0.12, airMat));            // main bronchus
  const h = hilum.clone().sub(lungs.position);                  // lung-local coords
  branch(h, new THREE.Vector3(side * 0.3, -1, 0.05).normalize(), 0.95, 0.09, 5, side);
  branch(h, new THREE.Vector3(side * 0.6, 0.6, 0.1).normalize(), 0.7, 0.08, 4, side);  // upper lobe
});

// ---------- Rib cage ----------
for (let i = 0; i < 7; i++) {
  const wx = 1.35 + 0.55 * Math.sin(((i + 1) / 7) * Math.PI / 2);
  const y0 = 1.2 - i * 0.45;
  [-1, 1].forEach(side => {
    const pts = [];
    for (let k = 0; k <= 24; k++) {
      const th = 0.15 + (k / 24) * Math.PI * 0.8;
      pts.push(new THREE.Vector3(side * wx * Math.sin(th), y0 - 0.5 * (th / Math.PI), -1.0 * Math.cos(th)));
    }
    root.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 40, 0.035, 5, false), boneMat));
  });
}
// Spine and sternum
for (let i = 0; i < 13; i++) {
  const v = new THREE.Mesh(new THREE.SphereGeometry(0.17, 10, 8), boneMat);
  v.scale.set(1, 0.55, 0.8);
  v.position.set(0, 2.4 - i * 0.37, -1.0);
  root.add(v);
}
const sternum = new THREE.Mesh(new THREE.BoxGeometry(0.28, 2.3, 0.07), boneMat);
sternum.position.set(0, 0.35, 0.99);
root.add(sternum);

// ---------- Diaphragm ----------
[-1, 1].forEach(side => {
  const dome = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), muscleMat);
  dome.scale.set(1.2, 0.5, 0.95);
  dome.position.set(side * 0.95, -2.25, 0);
  root.add(dome);
});

// ---------- Interaction: drag to rotate, slow auto-spin, breathing ----------
let dragging = false, lastX = 0, lastY = 0;
const el = renderer.domElement;
el.addEventListener('pointerdown', e => { dragging = true; lastX = e.clientX; lastY = e.clientY; });
window.addEventListener('pointerup', () => dragging = false);
window.addEventListener('pointermove', e => {
  if (!dragging) return;
  root.rotation.y += (e.clientX - lastX) * 0.01;
  root.rotation.x = Math.max(-0.6, Math.min(0.6, root.rotation.x + (e.clientY - lastY) * 0.005));
  lastX = e.clientX; lastY = e.clientY;
});
window.addEventListener('resize', () => {
  W = container.clientWidth; H = container.clientHeight;
  camera.aspect = W / H; camera.updateProjectionMatrix(); renderer.setSize(W, H);
});

const clock = new THREE.Clock();
root.rotation.y = -0.35;
function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();
  if (!dragging) root.rotation.y += 0.004;
  const s = Math.sin(t * 1.6);                       // breathing
  lungs.scale.set(1 + 0.025 * s, 1 + 0.04 * s, 1 + 0.025 * s);
  renderer.render(scene, camera);
}
animate();
</script>
</body>
</html>
"""

with col2:
    st.markdown('<div class="panel-title">Lung monitor</div>', unsafe_allow_html=True)
    components.html(THREEJS_TEMPLATE.replace("__COLOR__", accent), height=470)
    st.caption("Drag to rotate. The model and the page glow take the color of the latest result.")

st.caption("Research prototype. It does not replace a clinical diagnosis.")