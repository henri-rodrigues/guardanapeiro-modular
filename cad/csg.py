"""CSG por árvore BSP (porte do csg.js). Sólidos = listas de polígonos convexos."""
import sys, math
sys.setrecursionlimit(1_000_000)
EPS = 1e-5

def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def lerp(a, b, t): return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t)

class Plane:
    __slots__ = ('n', 'w')
    def __init__(self, n, w): self.n, self.w = n, w
    @staticmethod
    def from_points(a, b, c):
        n = cross(sub(b, a), sub(c, a)); l = math.sqrt(dot(n, n))
        n = (n[0]/l, n[1]/l, n[2]/l)
        return Plane(n, dot(n, a))
    def flipped(self): return Plane((-self.n[0], -self.n[1], -self.n[2]), -self.w)
    def split(self, poly, cf, cb, f, b):
        types = []; pt = 0
        for v in poly.v:
            t = dot(self.n, v) - self.w
            ty = 2 if t < -EPS else (1 if t > EPS else 0)
            pt |= ty; types.append(ty)
        if pt == 0:
            (cf if dot(self.n, poly.p.n) > 0 else cb).append(poly)
        elif pt == 1: f.append(poly)
        elif pt == 2: b.append(poly)
        else:
            fv, bv = [], []; n = len(poly.v)
            for i in range(n):
                j = (i + 1) % n
                ti, tj = types[i], types[j]; vi, vj = poly.v[i], poly.v[j]
                if ti != 2: fv.append(vi)
                if ti != 1: bv.append(vi)
                if (ti | tj) == 3:
                    t = (self.w - dot(self.n, vi)) / dot(self.n, sub(vj, vi))
                    v = lerp(vi, vj, t); fv.append(v); bv.append(v)
            if len(fv) >= 3: f.append(Polygon(fv, poly.p))
            if len(bv) >= 3: b.append(Polygon(bv, poly.p))

class Polygon:
    __slots__ = ('v', 'p')
    def __init__(self, v, p=None):
        self.v = v
        self.p = p or Plane.from_points(v[0], v[1], v[2])
    def flipped(self): return Polygon(self.v[::-1], self.p.flipped())

class Node:
    __slots__ = ('plane', 'front', 'back', 'polys')
    def __init__(self, polys=None):
        self.plane = None; self.front = None; self.back = None; self.polys = []
        if polys: self.build(polys)
    def invert(self):
        stack = [self]
        while stack:
            nd = stack.pop()
            nd.polys = [p.flipped() for p in nd.polys]
            if nd.plane: nd.plane = nd.plane.flipped()
            nd.front, nd.back = nd.back, nd.front
            if nd.front: stack.append(nd.front)
            if nd.back: stack.append(nd.back)
    def clip_polygons(self, polys):
        if not self.plane: return list(polys)
        f, b = [], []
        for p in polys: self.plane.split(p, f, b, f, b)
        f = self.front.clip_polygons(f) if self.front else f
        b = self.back.clip_polygons(b) if self.back else []
        return f + b
    def clip_to(self, bsp):
        stack = [self]
        while stack:
            nd = stack.pop()
            nd.polys = bsp.clip_polygons(nd.polys)
            if nd.front: stack.append(nd.front)
            if nd.back: stack.append(nd.back)
    def all_polygons(self):
        out = []; stack = [self]
        while stack:
            nd = stack.pop(); out.extend(nd.polys)
            if nd.front: stack.append(nd.front)
            if nd.back: stack.append(nd.back)
        return out
    def build(self, polys):
        work = [(self, polys)]
        while work:
            nd, ps = work.pop()
            if not ps: continue
            if not nd.plane: nd.plane = ps[0].p
            f, b = [], []
            for p in ps: nd.plane.split(p, nd.polys, nd.polys, f, b)
            if f:
                if not nd.front: nd.front = Node()
                work.append((nd.front, f))
            if b:
                if not nd.back: nd.back = Node()
                work.append((nd.back, b))

def union(A, B):
    a, b = Node(A), Node(B)
    a.clip_to(b); b.clip_to(a); b.invert(); b.clip_to(a); b.invert()
    a.build(b.all_polygons()); return a.all_polygons()

def subtract(A, B):
    a, b = Node(A), Node(B)
    a.invert(); a.clip_to(b); b.clip_to(a); b.invert(); b.clip_to(a); b.invert()
    a.build(b.all_polygons()); a.invert(); return a.all_polygons()

# ---------------- primitivas (sólidos convexos) ----------------
def convex_solid(faces):
    """faces: listas de vértices; orienta todas para fora do centróide"""
    pts = [v for f in faces for v in f]
    cen = tuple(sum(p[i] for p in pts) / len(pts) for i in range(3))
    out = []
    for f in faces:
        p = Polygon(list(f))
        fc = tuple(sum(v[i] for v in f) / len(f) for i in range(3))
        if dot(p.p.n, sub(fc, cen)) < 0: p = p.flipped()
        out.append(p)
    return out

def box(x0, y0, z0, x1, y1, z1):
    c = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    idx = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return convex_solid([[c[i] for i in f] for f in idx])

def prism(poly2d, axis, a0, a1):
    """extrusão de polígono convexo. axis 'x': poly em (y,z); 'y': (x,z); 'z': (x,y)"""
    def P(u, v, a):
        if axis == 'x': return (a, u, v)
        if axis == 'y': return (u, a, v)
        return (u, v, a)
    A = [P(u, v, a0) for u, v in poly2d]; B = [P(u, v, a1) for u, v in poly2d]
    n = len(A)
    faces = [A, B[::-1]] + [[A[i], A[(i+1) % n], B[(i+1) % n], B[i]] for i in range(n)]
    return convex_solid(faces)

def union_all(solids):
    acc = solids[0]
    for s in solids[1:]: acc = union(acc, s)
    return acc

# ---------------- malha ----------------
def to_mesh(polys, weld=1e-4):
    """triangula (com vértice central, sem T-junctions) e solda vértices"""
    import numpy as np
    from scipy.spatial import cKDTree
    allv = np.array([v for p in polys for v in p.v])
    tree = cKDTree(allv)
    parent = list(range(len(allv)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i, j in tree.query_pairs(5e-4):
        ri, rj = find(i), find(j)
        if ri != rj: parent[max(ri, rj)] = min(ri, rj)
    canon = {}
    k = 0
    snapped = []
    for p in polys:
        nv = []
        for v in p.v:
            nv.append(tuple(allv[find(k)])); k += 1
        snapped.append(Polygon(nv, p.p))
    polys = snapped
    key = lambda v: v
    V = np.unique(np.array([v for p in polys for v in p.v]), axis=0)
    tris = []
    for p in polys:
        ring = [p.v[0]]
        for i in range(len(p.v)):
            a, b = p.v[i], p.v[(i + 1) % len(p.v)]
            # vértices da malha sobre a aresta a-b (corrige T-junctions)
            A = np.array(a); B = np.array(b); d = B - A; L2 = d @ d
            if L2 < 1e-12: continue
            t = (V - A) @ d / L2
            q = A + np.outer(t, d)
            dist = np.linalg.norm(V - q, axis=1)
            m = (dist < 5e-4) & (t > 1e-6) & (t < 1 - 1e-6)
            inner = sorted([(t[k], tuple(V[k])) for k in np.nonzero(m)[0]])
            if i > 0: ring.append(a)
            ring.extend(tuple(float(c) for c in v) for _, v in inner)
        # remover duplicados consecutivos
        rr = []
        for v in ring:
            if not rr or key(v) != key(rr[-1]): rr.append(v)
        if len(rr) > 1 and key(rr[0]) == key(rr[-1]): rr.pop()
        if len(rr) < 3: continue
        if len(rr) == 3:
            tris.append(rr); continue
        cen = tuple(sum(v[k] for v in rr) / len(rr) for k in range(3))
        for i in range(len(rr)):
            tris.append([cen, rr[i], rr[(i + 1) % len(rr)]])
    T = np.array(tris, float)
    # descartar triângulos degenerados
    ar = np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1)
    return T[ar > 1e-9]

def check_mesh(T, weld=1e-4):
    import numpy as np
    from collections import Counter
    kv = lambda v: (float(v[0]), float(v[1]), float(v[2]))
    E = Counter()
    for t in T:
        k = [kv(v) for v in t]
        for i in range(3):
            E[(k[i], k[(i + 1) % 3])] += 1
    bad = 0
    for (a, b), n in E.items():
        if E.get((b, a), 0) != n or n != 1: bad += 1
    vol = float(np.sum(np.einsum('ij,ij->i', T[:, 0], np.cross(T[:, 1], T[:, 2]))) / 6)
    return dict(triangles=len(T), bad_edges=bad, volume_mm3=vol,
                bbox=(T.reshape(-1, 3).min(0).round(3).tolist(), T.reshape(-1, 3).max(0).round(3).tolist()))

def write_stl(T, path, name='part'):
    import numpy as np, struct
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    data = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    data['n'] = n; data['v'] = T
    with open(path, 'wb') as f:
        f.write(name.encode()[:80].ljust(80, b' '))
        f.write(struct.pack('<I', len(T)))
        f.write(data.tobytes())

def loft_x(profile, cy, cz, n=24):
    """Sólido de revolução ao longo do eixo x. profile: lista [(x, r), ...] em ordem.
    Fecha as pontas automaticamente se o primeiro/último raio for > 0."""
    rings = [[(x, cy + r * math.cos(2*math.pi*i/n), cz + r * math.sin(2*math.pi*i/n)) for i in range(n)]
             for x, r in profile]
    polys = []
    for k in range(len(profile) - 1):
        a, b = rings[k], rings[k+1]
        for i in range(n):
            j = (i + 1) % n
            polys.append(Polygon([a[i], a[j], b[j], b[i]]))
    if profile[0][1] > 1e-6:
        polys.append(Polygon(list(reversed(rings[0]))))
    if profile[-1][1] > 1e-6:
        polys.append(Polygon(rings[-1]))
    return polys
