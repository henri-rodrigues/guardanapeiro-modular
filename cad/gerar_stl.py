"""Regera todos os STL de produção em ../stl/ e valida cada malha.
Uso:  python gerar_stl.py
"""
import os
from parts import *

SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stl')
os.makedirs(SAIDA, exist_ok=True)

PECAS = [
    ('organizador_botoes', organizer_v2),
    ('base_display_botoes', base),
    ('placa_cardapio', plate),
    ('modulo_compartimentos_1', lambda: module_compartimentos(1)),
    ('modulo_compartimentos_2', lambda: module_compartimentos(2)),
    ('modulo_compartimentos_3', lambda: module_compartimentos(3)),
    ('modulo_suporte_celular', module_celular),
    ('modulo_porta_bisnaga_3', module_bisnaga_3),
    ('modulo_porta_bisnaga_6', module_bisnaga_6),
    ('teste_botao_macho', test_button_male),
    ('teste_botao_femea', test_button_female),
]

falhas = []
for nome, fn in PECAS:
    T = to_mesh(fn())
    T = T - T.reshape(-1, 3).min(0)          # canto na origem, apoiada em z=0
    info = check_mesh(T)
    ok = info['bad_edges'] == 0
    if not ok:
        falhas.append(nome)
    write_stl(T, os.path.join(SAIDA, nome + '.stl'), nome)
    dims = T.reshape(-1, 3).max(0).round(1)
    print(f"{'OK ' if ok else 'ERRO'} {nome:32s} {dims}  {info['volume_mm3']/1000:7.1f} cm3")

print('\nTodas as malhas fechadas.' if not falhas else f'\nMALHAS COM PROBLEMA: {falhas}')
