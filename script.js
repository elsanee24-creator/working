
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';

// ==========================================
// SOLAR SYSTEM 3D ENGINE
// ==========================================

const mount = document.querySelector('#scene');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x030611);
scene.fog = new THREE.FogExp2(0x030611, 0.0017);

const camera = new THREE.PerspectiveCamera(
    48,
    innerWidth / innerHeight,
    0.1,
    1800
);

camera.position.set(0, 95, 185);

const renderer = new THREE.WebGLRenderer({
    antialias: true,
    powerPreference: 'high-performance'
});

renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.18;

mount.appendChild(renderer.domElement);

// ==========================================
// CAMERA CONTROLS
// ==========================================

const controls = new OrbitControls(camera, renderer.domElement);

controls.enableDamping = true;
controls.dampingFactor = 0.045;
controls.minDistance = 12;
controls.maxDistance = 420;
controls.maxPolarAngle = Math.PI * 0.88;

// ==========================================
// LIGHTING
// ==========================================

scene.add(new THREE.AmbientLight(0x8a9ab8, 0.45));

const sunLight = new THREE.PointLight(
    0xffd7a0,
    3.8,
    700,
    1.25
);

scene.add(sunLight);

// ==========================================
// GLOBAL VARIABLES
// ==========================================

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

const clickable = [];
const planetObjects = [];

let selected = null;
let paused = false;
let speed = 1;

const clock = new THREE.Clock();

// ==========================================
// PROCEDURAL TEXTURE GENERATOR
// ==========================================

function makeCanvasTexture(kind, base, colors) {

    const canvas = document.createElement('canvas');

    canvas.width = 1024;
    canvas.height = 512;

    const ctx = canvas.getContext('2d');

    ctx.fillStyle = base;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    if (kind === 'bands') {

        for (let y = 0; y < 512; y++) {

            const wave =
                Math.sin(y * 0.055) * 10 +
                Math.sin(y * 0.013) * 15;

            ctx.fillStyle =
                colors[Math.floor((y + wave) / 25) % colors.length];

            ctx.globalAlpha = 0.75;

            ctx.fillRect(
                0,
                y,
                1024,
                Math.max(2, 16 + Math.sin(y * 0.08) * 9)
            );
        }

        ctx.globalAlpha = 1;

        for (let i = 0; i < 90; i++) {

            ctx.fillStyle = colors[i % colors.length];
            ctx.globalAlpha = 0.12;

            ctx.beginPath();

            ctx.ellipse(
                Math.random() * 1024,
                Math.random() * 512,
                20 + Math.random() * 100,
                2 + Math.random() * 9,
                0,
                0,
                Math.PI * 2
            );

            ctx.fill();
        }

    } else if (kind === 'cloud') {

        for (let i = 0; i < 9000; i++) {

            ctx.fillStyle =
                colors[Math.floor(Math.random() * colors.length)];

            ctx.globalAlpha = 0.12 + Math.random() * 0.22;

            ctx.beginPath();

            ctx.ellipse(
                Math.random() * 1024,
                Math.random() * 512,
                2 + Math.random() * 38,
                1 + Math.random() * 8,
                0,
                0,
                Math.PI * 2
            );

            ctx.fill();
        }

    } else {

        for (let i = 0; i < 18000; i++) {

            ctx.fillStyle =
                colors[Math.floor(Math.random() * colors.length)];

            ctx.globalAlpha = Math.random() * 0.4;

            ctx.fillRect(
                Math.random() * 1024,
                Math.random() * 512,
                1 + Math.random() * 5,
                1 + Math.random() * 2
            );
        }

        for (let i = 0; i < 220; i++) {

            ctx.fillStyle = colors[i % colors.length];
            ctx.globalAlpha = 0.12;

            ctx.beginPath();

            ctx.arc(
                Math.random() * 1024,
                Math.random() * 512,
                2 + Math.random() * 12,
                0,
                Math.PI * 2
            );

            ctx.fill();
        }
    }

    const texture = new THREE.CanvasTexture(canvas);

    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 8;

    return texture;
}

// ==========================================
// STAR FIELD
// ==========================================

function addStars() {

    const positions = [];

    for (let i = 0; i < 6500; i++) {

        const radius = THREE.MathUtils.randFloat(230, 850);

        const theta = Math.random() * Math.PI * 2;

        const phi = Math.acos(
            THREE.MathUtils.randFloatSpread(2)
        );

        positions.push(
            radius * Math.sin(phi) * Math.cos(theta),
            radius * Math.cos(phi),
            radius * Math.sin(phi) * Math.sin(theta)
        );
    }

    const geometry = new THREE.BufferGeometry();

    geometry.setAttribute(
        'position',
        new THREE.Float32BufferAttribute(positions, 3)
    );

    const material = new THREE.PointsMaterial({
        color: 0xc9dcff,
        size: 0.75,
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.85
    });

    scene.add(new THREE.Points(geometry, material));
}

addStars();

// ==========================================
// SUN
// ==========================================

const sunGeometry = new THREE.SphereGeometry(
    8.5,
    80,
    64
);

const sunMaterial = new THREE.MeshBasicMaterial({
    map: makeCanvasTexture(
        'cloud',
        '#f18b25',
        [
            '#ffb13b',
            '#ffd16b',
            '#f36d1d',
            '#fff0a3',
            '#c84c18'
        ]
    )
});

const sun = new THREE.Mesh(
    sunGeometry,
    sunMaterial
);

scene.add(sun);
clickable.push(sun);

// SUN GLOW

const glowCanvas = document.createElement('canvas');

glowCanvas.width = 256;
glowCanvas.height = 256;

const glowContext = glowCanvas.getContext('2d');

const gradient = glowContext.createRadialGradient(
    128, 128, 5,
    128, 128, 128
);

gradient.addColorStop(0, 'rgba(255,196,105,.55)');
gradient.addColorStop(0.3, 'rgba(255,125,40,.18)');
gradient.addColorStop(1, 'rgba(255,100,20,0)');

glowContext.fillStyle = gradient;
glowContext.fillRect(0, 0, 256, 256);

const glowTexture = new THREE.CanvasTexture(glowCanvas);

const glow = new THREE.Sprite(
    new THREE.SpriteMaterial({
        map: glowTexture,
        transparent: true,
        depthWrite: false
    })
);

glow.scale.set(46, 46, 1);
sun.add(glow);

// SUN CORONA

const corona = new THREE.Mesh(
    new THREE.SphereGeometry(9.1, 48, 32),
    new THREE.MeshBasicMaterial({
        color: 0xff9c38,
        transparent: true,
        opacity: 0.11,
        side: THREE.BackSide
    })
);

sun.add(corona);

// ==========================================
// PLANET DATA
// ==========================================

const planets = [

    {
        name: 'Mercury',
        type: 'TERRESTRIAL PLANET',
        radius: 1.35,
        distance: 13,
        speed: 0.95,
        rotation: 0.004,
        color: '#9b938b',
        texture: ['#77716b', '#c0b5a6', '#e0d6c8'],
        diameter: '4,879 km',
        orbit: '88 Earth days',
        day: '58.6 Earth days',
        desc: 'A small rocky world with a heavily cratered surface and extreme temperature changes.',
        kind: 'rock'
    },

    {
        name: 'Venus',
        type: 'TERRESTRIAL PLANET',
        radius: 2.25,
        distance: 20,
        speed: 0.72,
        rotation: -0.001,
        color: '#d5a76e',
        texture: ['#a76d3d', '#e4c18a', '#f5dca7'],
        diameter: '12,104 km',
        orbit: '225 Earth days',
        day: '243 Earth days',
        desc: 'A bright world wrapped in thick clouds and an exceptionally hot atmosphere.',
        kind: 'cloud'
    },

    {
        name: 'Earth',
        type: 'TERRESTRIAL PLANET',
        radius: 2.45,
        distance: 29,
        speed: 0.58,
        rotation: 0.018,
        color: '#3b91d2',
        texture: ['#124e91', '#238b55', '#b9d5e8'],
        diameter: '12,742 km',
        orbit: '365.25 days',
        day: '23 h 56 min',
        desc: 'Our home planet, with liquid-water oceans, continents and a protective atmosphere.',
        kind: 'earth'
    },

    {
        name: 'Mars',
        type: 'TERRESTRIAL PLANET',
        radius: 1.85,
        distance: 39,
        speed: 0.46,
        rotation: 0.015,
        color: '#c66c4b',
        texture: ['#7e3021', '#c56a45', '#e3a17b'],
        diameter: '6,779 km',
        orbit: '687 Earth days',
        day: '24 h 37 min',
        desc: 'A cold desert world with rusty terrain, giant volcanoes and ancient river valleys.',
        kind: 'rock'
    },

    {
        name: 'Jupiter',
        type: 'GAS GIANT',
        radius: 7.3,
        distance: 61,
        speed: 0.25,
        rotation: 0.035,
        color: '#d4a77f',
        texture: ['#9b6547', '#d7b38f', '#f0d9bb', '#b67d5b'],
        diameter: '139,820 km',
        orbit: '11.86 Earth years',
        day: '9 h 56 min',
        desc: 'The largest planet, famous for its striped cloud belts and Great Red Spot.',
        kind: 'bands'
    },

    {
        name: 'Saturn',
        type: 'GAS GIANT',
        radius: 6.2,
        distance: 85,
        speed: 0.17,
        rotation: 0.03,
        color: '#d7bd8a',
        texture: ['#9f815c', '#d8c39a', '#f1dfb8'],
        diameter: '116,460 km',
        orbit: '29.4 Earth years',
        day: '10 h 42 min',
        desc: 'A gas giant surrounded by an immense system of icy rings.',
        kind: 'bands',
        rings: true
    },

    {
        name: 'Uranus',
        type: 'ICE GIANT',
        radius: 4.1,
        distance: 108,
        speed: 0.12,
        rotation: -0.022,
        color: '#8bd4d8',
        texture: ['#66aeb8', '#a6e0df', '#d3f4eb'],
        diameter: '50,724 km',
        orbit: '84 Earth years',
        day: '17 h 14 min',
        desc: 'A pale blue ice giant that rotates on its side.',
        kind: 'cloud'
    },

    {
        name: 'Neptune',
        type: 'ICE GIANT',
        radius: 4.0,
        distance: 130,
        speed: 0.09,
        rotation: 0.02,
        color: '#426fe0',
        texture: ['#173a9a', '#356bd6', '#75a8ed'],
        diameter: '49,244 km',
        orbit: '164.8 Earth years',
        day: '16 h 6 min',
        desc: 'A distant deep-blue world with powerful winds and dynamic weather.',
        kind: 'cloud'
    }

];

// ==========================================
// PLANET CREATION
// ==========================================

planets.forEach((data) => {

    const orbit = new THREE.Group();

    scene.add(orbit);

    const orbitRing = new THREE.Mesh(
        new THREE.RingGeometry(
            data.distance - 0.055,
            data.distance + 0.055,
            220
        ),
        new THREE.MeshBasicMaterial({
            color: 0x8293ae,
            transparent: true,
            opacity: 0.25,
            side: THREE.DoubleSide
        })
    );

    orbitRing.rotation.x = -Math.PI / 2;

    scene.add(orbitRing);

    const group = new THREE.Group();

    orbit.add(group);

    const texture = makeCanvasTexture(
        data.kind,
        data.color,
        data.texture
    );

    const material = new THREE.MeshStandardMaterial({
        map: texture,
        roughness: 0.94,
        metalness: 0
    });

    const geometry = new THREE.SphereGeometry(
        data.radius,
        64,
        48
    );

    const planet = new THREE.Mesh(
        geometry,
        material
    );

    planet.position.x = data.distance;

    if (data.name === 'Uranus') {
        planet.rotation.z = Math.PI / 2;
    }

    group.add(planet);

    planet.userData.planet = data;

    clickable.push(planet);

    const object = {
        mesh: planet,
        group,
        orbit,
        data
    };

    planetObjects.push(object);

    // ======================================
    // SATURN RINGS
    // ======================================

    if (data.rings) {

        const ringGeometry = new THREE.RingGeometry(
            data.radius * 1.28,
            data.radius * 2.15,
            128
        );

        const ringMaterial = new THREE.MeshStandardMaterial({
            color: 0xc9b58f,
            roughness: 1,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.82
        });

        const saturnRing = new THREE.Mesh(
            ringGeometry,
            ringMaterial
        );

        saturnRing.rotation.x = -Math.PI / 2.35;
        saturnRing.rotation.y = 0.12;
        saturnRing.position.copy(planet.position);

        group.add(saturnRing);

        const innerRing = new THREE.Mesh(
            new THREE.RingGeometry(
                data.radius * 1.18,
                data.radius * 1.27,
                128
            ),
            new THREE.MeshBasicMaterial({
                color: 0x76624c,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.7
            })
        );

        innerRing.rotation.copy(saturnRing.rotation);
        innerRing.position.copy(planet.position);

        group.add(innerRing);
    }

    // ======================================
    // EARTH CLOUDS AND MOON
    // ======================================

    if (data.name === 'Earth') {

        const cloud = new THREE.Mesh(
            new THREE.SphereGeometry(
                data.radius * 1.018,
                48,
                32
            ),
            new THREE.MeshStandardMaterial({
                map: makeCanvasTexture(
                    'cloud',
                    '#ffffff',
                    ['#ffffff', '#d8f5ff', '#a9d4e8']
                ),
                transparent: true,
                opacity: 0.2,
                roughness: 1
            })
        );

        cloud.position.copy(planet.position);

        group.add(cloud);

        planet.userData.cloud = cloud;

        const moonPivot = new THREE.Group();

        moonPivot.position.x = data.distance;

        group.add(moonPivot);

        const moon = new THREE.Mesh(
            new THREE.SphereGeometry(0.68, 32, 24),
            new THREE.MeshStandardMaterial({
                map: makeCanvasTexture(
                    'rock',
                    '#88847e',
                    ['#5d5a56', '#c5c0b7', '#e1ddd4']
                ),
                roughness: 1
            })
        );

        moon.position.set(7, 0, 0);

        moonPivot.add(moon);

        planet.userData.moonPivot = moonPivot;
    }

});

// ==========================================
// ASTEROID BELT
// ==========================================

function addAsteroids() {

    const count = 1600;

    const geometry = new THREE.IcosahedronGeometry(
        0.22,
        0
    );

    const material = new THREE.MeshStandardMaterial({
        color: 0x8b8174,
        roughness: 1
    });

    const asteroids = new THREE.InstancedMesh(
        geometry,
        material,
        count
    );

    const dummy = new THREE.Object3D();

    for (let i = 0; i < count; i++) {

        const angle = Math.random() * Math.PI * 2;

        const radius = 46 + Math.random() * 8;

        const y = (Math.random() - 0.5) * 2.5;

        dummy.position.set(
            Math.cos(angle) * radius,
            y,
            Math.sin(angle) * radius
        );

        const size = 0.25 + Math.random() * 1.5;

        dummy.scale.set(
            size,
            size * (0.5 + Math.random()),
            size
        );

        dummy.rotation.set(
            Math.random() * 3,
            Math.random() * 3,
            Math.random() * 3
        );

        dummy.updateMatrix();

        asteroids.setMatrixAt(i, dummy.matrix);
    }

    scene.add(asteroids);
}

addAsteroids();

// ==========================================
// PLANET INFORMATION PANEL
// ==========================================

const info = document.querySelector('#infoPanel');

function selectObject(object) {

    selected = object;

    const data = object === sun
        ? null
        : object.userData.planet;

    document.querySelector('#planetType').textContent =
        data ? data.type : 'STAR';

    document.querySelector('#planetName').textContent =
        data ? data.name : 'The Sun';

    document.querySelector('#planetDesc').textContent =
        data
            ? data.desc
            : 'The star at the centre of our solar system, providing the light and energy that make life on Earth possible.';

    document.querySelector('#planetDiameter').textContent =
        data ? data.diameter : '1.39 million km';

    document.querySelector('#planetOrbit').textContent =
        data ? data.orbit : 'Centre';

    document.querySelector('#planetDay').textContent =
        data ? data.day : '~25 Earth days';

    document.querySelectorAll('.planet-chip').forEach(button => {

        button.classList.toggle(
            'active',
            button.dataset.name === (data ? data.name : 'The Sun')
        );

    });

    info.classList.remove('hidden');
}

// ==========================================
// PLANET SELECTION BUTTONS
// ==========================================

const list = document.querySelector('#planetList');

['The Sun', ...planets.map(p => p.name)].forEach(name => {

    const button = document.createElement('button');

    button.className = 'planet-chip';

    button.textContent = name;

    button.dataset.name = name;

    button.addEventListener('click', () => {

        const object = name === 'The Sun'
            ? sun
            : planetObjects.find(p => p.data.name === name).mesh;

        selectObject(object);

        focusSelected();
    });

    list.appendChild(button);
});

// ==========================================
// CAMERA FOCUS
// ==========================================

function focusSelected() {

    if (!selected) return;

    const target = new THREE.Vector3();

    selected.getWorldPosition(target);

    const radius = selected === sun
        ? 8.5
        : selected.geometry.parameters.radius;

    const offset = new THREE.Vector3(
        0,
        Math.max(12, radius * 3.5),
        Math.max(18, radius * 5)
    );

    controls.target.copy(target);

    camera.position.copy(target).add(offset);

    controls.update();
}

// ==========================================
// MOUSE PLANET SELECTION
// ==========================================

renderer.domElement.addEventListener(
    'pointerdown',
    event => {

        pointer.x = (event.clientX / innerWidth) * 2 - 1;

        pointer.y = -(event.clientY / innerHeight) * 2 + 1;

        raycaster.setFromCamera(pointer, camera);

        const hits = raycaster.intersectObjects(
            clickable,
            false
        );

        if (hits.length > 0) {

            selectObject(hits[0].object);

            focusSelected();
        }
    }
);

// ==========================================
// INTERFACE EVENTS
// ==========================================

document.querySelector('#closeInfo')
    .addEventListener('click', () => {

        info.classList.add('hidden');

    });

document.querySelector('#focusBtn')
    .addEventListener('click', focusSelected);

document.querySelector('#pauseBtn')
    .addEventListener('click', event => {

        paused = !paused;

        event.currentTarget.textContent =
            paused ? 'PLAY' : 'PAUSE';

        document.querySelector('#statusText').textContent =
            paused ? 'SIMULATION PAUSED' : 'SYSTEM RUNNING';

    });

document.querySelector('#resetBtn')
    .addEventListener('click', () => {

        camera.position.set(0, 95, 185);

        controls.target.set(0, 0, 0);

        controls.update();

        selectObject(sun);

    });

document.querySelector('#speed')
    .addEventListener('input', event => {

        speed = Number(event.target.value);

        document.querySelector('#speedValue').textContent =
            speed.toFixed(1) + '×';

    });

// ==========================================
// ANIMATION ENGINE
// ==========================================

function animate() {

    requestAnimationFrame(animate);

    const delta = Math.min(clock.getDelta(), 0.04);

    if (!paused) {

        sun.rotation.y += delta * 0.035 * speed;

        planetObjects.forEach(
            ({ mesh, orbit, data }) => {

                // Planet orbital revolution

                orbit.rotation.y +=
                    delta * data.speed * 0.12 * speed;

                // Planet axial rotation

                mesh.rotation.y +=
                    delta * data.rotation * 18 * speed;

                // Earth clouds

                if (mesh.userData.cloud) {

                    mesh.userData.cloud.rotation.y +=
                        delta * 0.003 * speed;
                }

                // Earth's Moon

                if (mesh.userData.moonPivot) {

                    mesh.userData.moonPivot.rotation.y +=
                        delta * 0.42 * speed;
                }

            }
        );
    }

    controls.update();

    renderer.render(scene, camera);
}

// ==========================================
// START SIMULATION
// ==========================================

selectObject(sun);

animate();

// ==========================================
// RESPONSIVE RESIZE
// ==========================================

window.addEventListener('resize', () => {

    camera.aspect = innerWidth / innerHeight;

    camera.updateProjectionMatrix();

    renderer.setSize(innerWidth, innerHeight);

    renderer.setPixelRatio(
        Math.min(devicePixelRatio, 2)
    );

});
                      
