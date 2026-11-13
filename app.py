import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Solar System 3D",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 50% 0%, #10243b 0%, #07111f 45%, #030711 100%);
    color: #eaf2ff;
    font-family: Inter, sans-serif;
}
[data-testid="stHeader"], [data-testid="stToolbar"] { background: transparent; }
.block-container { max-width: 1500px; padding: 1.2rem 1.5rem 2rem; }
.hero {
    display:flex; align-items:center; justify-content:space-between; gap:16px;
    padding: 8px 4px 18px; flex-wrap:wrap;
}
.eyebrow { color:#73d9ff; font-size:11px; font-weight:800; letter-spacing:3px; text-transform:uppercase; }
.hero h1 { margin:5px 0 0; font-size:clamp(28px,4vw,46px); letter-spacing:-1.8px; font-weight:800; }
.hero p { color:#9fb2ca; margin:6px 0 0; font-size:14px; }
.pill {
    border:1px solid #24405d; background:rgba(13,31,51,.75); border-radius:999px;
    padding:9px 14px; color:#a9c6df; font-size:12px; font-weight:600;
}
.info-card {
    background:linear-gradient(145deg,rgba(17,37,59,.94),rgba(8,19,34,.94));
    border:1px solid #203b57; border-radius:18px; padding:17px 18px; min-height:110px;
}
.info-label { color:#8ba7c4; font-size:11px; text-transform:uppercase; letter-spacing:1.4px; font-weight:700; }
.info-value { color:#f3f8ff; font-size:23px; font-weight:800; margin-top:7px; }
.info-sub { color:#91a9c2; font-size:12px; margin-top:4px; }
.stButton>button {
    border-radius:12px; border:1px solid #294865; background:#10253b; color:#eaf6ff;
    font-weight:650; min-height:42px; transition:all .2s ease;
}
.stButton>button:hover { border-color:#65d7ff; color:#75dcff; background:#15324c; }
div[data-testid="stSlider"] { padding-top:2px; }
section[data-testid="stSidebar"] { background:#071322; border-right:1px solid #1c354e; }
small { color:#91a9c2; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div>
    <div class="eyebrow">Interactive space explorer</div>
    <h1>Solar System <span style="color:#65d7ff">3D</span></h1>
    <p>Explore the Sun, eight planets, their orbits and the asteroid belt.</p>
  </div>
  <div class="pill">✦ REAL-TIME 3D SCENE &nbsp; · &nbsp; DESKTOP + MOBILE</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Mission controls")
    st.caption("These controls affect the 3D simulation.")
    speed = st.slider("Orbital speed", 0.0, 5.0, 1.0, 0.1)
    scale = st.select_slider("Planet size", options=["Realistic-ish", "Enhanced", "Large"], value="Enhanced")
    show_orbits = st.toggle("Show orbital paths", True)
    show_labels = st.toggle("Show planet labels", True)
    show_asteroids = st.toggle("Show asteroid belt", True)
    show_stars = st.toggle("Show star field", True)
    st.markdown("---")
    st.markdown("**Navigation**")
    st.caption("Drag to rotate · Scroll or pinch to zoom · Right-drag to pan")
    st.caption("Select a planet from the scene or the buttons below it.")

size_map = {"Realistic-ish": 0.78, "Enhanced": 1.0, "Large": 1.28}
size_factor = size_map[scale]

# The scene is embedded in one HTML component so the entire app remains a single app.py file.
scene_html = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box}
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#030914;font-family:Inter,Arial,sans-serif}
#wrap{position:relative;width:100%;height:660px;min-height:460px;border:1px solid #203b57;border-radius:20px;overflow:hidden;background:radial-gradient(ellipse at 50% 50%,#0b1b2e,#030914 70%)}
#scene{position:absolute;inset:0}
canvas{display:block;width:100%;height:100%}
#hud{position:absolute;top:15px;left:16px;z-index:4;pointer-events:none}
#hud .tag{font-size:10px;letter-spacing:2px;color:#74dfff;font-weight:800}
#hud .hint{font-size:11px;color:#91a9c2;margin-top:5px}
#sceneControls{position:absolute;left:16px;top:65px;z-index:6;display:flex;gap:7px}
#sceneControls button{border:1px solid #294865;background:rgba(9,26,43,.88);color:#dff4ff;border-radius:9px;padding:8px 11px;font-size:11px;cursor:pointer}
#sceneControls button:hover{border-color:#65d7ff;color:#75dcff}
#planetInfo{position:absolute;right:14px;top:14px;width:220px;z-index:5;padding:14px;border-radius:15px;
 background:rgba(7,19,34,.82);border:1px solid rgba(91,153,196,.35);backdrop-filter:blur(12px);color:#eef7ff}
#planetInfo .name{font-size:18px;font-weight:800;margin-bottom:4px}
#planetInfo .type{font-size:10px;color:#78dfff;text-transform:uppercase;letter-spacing:1.5px}
#planetInfo .desc{font-size:11px;color:#a9bed2;line-height:1.5;margin:9px 0}
#planetInfo .stat{display:flex;justify-content:space-between;gap:8px;font-size:10px;padding:5px 0;border-top:1px solid rgba(117,161,194,.15);color:#9bb1c7}
#planetInfo .stat b{color:#edf6ff;font-weight:650;text-align:right}
#bottomBar{position:absolute;left:14px;right:14px;bottom:13px;z-index:5;display:flex;align-items:center;justify-content:space-between;gap:10px;pointer-events:none}
#bottomBar .legend{font-size:10px;color:#829bb4;background:rgba(5,15,27,.7);padding:7px 10px;border-radius:9px}
#bottomBar .status{font-size:10px;color:#8bdfff;background:rgba(5,15,27,.7);padding:7px 10px;border-radius:9px}
#loading{position:absolute;inset:0;z-index:10;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px;background:#030914;color:#9dbbd5;font-size:12px;transition:opacity .4s}
.spinner{width:30px;height:30px;border:2px solid #1b3b57;border-top-color:#6cdbff;border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
#error{display:none;position:absolute;inset:20px;z-index:11;color:#ffd0d0;background:#24121a;border:1px solid #743b4b;border-radius:12px;padding:18px;font:13px/1.5 Arial}
@media(max-width:650px){#wrap{height:590px}#planetInfo{top:auto;bottom:55px;right:10px;width:175px;padding:10px}#planetInfo .desc{display:none}#hud{top:10px;left:11px}#bottomBar{left:9px;right:9px;bottom:9px}}
</style>
</head>
<body>
<div id="wrap">
 <div id="scene"></div>
 <div id="hud"><div class="tag">SOLAR SYSTEM / LIVE SIMULATION</div><div class="hint">Drag · Zoom · Select a world</div></div>
 <div id="sceneControls"><button id="pauseBtn">Ⅱ Pause</button><button id="resetBtn">↺ Reset camera</button></div>
 <div id="planetInfo">
  <div class="type" id="pType">Star</div><div class="name" id="pName">The Sun</div>
  <div class="desc" id="pDesc">The star at the center of our solar system. Its gravity holds the system together.</div>
  <div class="stat"><span>Diameter</span><b id="pDiameter">1.39 million km</b></div>
  <div class="stat"><span>Year</span><b id="pYear">—</b></div>
  <div class="stat"><span>Day</span><b id="pDay">—</b></div>
 </div>
 <div id="bottomBar"><div class="legend">☀ Sun &nbsp; · &nbsp; 8 planets &nbsp; · &nbsp; asteroid belt</div><div class="status" id="status">● INITIALIZING</div></div>
 <div id="loading"><div class="spinner"></div><div>Preparing the universe…</div></div>
 <div id="error"></div>
</div>
<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';

const CFG = {
 speed: __SPEED__,
 size: __SIZE__,
 orbits: __ORBITS__,
 labels: __LABELS__,
 asteroids: __ASTEROIDS__,
 stars: __STARS__
};
const host=document.getElementById('scene');
const loading=document.getElementById('loading');
const errorBox=document.getElementById('error');
const statusEl=document.getElementById('status');
const scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(0x030914,0.0018);
const camera=new THREE.PerspectiveCamera(48,1,0.1,1800);
camera.position.set(0,72,155);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.18;
host.appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true; controls.dampingFactor=.055;
controls.minDistance=18; controls.maxDistance=380;
controls.target.set(0,0,0);
scene.add(new THREE.AmbientLight(0x526987,0.55));
const sunLight=new THREE.PointLight(0xffe0a1,3.6,650,1.2);
scene.add(sunLight);

function seeded(i){let x=Math.sin(i*127.1+311.7)*43758.5453;return x-Math.floor(x)}
function makeTexture(base,kind,seed){
 const c=document.createElement('canvas');c.width=1024;c.height=512;
 const ctx=c.getContext('2d');
 ctx.fillStyle=base;ctx.fillRect(0,0,c.width,c.height);
 for(let i=0;i<kind.count;i++){
  const y=seeded(i+seed)*512, x=seeded(i+seed+90)*1024;
  const alpha=.04+seeded(i+seed+8)*.18;
  if(kind.mode==='bands'){
   ctx.fillStyle=`rgba(${kind.rgb},${alpha})`;ctx.fillRect(0,y,1024,2+seeded(i+seed+3)*12);
  }else{
   ctx.fillStyle=`rgba(${kind.rgb},${alpha})`;ctx.beginPath();
   ctx.ellipse(x,y,8+seeded(i+seed+4)*75,2+seeded(i+seed+5)*18,seeded(i+seed+6),0,Math.PI*2);ctx.fill();
  }
 }
 // Subtle longitude/latitude variation.
 const grad=ctx.createLinearGradient(0,0,0,512);
 grad.addColorStop(0,'rgba(255,255,255,.12)');grad.addColorStop(.5,'rgba(0,0,0,.03)');grad.addColorStop(1,'rgba(0,0,0,.25)');
 ctx.fillStyle=grad;ctx.fillRect(0,0,1024,512);
 const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;tex.anisotropy=8;return tex;
}
function sphereMaterial(color,opts={}){
 return new THREE.MeshStandardMaterial({color,roughness:opts.roughness??.9,metalness:0,map:opts.map||null});
}
const planetData=[
 {name:'Mercury',type:'Terrestrial planet',color:0x9b9187,r:1.05,d:4879,year:'88 Earth days',day:'58.6 Earth days',dist:13,period:88,desc:'The smallest planet, with a heavily cratered rocky surface and almost no atmosphere.',rgb:'205,190,170',mode:'spots',count:190},
 {name:'Venus',type:'Terrestrial planet',color:0xd7a66e,r:1.75,d:12104,year:'225 Earth days',day:'243 Earth days',dist:19,period:225,desc:'A world wrapped in thick clouds. Its dense atmosphere traps heat, making it the hottest planet.',rgb:'255,220,160',mode:'bands',count:110},
 {name:'Earth',type:'Terrestrial planet',color:0x397bc4,r:1.85,d:12742,year:'365.25 days',day:'23 h 56 min',dist:27,period:365.25,desc:'Our home world: liquid-water oceans, a protective atmosphere and a rich variety of life.',rgb:'90,170,115',mode:'spots',count:250},
 {name:'Mars',type:'Terrestrial planet',color:0xc66e4c,r:1.35,d:6779,year:'687 Earth days',day:'24 h 37 min',dist:36,period:687,desc:'The red planet has giant volcanoes, ancient river features and two small moons.',rgb:'230,130,85',mode:'spots',count:210},
 {name:'Jupiter',type:'Gas giant',color:0xc99b72,r:5.0,d:139820,year:'11.86 Earth years',day:'9 h 56 min',dist:57,period:4333,desc:'The largest planet, known for its colorful cloud bands and the enormous Great Red Spot.',rgb:'255,220,185',mode:'bands',count:150},
 {name:'Saturn',type:'Gas giant',color:0xd8bd8a,r:4.25,d:116460,year:'29.4 Earth years',day:'10 h 33 min',dist:79,period:10759,desc:'A gas giant surrounded by a spectacular ring system made mostly of icy particles.',rgb:'255,230,175',mode:'bands',count:120},
 {name:'Uranus',type:'Ice giant',color:0x8ed8dc,r:3.0,d:50724,year:'84 Earth years',day:'17 h 14 min',dist:101,period:30687,desc:'An ice giant with a blue-green atmosphere. Its rotation axis is tilted dramatically.',rgb:'170,245,245',mode:'bands',count:75},
 {name:'Neptune',type:'Ice giant',color:0x416cdb,r:2.95,d:49244,year:'165 Earth years',day:'16 h 6 min',dist:123,period:60190,desc:'A distant, windy ice giant with a deep blue atmosphere and faint rings.',rgb:'125,160,255',mode:'spots',count:100}
];
const worldMeshes=[];
const pickables=[];
const orbitGroups=[];
const labels=[];
const sunGeo=new THREE.SphereGeometry(6.8,64,48);
const sunMat=new THREE.MeshBasicMaterial({color:0xffc65e});
const sun=new THREE.Mesh(sunGeo,sunMat);scene.add(sun);pickables.push(sun);
const sunGlow=new THREE.Sprite(new THREE.SpriteMaterial({map:(()=>{const c=document.createElement('canvas');c.width=c.height=256;const x=c.getContext('2d');const g=x.createRadialGradient(128,128,8,128,128,128);g.addColorStop(0,'rgba(255,220,140,.65)');g.addColorStop(.25,'rgba(255,155,65,.22)');g.addColorStop(1,'rgba(255,120,30,0)');x.fillStyle=g;x.fillRect(0,0,256,256);const t=new THREE.CanvasTexture(c);return t;})(),transparent:true,depthWrite:false}));
sunGlow.scale.set(34,34,1);sun.add(sunGlow);
const sunHalo=new THREE.Mesh(new THREE.SphereGeometry(7.3,48,32),new THREE.MeshBasicMaterial({color:0xffa83a,transparent:true,opacity:.12,side:THREE.BackSide}));sun.add(sunHalo);

const sizeFactor=CFG.size;
for(let i=0;i<planetData.length;i++){
 const p=planetData[i];
 const pivot=new THREE.Group();scene.add(pivot);orbitGroups.push(pivot);
 const tex=makeTexture('#'+p.color.toString(16).padStart(6,'0'),p,i*31+12);
 const mat=sphereMaterial(0xffffff,{map:tex});
 const geo=new THREE.SphereGeometry(p.r*sizeFactor,48,36);
 const mesh=new THREE.Mesh(geo,mat);mesh.position.x=p.dist;mesh.rotation.z=(p.name==='Uranus'?Math.PI/2.2:.02);
 mesh.userData.index=i;pivot.add(mesh);worldMeshes.push(mesh);pickables.push(mesh);
 if(p.name==='Earth'){
  const moonPivot=new THREE.Group();mesh.add(moonPivot);
  const moon=new THREE.Mesh(new THREE.SphereGeometry(.48*sizeFactor,24,18),sphereMaterial(0xb8b9b7));
  moon.position.x=3.5;moonPivot.add(moon);mesh.userData.moonPivot=moonPivot;
 }
 if(p.name==='Saturn'){
  const ringGeo=new THREE.RingGeometry(p.r*1.35*sizeFactor,p.r*2.25*sizeFactor,96);
  const ringMat=new THREE.MeshStandardMaterial({color:0xcbb58f,side:THREE.DoubleSide,transparent:true,opacity:.78,roughness:1});
  const rings=new THREE.Mesh(ringGeo,ringMat);rings.rotation.x=Math.PI/2.25;mesh.add(rings);
  const inner=new THREE.Mesh(new THREE.RingGeometry(p.r*1.12*sizeFactor,p.r*1.32*sizeFactor,96),new THREE.MeshStandardMaterial({color:0x8f806b,side:THREE.DoubleSide,transparent:true,opacity:.55}));
  inner.rotation.x=Math.PI/2.25;mesh.add(inner);
 }
 if(CFG.orbits){
  const pts=[];for(let j=0;j<=256;j++){const a=j/256*Math.PI*2;pts.push(new THREE.Vector3(Math.cos(a)*p.dist,0,Math.sin(a)*p.dist));}
  const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({color:0x42617d,transparent:true,opacity:.38}));
  scene.add(line);
 }
 if(CFG.labels){
  const el=document.createElement('div');el.textContent=p.name;
  el.style.cssText='position:absolute;color:#c5d9eb;font:11px Inter,Arial,sans-serif;text-shadow:0 1px 5px #000;pointer-events:none;white-space:nowrap';
  host.appendChild(el);labels.push({el,mesh});
 }
}
function addStars(){
 const count=CFG.stars?6500:0;const pos=new Float32Array(count*3);const colors=new Float32Array(count*3);
 for(let i=0;i<count;i++){
  const r=220+seeded(i+1000)*500,theta=seeded(i+2000)*Math.PI*2,phi=Math.acos(2*seeded(i+3000)-1);
  pos[i*3]=r*Math.sin(phi)*Math.cos(theta);pos[i*3+1]=r*Math.cos(phi);pos[i*3+2]=r*Math.sin(phi)*Math.sin(theta);
  const tint=.65+seeded(i+4000)*.35;colors[i*3]=tint*.72;colors[i*3+1]=tint*.84;colors[i*3+2]=tint;
 }
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(pos,3));g.setAttribute('color',new THREE.BufferAttribute(colors,3));
 const m=new THREE.PointsMaterial({size:.75,vertexColors:true,transparent:true,opacity:.9,sizeAttenuation:true});
 scene.add(new THREE.Points(g,m));
}
addStars();
if(CFG.asteroids){
 const count=2600,geo=new THREE.DodecahedronGeometry(.12,0),mat=new THREE.MeshStandardMaterial({color:0x8c8c86,roughness:1});
 const belt=new THREE.InstancedMesh(geo,mat,count);const dummy=new THREE.Object3D();
 for(let i=0;i<count;i++){
  const a=seeded(i+5000)*Math.PI*2,r=43+seeded(i+6000)*7;
  dummy.position.set(Math.cos(a)*r,(seeded(i+7000)-.5)*1.7,Math.sin(a)*r);
  const s=.25+seeded(i+8000)*1.5;dummy.scale.set(s,s*(.5+seeded(i+9000)),s);dummy.rotation.set(seeded(i+10000)*3,seeded(i+11000)*3,0);dummy.updateMatrix();belt.setMatrixAt(i,dummy.matrix);
 }
 scene.add(belt);
}

let selected=-1,paused=false,elapsed=0;
const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();
function select(index){
 selected=index;
 const sunSelected=index===-1;
 const p=sunSelected?null:planetData[index];
 document.getElementById('pType').textContent=sunSelected?'Star':p.type;
 document.getElementById('pName').textContent=sunSelected?'The Sun':p.name;
 document.getElementById('pDesc').textContent=sunSelected?'The star at the center of our solar system. Its gravity holds the system together.':p.desc;
 document.getElementById('pDiameter').textContent=sunSelected?'1.39 million km':p.d.toLocaleString()+' km';
 document.getElementById('pYear').textContent=sunSelected?'—':p.year;
 document.getElementById('pDay').textContent=sunSelected?'—':p.day;
 statusEl.textContent='● SELECTED: '+(sunSelected?'SUN':p.name.toUpperCase());
}
select(-1);
document.getElementById('pauseBtn').addEventListener('click',()=>{
 paused=!paused;
 document.getElementById('pauseBtn').textContent=paused?'▶ Resume':'Ⅱ Pause';
 statusEl.textContent=paused?'Ⅱ SIMULATION PAUSED':'● SYSTEM ONLINE';
});
document.getElementById('resetBtn').addEventListener('click',()=>{
 camera.position.set(0,72,155);controls.target.set(0,0,0);controls.update();select(-1);
});
const onPointer=(event)=>{
 const rect=renderer.domElement.getBoundingClientRect();
 pointer.x=((event.clientX-rect.left)/rect.width)*2-1;
 pointer.y=-((event.clientY-rect.top)/rect.height)*2+1;
 raycaster.setFromCamera(pointer,camera);
 const hits=raycaster.intersectObjects(pickables,false);
 if(hits.length){const idx=hits[0].object.userData.index;select(idx===undefined?-1:idx);}
};
renderer.domElement.addEventListener('click',onPointer);
function resize(){
 const w=host.clientWidth,h=host.clientHeight;
 camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false);
}
window.addEventListener('resize',resize);resize();
let last=performance.now();
function animate(now){
 requestAnimationFrame(animate);
 const dt=Math.min((now-last)/1000,.05);last=now;
 if(!paused){elapsed+=dt*CFG.speed;
  sun.rotation.y+=dt*.035*CFG.speed;
  for(let i=0;i<planetData.length;i++){
   const p=planetData[i],mesh=worldMeshes[i];
   const normalized=Math.sqrt(365.25/p.period);
   orbitGroups[i].rotation.y+=dt*.055*normalized*CFG.speed;
   mesh.rotation.y+=dt*(p.name==='Jupiter'?.28:.12)*CFG.speed;
   if(mesh.userData.moonPivot)mesh.userData.moonPivot.rotation.y+=dt*.7*CFG.speed;
  }
 }
 controls.update();
 for(const item of labels){
  const v=item.mesh.getWorldPosition(new THREE.Vector3());v.project(camera);
  const x=(v.x*.5+.5)*host.clientWidth,y=(-v.y*.5+.5)*host.clientHeight;
  item.el.style.left=x+'px';item.el.style.top=y+'px';
  item.el.style.display=(v.z<1&&x>0&&x<host.clientWidth&&y>0&&y<host.clientHeight)?'block':'none';
 }
 renderer.render(scene,camera);
}
requestAnimationFrame(animate);
loading.style.opacity='0';setTimeout(()=>loading.style.display='none',450);
statusEl.textContent='● SYSTEM ONLINE';
window.addEventListener('message',(event)=>{
 const d=event.data;if(!d||d.source!=='streamlit')return;
 if(d.type==='control'){
  paused=!!d.paused;
  if(d.speed!==undefined)CFG.speed=Number(d.speed);
 }
 if(d.type==='select'&&Number.isInteger(d.index))select(d.index);
 if(d.type==='reset'){camera.position.set(0,72,155);controls.target.set(0,0,0);controls.update();select(-1);}
});
window.parent.postMessage({isStreamlitMessage:true,type:'streamlit:componentReady',apiVersion:1},'*');
window.parent.postMessage({isStreamlitMessage:true,type:'streamlit:setFrameHeight',height:660},'*');
</script>
</div>
</body>
</html>
"""
scene_html = (scene_html
    .replace("__SPEED__", str(speed))
    .replace("__SIZE__", str(size_factor))
    .replace("__ORBITS__", str(show_orbits).lower())
    .replace("__LABELS__", str(show_labels).lower())
    .replace("__ASTEROIDS__", str(show_asteroids).lower())
    .replace("__STARS__", str(show_stars).lower())
)

# Controls are built into the interactive 3D frame.\ncomponents.html(scene_html, height=675, scrolling=False)

st.markdown("""
<div style="margin-top:18px;padding:15px 17px;border:1px solid #1d3852;border-radius:15px;background:rgba(9,23,39,.72)">
  <div style="font-weight:750;color:#dceeff;margin-bottom:5px">About this simulation</div>
  <div style="font-size:12px;line-height:1.6;color:#91a9c2">
  This is an interactive educational visualization. Planet sizes, distances and orbital speeds are compressed
  so the whole system can be explored on one screen; they are not shown to a single true scale.
  Procedural surface patterns are illustrative, not scientific spacecraft imagery. An internet connection
  is required to load the Three.js 3D engine from its CDN.
  </div>
</div>
""", unsafe_allow_html=True)

