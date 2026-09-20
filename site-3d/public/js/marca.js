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

  return { primaria, secundaria, base, base2, texto, logoClara };
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
    logoClara: escura
  };
}

/* ---------- desenho ---------- */
/* Visual único, limpo: fundo liso na cor da marca + cartões brancos
   arredondados (com sombra) para a logo e para o número da mesa —
   mesma linguagem visual do configurador (cards, sombra suave, tudo
   bem espaçado), sem padrões chamativos por trás do conteúdo. */

function pintarFundo(ctx, w, h, p) {
  ctx.fillStyle = paraHex(p.primaria);
  ctx.fillRect(0, 0, w, h);
  const bril = ctx.createRadialGradient(w * 0.16, h * 0.1, 0, w * 0.16, h * 0.1, h * 1.4);
  bril.addColorStop(0, 'rgba(255,255,255,0.16)');
  bril.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = bril;
  ctx.fillRect(0, 0, w, h);
  const sombra = ctx.createLinearGradient(0, h * 0.7, 0, h);
  sombra.addColorStop(0, 'rgba(0,0,0,0)');
  sombra.addColorStop(1, 'rgba(0,0,0,0.16)');
  ctx.fillStyle = sombra;
  ctx.fillRect(0, 0, w, h);
}

function cartao(ctx, x, y, w, h, r = 28) {
  ctx.save();
  ctx.shadowColor = 'rgba(10,12,18,0.32)';
  ctx.shadowBlur = 38;
  ctx.shadowOffsetY = 16;
  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
  ctx.fill();
  ctx.restore();
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

/** Arte do fundo da peça: cartão da logo + cartão com o número da mesa. */
export function arteFundo(img, p, mesa) {
  const W = 1600, H = 600;
  const { c, ctx } = novaTela(W, H);
  pintarFundo(ctx, W, H, p);

  const pad = 54, gap = 40, cardH = H - pad * 2, logoW = 460;
  const mesaX = pad + logoW + gap, mesaW = W - pad - mesaX;
  const interno = 52;

  // cartão da logo
  cartao(ctx, pad, pad, logoW, cardH);
  if (img) {
    desenharLogo(ctx, img, pad + logoW / 2, pad + cardH / 2, logoW - interno * 2, cardH - interno * 2);
  } else {
    ctx.strokeStyle = 'rgba(20,22,28,0.28)'; ctx.lineWidth = 3; ctx.setLineDash([14, 12]);
    ctx.strokeRect(pad + 22, pad + 22, logoW - 44, cardH - 44); ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(20,22,28,0.45)';
    ctx.textAlign = 'center'; ctx.font = '700 40px Inter, system-ui, Arial, sans-serif';
    ctx.fillText('SUA LOGO', pad + logoW / 2, pad + cardH / 2 - 10);
    ctx.fillText('AQUI', pad + logoW / 2, pad + cardH / 2 + 46);
  }

  // cartão da mesa
  cartao(ctx, mesaX, pad, mesaW, cardH);
  ctx.textAlign = 'left';
  ctx.fillStyle = '#3c414c';
  ctx.font = '700 78px Inter, system-ui, Arial, sans-serif';
  ctx.fillText('Mesa', mesaX + interno, pad + interno + 62);
  ctx.fillStyle = '#15171d';
  ctx.font = '800 214px Inter, system-ui, Arial, sans-serif';
  ctx.fillText(String(mesa).padStart(2, '0'), mesaX + interno - 6, pad + cardH - 54);

  return c;
}

/** Arte da frente da peça: cartão branco com a logo, sobre a cor da marca. */
export function arteFrente(img, p) {
  if (!img) return null;
  const W = 1600, H = 340;
  const { c, ctx } = novaTela(W, H);
  pintarFundo(ctx, W, H, p);
  const pad = 36, interno = 26;
  const altLogo = H - pad * 2 - interno * 2;
  const largLogo = Math.min(altLogo * (img.width / img.height), W * 0.7);
  const cw = largLogo + interno * 2, ch = H - pad * 2;
  cartao(ctx, (W - cw) / 2, pad, cw, ch, 24);
  desenharLogo(ctx, img, W / 2, H / 2, largLogo, altLogo);
  return c;
}
