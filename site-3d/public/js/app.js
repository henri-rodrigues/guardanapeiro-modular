/* =====================================================================
   Lógica da página: painel de customização, tema automático pela logo
   e link do WhatsApp.
   ===================================================================== */
import { Configurador3D } from './viewer.js';
import { WHATSAPP, MODULOS_ESQUERDA, MODULO_CARDAPIO, CORES } from './config.js';
import { extrairPaleta, paletaNeutra, arteFundo, arteFrente, paraHex, paraInt } from './marca.js';

const $ = (sel) => document.querySelector(sel);
const sortearMesa = () => 1 + Math.floor(Math.random() * 30);

const estado = {
  cor: CORES[0],
  corMarca: null,              // swatch extraído da logo, quando houver
  modulos: new Map(),          // id do módulo -> variante escolhida
  cardapio: true,
  logo: null,
  logoImg: null,
  paleta: null,
  mesa: sortearMesa()
};

const viewer = new Configurador3D($('#canvas3d'));

/* ---------- carregamento inicial ---------- */
(async function iniciar() {
  const aviso = $('#carregando');
  try {
    await viewer.carregarBase();
    await viewer.ativarCardapio(true);
    viewer.setCor(estado.cor.hex, estado.cor.rug);
    aviso.classList.add('hidden');
  } catch (e) {
    aviso.innerHTML = `<p class="text-red-300 text-sm">Erro ao carregar os modelos.<br>
      Verifique se os arquivos .stl estão em <code>public/modelos/</code> e se o servidor está rodando.<br>
      <span class="opacity-70">${e.message}</span></p>`;
  }
  montarPainel();
  redesenharArte();
  atualizarResumo();
})();

/* ---------- painel ---------- */
function montarPainel() {
  const box = $('#lista-modulos');
  box.innerHTML = '';

  // cardápio (lateral direita) — sem variantes
  box.appendChild(cardSimples(MODULO_CARDAPIO, estado.cardapio, async (ativo) => {
    estado.cardapio = ativo;
    await viewer.ativarCardapio(ativo);
    atualizarResumo();
  }));

  for (const def of MODULOS_ESQUERDA) box.appendChild(cardModulo(def));

  montarCores();
}

function cardSimples(def, inicial, onChange) {
  const el = document.createElement('div');
  el.className = 'mod-card' + (inicial ? ' ativo' : '');
  el.innerHTML = `
    <label class="mod-cab">
      <input type="checkbox" ${inicial ? 'checked' : ''}>
      <span style="flex:1">
        <span class="mod-nome">${def.nome}</span>
        <span class="mod-desc">${def.descricao}</span>
        ${def.medidas ? `<span class="mod-med">${def.medidas}</span>` : ''}
      </span>
    </label>`;
  const input = el.querySelector('input');
  input.addEventListener('change', async () => {
    el.classList.toggle('ativo', input.checked);
    el.classList.add('ocupado');
    await onChange(input.checked);
    el.classList.remove('ocupado');
  });
  return el;
}

function cardModulo(def) {
  const varPadrao = def.variantes.find((v) => v.valor === def.padrao) || def.variantes[0];
  let escolhida = varPadrao;

  const el = document.createElement('div');
  el.className = 'mod-card';
  el.innerHTML = `
    <label class="mod-cab">
      <input type="checkbox" data-mod="${def.id}">
      <span style="flex:1">
        <span class="mod-nome">${def.nome}</span>
        <span class="mod-desc">${def.descricao}</span>
        <span class="mod-med"></span>
      </span>
    </label>`;

  const input = el.querySelector('input');
  const med = el.querySelector('.mod-med');
  med.textContent = escolhida.medidas;

  let botoes = [];
  if (def.variantes.length > 1) {
    const linha = document.createElement('div');
    linha.className = 'qtd';
    if (def.rotulo) linha.setAttribute('aria-label', def.rotulo);
    for (const v of def.variantes) {
      const b = document.createElement('button');
      b.className = 'qtd-btn' + (v === escolhida ? ' ativo' : '');
      b.textContent = v.texto;
      b.addEventListener('click', async () => {
        escolhida = v;
        botoes.forEach((x) => x.classList.toggle('ativo', x === b));
        med.textContent = v.medidas;
        if (!input.checked) {           // escolher a quantidade já liga o módulo
          input.checked = true;
          el.classList.add('ativo');
        }
        await aplicar();
      });
      botoes.push(b);
      linha.appendChild(b);
    }
    el.appendChild(linha);
  }

  async function aplicar() {
    el.classList.add('ocupado');
    if (input.checked) estado.modulos.set(def.id, escolhida);
    else estado.modulos.delete(def.id);
    await viewer.ativarModulo(def, escolhida, input.checked);
    el.classList.remove('ocupado');
    atualizarResumo();
  }

  input.addEventListener('change', async () => {
    el.classList.toggle('ativo', input.checked);
    await aplicar();
  });
  return el;
}

/* ---------- cores ---------- */
function montarCores() {
  const cores = $('#lista-cores');
  cores.innerHTML = '';
  const lista = estado.corMarca ? [estado.corMarca, ...CORES] : [...CORES];

  for (const cor of lista) {
    const b = document.createElement('button');
    b.className = 'cor-btn' + (cor.id === estado.cor.id ? ' ativo' : '');
    b.style.background = cor.css;
    b.title = cor.nome;
    b.setAttribute('aria-label', cor.nome);
    b.onclick = () => {
      estado.cor = cor;
      viewer.setCor(cor.hex, cor.rug);
      cores.querySelectorAll('.cor-btn').forEach((x) => x.classList.remove('ativo'));
      b.classList.add('ativo');
      $('#cor-nome').textContent = cor.nome;
      if (!estado.logoImg) redesenharArte();     // sem logo, a arte segue a cor da peça
      atualizarResumo();
    };
    cores.appendChild(b);
  }
  $('#cor-nome').textContent = estado.cor.nome;
}

/* ---------- arte aplicada na peça ---------- */
function redesenharArte() {
  const p = estado.paleta || paletaNeutra(hexParaRgb(estado.cor.css));
  viewer.aplicarArte({
    frente: arteFrente(estado.logoImg, p),
    fundo: arteFundo(estado.logoImg, p, estado.mesa)
  });
}

function hexParaRgb(css) {
  const n = parseInt(css.replace('#', ''), 16);
  return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 };
}

/** Reescreve o acento da página a partir da paleta da logo. */
function aplicarTemaPagina(p) {
  const raiz = document.documentElement.style;
  const acc = paraHex(p.primaria);
  const acc2 = paraHex(p.secundaria);
  const { r, g, b } = p.primaria;
  const rgb = `${Math.round(r)},${Math.round(g)},${Math.round(b)}`;
  const s = p.secundaria;
  raiz.setProperty('--acc', acc);
  raiz.setProperty('--acc2', acc2);
  raiz.setProperty('--acc-txt', luminancia(p.primaria) > 0.62 ? '#14161c' : '#ffffff');
  raiz.setProperty('--acc-soft', `rgba(${rgb},.12)`);
  raiz.setProperty('--acc-line', `rgba(${rgb},.38)`);
  raiz.setProperty('--acc-glow', `rgba(${rgb},.18)`);
  raiz.setProperty('--acc2-glow', `rgba(${Math.round(s.r)},${Math.round(s.g)},${Math.round(s.b)},.15)`);
}

function limparTemaPagina() {
  const raiz = document.documentElement.style;
  ['--acc', '--acc2', '--acc-txt', '--acc-soft', '--acc-line', '--acc-glow', '--acc2-glow']
    .forEach((v) => raiz.removeProperty(v));
}

const luminancia = ({ r, g, b }) => (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;

/* ---------- logo ---------- */
$('#input-logo').addEventListener('change', (ev) => {
  const file = ev.target.files?.[0];
  if (!file) return;
  const img = new Image();
  img.onload = () => {
    estado.logo = file.name;
    estado.logoImg = img;
    estado.paleta = extrairPaleta(img);

    // o site escolhe sozinho a cor da peça e o estilo da arte
    estado.corMarca = {
      id: 'marca',
      nome: 'Cor da marca',
      hex: paraInt(estado.paleta.primaria),
      css: paraHex(estado.paleta.primaria),
      rug: 0.6
    };
    estado.cor = estado.corMarca;
    viewer.setCor(estado.corMarca.hex, estado.corMarca.rug);
    aplicarTemaPagina(estado.paleta);
    montarCores();
    redesenharArte();

    $('#logo-nome').textContent = file.name;
    $('#logo-tema').textContent =
      `Cores definidas pela logo: ${paraHex(estado.paleta.primaria)} + ${paraHex(estado.paleta.secundaria)}.`;
    $('#btn-remover-logo').classList.remove('hidden');
    atualizarResumo();
  };
  img.src = URL.createObjectURL(file);
});

$('#btn-remover-logo').addEventListener('click', () => {
  estado.logo = null;
  estado.logoImg = null;
  estado.paleta = null;
  estado.corMarca = null;
  estado.cor = CORES[0];
  viewer.setCor(estado.cor.hex, estado.cor.rug);
  limparTemaPagina();
  montarCores();
  redesenharArte();
  $('#input-logo').value = '';
  $('#logo-nome').textContent = 'Nenhuma imagem enviada';
  $('#logo-tema').textContent =
    'Ao enviar a logo, o configurador escolhe sozinho as cores e o estilo da arte.';
  $('#btn-remover-logo').classList.add('hidden');
  atualizarResumo();
});

/* ---------- número da mesa ---------- */
function mostrarMesa() {
  $('#mesa-num').textContent = String(estado.mesa).padStart(2, '0');
}
$('#btn-mesa').addEventListener('click', () => {
  let n = sortearMesa();
  if (n === estado.mesa) n = (n % 30) + 1;
  estado.mesa = n;
  mostrarMesa();
  redesenharArte();
  atualizarResumo();
});
mostrarMesa();

/* ---------- controles da cena ---------- */
$('#btn-reset').addEventListener('click', () => viewer.resetCamera());
$('#btn-girar').addEventListener('click', (e) => {
  const on = e.currentTarget.getAttribute('aria-pressed') !== 'true';
  e.currentTarget.setAttribute('aria-pressed', String(on));
  e.currentTarget.textContent = on ? '⏸ Parar rotação' : '▶ Girar 360°';
  viewer.setAutoRotate(on);
});

/* ---------- resumo + WhatsApp ---------- */
function nomesModulos() {
  const nomes = MODULOS_ESQUERDA
    .filter((def) => estado.modulos.has(def.id))
    .sort((a, b) => a.ordem - b.ordem)
    .map((def) => {
      const v = estado.modulos.get(def.id);
      return def.variantes.length > 1 ? `${def.nome} (${v.texto})` : def.nome;
    });
  if (estado.cardapio) nomes.unshift(MODULO_CARDAPIO.nome);
  return nomes;
}

function atualizarResumo() {
  const mods = nomesModulos();
  $('#resumo-cor').textContent = estado.cor.nome;
  $('#resumo-modulos').textContent = mods.length ? mods.join(', ') : 'Somente a peça base';
  $('#resumo-mesa').textContent = String(estado.mesa).padStart(2, '0');
  $('#resumo-logo').textContent = estado.logo ? `Sim (${estado.logo})` : 'Não';
  $('#link-whatsapp').href = montarLinkWhatsApp();
}

function montarLinkWhatsApp() {
  const mods = nomesModulos();
  const texto =
    `${WHATSAPP.saudacao} com as configurações: ` +
    `Cor: ${estado.cor.nome} | ` +
    `Módulos: ${mods.length ? mods.join(', ') : 'nenhum (só a peça base)'} | ` +
    `Com Logo: ${estado.logo ? 'Sim' : 'Não'}`;
  return `https://wa.me/${WHATSAPP.numero}?text=${encodeURIComponent(texto)}`;
}

/* ---------- navegação suave ---------- */
document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener('click', (e) => {
    const alvo = document.querySelector(a.getAttribute('href'));
    if (!alvo) return;
    e.preventDefault();
    alvo.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});
