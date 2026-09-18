import numpy as np
from parts import *
from views import add_mesh, raster, Scene, sticker_texture, C_ORG, C_BASE, C_PL, hexc
from assemble import transform, plate_world

C_M1 = hexc('#3a5a78'); C_M2 = hexc('#3a6b4a'); C_M3 = hexc('#7a4a2e')

def shift(T, dx, dy=0.0, dz=0.0):
    return T + np.array((dx, dy, dz))

MESH = {}
def m(name, fn):
    if name not in MESH: MESH[name] = to_mesh(fn())
    return MESH[name]

def full_scene(module_fn=None, mod_w=0.0, mod_color=None, explode_mod=0.0):
    S = Scene(); S.cmap = {}
    add_mesh(S, m('org', organizer_v2), C_ORG, 'org')
    add_mesh(S, m('base', base), C_BASE, 'base')
    tex = sticker_texture()
    Tp = m('plate', plate)
    Tw = np.array([[plate_world(v) for v in t] for t in Tp])
    from views import add_mesh_uv
    add_mesh_uv(S, Tp, Tw, C_PL, 'plate')
    if module_fn:
        Tm = to_mesh(module_fn())
        add_mesh(S, shift(Tm, -mod_w - explode_mod), mod_color, 'mod')
    return S, tex

def module_alone_scene(fn, color):
    S = Scene(); S.cmap = {}
    add_mesh(S, to_mesh(fn()), color, 'm')
    return S

if __name__ == '__main__':
    jobs = [('compartimentos', module_compartimentos, M1_W, C_M1),
            ('celular', module_celular, M2_W, C_M2),
            ('bisnaga', module_bisnaga, M3_W, C_M3)]
    for name, fn, w, col in jobs:
        Sa = module_alone_scene(fn, col)
        raster.render(Sa, (1, -1, 1), (1, 1, 0), s=10).save(f'mod_{name}_alone.png')
        Sm, tex = full_scene(fn, w, col)
        raster.render(Sm, (1, -1, 1), (1, 1, 0), s=6, tex=tex).save(f'mod_{name}_full.png')
        Sm2, tex2 = full_scene(fn, w, col, explode_mod=40.0)
        raster.render(Sm2, (1, -1, 1), (1, 1, 0), s=6, tex=tex2).save(f'mod_{name}_exp.png')
    print('ok')
