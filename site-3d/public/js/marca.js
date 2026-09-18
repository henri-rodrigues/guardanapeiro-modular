/* =====================================================================
   Marca — lê a logo do cliente, deduz uma paleta e desenha as artes que
   vão aplicadas na peça (frente e fundo). Tudo em <canvas>, então cada
   arte vira textura direto no Three.js.
   ===================================================================== */

const trava = (v, a, b) => Math.max(a, Math.min(b, v));
const hx = (v) => trava(Math.round(v), 0, 255).toString(16).padStart(2, '0');

export const paraHex = ({ r, g, b }) => `#${hx(r)}${hx(g)}${hx(b)}`;
export const paraInt = ({ r, g, b }) =>
  (trava(Math.round(r), 0, 255) << 16) | (trava(Math.round(g), 0, 255) << 8) | trava(Math.round(b), 0, 255);

const rgba = ({ r, g, b }, a) => `rgba(${Math.round(r)},${Math.round(g)},${Math.round(b)},${a})`;
const lum = ({ r, g, b }) => (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;

function paraHsl({ r, g, b }) {
  const R = r / 255, G = g / 255, B = b / 255;
  const mx = Math.max(R, G, B), mn = Math.min(R, G, B), d = mx - mn;
  let h = 0;
  if (d) {
    if (mx === R) h = ((G - B) / d) % 6;
    else if (mx === G) h = (B - R) / d + 2;
    else h = (R - G) / d + 4;
    h *= 60;
    if (h < 0) h += 360;
  }
  const l = (mx + mn) / 2;
  return { h, s: d ? d / (1 - Math.abs(2 * l - 1)) : 0, l };
}

function deHsl(h, s, l) {
  h = ((h % 360) + 360) % 360; s = trava(s, 0, 1); l = trava(l, 0, 1);
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = l - c / 2;
  const t = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x]
          : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
  return { r: (t[0] + m) * 255, g: (t[1] + m) * 255, b: (t[2] + m) * 255 };
}

const mexer = (cor, dh, ds, dl) => {
  const p = paraHsl(cor);
  return deHsl(p.h + dh, p.s + ds, p.l + dl);
};

/* ---------- extração da paleta ---------- */

function amostrar(img, lado = 96) {
  const c = document.createElement('canvas');
  const k = Math.min(lado / img.width, lado / img.height, 1);
  c.width = Math.max(1, Math.round(img.width * k));
  c.height = Math.max(1, Math.round(img.height * k));
  const ctx = c.getContext('2d', { willReadFrequently: true });
  ctx.drawImage(img, 0, 0, c.width, c.height);
  return ctx.getImageData(0, 0, c.width, c.height).data;
}

/** Cores dominantes da logo, favorecendo as saturadas (as da marca). */
export function extrairPaleta(img) {
  const px = amostrar(img);
  const baldes = new Map();
  let somaLum = 0, visiveis = 0;

  for (let i = 0; i < px.length; i += 4) {
    if (px[i + 3] < 128) continue;                       // transparente
    const r = px[i], g = px[i + 1], b = px[i + 2];
    somaLum += lum({ r, g, b });
    visiveis++;
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    if (mn > 238) continue;                              // branco de fundo
    if (mx < 18) continue;                               // preto chapado
    const k = (r >> 4) * 256 + (g >> 4) * 16 + (b >> 4);
    let acc = baldes.get(k);
    if (!acc) baldes.set(k, (acc = { r: 0, g: 0, b: 0, n: 0 }));
    acc.r += r; acc.g += g; acc.b += b; acc.n++;
  }

  const cands = [...baldes.values()]
    .map((a) => {
      const cor = { r: a.r / a.n, g: a.g / a.n, b: a.b / a.n };
      return { cor, peso: a.n * (0.25 + paraHsl(cor).s) };
    })
    .sort((a, b) => b.peso - a.peso)
    .slice(0, 8);

  const logoClara = visiveis ? somaLum / visiveis > 0.55 : false;
  const primaria = cands.length ? cands[0].cor : { r: 224, g: 163, b: 0 };
  const hp = paraHsl(primaria);

  // secundária: a candidata de matiz mais distante; se não houver, deriva da primária
  let secundaria = null, melhor = 0;
  for (const c of cands.slice(1)) {
    const d = Math.abs(((paraHsl(c.cor).h - hp.h + 540) % 360) - 180);
    const nota = (180 - d) * c.peso;
    if (nota > melhor) { melhor = nota; secundaria = c.cor; }
  }
  if (!secundaria) secundaria = mexer(primaria, 150, 0, hp.l > 0.5 ? -0.12 : 0.14);

  // fundo da arte: escuro se a logo é clara, claro se a logo é escura
  const base  = logoClara ? deHsl(hp.h, Math.min(hp.s, 0.42), 0.11)
                          : deHsl(hp.h, Math.min(hp.s, 0.20), 0.94);
  const base2 = logoClara ? deHsl(hp.h, Math.min(hp.s, 0.50), 0.20)
                          : deHsl(hp.h, Math.min(hp.s, 0.28), 0.86);
  const texto = logoClara ? { r: 245, g: 247, b: 250 } : { r: 22, g: 24, b: 30 };

  // o estilo sai da própria logo: matiz define o desenho, saturação baixa vira faixas
  const estilo = hp.s < 0.18 ? 'faixas'
               : ['gradiente', 'faixas', 'diagonal'][Math.floor(hp.h / 120) % 3];

  return { primaria, secundaria, base, base2, texto, logoClara, estilo };
}

/** Paleta neutra usada enquanto não há logo (segue a cor escolhida da peça).
    Cor de peça quase sem saturação (preto, branco, cinza) vira arte cinza. */
export function paletaNeutra(corProduto) {
  const p = paraHsl(corProduto);
  const s = p.s < 0.18 ? 0 : Math.min(p.s, 0.55);
  const escura = p.l < 0.5;
  return {
    primaria: deHsl(p.h, s, escura ? 0.62 : 0.42),
    secundaria: deHsl(p.h, s * 0.6, escura ? 0.38 : 0.62),
    base: deHsl(p.h, s * 0.35, escura ? 0.12 : 0.92),
    base2: deHsl(p.h, s * 0.42, escura ? 0.20 : 0.84),
    texto: escura ? { r: 245, g: 247, b: 250 } : { r: 22, g: 24, b: 30 },
    logoClara: escura,
    estilo: 'gradiente'
  };
}

/* ---------- desenho ---------- */

function pintarFundo(ctx, w, h, p) {
  if (p.estilo === 'faixas') {
    ctx.fillStyle = paraHex(p.base);
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = rgba(p.primaria, 0.16);
    for (let y = -h; y < h * 2; y += h * 0.16) ctx.fillRect(0, y, w, h * 0.07);
    ctx.fillStyle = paraHex(p.primaria);
    ctx.fillRect(0, h * 0.86, w, h * 0.06);
    ctx.fillStyle = paraHex(p.secundaria);
    ctx.fillRect(0, h * 0.08, w, h * 0.025);
  } else if (p.estilo === 'diagonal') {
    ctx.fillStyle = paraHex(p.base);
    ctx.fillRect(0, 0, w, h);
    ctx.save();
    ctx.translate(w * 0.5, h * 0.5);
    ctx.rotate(-Math.PI / 9);
    ctx.translate(-w * 0.5, -h * 0.5);
    const faixa = h * 0.34;
    ctx.fillStyle = rgba(p.primaria, 0.9);
    ctx.fillRect(-w, h * 0.62, w * 3, faixa);
    ctx.fillStyle = rgba(p.secundaria, 0.55);
    ctx.fillRect(-w, h * 0.62 - faixa * 0.42, w * 3, faixa * 0.3);
    ctx.restore();
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, rgba(p.base, 0.9));
    g.addColorStop(0.6, rgba(p.base, 0));
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
  } else {
    const g = ctx.createLinearGradient(0, 0, w, h);
    g.addColorStop(0, paraHex(p.base));
    g.addColorStop(0.55, paraHex(p.base2));
    g.addColorStop(1, paraHex(p.base));
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
    const bril = ctx.createRadialGradient(w * 0.24, h * 0.08, 0, w * 0.24, h * 0.08, h * 1.5);
    bril.addColorStop(0, rgba(p.primaria, 0.34));
    bril.addColorStop(1, rgba(p.primaria, 0));
    ctx.fillStyle = bril;
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = paraHex(p.primaria);
    ctx.fillRect(0, h - h * 0.045, w, h * 0.045);
  }
}

function desenharLogo(ctx, img, cx, cy, maxW, maxH) {
  const k = Math.min(maxW / img.width, maxH / img.height);
  const w = img.width * k, h = img.height * k;
  ctx.drawImage(img, cx - w / 2, cy - h / 2, w, h);
}

function novaTela(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return { c, ctx: c.getContext('2d') };
}

/** Arte do fundo da peça: logo + número da mesa. */
export function arteFundo(img, p, mesa) {
  const W = 1200, H = 450;
  const { c, ctx } = novaTela(W, H);
  pintarFundo(ctx, W, H, p);

  const corteX = W * 0.63;

  // bloco do número da mesa
  ctx.fillStyle = paraHex(p.primaria);
  ctx.fillRect(corteX, 0, W - corteX, H);
  const alvo = lum(p.primaria) > 0.62 ? { r: 20, g: 22, b: 28 } : { r: 255, g: 255, b: 255 };
  ctx.fillStyle = paraHex(alvo);
  ctx.textAlign = 'center';
  ctx.font = '600 44px Inter, system-ui, Arial, sans-serif';
  ctx.globalAlpha = 0.72;
  ctx.fillText('MESA', corteX + (W - corteX) / 2, H * 0.31);
  ctx.globalAlpha = 1;
  ctx.font = '800 210px Inter, system-ui, Arial, sans-serif';
  ctx.fillText(String(mesa).padStart(2, '0'), corteX + (W - corteX) / 2, H * 0.83);

  // logo (ou marca de água textual, quando ainda não há logo)
  if (img) {
    desenharLogo(ctx, img, corteX * 0.5, H * 0.47, corteX * 0.74, H * 0.6);
  } else {
    ctx.fillStyle = rgba(p.texto, 0.5);
    ctx.font = '700 52px Inter, system-ui, Arial, sans-serif';
    ctx.fillText('SUA LOGO AQUI', corteX * 0.5, H * 0.54);
  }
  return c;
}

/** Arte da frente da peça: faixa com a logo. */
export function arteFrente(img, p) {
  if (!img) return null;
  const W = 1200, H = 255;
  const { c, ctx } = novaTela(W, H);
  pintarFundo(ctx, W, H, p);
  ctx.fillStyle = paraHex(p.secundaria);
  ctx.fillRect(0, 0, W * 0.012, H);
  ctx.fillRect(W - W * 0.012, 0, W * 0.012, H);
  desenharLogo(ctx, img, W / 2, H * 0.47, W * 0.56, H * 0.62);
  return c;
}
