"""Verifica o encaixe dos módulos: na posição final montada a interferência
deve ser 0 mm3 (a pressão do botão existe só durante a inserção).
Uso:  python check_modules.py
"""
from parts import *
from csg import subtract as sub_

def vol(P):
    if not P: return 0.0
    return check_mesh(to_mesh(P))['volume_mm3']

def intersect(A, B):
    return sub_(A, sub_(A, B))

def shift(P, dx):
    return [Polygon([(v[0] + dx, v[1], v[2]) for v in p.v]) for p in P]

MODULOS = [
    ('compartimentos x1', lambda: module_compartimentos(1), m1_width(1)),
    ('compartimentos x2', lambda: module_compartimentos(2), m1_width(2)),
    ('compartimentos x3', lambda: module_compartimentos(3), m1_width(3)),
    ('suporte celular',   module_celular,                   M2_W),
    ('porta-bisnaga 3',   module_bisnaga_3,                 module_bisnaga_grid(3, 1)[1]),
    ('porta-bisnaga 6',   module_bisnaga_6,                 module_bisnaga_grid(3, 2)[1]),
]

O = organizer_v2()
feitos = []
for nome, fn, w in MODULOS:
    M = fn()
    Mw = shift(M, -w)                    # face de encaixe (x=w) encosta no organizador (x=0)
    v = vol(intersect(O, Mw))
    print(f'{nome:20s} largura {w:7.2f}  org n modulo = {v:8.3f} mm3')
    feitos.append((nome, M, w))

# encadeamento: a saída de um módulo encaixa na entrada do seguinte
(_, A, wa), (_, B, wb) = feitos[0], feitos[3]
print('\ncompartimentos x1 -> celular (encadeados) =',
      round(vol(intersect(shift(A, -wa), shift(B, -wa - wb))), 3), 'mm3')
