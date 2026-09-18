import math
import numpy as np
from PIL import Image
class Scene:
    def __init__(self):
        self.tris, self.cols, self.mids, self.tex, self.uvs, self.cmap = [], [], [], [], [], {}
    def _add_faces(self, faces, color, uvfaces=None):
        V = np.array([v for f in faces for v in f]); cen = V.mean(0)
        mid = self.cmap.setdefault(tuple(np.round(color, 3)), len(self.cmap))
        for fi, f in enumerate(faces):
            f = [np.array(v, float) for v in f]
            n = np.cross(f[1] - f[0], f[2] - f[0])
            flip = np.dot(n, np.mean(f, 0) - cen) < 0
            uv = uvfaces[fi] if uvfaces and uvfaces[fi] is not None else None
            for k in range(1, len(f) - 1):
                tri = [f[0], f[k], f[k + 1]]
                tuv = None if uv is None else [uv[0], uv[k], uv[k + 1]]
                if flip:
                    tri = tri[::-1]; tuv = None if tuv is None else tuv[::-1]
                self.tris.append(tri); self.cols.append(color); self.mids.append(mid)
                self.tex.append(tuv is not None); self.uvs.append(tuv if tuv is not None else [(0, 0)] * 3)
    def box(self, x0, y0, z0, x1, y1, z1, color, xf=None, tex_front=False):
        L = lambda x, y, z: (x, y, z) if xf is None else xf(x, y, z)
        c = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
        idx = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        uvf = None
        if tex_front:
            uvf = [None] * 6
            uvf[2] = [((c[i][0] - x0) / (x1 - x0), (c[i][2] - z0) / (z1 - z0)) for i in idx[2]]
        self._add_faces([[L(*c[i]) for i in f] for f in idx], color, uvf)
    def prism_x(self, poly, x0, x1, color):
        a = [(x0, y, z) for y, z in poly]; b = [(x1, y, z) for y, z in poly]
        self._add_faces([a, b] + [[a[i], a[(i+1) % len(a)], b[(i+1) % len(a)], b[i]] for i in range(len(a))], color)
    def disc(self, center, n, r, h, color, seg=24):
        """disco saindo da face: centro na face, normal n (unitária), altura h"""
        c = np.array(center, float); n = np.array(n, float); n /= np.linalg.norm(n)
        a = np.cross(n, [0, 0, 1]) if abs(n[2]) < 0.9 else np.cross(n, [1, 0, 0])
        a /= np.linalg.norm(a); b = np.cross(n, a)
        ring = [c + r * (math.cos(2*math.pi*i/seg) * a + math.sin(2*math.pi*i/seg) * b) for i in range(seg)]
        top = [p + h * n for p in ring]; bot = [p - 0.01 * n for p in ring]
        faces = [bot, top] + [[bot[i], bot[(i+1) % seg], top[(i+1) % seg], top[i]] for i in range(seg)]
        self._add_faces(faces, color)

def render(S, d, r, s=7.0, tex=None, pad=30):
    d = np.array(d, float); d /= np.linalg.norm(d)
    r = np.array(r, float); r /= np.linalg.norm(r)
    u = np.cross(d, r); u /= np.linalg.norm(u)
    P = np.array(S.tris); C = np.array(S.cols); M = np.array(S.mids)
    TX = np.array(S.tex); UV = np.array(S.uvs, float)
    N = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    vis = N @ d > 1e-6
    P, C, M, TX, UV, N = P[vis], C[vis], M[vis], TX[vis], UV[vis], N[vis]
    X, Y, Z = P @ r, P @ u, P @ d
    minx, maxx, miny, maxy = X.min(), X.max(), Y.min(), Y.max()
    W = int((maxx - minx) * s) + 2 * pad; H = int((maxy - miny) * s) + 2 * pad
    SX = (X - minx) * s + pad; SY = (maxy - Y) * s + pad
    zb = np.full((H, W), -np.inf); img = np.ones((H, W, 3))
    nb = np.zeros((H, W, 3)); mb = np.full((H, W), -1)
    L = np.array([-0.35, -0.55, 1.0]); L /= np.linalg.norm(L)
    shade = 0.66 + 0.34 * np.clip(N @ L, 0, 1)
    if tex is not None: th, tw, _ = tex.shape
    for i in range(len(P)):
        x0, x1 = int(max(SX[i].min(), 0)), int(min(SX[i].max() + 1, W))
        y0, y1 = int(max(SY[i].min(), 0)), int(min(SY[i].max() + 1, H))
        if x1 <= x0 or y1 <= y0: continue
        px, py = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        (ax, bx, cx), (ay, by, cy) = SX[i], SY[i]
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9: continue
        w0 = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / den
        w1 = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / den
        w2 = 1 - w0 - w1; e = -2e-3
        ins = (w0 >= e) & (w1 >= e) & (w2 >= e)
        if not ins.any(): continue
        z = w0 * Z[i, 0] + w1 * Z[i, 1] + w2 * Z[i, 2]
        reg = zb[y0:y1, x0:x1]; up = ins & (z > reg)
        if not up.any(): continue
        reg[up] = z[up]
        if TX[i] and tex is not None:
            uu = w0 * UV[i, 0, 0] + w1 * UV[i, 1, 0] + w2 * UV[i, 2, 0]
            vv = w0 * UV[i, 0, 1] + w1 * UV[i, 1, 1] + w2 * UV[i, 2, 1]
            ti = np.clip(((1 - vv) * th).astype(int), 0, th - 1)
            tj = np.clip((uu * tw).astype(int), 0, tw - 1)
            img[y0:y1, x0:x1][up] = (tex[ti, tj] * (0.75 + 0.25 * shade[i]))[up]
        else:
            img[y0:y1, x0:x1][up] = C[i] * shade[i]
        nb[y0:y1, x0:x1][up] = N[i]; mb[y0:y1, x0:x1][up] = M[i]
    edge = np.zeros((H, W), bool)
    zz = np.where(np.isfinite(zb), zb, -1e6)
    for ax_ in (0, 1):
        e_ = (np.linalg.norm(np.diff(nb, axis=ax_), axis=2) > 0.15) | (np.diff(mb, axis=ax_) != 0) | \
             (np.abs(np.diff(zz, axis=ax_)) > 2.5)
        if ax_ == 0: edge[1:, :] |= e_; edge[:-1, :] |= e_
        else: edge[:, 1:] |= e_; edge[:, :-1] |= e_
    lum = img.mean(2)
    ec = np.where(lum[..., None] < 0.35, np.array([0.62, 0.62, 0.66]), np.array([0.12, 0.12, 0.14]))
    img = np.where(edge[..., None], ec, img)
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    return im.resize((W // 2, H // 2), Image.LANCZOS)

