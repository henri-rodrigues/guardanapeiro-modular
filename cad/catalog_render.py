"""Gera os renders isométricos do catálogo-conceito: produto montado (com
módulos), em cima de um balcão de bar estilizado, com a logo/cores de uma
marca de demonstração — para vendedores mostrarem as opções ao cliente.

Reaproveita o motor de raster próprio (raster.py) e o CSG (parts.py); só
acrescenta um cenário simples de balcão e decalques de marca nas mesmas
posições usadas no configurador do site (ver site-3d/public/js/config.js,
export const ARTE).

Uso:  python catalog_render.py
Saída: catalog_assets/*.png
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import raster
from raster import Scene
from parts import *
from assemble import plate_world
import views
from views import add_mesh, sticker_texture, hexc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'catalog_assets')
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------
# marca de demonstração (troque por um cliente real: nome + 2 cores + mesa)
# ---------------------------------------------------------------------
MARCA = dict(nome='BRASA BAR', primaria='#c8622a', secundaria='#20242b', mesa='07')

# paleta de cores de produto (mesma ideia do configurador do site)
CORES = {
    'preto':    '#2b2b30',
    'branco':   '#e8e8e6',
    'vermelho': '#b3161f',
    'amarelo':  '#e0a300',
    'marca':    MARCA['primaria'],
}

C_MOD  = hexc('#c9cdd6')          # módulos em cinza-claro nos spreads de especificação
WOOD   = hexc('#6b4226')          # tampo do balcão (nogueira escura — contrasta com o produto)
WOOD2  = hexc('#48291a')
STEEL  = hexc('#e2e6ea')          # friso metálico claro, para separar visualmente da madeira

FONT_BOLD = FONT_REG = None
for cand_b, cand_r in [
    ('C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/segoeui.ttf'),
    ('C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/arial.ttf'),
]:
    if os.path.exists(cand_b):
        FONT_BOLD, FONT_REG = cand_b, cand_r
        break

if FONT_BOLD:
    views.BOLD = FONT_BOLD   # views.py traz um caminho de fonte fixo (Linux); substitui pelo do Windows

def font(size, bold=True):
    path = FONT_BOLD if bold else (FONT_REG or FONT_BOLD)
    return ImageFont.truetype(path, size) if path else ImageFont.load_default()

# ---------------------------------------------------------------------
# decalques de marca (mesma posição/proporção que ARTE.frente / ARTE.fundo
# no configurador web: ver site-3d/public/js/config.js e marca.js)
# ---------------------------------------------------------------------
def decal_frente(k=8):
    W, H = int(160 * k), int(34 * k)
    im = Image.new('RGB', (W, H), MARCA['secundaria'])
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(3 * k)], fill=MARCA['primaria'])
    d.rectangle([0, H - int(3 * k), W, H], fill=MARCA['primaria'])
    f = font(int(H * 0.42))
    tw = d.textlength(MARCA['nome'], font=f)
    d.text(((W - tw) / 2, H * 0.24), MARCA['nome'], font=f, fill='#f4f1ea')
    return np.asarray(im).astype(float) / 255

def decal_fundo(k=8):
    W, H = int(160 * k), int(60 * k)
    im = Image.new('RGB', (W, H), MARCA['secundaria'])
    d = ImageDraw.Draw(im)
    corte = int(W * 0.66)
    d.rectangle([corte, 0, W, H], fill=MARCA['primaria'])
    f1 = font(int(H * 0.15))
    tw = d.textlength('MESA', font=f1)
    d.text((corte + (W - corte - tw) / 2, H * 0.12), 'MESA', font=f1, fill='#1c1c20')
    f2 = font(int(H * 0.58))
    tw2 = d.textlength(MARCA['mesa'], font=f2)
    d.text((corte + (W - corte - tw2) / 2, H * 0.32), MARCA['mesa'], font=f2, fill='#1c1c20')
    f3 = font(int(H * 0.15))
    tw3 = d.textlength(MARCA['nome'], font=f3)
    d.text(((corte - tw3) / 2, H * 0.42), MARCA['nome'], font=f3, fill='#f4f1ea')
    return np.asarray(im).astype(float) / 255

# ---------------------------------------------------------------------
# atlas: junta as texturas usadas numa cena (placa + decal frente/fundo)
# num único bitmap, porque o rasterizador só aceita 1 textura por render.
# ---------------------------------------------------------------------
def montar_atlas(partes):
    """partes: {chave: array HxWx3 float 0..1} -> (atlas, slices)
    slices[chave] = (x0_px, w_px, h_px, atlas_w, atlas_h)"""
    keys = list(partes.keys())
    ims = [partes[k] for k in keys]
    hmax = max(im.shape[0] for im in ims)
    wtot = sum(im.shape[1] for im in ims)
    atlas = np.ones((hmax, wtot, 3))
    slices = {}
    xo = 0
    for k, im in zip(keys, ims):
        h, w, _ = im.shape
        atlas[0:h, xo:xo + w] = im
        slices[k] = (xo, w, h, wtot, hmax)
        xo += w
    return atlas, slices

def remapear_uvs(S, slices):
    """reescreve S.uvs para apontar para a fatia certa do atlas, usando a
    chave do material (S.cmap) de cada triângulo."""
    inv = {v: k for k, v in S.cmap.items()}
    new_uvs = []
    for tx, uv, mid in zip(S.tex, S.uvs, S.mids):
        key = inv.get(mid)
        if not tx or key not in slices:
            new_uvs.append(uv)
            continue
        x0, w, h, W_, H_ = slices[key]
        # atlas guarda cada fatia no TOPO (linha 0); o sampler do raster usa
        # v invertido (ti = (1-v)*H_), então v=1 tem que cair na linha 0
        # e v=0 na última linha da própria fatia (h-1), não da folha toda.
        new_uvs.append([((x0 + u * w) / W_, 1 - (1 - v) * h / H_) for u, v in uv])
    S.uvs = new_uvs

def add_decal(S, cx, cz, y, largura, altura, key, normal_neg_y=True):
    """cola um decalque plano (single-sided) numa face do organizador.
    normal_neg_y=True -> decalque visível olhando de -y (parede da frente, y~0);
    False -> visível olhando de +y (parede do fundo, y~OD). Nesse segundo caso
    o eixo x aparece invertido aos olhos de quem olha de +y, então a textura
    precisa ser espelhada horizontalmente para o texto sair legível."""
    x0, x1 = cx - largura / 2, cx + largura / 2
    z0, z1 = cz - altura / 2, cz + altura / 2
    pts = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)] if normal_neg_y else [(1, 0), (0, 0), (0, 1), (1, 1)]
    p0, p1, p2 = (np.array(p, float) for p in pts[:3])
    n = np.cross(p1 - p0, p2 - p0)
    alvo = np.array([0.0, -1.0, 0.0]) if normal_neg_y else np.array([0.0, 1.0, 0.0])
    if np.dot(n, alvo) < 0:
        pts, uvs = pts[::-1], uvs[::-1]
    mid = S.cmap.setdefault(key, len(S.cmap))
    for tri_idx in ((0, 1, 2), (0, 2, 3)):
        S.tris.append([np.array(pts[i], float) for i in tri_idx])
        S.cols.append(np.array([1.0, 1.0, 1.0]))
        S.mids.append(mid)
        S.tex.append(True)
        S.uvs.append([uvs[i] for i in tri_idx])

# ---------------------------------------------------------------------
# montagem do produto (organizador + display/placa + módulos encadeados)
# ---------------------------------------------------------------------
MESH = {}
def mesh(key, fn):
    if key not in MESH:
        MESH[key] = to_mesh(fn())
    return MESH[key]

def add_produto(S, cor_hex, modulos=(), com_decal=False, mod_color=None):
    cor = hexc(cor_hex)
    add_mesh(S, mesh('org', organizer_v2), cor, 'org')
    add_mesh(S, mesh('base', base), cor, 'base')
    Tp = mesh('plate', plate)
    Tw = np.array([[plate_world(v) for v in t] for t in Tp])
    mid = S.cmap.setdefault('plate', len(S.cmap))
    f = plate_tex_uv()
    for tp, tw in zip(Tp, Tw):
        uv = f(tp)
        S.tris.append([np.array(v) for v in tw]); S.cols.append(hexc('#242428')); S.mids.append(mid)
        S.tex.append(uv is not None); S.uvs.append(uv if uv is not None else [(0, 0)] * 3)

    x = 0.0
    for fn, w in modulos:
        Tm = to_mesh(fn())
        x -= w
        add_mesh(S, Tm + np.array((x, 0.0, 0.0)), mod_color if mod_color is not None else cor, f'mod{len(S.cmap)}')

    if com_decal:
        add_decal(S, 114, 32, -0.05, 150, 30, 'frente', normal_neg_y=True)
        add_decal(S, 114, 46, OD + 0.05, 150, 56, 'fundo', normal_neg_y=False)
    return x  # borda esquerda da fila de módulos (para enquadrar a cena)

def plate_tex_uv():
    def f(t_print):
        if all(abs(v[2] - (PT - REC_D)) < 1e-6 for v in t_print) and \
           all(-REC_W/2 - 1e-6 <= v[0] <= REC_W/2 + 1e-6 and REC_Z - 1e-6 <= v[1] <= REC_Z + REC_H + 1e-6 for v in t_print):
            return [((v[0] + REC_W/2) / REC_W, (v[1] - REC_Z) / REC_H) for v in t_print]
        return None
    return f

MODULOS_PADRAO = [
    (lambda: module_compartimentos(2), m1_width(2)),
    (module_celular, M2_W),
    (module_bisnaga_3, module_bisnaga_grid(3, 1)[1]),
]

# ---------------------------------------------------------------------
# cenário: balcão de bar visto em isometria
# ---------------------------------------------------------------------
def balcao(S, x0, x1, y0, y1, z_top=-2.0, espessura=18.0):
    S.box(x0, y0, z_top - espessura, x1, y1, z_top, WOOD)
    S.box(x0, y0, z_top - espessura - 1.2, x1, y1, z_top - espessura, WOOD2)
    S.box(x0, y0 - 0.6, z_top - 1.6, x1, y0, z_top, STEEL)   # friso metálico na borda frontal

def porta_copo(S, cx, cy, r=17.0, z_top=-2.0):
    S.disc((cx, cy, z_top), (0, 0, 1), r, 0.6, hexc('#e9e4d6'))

def guardanapo_dobrado(S, cx, cy, ang=18, z_top=-2.0):
    a = math.radians(ang); w, h = 30.0, 30.0
    corners = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
    def rot(p): return (cx + p[0]*math.cos(a) - p[1]*math.sin(a), cy + p[0]*math.sin(a) + p[1]*math.cos(a))
    poly = [rot(p) for p in corners]
    S._add_faces([[(*p, z_top) for p in poly]], hexc('#f7f4ec'))
    diag = [poly[0], poly[2]]
    tri = [poly[0], poly[1], poly[2]]
    S._add_faces([[(*p, z_top + 0.4) for p in tri]], hexc('#efe9db'))

# ---------------------------------------------------------------------
# cenas de catálogo
# ---------------------------------------------------------------------
def cena_hero(cor_hex='marca'):
    S = Scene(); S.cmap = {}
    xmin = add_produto(S, CORES[cor_hex], MODULOS_PADRAO, com_decal=True)
    balcao(S, xmin - 70, 345, -80, 200, z_top=-2.0, espessura=24.0)
    porta_copo(S, xmin - 32, 30, r=19)
    porta_copo(S, xmin - 32, 150, r=19)
    porta_copo(S, 330, 40, r=19)
    guardanapo_dobrado(S, 328, 158, ang=-16)

    atlas, slices = montar_atlas({
        'plate': sticker_texture(),
        'frente': decal_frente(),
        'fundo': decal_fundo(),
    })
    remapear_uvs(S, slices)
    return S, atlas

def cena_produto_estudio(cor_hex='marca', modulos=MODULOS_PADRAO, com_decal=True):
    """produto sozinho, sem cenário (fundo transparente/branco) — 'packshot'."""
    S = Scene(); S.cmap = {}
    add_produto(S, CORES[cor_hex], modulos, com_decal=com_decal)
    if com_decal:
        atlas, slices = montar_atlas({
            'plate': sticker_texture(), 'frente': decal_frente(), 'fundo': decal_fundo(),
        })
        remapear_uvs(S, slices)
        return S, atlas
    atlas, slices = montar_atlas({'plate': sticker_texture()})
    remapear_uvs(S, slices)
    return S, atlas

def cena_modulo(fn, color=C_MOD):
    S = Scene(); S.cmap = {}
    add_mesh(S, to_mesh(fn()), color, 'm')
    return S

# ---------------------------------------------------------------------
# fundo branco/estúdio: raster.render devolve fundo branco por padrão (img=ones),
# então basta compor com leve sombra elíptica sob a peça para dar chão.
# ---------------------------------------------------------------------
def com_sombra(im, largura_frac=0.62, altura_px=26, y_offset_frac=0.03):
    im = im.convert('RGB')
    w, h = im.size
    sombra = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(sombra)
    sw = int(w * largura_frac)
    cx, cy = w // 2, int(h * (1 - y_offset_frac)) - altura_px // 2
    d.ellipse([cx - sw//2, cy - altura_px//2, cx + sw//2, cy + altura_px//2], fill=(20, 20, 24, 70))
    sombra = sombra.filter(__import__('PIL.ImageFilter', fromlist=['GaussianBlur']).GaussianBlur(10))
    base = Image.new('RGB', (w, h), 'white')
    base.paste(im, (0, 0))
    out = Image.alpha_composite(base.convert('RGBA'), sombra)
    return out.convert('RGB')

# ---------------------------------------------------------------------
def salvar(im, nome):
    path = os.path.join(OUT, nome)
    im.save(path)
    print('  ', nome, im.size)

def main():
    print('Render 1/4: hero (balcão de bar, módulos completos, marca demo)')
    S, atlas = cena_hero('marca')
    im = raster.render(S, (1, -1, 0.6), (1, 1, 0), s=5.6, tex=atlas, pad=60)
    salvar(im, 'hero_balcao.png')

    S2, atlas2 = cena_hero('marca')
    im2 = raster.render(S2, (-1, -1, 0.55), (1, -1, 0), s=5.6, tex=atlas2, pad=60)
    salvar(im2, 'hero_balcao_alt.png')

    S2b, atlas2b = cena_produto_estudio('marca', MODULOS_PADRAO, com_decal=True)
    im2b = raster.render(S2b, (-1, 1, 0.8), (-1, -1, 0), s=6.6, tex=atlas2b, pad=40)
    salvar(com_sombra(im2b), 'verso_mesa_logo.png')

    print('Render 2/4: packshots de produto (estúdio, com marca)')
    for cor in ('marca', 'preto', 'vermelho'):
        S3, atlas3 = cena_produto_estudio(cor, MODULOS_PADRAO, com_decal=(cor == 'marca'))
        im3 = raster.render(S3, (1, -1, 0.85), (1, 1, 0), s=7.5, tex=atlas3, pad=40)
        salvar(com_sombra(im3), f'packshot_{cor}.png')

    print('Render 3/4: módulos isolados (spec sheet)')
    jobs = [
        ('modulo_compartimentos_1', lambda: module_compartimentos(1)),
        ('modulo_compartimentos_2', lambda: module_compartimentos(2)),
        ('modulo_compartimentos_3', lambda: module_compartimentos(3)),
        ('modulo_celular', module_celular),
        ('modulo_bisnaga_3', module_bisnaga_3),
        ('modulo_bisnaga_6', module_bisnaga_6),
    ]
    for nome, fn in jobs:
        Sm = cena_modulo(fn)
        im = raster.render(Sm, (1, -1, 0.9), (1, 1, 0), s=9.5, pad=30)
        salvar(com_sombra(im, largura_frac=0.5, altura_px=16), f'{nome}.png')

    print('Render 4/4: paleta de cores (produto base, sem módulos)')
    for nome, hexcor in CORES.items():
        S4, atlas4 = cena_produto_estudio(nome, modulos=(), com_decal=False)
        im4 = raster.render(S4, (1, -1, 0.85), (1, 1, 0), s=7.0, tex=atlas4, pad=30)
        salvar(com_sombra(im4, largura_frac=0.55, altura_px=18), f'cor_{nome}.png')

    print('\nOK — assets em', OUT)

if __name__ == '__main__':
    main()
