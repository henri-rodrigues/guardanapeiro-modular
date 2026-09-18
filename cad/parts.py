"""Projeto V1.1 – paredes externas 3 mm, internas 1,5 mm, encaixes por pressão. mm.
x: esquerda→direita, y: frente(0)→fundo, z: cima"""
import math
from csg import *

TE, TI = 3.0, 1.5                  # parede externa / interna
# ---------------- organizador ----------------
OW, OD = 220.0, 110.0
H_FRONT, H_BACK = 60.0, 85.0
RAMP = (69.0, 81.0)
Y_DIV = 71.0                       # face frontal da divisória do guardanapo
H_DIV, H_COMP = 68.0, 54.0
N_COMP = 4
# encaixe cauda-de-andorinha (trilho no organizador, rasgo na base)
DT_ROOT, DT_TIP, DT_H = 6.0, 9.0, 4.0   # largura na raiz, na ponta, altura do trilho
DT_Z = 24.0                             # altura do trilho
DT_Y = (18.0, 52.0)                     # centros dos trilhos
CL_DT = 0.15                            # folga por lado no rasgo
# ---------------- base do display ----------------
BX0 = OW                                # base encosta no organizador
BW, BD = 92.0, 70.0
BX1 = BX0 + BW
H_LIP, H_SIDE = 16.0, 24.0
BLOCK_W = 9.0                           # bloco esquerdo com os rasgos
BLOCK_H = 38.0
# ---------------- placa ----------------
PW, PT, PH = 76.0, 8.0, 140.0
TILT = math.radians(12)
PXC = BX0 + BLOCK_W + 1.0 + PW / 2      # centro x da placa
Y0 = 10.0
Z0 = TE + PT / 2 * math.sin(TILT)
CL_PT = 0.10                            # folga por lado na espessura (pressão)
CL_PX = 0.30                            # folga nas laterais
CL_PZ = 0.30                            # folga no fundo do encaixe
CL_WEDGE = 0.10
REC_W, REC_H, REC_D, REC_Z = 68.0, 122.0, 0.4, 14.0  # rebaixo p/ adesivo

def pw_(ly, lz):
    c, s = math.cos(TILT), math.sin(TILT)
    return (Y0 + ly * c + lz * s, Z0 - ly * s + lz * c)

def comp_x():
    w = (OW - 2 * TE - (N_COMP - 1) * TI) / N_COMP
    xs = []; x = TE
    for i in range(N_COMP):
        xs.append((x, x + w)); x += w + TI
    return xs

SIDE_A = [(0, 0), (OD, 0), (OD, H_FRONT), (0, H_FRONT)]
SIDE_B = [(RAMP[0], H_FRONT), (OD, H_FRONT), (OD, H_BACK), (RAMP[1], H_BACK)]

def dovetail(yc, x_root, grow, root, tip, h):
    """trapézio no plano xy; grow=+1 cresce para +x"""
    return [(x_root, yc - root / 2), (x_root + grow * h, yc - tip / 2),
            (x_root + grow * h, yc + tip / 2), (x_root, yc + root / 2)]

def ccw(poly):
    a = sum(poly[i][0] * poly[(i+1) % len(poly)][1] - poly[(i+1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return poly if a > 0 else poly[::-1]

def organizer():
    S = [box(0, 0, 0, OW, OD, TE),
         box(0, 0, 0, OW, TE, H_FRONT),
         box(0, OD - TE, 0, OW, OD, H_BACK),
         box(TE, Y_DIV, 0, OW - TE, Y_DIV + TI, H_DIV)]
    for x0, x1 in ((0, TE), (OW - TE, OW)):
        S += [prism(SIDE_A, 'x', x0, x1), prism(SIDE_B, 'x', x0, x1)]
    for (a, b) in comp_x()[:-1]:
        S.append(box(b, TE, 0, b + TI, Y_DIV, H_COMP))
    return union_all(S)  # trilhos adicionados depois (ver rail_pair, abaixo)

def plate_slot_poly():
    c = CL_PT
    pts = [pw_(-PT/2 - c, -CL_PZ), pw_(PT/2 + c, -CL_PZ), pw_(PT/2 + c, 40), pw_(-PT/2 - c, 40)]
    return ccw(pts)

def wedge_poly():
    p0 = pw_(PT/2 + CL_WEDGE, 12.0); p1 = pw_(PT/2 + CL_WEDGE, 110.0)
    return ccw([(p0[0], TE), (BD, TE), (BD, H_LIP), (p1[0], p1[1]), (p0[0], p0[1])])

def base():
    top_back = pw_(PT/2 + CL_PT, (H_LIP - Z0) / math.cos(TILT) + 2)[0]
    YB = top_back + 3.0
    S = [box(BX0, 0, 0, BX1, BD, TE),                          # fundo
         box(BX0, 0, 0, BX1, TE, H_LIP),                       # aba frontal
         box(BX1 - TE, 0, 0, BX1, 30, H_SIDE),                 # aba direita
         box(BX0, 0, 0, BX0 + BLOCK_W, BD, BLOCK_H),           # bloco de encaixe
         box(BX0, 0, 0, BX1 - TE, YB, H_LIP),                  # bloco do encaixe da placa
         prism(wedge_poly(), 'x', PXC - 34, PXC + 34)]         # cunha de apoio
    body = union_all(S)
    cuts = socket_cuts(BX0, +1.0)                 # soquetes p/ botões do organizador
    cuts.append(prism(plate_slot_poly(), 'x', PXC - PW/2 - CL_PX, PXC + PW/2 + CL_PX))
    for cu in cuts: body = subtract(body, cu)
    return body

def plate(flat=True):
    """placa na posição de impressão: verso na mesa (z=0), frente em z=PT"""
    S = box(-PW/2, 0, 0, PW/2, PH, PT)
    rec = box(-REC_W/2, REC_Z, PT - REC_D, REC_W/2, REC_Z + REC_H, PT + 1)
    # chanfro de entrada no pé da placa (facilita o encaixe)
    ch = prism(ccw([(-0.1, -0.1), (1.0, -0.1), (-0.1, 1.0)]), 'x', -PW/2 - 1, PW/2 + 1)
    ch2 = prism(ccw([(-0.1, PT + 0.1), (-0.1, PT - 1.0), (1.0, PT + 0.1)]), 'x', -PW/2 - 1, PW/2 + 1)
    return subtract(subtract(subtract(S, rec), ch), ch2)

# ---------------- peças de teste de tolerância ----------------
TEST_CL = (0.10, 0.15, 0.20)
K_DT = (DT_TIP - DT_ROOT) / 2 / DT_H

def test_female():
    """3 rasgos cauda-de-andorinha + 3 fendas de placa, folgas 0,10 / 0,15 / 0,20.
    Marcas no topo: 1, 2 e 3 entalhes."""
    body = box(0, 0, 0, 90, 30, 14)
    for i, c in enumerate(TEST_CL):
        xc = 15 + 30 * i
        hw = lambda d: DT_ROOT / 2 + K_DT * d + c
        de = DT_H + c
        sl = [(xc - hw(-1), -1), (xc + hw(-1), -1), (xc + hw(de), de), (xc - hw(de), de)]
        body = subtract(body, prism(ccw(sl), 'z', -1, 15))
        body = subtract(body, box(xc - 11, 14 - c, 4, xc + 11, 14 + PT + c, 15))
        for m in range(i + 1):
            x0 = xc - 4 + m * 3
            body = subtract(body, box(x0, 27, 12, x0 + 1.5, 31, 15))
    return body

def test_male():
    """parede com trilho (igual ao do organizador) + lâmina de 8 mm (igual à placa)"""
    S = [box(0, -14, 0, 20, 0, 2), box(0, -3, 0, 20, 0, 20)]
    hr = DT_ROOT / 2 - K_DT * 0.5
    rail = [(10 - hr, -0.5), (10 + hr, -0.5), (10 + DT_TIP / 2, DT_H), (10 - DT_TIP / 2, DT_H)]
    S.append(prism(ccw(rail), 'z', 0, 20))
    S.append(box(30, -20, 0, 50, 0, PT))
    return union_all(S)

if __name__ == '__main__':
    import time
    for name, fn in (('organizador', organizer), ('base_display', base), ('placa_cardapio', plate),
                     ('teste_encaixe_femea', test_female), ('teste_encaixe_macho', test_male)):
        t = time.time(); P_ = fn(); T = to_mesh(P_)
        print(name, check_mesh(T), f'{time.time()-t:.1f}s')

# =====================================================================
#  SISTEMA MODULAR — interface padrão de encaixe (mesma cauda-de-
#  andorinha já validada organizador↔base). Qualquer módulo novo usa
#  slot_pair() na face que encaixa no organizador (ou no módulo
#  anterior) e pode oferecer rail_pair() na face oposta, para
#  encadear mais um módulo em seguida.
# =====================================================================
K_DT = (DT_TIP - DT_ROOT) / 2 / DT_H
MOD_D = BD                              # profundidade padrão dos módulos (= base do display)
MOD_Y = DT_Y                            # mesmas posições y dos trilhos

def rail_pair(x_face, grow, y_positions=DT_Y, z0=0.0, z1=DT_Z):
    """trilhos macho (cauda-de-andorinha) saindo de x_face na direção `grow` (+1/-1)."""
    hr = DT_ROOT / 2 - K_DT * 0.5
    out = []
    for yc in y_positions:
        tr = [(x_face - grow * 0.5, yc - hr), (x_face + grow * DT_H, yc - DT_TIP / 2),
              (x_face + grow * DT_H, yc + DT_TIP / 2), (x_face - grow * 0.5, yc + hr)]
        out.append(prism(ccw(tr), 'z', z0, z1))
    return out

def slot_pair(x_face, grow, y_positions=DT_Y, clearance=CL_DT, z0=-1.0, z1=DT_Z + 0.3):
    """rasgos fêmea que recebem rail_pair(x_face, grow, ...) com a folga `clearance`."""
    out = []
    for yc in y_positions:
        w_at = lambda d: DT_ROOT / 2 + K_DT * d + clearance
        d0, d1 = -1.0, DT_H + clearance
        xA, xB = x_face + grow * d0, x_face + grow * d1
        sl = [(xA, yc - w_at(d0)), (xB, yc - w_at(d1)), (xB, yc + w_at(d1)), (xA, yc + w_at(d0))]
        out.append(prism(ccw(sl), 'z', z0, z1))
    return out

def circle_poly(cx, cy, r, n=32):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]

def rrect_poly(u0, v0, u1, v1, r, n=5):
    """retângulo de cantos arredondados no plano (u,v) — sempre convexo."""
    r = min(r, (u1 - u0) / 2 - 1e-3, (v1 - v0) / 2 - 1e-3)
    if r <= 0:
        return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    pts = []
    for cu, cv, a0 in ((u1 - r, v0 + r, -90.0), (u1 - r, v1 - r, 0.0),
                       (u0 + r, v1 - r, 90.0), (u0 + r, v0 + r, 180.0)):
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts

def arch_poly(u0, v0, u1, v1, n=12):
    """arco de laterais retas e topo semicircular (convexo, auto-sustentado)."""
    r = (u1 - u0) / 2
    cu, vt = (u0 + u1) / 2, v1 - r
    pts = [(u0, v0), (u1, v0)]
    for i in range(n + 1):
        a = math.pi * i / n
        pts.append((cu + r * math.cos(a), vt + r * math.sin(a)))
    return pts

# ---------------- Módulo 1 — compartimentos extras ----------------
# O vão é idêntico ao dos compartimentos de sachê do organizador, para que
# um módulo de N vãos pareça continuação da peça base.
COMP_W = (OW - 2 * TE - (N_COMP - 1) * TI) / N_COMP   # 52,375 mm
M1_H = H_FRONT                                        # mesma altura da parede frontal
M1_DIV_H = H_COMP                                     # divisórias na mesma altura do organizador

def m1_width(n):
    return 2 * TE + n * COMP_W + (n - 1) * TI

def module_compartimentos(n=1):
    """n vãos do mesmo tamanho dos compartimentos de sachê do organizador."""
    w = m1_width(n)
    S = [box(0, 0, 0, w, MOD_D, TE),
         box(0, 0, 0, w, TE, M1_H),
         box(0, MOD_D - TE, 0, w, MOD_D, M1_H),
         box(0, 0, 0, TE, MOD_D, M1_H),
         box(w - TE, 0, 0, w, MOD_D, M1_H)]
    x = TE
    for _ in range(n - 1):
        x += COMP_W
        S.append(box(x, TE, 0, x + TI, MOD_D - TE, M1_DIV_H))
        x += TI
    S += docking_tabs(w)                             # engrossa a parede p/ o alojamento ficar cego
    S += button_pair(0.0, -1.0)                      # saída p/ encadear outro módulo
    body = union_all(S)
    for cu in socket_cuts(w, -1.0):                  # entrada – encaixa no organizador
        body = subtract(body, cu)
    return body

# ---------------- Módulo 2 — suporte de celular/tablet ----------------
# Pedestal vazado por um arco (auto-sustentado na impressão) + painel
# inclinado com janela de alívio, rebordo de apoio e nervuras traseiras.
M2_W      = 66.0
PED_H     = 40.0                        # altura do pedestal (aloja os botões em z = 9 e 33)
PED_SIDE  = 7.0                         # paredes laterais: hospedam botão e soquete
PED_FLOOR = 4.0                         # piso do pedestal
ARCH_TOP  = 34.0                        # topo do arco vazado
PANEL_W2, PANEL_T2, PANEL_H2 = 52.0, 5.0, 58.0
TILT2     = math.radians(26)            # inclinação do painel a partir da vertical
Y_PIV2    = 42.0                        # y do pé do painel, sobre o deck do pedestal
LIP_D2    = 13.0                        # recuo do rebordo em relação ao painel
LIP_H2, LIP_T2, LIP_W2 = 11.0, 4.0, 46.0
Y_RIM     = Y_PIV2 - LIP_D2
CABLE_W2  = 14.0
WIN_M2    = 10.0                        # moldura em volta da janela do painel

def pw2_(ly, lz):
    """(ly = através da espessura, lz = ao longo do painel) → (y, z) do módulo."""
    c, s = math.cos(TILT2), math.sin(TILT2)
    return (Y_PIV2 + ly * c + lz * s, PED_H - ly * s + lz * c)

def _panel_poly():
    """perfil lateral do painel: retângulo fino com a ponta chanfrada."""
    t = PANEL_T2 / 2
    return ccw([pw2_(-t, 0), pw2_(t, 0),
                pw2_(t, PANEL_H2 - 4.0), pw2_(t - 1.6, PANEL_H2),
                pw2_(-t + 1.6, PANEL_H2), pw2_(-t, PANEL_H2 - 4.0)])

def module_celular():
    cx = M2_W / 2
    ped = subtract(box(0, 0, 0, M2_W, MOD_D, PED_H),
                   prism(ccw(arch_poly(PED_SIDE, PED_FLOOR, M2_W - PED_SIDE, ARCH_TOP)),
                         'y', -1, MOD_D + 1))
    S = [ped, prism(_panel_poly(), 'x', cx - PANEL_W2 / 2, cx + PANEL_W2 / 2)]
    # nervuras traseiras (apoiam o painel; a aresta interna fica embutida nele)
    nerv = ccw([(Y_PIV2 + 1.0, PED_H - 2.0), (MOD_D - 5.0, PED_H - 2.0), pw2_(0.0, 18.0)])
    for xg in (cx - 13.0, cx + 13.0):
        S.append(prism(nerv, 'x', xg - 2.0, xg + 2.0))
    # rebordo que segura a borda inferior do aparelho
    S.append(prism(ccw(rrect_poly(Y_RIM, PED_H - 3.0, Y_RIM + LIP_T2, PED_H + LIP_H2, 1.6)),
                   'x', cx - LIP_W2 / 2, cx + LIP_W2 / 2))
    S += button_pair(0.0, -1.0)
    body = union_all(S)

    ztop = pw2_(0.0, PANEL_H2)[1]
    # janela de alívio (cortada ao longo de y, atravessa o painel inclinado)
    win = rrect_poly(cx - (PANEL_W2 / 2 - WIN_M2), PED_H + 17.0,
                     cx + (PANEL_W2 / 2 - WIN_M2), ztop - 11.0, 7.0)
    body = subtract(body, prism(ccw(win), 'y', Y_PIV2 - 6.0, MOD_D + 6.0))
    # chanfros nas quinas superiores do painel
    for sx in (-1.0, 1.0):
        xe = cx + sx * PANEL_W2 / 2
        tri = [(xe - sx * 11.0, ztop + 3.0), (xe + sx * 3.0, ztop + 3.0), (xe + sx * 3.0, ztop - 11.0)]
        body = subtract(body, prism(ccw(tri), 'y', Y_PIV2 + 10.0, MOD_D + 10.0))
    # passagem de cabo no rebordo
    body = subtract(body, box(cx - CABLE_W2 / 2, Y_RIM - 2.0, PED_H - 1.0,
                              cx + CABLE_W2 / 2, Y_RIM + LIP_T2 + 2.0, PED_H + 5.5))
    for cu in socket_cuts(M2_W, -1.0):
        body = subtract(body, cu)
    return body

# ---------------- Módulo 3 — porta-bisnaga (2 versões: 3 ou 6 copos) ----------------
# Corpo externo RETANGULAR (paredes retas, como os demais módulos); só os
# furos são cilíndricos. Os tubos ficam tangentes entre si e às paredes, e os
# cantos entre o quadrado e o círculo ficam vazios e abertos em cima — a peça
# não é maciça, mas por fora continua quadrada.
BOTTLE_D = 52.0                         # diâmetro interno (ajuste ao seu frasco)
CUP_H = 46.0
DRAIN_D = 8.0
NOTCH_W, NOTCH_D = 18.0, 9.0
TUBE_W = 1.5                            # parede do tubo cilíndrico
CUP_OVL = 0.6                           # sobreposição: evita tangência exata no boolean
CUP_R_OUT = BOTTLE_D / 2 + TUBE_W
CUP_PITCH = 2 * CUP_R_OUT - CUP_OVL     # distância entre centros de copos vizinhos
CUP_EDGE = TE - CUP_OVL / 2             # da face externa da parede ao início do tubo

def _cup_cuts(cx, cy):
    return [prism(ccw(circle_poly(cx, cy, BOTTLE_D / 2, 24)), 'z', TE, CUP_H + 1),
            prism(ccw(circle_poly(cx, cy, DRAIN_D / 2, 16)), 'z', -1, TE + 1)]

def module_bisnaga_grid(cols=3, rows=1):
    """cols copos lado a lado (eixo x) × rows copos em profundidade (eixo y).
    A profundidade nunca é menor que MOD_D (70 mm), para os botões ficarem
    sempre nas mesmas posições padrão (y = 18 e 52 mm)."""
    w = 2 * CUP_EDGE + 2 * CUP_R_OUT + (cols - 1) * CUP_PITCH
    d_nat = 2 * CUP_EDGE + 2 * CUP_R_OUT + (rows - 1) * CUP_PITCH
    d = max(d_nat, MOD_D)
    y_pad = (d - d_nat) / 2
    xs = [CUP_EDGE + CUP_R_OUT + i * CUP_PITCH for i in range(cols)]
    ys = [y_pad + CUP_EDGE + CUP_R_OUT + j * CUP_PITCH for j in range(rows)]
    S = [box(0, 0, 0, w, d, TE),                      # piso
         box(0, 0, 0, w, TE, CUP_H),                  # parede frontal
         box(0, d - TE, 0, w, d, CUP_H),              # parede do fundo
         box(0, 0, 0, TE, d, CUP_H),                  # parede esquerda
         box(w - TE, 0, 0, w, d, CUP_H)]              # parede direita
    for cx in xs:
        for cy in ys:
            S.append(prism(ccw(circle_poly(cx, cy, CUP_R_OUT, 24)), 'z', 0, CUP_H))
    S += docking_tabs(w)
    S += button_pair(0.0, -1.0)
    body = union_all(S)
    for cx in xs:
        for cy in ys:
            for cu in _cup_cuts(cx, cy):
                body = subtract(body, cu)
    # entalhes de pegada: atravessam a parede externa e o tubo, até o furo
    zn = CUP_H - NOTCH_D
    for cx in xs:
        body = subtract(body, box(cx - NOTCH_W / 2, -1, zn,
                                  cx + NOTCH_W / 2, ys[0] - BOTTLE_D / 2 + 0.5, CUP_H + 1))
        body = subtract(body, box(cx - NOTCH_W / 2, ys[-1] + BOTTLE_D / 2 - 0.5, zn,
                                  cx + NOTCH_W / 2, d + 1, CUP_H + 1))
    for cu in socket_cuts(w, -1.0):
        body = subtract(body, cu)
    return body, w, d

def module_bisnaga_3():
    """3 bisnagas em linha (1 fileira)."""
    return module_bisnaga_grid(cols=3, rows=1)[0]

def module_bisnaga_6():
    """6 bisnagas (3 colunas × 2 fileiras)."""
    return module_bisnaga_grid(cols=3, rows=2)[0]

def organizer_v2():
    """organizador com botões de encaixe dos dois lados: direito (base/placa) e esquerdo (módulos)."""
    body = organizer()
    return union_all([body] + button_pair(OW, +1.0) + button_pair(0.0, -1.0))

# =====================================================================
#  CONECTOR DISCRETO — botão de pressão (substitui a cauda-de-andorinha)
#  Pequeno pino com cabeça abaulada que passa, com leve pressão, por um
#  furo mais estreito num disco fino (que flexiona) e trava atrás dele
#  num rasgo de alívio. 4 botões por interface (retângulo 34×24 mm),
#  bem mais discretos que um trilho contínuo quando o módulo não está
#  instalado — ficam só 4 pontinhos na parede.
# =====================================================================
BTN_NECK_D, BTN_NECK_L = 6.0, 2.4      # pescoço: diâmetro / comprimento
BTN_HEAD_D, BTN_HEAD_L = 6.8, 1.6      # cabeça (bulbo de retenção)
SOCK_HOLE_D = 6.2                      # furo no disco fino (trava no pescoço)
SOCK_DISC_T = 1.3                      # espessura do disco flexível
SOCK_RELIEF_D = 8.6                    # rasgo de alívio atrás do disco
BTN_Y = DT_Y                           # reaproveita as posições (18, 52)
BTN_Z = (9.0, 33.0)                    # 2 alturas → retângulo de 4 botões

def button_profile(head_d=BTN_HEAD_D):
    return [(-0.5, BTN_NECK_D/2), (BTN_NECK_L, BTN_NECK_D/2),          # -0.5: embutido na parede (evita face coplanar na união)
            (BTN_NECK_L + BTN_HEAD_L*0.55, head_d/2),
            (BTN_NECK_L + BTN_HEAD_L, BTN_NECK_D/2*0.8)]

def button_solid(x_face, grow, yc, zc, head_d=BTN_HEAD_D, n=20):
    prof = [(x_face + grow*x, r) for x, r in button_profile(head_d)]
    polys = loft_x(prof, yc, zc, n)
    if grow < 0:                      # espelhar em x inverte a orientação: recompor as normais
        polys = [Polygon(list(reversed(p.v))) for p in polys]
    return polys

def button_pair(x_face, grow, y_positions=BTN_Y, z_positions=BTN_Z, head_d=BTN_HEAD_D):
    """devolve uma LISTA DE SÓLIDOS (um por botão)."""
    return [button_solid(x_face, grow, yc, zc, head_d)
            for yc in y_positions for zc in z_positions]

def socket_cuts(x_face, grow, y_positions=BTN_Y, z_positions=BTN_Z,
                hole_d=SOCK_HOLE_D, relief_d=SOCK_RELIEF_D, n=20):
    out = []
    depth2 = BTN_NECK_L + BTN_HEAD_L + 0.6
    for yc in y_positions:
        for zc in z_positions:
            xA, xB = x_face, x_face + grow*SOCK_DISC_T
            out.append(prism(ccw(circle_poly(yc, zc, hole_d/2, n)), 'x', *sorted((xA, xB))))
            xC = x_face + grow*depth2
            out.append(prism(ccw(circle_poly(yc, zc, relief_d/2, n)), 'x', *sorted((xB, xC))))
    return out


# ---- abas e posições de botão ----
DOCK_T, DOCK_H = 8.0, 40.0              # espessura (x) e altura das abas de encaixe

def btn_ys(depth):
    """posições y dos botões para um módulo de dada profundidade."""
    if depth <= MOD_D + 1:
        return BTN_Y
    return (BTN_Y[0], depth - BTN_Y[0])

def docking_tabs(module_w, y_positions=BTN_Y, h=DOCK_H, t=DOCK_T):
    """duas abas verticais (uma em cada ponta) que hospedam botões e soquetes,
    para módulos cujo corpo não tem parede cheia na altura dos botões."""
    y0, y1 = min(y_positions) - 8.0, max(y_positions) + 8.0
    return [box(0, y0, 0, t, y1, h),
            box(module_w - t, y0, 0, module_w, y1, h)]


# ---------------- peça de teste do botão ----------------
BTN_TEST_HEADS = (6.6, 6.8, 7.0)        # 1, 2 e 3 entalhes

def test_button_male():
    S = [box(0, 0, 0, 6, 70, 22)]
    for i, hd in enumerate(BTN_TEST_HEADS):
        yc = 15 + i * 20
        S.append(button_solid(6.0, +1.0, yc, 11.0, head_d=hd))
    body = union_all(S)
    for i in range(len(BTN_TEST_HEADS)):
        yc = 15 + i * 20
        for m in range(i + 1):
            body = subtract(body, box(-1, yc - 4 + m * 3, 20.5, 7, yc - 2.5 + m * 3, 23))
    return body

def test_button_female():
    body = box(0, 0, 0, 10, 70, 22)
    for i in range(len(BTN_TEST_HEADS)):
        yc = 15 + i * 20
        for cu in socket_cuts(0.0, +1.0, y_positions=(yc,), z_positions=(11.0,)):
            body = subtract(body, cu)
        for m in range(i + 1):
            body = subtract(body, box(-1, yc - 4 + m * 3, 20.5, 11, yc - 2.5 + m * 3, 23))
    return body
