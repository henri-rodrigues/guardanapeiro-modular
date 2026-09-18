/* =====================================================================
   Visualizador 3D — Three.js + STLLoader + OrbitControls
   ===================================================================== */
import * as THREE from 'three';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { PECA_BASE, MODULO_CARDAPIO, OFFSET_GLOBAL, PLACA, BASE_CARDAPIO_X, ARTE } from './config.js';

const loader = new STLLoader();
const cacheGeo = new Map();

export class Configurador3D {
  constructor(canvas) {
    this.canvas = canvas;
    this.pecas = new Map();          // id -> THREE.Object3D
    this.encaixados = new Map();     // id -> { largura, ordem, arquivo }
    this.decalques = [];
    this.cor = new THREE.Color(0x2b2b30);
    this.rugosidade = 0.85;
    this._initCena();
    this._loop();
    window.addEventListener('resize', () => this._resize());
  }

  _initCena() {
    const { canvas } = this;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;

    this.scene = new THREE.Scene();
    this.scene.background = null;

    this.camera = new THREE.PerspectiveCamera(38, 1, 1, 5000);
    this.camera.position.set(430, 300, 430);

    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.minDistance = 160;
    this.controls.maxDistance = 1400;
    this.controls.maxPolarAngle = Math.PI * 0.52;
    this.controls.autoRotate = true;
    this.controls.autoRotateSpeed = 0.7;

    // Raiz com Z para cima (os STL foram modelados em Z-up)
    this.root = new THREE.Group();
    this.root.rotation.x = -Math.PI / 2;
    this.scene.add(this.root);

    // ---- iluminação (estúdio suave) ----
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x5a5a66, 0.75));

    const key = new THREE.DirectionalLight(0xffffff, 2.1);
    key.position.set(320, 480, 260);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    key.shadow.camera.near = 50;
    key.shadow.camera.far = 1800;
    const d = 420;
    Object.assign(key.shadow.camera, { left: -d, right: d, top: d, bottom: -d });
    key.shadow.bias = -0.0008;
    key.shadow.radius = 3;
    this.scene.add(key);

    const fill = new THREE.DirectionalLight(0xdfe6ff, 0.6);
    fill.position.set(-360, 220, -180);
    this.scene.add(fill);

    const rim = new THREE.DirectionalLight(0xffffff, 0.5);
    rim.position.set(-120, 160, -420);
    this.scene.add(rim);

    // ---- chão que recebe sombra ----
    const chao = new THREE.Mesh(
      new THREE.PlaneGeometry(4000, 4000),
      new THREE.ShadowMaterial({ opacity: 0.22 })
    );
    chao.rotation.x = -Math.PI / 2;
    chao.position.y = 0;
    chao.receiveShadow = true;
    this.scene.add(chao);

    this.material = new THREE.MeshStandardMaterial({
      color: this.cor, roughness: this.rugosidade, metalness: 0.05
    });

    this._resize();
  }

  _resize() {
    const r = this.canvas.parentElement.getBoundingClientRect();
    const w = Math.max(320, r.width), h = Math.max(320, r.height);
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }

  _loop() {
    requestAnimationFrame(() => this._loop());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }

  async _geometria(url) {
    if (cacheGeo.has(url)) return cacheGeo.get(url);
    const geo = await new Promise((resolve, reject) =>
      loader.load(url, resolve, undefined, () => reject(new Error(`Falha ao carregar ${url}`)))
    );
    geo.computeVertexNormals();
    geo.computeBoundingBox();
    // leva o canto mínimo para a origem (STL já vem assim, mas garante)
    const min = geo.boundingBox.min.clone();
    geo.translate(-min.x, -min.y, -min.z);
    geo.computeBoundingBox();
    cacheGeo.set(url, geo);
    return geo;
  }

  _mesh(geo) {
    const m = new THREE.Mesh(geo, this.material);
    m.castShadow = true;
    m.receiveShadow = true;
    return m;
  }

  async carregarBase() {
    const geo = await this._geometria(PECA_BASE.arquivo);
    const mesh = this._mesh(geo);
    const grupo = new THREE.Group();
    grupo.add(mesh);
    this.root.add(grupo);
    this.pecas.set(PECA_BASE.id, grupo);
    this.enquadrar();
    return grupo;
  }

  /** Encadeia os módulos da esquerda: os de menor 'ordem' ficam junto da peça base. */
  reposicionarEsquerda() {
    const fila = [...this.encaixados.entries()].sort((a, b) => a[1].ordem - b[1].ordem);
    let x = 0;                              // face esquerda do organizador (x=0 no mundo original)
    for (const [id, info] of fila) {
      x -= info.largura;
      this.pecas.get(id).position.set(x, 0, 0);
    }
  }

  /** Liga/desliga um módulo e já aplica a variante escolhida (quantidade). */
  async ativarModulo(def, variante, ativo) {
    if (!ativo) {
      const g = this.pecas.get(def.id);
      if (g) { this.root.remove(g); this.pecas.delete(def.id); }
      this.encaixados.delete(def.id);
      this.reposicionarEsquerda();
      this.enquadrar();
      return;
    }
    const atual = this.encaixados.get(def.id);
    if (!atual || atual.arquivo !== variante.arquivo) {
      const antigo = this.pecas.get(def.id);
      if (antigo) this.root.remove(antigo);
      const geo = await this._geometria(variante.arquivo);
      const g = new THREE.Group();
      g.add(this._mesh(geo));
      this.root.add(g);
      this.pecas.set(def.id, g);
    }
    this.encaixados.set(def.id, { largura: variante.largura, ordem: def.ordem, arquivo: variante.arquivo });
    this.reposicionarEsquerda();
    this.enquadrar();
  }

  async ativarCardapio(ativo) {
    const id = MODULO_CARDAPIO.id;
    if (!ativo) {
      const g = this.pecas.get(id);
      if (g) { this.root.remove(g); this.pecas.delete(id); }
      this.enquadrar();
      return;
    }
    if (this.pecas.has(id)) return;

    const grupo = new THREE.Group();
    const [defBase, defPlaca] = MODULO_CARDAPIO.pecas;

    const geoBase = await this._geometria(defBase.arquivo);
    const mBase = this._mesh(geoBase);
    mBase.position.set(BASE_CARDAPIO_X + OFFSET_GLOBAL, 0, 0);
    grupo.add(mBase);

    // placa: mesma transformação da montagem real (inclinada 12°)
    const geoPlaca = await this._geometria(defPlaca.arquivo);
    const mPlaca = this._mesh(geoPlaca);
    const c = Math.cos(PLACA.TILT), s = Math.sin(PLACA.TILT);
    const half = PLACA.ESPESSURA / 2;
    // (px,py,pz) -> x: PXC-38+px ; y: Y0+(half-pz)c+py·s ; z: Z0-(half-pz)s+py·c
    const M = new THREE.Matrix4();
    M.set(
      1, 0,  0,  PLACA.PXC - PLACA.LARGURA / 2 + OFFSET_GLOBAL,
      0, s, -c,  PLACA.Y0 + half * c,
      0, c,  s,  PLACA.Z0 - half * s,
      0, 0,  0,  1
    );
    mPlaca.applyMatrix4(M);
    mPlaca.matrixAutoUpdate = false;
    mPlaca.updateMatrix ();
    grupo.add(mPlaca);
    this.placaMesh = mPlaca;

    this.root.add(grupo);
    this.pecas.set(id, grupo);
    this.enquadrar();
  }

  setCor(hex, rugosidade = 0.8) {
    this.material.color.setHex(hex);
    this.material.roughness = rugosidade;
    this.material.needsUpdate = true;
  }

  /** Decalque plano colado numa face do organizador, orientado pela normal. */
  _decalque(tela, spec) {
    const tex = new THREE.CanvasTexture(tela);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = this.renderer.capabilities.getMaxAnisotropy();

    const mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(spec.largura, spec.altura),
      new THREE.MeshStandardMaterial({
        map: tex, transparent: true, roughness: 0.55, metalness: 0,
        side: THREE.DoubleSide,
        polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2
      })
    );
    // base ortonormal do decalque: X = direita, Y = cima (+Z da peça), Z = normal
    const N = new THREE.Vector3(...spec.normal).normalize();
    const U = new THREE.Vector3(0, 0, 1);
    const R = new THREE.Vector3().crossVectors(U, N).normalize();
    const M = new THREE.Matrix4().makeBasis(R, U, N);
    M.setPosition(new THREE.Vector3(spec.cx, spec.y, spec.cz));
    mesh.applyMatrix4(M);

    this.root.add(mesh);
    this.decalques.push(mesh);
    return mesh;
  }

  /** Aplica as artes geradas a partir da logo: faixa na frente e painel no fundo. */
  aplicarArte({ frente, fundo }) {
    this.limparArte();
    if (frente) this._decalque(frente, ARTE.frente);
    if (fundo) this._decalque(fundo, ARTE.fundo);
  }

  limparArte() {
    for (const m of this.decalques) {
      this.root.remove(m);
      m.geometry.dispose();
      m.material.map?.dispose();
      m.material.dispose();
    }
    this.decalques = [];
  }

  /** Enquadra a câmera suavemente em tudo que está na cena. */
  enquadrar(animar = true) {
    const bbox = new THREE.Box3();
    let vazio = true;
    this.root.traverse((o) => {
      if (o.isMesh) { bbox.expandByObject(o); vazio = false; }
    });
    if (vazio) return;
    const centro = bbox.getCenter(new THREE.Vector3());
    const tam = bbox.getSize(new THREE.Vector3());
    const raio = Math.max(tam.x, tam.y, tam.z) * 0.62;
    const dist = raio / Math.sin((this.camera.fov * Math.PI / 180) / 2) * 1.12;

    const alvo = centro.clone();
    const dir = new THREE.Vector3(0.78, 0.52, 0.78).normalize();
    const posFinal = alvo.clone().add(dir.multiplyScalar(dist));

    if (!animar) {
      this.controls.target.copy(alvo);
      this.camera.position.copy(posFinal);
      return;
    }
    const p0 = this.camera.position.clone(), t0 = this.controls.target.clone();
    const t = { k: 0 };
    const passo = () => {
      t.k = Math.min(1, t.k + 0.06);
      const e = 1 - Math.pow(1 - t.k, 3);          // easeOutCubic
      this.camera.position.lerpVectors(p0, posFinal, e);
      this.controls.target.lerpVectors(t0, alvo, e);
      if (t.k < 1) requestAnimationFrame(passo);
    };
    passo();
  }

  setAutoRotate(v) { this.controls.autoRotate = v; }
  resetCamera() { this.enquadrar(true); }
}
