from parts import *
def transform(polys, f):
    return [Polygon([f(v) for v in p.v]) for p in polys]
def plate_world(v):
    x, y, z = v
    ly, lz = PT/2 - z, y
    yy, zz = pw_(ly, lz)
    return (PXC + x, yy, zz)
def intersect(A, B):
    return subtract(A, subtract(A, B))
def vol(P):
    import numpy as np
    if not P: return 0.0
    T = to_mesh(P); return check_mesh(T)['volume_mm3']
if __name__ == '__main__':
    O, B, PL = organizer(), base(), transform(plate(), plate_world)
    print('org∩base', vol(intersect(O, B)))
    print('base∩placa', vol(intersect(B, PL)))
    print('org∩placa', vol(intersect(O, PL)))
    T = to_mesh(PL); print('placa montada bbox', check_mesh(T)['bbox'])
