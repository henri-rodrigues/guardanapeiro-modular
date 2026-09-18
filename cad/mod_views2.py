import numpy as np
from parts import *
from views import add_mesh, add_mesh_uv, raster, Scene, sticker_texture, C_ORG, C_BASE, C_PL, hexc
from assemble import plate_world

C_M1 = hexc('#3a5a78'); C_M2 = hexc('#3a6b4a'); C_M3 = hexc('#7a4a2e')
def shift(T, dx): return T + np.array((dx, 0, 0))

M = {}
def mesh(k, fn):
    if k not in M: M[k] = to_mesh(fn())
    return M[k]

def base_scene():
    S = Scene(); S.cmap = {}
    add_mesh(S, mesh('org', organizer_v2), C_ORG, 'org')
    add_mesh(S, mesh('base', base), C_BASE, 'base')
    Tp = mesh('plate', plate)
    add_mesh_uv(S, Tp, np.array([[plate_world(v) for v in t] for t in Tp]), C_PL, 'plate')
    return S

def alone(fn, color, s=9):
    S = Scene(); S.cmap = {}
    add_mesh(S, to_mesh(fn()), color, 'm')
    return S

if __name__ == '__main__':
    tex = sticker_texture()
    for name, fn, w in (('bisnaga3', module_bisnaga_3, 165.0), ('bisnaga6', module_bisnaga_6, 165.0)):
        S = base_scene()
        add_mesh(S, shift(to_mesh(fn()), -w), C_M3, 'mod')
        raster.render(S, (-1, -1, 1), (1, -1, 0), s=5, tex=tex).save(f'v3_{name}_full.png')
        raster.render(alone(fn, C_M3), (1, -1, 1), (1, 1, 0), s=8).save(f'v3_{name}_alone.png')
    # botão: detalhe macho/fêmea
    S = Scene(); S.cmap = {}
    add_mesh(S, to_mesh(test_button_male()), C_ORG, 'a')
    add_mesh(S, shift(to_mesh(test_button_female()), 26), C_M1, 'b')
    raster.render(S, (1, -1, 0.8), (1, 1, 0), s=9).save('v3_botao_teste.png')
    # organizador sozinho, mostrando como fica discreto sem módulo
    raster.render(alone(organizer_v2, C_ORG, s=6), (-1, -1, 0.9), (1, -1, 0), s=6).save('v3_org_sem_modulo.png')
    print('ok')
