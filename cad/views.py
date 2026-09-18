import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import raster
from raster import Scene
from parts import *
from assemble import transform, plate_world

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def hexc(h): h = h.lstrip('#'); return np.array([int(h[i:i+2], 16)/255 for i in (0, 2, 4)])
C_ORG = hexc('#34343a'); C_BASE = hexc('#3d3d44'); C_PL = hexc('#2e2e33')

# QR ilustrativo (vai no adesivo)
rng = random.Random(7); NQ = 25
QR = [[rng.random() < 0.5 for _ in range(NQ)] for _ in range(NQ)]
for R, C in ((0, 0), (0, NQ-7), (NQ-7, 0)):
    for r in range(-1, 8):
        for cc in range(-1, 8):
            rr, c2 = R+r, C+cc
            if 0 <= rr < NQ and 0 <= c2 < NQ:
                ins = 0 <= r <= 6 and 0 <= cc <= 6
                QR[rr][c2] = ins and (r in (0, 6) or cc in (0, 6) or (2 <= r <= 4 and 2 <= cc <= 4))
# layout do adesivo no referencial da placa (lx, lz)
LAYOUT = dict(t1=(123, 11), t2=(109.5, 10), qr=(50, 100), l1=(24.5, 4.6), l2=(18.5, 4.6), icon=(31, 44))

def sticker_texture(k=10):
    W_, H_ = int(REC_W*k), int(REC_H*k)
    im = Image.new('RGB', (W_, H_), '#141417'); d = ImageDraw.Draw(im)
    P = lambda lx, lz: ((lx + REC_W/2)*k, (REC_Z + REC_H - lz)*k)
    def t(s, lz, size): d.text(P(0, lz), s, font=ImageFont.truetype(BOLD, int(size*k)), fill='white', anchor='mm')
    t('CARDÁPIO', *LAYOUT['t1']); t('– DIGITAL –', *LAYOUT['t2'])
    t('APONTE A CÂMERA', *LAYOUT['l1']); t('DO SEU CELULAR', *LAYOUT['l2'])
    q0, q1 = LAYOUT['qr']; s_ = q1 - q0
    d.rectangle([P(-s_/2, q1), P(s_/2, q0)], fill='white')
    m = (s_ - 4) / NQ
    for r in range(NQ):
        for c in range(NQ):
            if QR[r][c]:
                x0 = -s_/2 + 2 + c*m; zt = q1 - 2 - r*m
                d.rectangle([P(x0, zt), P(x0+m, zt-m)], fill='#111')
    i0, i1 = LAYOUT['icon']
    d.rectangle([P(-4.5, i1), P(4.5, i0)], outline='white', width=int(0.7*k))
    for s2 in (-1, 1):
        for a in (-35, 0, 35):
            cx, cz = s2*9, (i0+i1)/2 + 3.5*math.sin(math.radians(a))
            dx = 1.4*math.cos(math.radians(a)); dz = 1.4*math.sin(math.radians(a))*s2
            d.line([P(cx-dx, cz-dz), P(cx+dx, cz+dz)], fill='white', width=int(0.5*k))
    return np.asarray(im).astype(float)/255

def add_mesh(S, T, color, key, tex_fn=None):
    mid = S.cmap.setdefault(key, len(S.cmap))
    for t in T:
        uv = tex_fn(t) if tex_fn else None
        S.tris.append([np.array(v) for v in t]); S.cols.append(color); S.mids.append(mid)
        S.tex.append(uv is not None); S.uvs.append(uv if uv is not None else [(0, 0)] * 3)

def plate_tex_fn(xf):
    """recebe triângulo no referencial de impressão e devolve uv se estiver no rebaixo"""
    def f(t_print):
        if all(abs(v[2] - (PT - REC_D)) < 1e-6 for v in t_print) and \
           all(-REC_W/2 - 1e-6 <= v[0] <= REC_W/2 + 1e-6 and REC_Z - 1e-6 <= v[1] <= REC_Z + REC_H + 1e-6 for v in t_print):
            return [((v[0] + REC_W/2) / REC_W, (v[1] - REC_Z) / REC_H) for v in t_print]
        return None
    return f

MESH = {}
def meshes():
    if not MESH:
        MESH['org'] = to_mesh(organizer())
        MESH['base'] = to_mesh(base())
        MESH['plate_print'] = to_mesh(plate())
    return MESH

def scene(explode=False, plate_on=True, base_on=True, org_on=True, plate_front_up=False):
    M = meshes(); S = Scene(); S.cmap = {}
    if org_on: add_mesh(S, M['org'], C_ORG, 'org')
    dx = 45.0 if explode else 0.0
    if base_on: add_mesh(S, M['base'] + np.array((dx, 0, 0)), C_BASE, 'base')
    if plate_on:
        Tp = M['plate_print']
        if explode:
            off = np.array((PXC + dx + 100, 0, 0))
            Tw = Tp + off
            add_mesh_uv(S, Tp, Tw, C_PL, 'plate')
        else:
            Tw = np.array([[plate_world(v) for v in t] for t in Tp])
            add_mesh_uv(S, Tp, Tw, C_PL, 'plate')
    return S

def add_mesh_uv(S, Tp, Tw, color, key):
    mid = S.cmap.setdefault(key, len(S.cmap)); f = plate_tex_fn(None)
    for tp, tw in zip(Tp, Tw):
        uv = f(tp)
        S.tris.append([np.array(v) for v in tw]); S.cols.append(color); S.mids.append(mid)
        S.tex.append(uv is not None); S.uvs.append(uv if uv is not None else [(0, 0)] * 3)

# render com retorno do mapeamento (para desenhar cotas em escala)
def render_map(S, d, r, s, tex=None, pad=30):
    d_ = np.array(d, float); d_ /= np.linalg.norm(d_)
    r_ = np.array(r, float); r_ /= np.linalg.norm(r_)
    u_ = np.cross(d_, r_); u_ /= np.linalg.norm(u_)
    P = np.array(S.tris); N = np.cross(P[:, 1]-P[:, 0], P[:, 2]-P[:, 0])
    vis = (N @ d_) > 1e-9
    X = P[vis] @ r_; Y = P[vis] @ u_
    im = raster.render(S, d, r, s=s, tex=tex, pad=pad)
    return im, dict(minx=X.min(), maxy=Y.max(), s=s, pad=pad)

if __name__ == '__main__':
    tex = sticker_texture()
    S = scene()
    raster.render(S, (1, -1, 1), (1, 1, 0), s=7, tex=tex).save('iso_fd.png')
    raster.render(S, (-1, -1, 1), (1, -1, 0), s=7, tex=tex).save('iso_fe.png')
    E = scene(explode=True)
    raster.render(E, (1, -1, 1), (1, 1, 0), s=6, tex=tex).save('exp_fd.png')
    E2 = scene(explode=True)
    raster.render(E2, (-1, -1, 1.1), (1, -1, 0), s=6, tex=tex).save('exp_fe.png')
    print('ok')
