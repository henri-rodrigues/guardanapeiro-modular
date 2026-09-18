import math
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from parts import *
import json
OM = json.load(open('ortho_map.json'))

pdfmetrics.registerFont(TTFont('DV', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
pdfmetrics.registerFont(TTFont('DVC', '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf'))

registerFontFamily('DV', normal='DV', bold='DVB', italic='DV', boldItalic='DVB')
PW, PH = landscape(A4)
BLACK = HexColor('#34343a'); DARK = HexColor('#1c1c20'); INNER = HexColor('#4a4a52')
SLOPE = HexColor('#55555c'); NAP = HexColor('#f4f4f0'); RED = HexColor('#c8102e')
YEL = HexColor('#f2b705'); WHT = HexColor('#e6e6e6'); WOOD = HexColor('#d2a06a')
DIM = HexColor('#0b5cad'); ACC = HexColor('#c8102e'); GRID = HexColor('#9a9aa2')
TOTAL = 5
MAG = HexColor('#c9ccd4'); HOLE = HexColor('#0e0e10')

c = canvas.Canvas('/mnt/user-data/outputs/Projeto_Organizador_Cardapio_V1-1.pdf', pagesize=(PW, PH))
c.setTitle('Projeto – Organizador de Mesa com Cardápio Digital')
c.setAuthor('Projeto técnico')

# ---------------- utilidades ----------------
def frame_page(n, title, escala):
    c.setStrokeColor(colors.black); c.setLineWidth(1.2)
    c.rect(8*mm, 8*mm, PW - 16*mm, PH - 16*mm)
    c.setFont('DVB', 15); c.setFillColor(colors.black)
    c.drawString(14*mm, PH - 18*mm, title)
    c.setStrokeColor(ACC); c.setLineWidth(1.5)
    c.line(14*mm, PH - 20.5*mm, 60*mm, PH - 20.5*mm)
    # carimbo
    x0, y0, w, h = PW - 8*mm - 112*mm, 8*mm, 112*mm, 26*mm
    c.setStrokeColor(colors.black); c.setLineWidth(0.8); c.setFillColor(colors.white)
    c.rect(x0, y0, w, h, fill=1)
    c.line(x0, y0 + 16*mm, x0 + w, y0 + 16*mm)
    c.line(x0, y0 + 8*mm, x0 + w, y0 + 8*mm)
    for dx in (38, 70, 92): c.line(x0 + dx*mm, y0, x0 + dx*mm, y0 + 16*mm)
    c.setFillColor(colors.black)
    c.setFont('DVB', 9.5); c.drawString(x0 + 3*mm, y0 + 20*mm, 'ORGANIZADOR + CARDÁPIO DIGITAL – V1.1')
    lab = [('ESCALA', escala), ('UNIDADE', 'mm'), ('PROJEÇÃO', '1º diedro'), ('FOLHA', f'{n}/{TOTAL}')]
    xs = [0, 38, 70, 92]
    for (k, v), dx in zip(lab, xs):
        c.setFont('DV', 6); c.drawString(x0 + (dx + 2)*mm, y0 + 13.2*mm, k)
        c.setFont('DVB', 8.5); c.drawString(x0 + (dx + 2)*mm, y0 + 9.6*mm, v)
    c.setFont('DV', 6); c.drawString(x0 + 2*mm, y0 + 5.2*mm, 'MATERIAL')
    c.setFont('DVB', 8); c.drawString(x0 + 2*mm, y0 + 1.8*mm, 'PLA / PETG preto')
    c.setFont('DV', 6); c.drawString(x0 + 40*mm, y0 + 5.2*mm, 'DATA')
    c.setFont('DVB', 8); c.drawString(x0 + 40*mm, y0 + 1.8*mm, '16/09/2026')
    c.setFont('DV', 6); c.drawString(x0 + 72*mm, y0 + 5.2*mm, 'TOLERÂNCIA')
    c.setFont('DVB', 8); c.drawString(x0 + 72*mm, y0 + 1.8*mm, '± 0,3 mm')

class View:
    def __init__(self, ox, oy, s): self.ox, self.oy, self.s = ox, oy, s
    def P(self, a, b): return ((self.ox + a*self.s)*mm, (self.oy + b*self.s)*mm)
    def rect(self, a0, b0, a1, b1, fill, stroke=colors.black, lw=0.6, dash=None):
        x0, y0 = self.P(a0, b0); x1, y1 = self.P(a1, b1)
        if fill is not None: c.setFillColor(fill)
        if stroke is not None: c.setStrokeColor(stroke)
        c.setLineWidth(lw)
        c.setDash(*dash) if dash else c.setDash()
        c.rect(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0),
               fill=1 if fill is not None else 0, stroke=1 if stroke is not None else 0)
        c.setDash()
    def poly(self, pts, fill, stroke=colors.black, lw=0.6):
        p = c.beginPath(); x, y = self.P(*pts[0]); p.moveTo(x, y)
        for q in pts[1:]: p.lineTo(*self.P(*q))
        p.close(); c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(lw)
        c.drawPath(p, fill=1, stroke=1)
    def line(self, a0, b0, a1, b1, col=colors.black, lw=0.5, dash=None):
        c.setStrokeColor(col); c.setLineWidth(lw)
        c.setDash(*dash) if dash else c.setDash()
        c.line(*self.P(a0, b0), *self.P(a1, b1)); c.setDash()
    def hidden(self, a0, b0, a1, b1): self.line(a0, b0, a1, b1, HexColor('#8c8c96'), 0.45, (2, 1.6))

def arrow(x, y, ang):
    L, Wd = 2.2*mm, 0.7*mm
    ca, sa = math.cos(ang), math.sin(ang)
    p = c.beginPath(); p.moveTo(x, y)
    p.lineTo(x - L*ca + Wd*sa, y - L*sa - Wd*ca); p.lineTo(x - L*ca - Wd*sa, y - L*sa + Wd*ca); p.close()
    c.setFillColor(DIM); c.drawPath(p, fill=1, stroke=0)

def dim_h(v, a1, a2, b_dim, b_ref1, b_ref2, label, size=7.5):
    """cota horizontal: b_dim em mm de papel (offset absoluto na folha)"""
    x1, _ = v.P(a1, 0); x2, _ = v.P(a2, 0)
    yd = b_dim*mm
    c.setStrokeColor(DIM); c.setLineWidth(0.35)
    for x, br in ((x1, b_ref1), (x2, b_ref2)):
        yr = v.P(0, br)[1]
        sgn = 1 if yd > yr else -1
        c.line(x, yr + sgn*1*mm, x, yd + sgn*1.5*mm)
    c.line(x1, yd, x2, yd)
    arrow(x2, yd, 0); arrow(x1, yd, math.pi)
    c.setFillColor(DIM); c.setFont('DVB', size)
    tw = c.stringWidth(label, 'DVB', size)
    if tw + 2 > abs(x2 - x1):
        c.drawString(max(x1, x2) + 1.5*mm, yd + 0.8*mm, label)
    else:
        c.drawCentredString((x1 + x2)/2, yd + 0.9*mm, label)

def dim_v(v, b1, b2, a_dim, a_ref1, a_ref2, label, size=7.5):
    y1 = v.P(0, b1)[1]; y2 = v.P(0, b2)[1]
    xd = a_dim*mm
    c.setStrokeColor(DIM); c.setLineWidth(0.35)
    for y, ar in ((y1, a_ref1), (y2, a_ref2)):
        xr = v.P(ar, 0)[0]
        sgn = 1 if xd > xr else -1
        c.line(xr + sgn*1*mm, y, xd + sgn*1.5*mm, y)
    c.line(xd, y1, xd, y2)
    arrow(xd, y2, math.pi/2 if y2 > y1 else -math.pi/2); arrow(xd, y1, -math.pi/2 if y2 > y1 else math.pi/2)
    c.saveState(); c.translate(xd - 0.9*mm, (y1 + y2)/2); c.rotate(90)
    c.setFillColor(DIM); c.setFont('DVB', size)
    tw = c.stringWidth(label, 'DVB', size)
    if tw + 2 > abs(y2 - y1):
        c.drawString(abs(y2 - y1)/2 + 1.5*mm, 0, label)
    else:
        c.drawCentredString(0, 0, label)
    c.restoreState()

def view_label(x, y, text, sub):
    c.setFillColor(colors.black); c.setFont('DVB', 9.5); c.drawString(x*mm, y*mm, text)
    w = c.stringWidth(text, 'DVB', 9.5)
    c.setFont('DV', 7.5); c.setFillColor(HexColor('#555555')); c.drawString(x*mm + w + 2*mm, y*mm, sub)
    c.setStrokeColor(colors.black); c.setLineWidth(0.6); c.line(x*mm, y*mm - 1.3*mm, x*mm + w, y*mm - 1.3*mm)

def plate_face(v, map_, full=True):
    """desenha a face frontal da placa. map_(lx,lz)->(a,b) na vista"""
    def R(lx0, lz0, lx1, lz1, fill, stroke=None, lw=0.3):
        a0, b0 = map_(lx0, lz0); a1, b1 = map_(lx1, lz1)
        v.rect(a0, b0, a1, b1, fill, stroke, lw)
    R(-38, 0, 38, 140, BLACK, colors.black, 0.6)
    R(-33.5, 5.5, 33.5, 134.5, DARK, HexColor('#666666'), 0.3)
    kz = abs(map_(0, 1)[1] - map_(0, 0)[1])
    def T(s, lz, em):
        a, b = map_(0, lz); x, y = v.P(a, b)
        size = em * v.s * mm * 0.98
        c.setFillColor(colors.white); c.setFont('DVB', size)
        c.drawCentredString(x, y - size*0.36*kz, s)
    if full:
        T('CARDÁPIO', 120, 11); T('– DIGITAL –', 106.5, 10)
        T('APONTE A CÂMERA', 20, 4.6); T('DO SEU CELULAR', 13, 4.6)
    R(-24.5, 47.5, 24.5, 97.5, colors.white)
    c.setFillColor(HexColor('#111111'))
    for r in range(N_QR):
        for q in range(N_QR):
            if QR[r][q]:
                x0 = QR_X0 + q*QR_M; zt = QR_TOP - r*QR_M
                a0, b0 = map_(x0, zt - QR_M); a1, b1 = map_(x0 + QR_M, zt)
                (X0, Y0), (X1, Y1) = v.P(a0, b0), v.P(a1, b1)
                c.rect(X0, Y0, X1 - X0 + 0.15, Y1 - Y0 + 0.15, fill=1, stroke=0)
    if full:
        a0, b0 = map_(-4.5, 27); a1, b1 = map_(4.5, 42)
        v.rect(a0, b0, a1, b1, None, colors.white, max(0.7*v.s*2.2, 0.5))
        for s_ in (-1, 1):
            for ang in (-35, 0, 35):
                cx, cz = s_*9, 34.5 + 3.5*math.sin(math.radians(ang))
                dx = 1.4*math.cos(math.radians(ang)); dz = 1.4*math.sin(math.radians(ang))*s_
                p = map_(cx - dx, cz - dz); q = map_(cx + dx, cz + dz)
                v.line(p[0], p[1], q[0], q[1], colors.white, max(0.5*v.s*2.2, 0.4))

def legend(x, y, cols=1):
    items = [(BLACK, 'Organizador – PLA preto'),
             (HexColor('#3d3d44'), 'Base do display – PLA preto'),
             (DARK, 'Placa + adesivo (QR e textos)')]
    c.setFont('DVB', 9); c.setFillColor(colors.black); c.drawString(x*mm, y*mm, 'LEGENDA DE CORES')
    for i, (col, t) in enumerate(items):
        if cols == 2:
            t = t.replace(' – PLA preto fosco', ' (PLA preto)').replace(' – PLA branco (troca de cor)', ' (PLA branco)')
            xo = x + (0 if i < 2 else 70)
            yy = (y - 6 - (i if i < 2 else i - 2)*5.2)*mm
            X_ = xo
        else:
            yy = (y - 6 - i*5.2)*mm; X_ = x
        x_ = X_
        c.setFillColor(col); c.setStrokeColor(colors.black); c.setLineWidth(0.5)
        c.rect(x_*mm, yy - 1*mm, 7*mm, 3.6*mm, fill=1)
        c.setFillColor(colors.black); c.setFont('DV', 7.5); c.drawString((x_ + 9.5)*mm, yy, t)

def notes(x, y, title, lines, size=7.5, lead=4.2):
    c.setFont('DVB', 9); c.setFillColor(colors.black); c.drawString(x*mm, y*mm, title)
    c.setFont('DV', size)
    for i, t in enumerate(lines):
        c.drawString(x*mm, (y - 5.5 - i*lead)*mm, t)

import parts as _PP
PL_W, PL_H = _PP.PW, _PP.PH
from views import LAYOUT, QR as QRR, NQ
GRAY = HexColor('#555555'); GR = HexColor('#b0b0ba'); BASEC = HexColor('#3d3d44')
def fmt(v, d=1):
    s_ = f"{v:.{d}f}".replace('.', ',')
    return s_[:-2] if s_.endswith(',0') else s_
TOP_H = OM['frontal']['maxy']

class IView(View):
    """vista a partir de imagem renderizada: mapeia coordenadas do modelo para o papel"""
    def __init__(self, path, x0, y0, k, key):
        self.im = ImageReader(path); self.iw, self.ih = self.im.getSize()
        self.m = OM[key]; self.k = k; self.x0, self.y0 = x0, y0
        self.f = k * 2 / self.m['s']            # mm de papel por pixel
        self.w, self.h = self.iw * self.f, self.ih * self.f
        self.s = k; self.ox = 0; self.oy = 0
        c.drawImage(self.im, x0*mm, y0*mm, self.w*mm, self.h*mm, mask='auto')
    def P(self, a, b):
        px = ((a - self.m['minx']) * self.m['s'] + self.m['pad']) / 2
        py = ((self.m['maxy'] - b) * self.m['s'] + self.m['pad']) / 2
        return ((self.x0 + px * self.f)*mm, (self.y0 + self.h - py * self.f)*mm)

def txt(x, y, s_, size=7, font='DV', col=colors.black, center=False):
    c.setFont(font, size); c.setFillColor(col)
    (c.drawCentredString if center else c.drawString)(x*mm, y*mm, s_)

def img_fit(path, x, y, w, hmax):
    im = ImageReader(path); iw, ih = im.getSize(); h = w*ih/iw
    if h > hmax: h = hmax; w = h*iw/ih
    c.drawImage(im, x*mm, y*mm, w*mm, h*mm, mask='auto'); return w, h

def leader(v, a, b, dx, dy, text, size=6.8, col=HexColor('#333333')):
    X, Y = v.P(a, b)
    c.setStrokeColor(col); c.setLineWidth(0.35); c.line(X, Y, X + dx*mm, Y + dy*mm)
    c.setFillColor(col); c.circle(X, Y, 0.45*mm, fill=1, stroke=0); c.setFont('DV', size)
    if dx >= 0: c.drawString(X + dx*mm + 1*mm, Y + dy*mm - 0.8*mm, text)
    else: c.drawRightString(X + dx*mm - 1*mm, Y + dy*mm - 0.8*mm, text)

VOL = {}
for nm, fn in (('org', organizer), ('base', base), ('placa', plate)):
    VOL[nm] = check_mesh(to_mesh(fn()))['volume_mm3'] / 1000

# ================= FOLHA 1 =================
frame_page(1, 'Visão geral – V1.1', 'S/ escala')
img_fit('iso_fd.png', 14, 58, 118, 128)
view_label(16, 53, 'ISOMÉTRICA – MONTADO', '')
img_fit('exp_fd.png', 140, 116, 100, 70)
view_label(142, 112, 'EXPLODIDA – TRILHOS NO ORGANIZADOR', '')
img_fit('exp_fe.png', 140, 44, 100, 64)
view_label(142, 40, 'EXPLODIDA – RASGOS NA BASE', '')
legend(16, 44, cols=2)
bx = 246
c.setFillColor(HexColor('#f3f3f5')); c.setStrokeColor(HexColor('#999999')); c.setLineWidth(0.5)
c.roundRect(bx*mm, 40*mm, 42*mm, 146*mm, 2*mm, fill=1)
notes(bx + 3, 181, 'MUDANÇAS NA V1.1', [
    'Paredes externas: 3 mm', 'Paredes internas: 1,5 mm', '',
    'Ímãs substituídos por', 'encaixe por pressão:', '',
    '• Base ↔ organizador:', '  2 trilhos cauda-de-', '  andorinha verticais', '  (folga 0,15 mm)', '',
    '• Placa ↔ base:', '  fenda inclinada 12°', '  (folga 0,10 mm)', '',
    'QR e textos em adesivo', '68 × 122 mm'], size=7.1, lead=4.2)
notes(bx + 3, 99, 'MEDIDAS', [
    'Conjunto: 312 × 110 × 142',
    'Organizador: 220 × 110 × 85', '  + trilhos de 4 mm',
    'Base: 92 × 70 × 111',
    'Placa: 76 × 8 × 140'], size=7.1, lead=4.2)
notes(bx + 3, 70, 'VOLUME SÓLIDO', [
    f'Organizador: {fmt(VOL["org"])} cm³', f'Base: {fmt(VOL["base"])} cm³', f'Placa: {fmt(VOL["placa"])} cm³',
    'A massa real depende', 'do preenchimento –', 'confira no fatiador.'], size=7.1, lead=4.2)
c.showPage()

# ================= FOLHA 2 =================
frame_page(2, 'Vista frontal e vista superior', '1:2')
F = IView('orto_frontal.png', 22, 100, 0.5, 'frontal')
view_label(40, 95, 'VISTA FRONTAL', 'ESC 1:2')
dim_h(F, 0, BX1, 185, H_BACK, TOP_H, '312')
dim_h(F, 0, OW, 179.5, H_BACK, H_BACK, '220')
dim_h(F, OW, BX1, 179.5, TOP_H, TOP_H, '92')
dim_h(F, PXC - PL_W/2, PXC + PL_W/2, 174, TOP_H, TOP_H, '76')
dim_v(F, 0, H_FRONT, 20, 0, 0, '60')
dim_v(F, 0, H_BACK, 15, 0, 0, '85')
dim_v(F, 0, H_LIP, 185, BX1, BX1, '16')
dim_v(F, 0, H_SIDE, 190, BX1, BX1, '24')
dim_v(F, 0, TOP_H, 195, BX1, PXC + PL_W/2, '142')
dim_v(F, 0, BLOCK_H, 175, OW + BLOCK_W, OW + BLOCK_W, '30') if False else None

Tv = IView('orto_superior.png', 22, 30, 0.5, 'superior')
view_label(24, 14, 'VISTA SUPERIOR', 'ESC 1:2')
cx = comp_x()
for (a, b) in cx:
    dim_h(Tv, a, b, 25, TE, TE, fmt((b - a), 1))
dim_v(Tv, 0, OD, 15, 0, 0, '110')
dim_v(Tv, TE, Y_DIV, 20, 0, 0, '68')
dim_v(Tv, Y_DIV + TI, OD - TE, 20, 0, 0, fmt(OD - TE - Y_DIV - TI))
dim_v(Tv, 0, BD, 186, BX1, BX1, '70')
leader(Tv, OW + DT_H/2, DT_Y[0], 12, -14, 'trilho + rasgo', col=ACC)
notes(205, 180, 'NOTAS', [
    '1. Cotas em mm.',
    '2. Paredes externas e fundo: 3 mm.',
    '3. Divisórias internas: 1,5 mm',
    '    (sachês h 54 mm, guardanapo h 68 mm).',
    '4. Compartimentos úteis: 4 × 52,4 × 68 mm.',
    '5. Rasgo do guardanapo: 214 × 34,5 mm.',
    '6. A base encaixa por cima nos 2 trilhos',
    '    do organizador (detalhe A, folha 4).',
    '7. A placa entra sob pressão na fenda',
    '    inclinada da base (corte B, folha 4).',
    '8. Folgas de encaixe ajustáveis com as',
    '    peças de teste (folha 5).',
])
legend(205, 112)
c.showPage()

# ================= FOLHA 3 =================
frame_page(3, 'Vistas laterais', '1:1,25')
R = IView('orto_dir.png', 24, 44, 0.8, 'dir')
view_label(24, 175, 'VISTA LATERAL DIREITA', 'ESC 1:1,25')
dim_h(R, 0, OD, 36, 0, 0, '110')
dim_h(R, 0, BD, 31, 0, 0, '70') if False else None
dim_h(R, 0, RAMP[0], 158, H_BACK, H_BACK, '69')
dim_h(R, RAMP[0], RAMP[1], 158, H_BACK, H_BACK, '12')
dim_v(R, 0, H_FRONT, 124, OD, OD, '60') if False else None
dim_v(R, 0, H_BACK, 118, OD, OD, '85')
dim_v(R, 0, TOP_H, 18, 0, 6, '142')
Xa, Ya = R.P(*pw_(-PT/2, 0))
c.setStrokeColor(ACC); c.setLineWidth(0.5); c.line(Xa, Ya, Xa, Ya + 75*mm)
c.arc(Xa - 65*mm, Ya - 65*mm, Xa + 65*mm, Ya + 65*mm, 78, 12)
txt(Xa/mm + 4, Ya/mm + 66, '12°', 8, 'DVB', ACC)

L = IView('orto_esq.png', 140, 44, 0.8, 'esq')
view_label(140, 175, 'VISTA LATERAL ESQUERDA', 'ESC 1:1,25')
dim_h(L, -OD, 0, 36, 0, 0, '110')
dim_v(L, 0, H_FRONT, 240, 0, 0, '60')
dim_v(L, 0, H_BACK, 134, -OD, -OD, '85')
notes(250, 170, 'DETALHES', [
    'Placa inclinada 12°.', 'Entra 12 mm na', 'fenda da base e', 'encosta na cunha.', '',
    'Rampa lateral de', '60 → 85 mm entre', 'y = 69 e y = 81.', '',
    'Base com fundo de', '3 mm e cunha de', 'apoio de 68 mm.'])
c.showPage()

# ================= FOLHA 4 – ENCAIXES =================
frame_page(4, 'Detalhes dos encaixes por pressão', 'Indicada')
# Detalhe A – cauda-de-andorinha (vista superior 3:1)
yc = DT_Y[0]; SA = 3.0
A = View(34 - 214*SA, 128 - (yc - 7)*SA, SA)
A.rect(214, yc - 7, OW - TE, yc + 7, HexColor('#e9e9ee'), None)
A.rect(OW - TE, yc - 7, OW, yc + 7, BLACK)
A.rect(OW, yc - 7, OW + BLOCK_W, yc + 7, BASEC)
k_ = (DT_TIP - DT_ROOT) / 2 / DT_H
hw = lambda x: DT_ROOT / 2 + k_ * (x - OW) + CL_DT
xe = OW + DT_H + CL_DT
A.poly([(OW, yc - hw(OW)), (xe, yc - hw(xe)), (xe, yc + hw(xe)), (OW, yc + hw(OW))], colors.white, colors.black, 0.4)
A.poly([(OW, yc - DT_ROOT/2), (OW + DT_H, yc - DT_TIP/2), (OW + DT_H, yc + DT_TIP/2), (OW, yc + DT_ROOT/2)], BLACK, colors.black, 0.5)
view_label(22, 181, 'DETALHE A – TRILHO CAUDA-DE-ANDORINHA', '')
txt(22, 176.5, 'ESC 3:1 – vista superior (corte na altura do trilho)', 6.5, col=GRAY)
txt(A.P(OW - TE/2, 0)[0]/mm, A.P(0, yc + 7)[1]/mm + 2, 'organizador', 6.5, col=GRAY, center=True)
txt(A.P(OW + BLOCK_W/2, 0)[0]/mm, A.P(0, yc + 7)[1]/mm + 2, 'base', 6.5, col=GRAY, center=True)
xr_ = A.P(OW + BLOCK_W, 0)[0]/mm
dim_v(A, yc - DT_ROOT/2, yc + DT_ROOT/2, 28, OW, OW, '6')
dim_v(A, yc - DT_TIP/2, yc + DT_TIP/2, xr_ + 5, OW + DT_H, OW + DT_H, '9')
dim_v(A, yc - hw(xe), yc + hw(xe), xr_ + 11, xe, xe, '9,3 rasgo')
dim_h(A, OW, OW + DT_H, 121, yc - 7, yc - 7, '4')
dim_h(A, OW - TE, OW, 121, yc - 7, yc - 7, '3')
dim_h(A, OW, OW + BLOCK_W, 115.5, yc - 7, yc - 7, '9')
notes(22, 104, 'COMO FUNCIONA', [
    '• 2 trilhos na lateral direita do organizador',
    '  (y = 18 e 52 mm, altura 24 mm).',
    '• A base desce por cima e trava nos trilhos;',
    '  o topo do rasgo é fechado (batente).',
    '• Folga de 0,15 mm por lado = pressão firme.',
    '• Trilho e rasgo são impressos em pé:',
    '  sem suporte e com boa resistência.'], size=7, lead=4.0)

# Corte B – fenda da placa (2:1) plano yz
SB = 2.0; ZC = 36.0; YC = 52.0
B = View(118, 104, SB)
def clip_poly(poly, zmax, ymax):
    out = poly
    for axis, lim in ((1, zmax), (0, ymax)):
        res = []
        for i in range(len(out)):
            p, q = out[i], out[(i + 1) % len(out)]
            pin, qin = p[axis] <= lim, q[axis] <= lim
            if pin: res.append(p)
            if pin != qin:
                t = (lim - p[axis]) / (q[axis] - p[axis])
                res.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        out = res
    return out
YBv = pw_(PT/2 + CL_PT, (H_LIP - Z0) / math.cos(TILT) + 2)[0] + 3.0
B.poly(clip_poly(wedge_poly(), ZC, YC), HexColor('#55555c'))
B.poly([(0, 0), (YBv, 0), (YBv, H_LIP), (0, H_LIP)], BASEC)
B.rect(0, 0, YC, TE, BASEC)
B.poly(plate_slot_poly_clip := clip_poly(plate_slot_poly(), H_LIP + 0.01, YC), colors.white, colors.black, 0.4)
B.poly(clip_poly([pw_(-PT/2, 0), pw_(PT/2, 0), pw_(PT/2, 60), pw_(-PT/2, 60)], ZC, YC), BLACK, colors.black, 0.6)
c.setStrokeColor(colors.black); c.setLineWidth(0.4); c.setDash(3, 2)
c.line(*B.P(0, ZC), *B.P(YC, ZC)); c.line(*B.P(YC, 0), *B.P(YC, ZC)); c.setDash()
view_label(122, 181, 'CORTE B – FENDA DA PLACA', 'ESC 2:1')
txt(122, 176.5, 'corte no plano y-z (vista pela direita), recortado', 6.5, col=GRAY)
def lead_to(v, a, b, xend, yoff, text, col):
    X, Y = v.P(a, b); leader(v, a, b, xend - X/mm, yoff, text, col=col)
lead_to(B, *pw_(PT/2 + CL_PT, 7), 226, 14, 'fenda 8,2 mm (0,10 por lado)', ACC)
lead_to(B, *pw_(-PT/2 - CL_PT, 5), 226, 6, 'placa encosta na aba frontal', GRAY)
lead_to(B, *pw_(0, -CL_PZ), 226, -4, 'folga de fundo 0,3 + chanfro 1 mm', GRAY)
lead_to(B, *pw_(PT/2 + CL_WEDGE, 25), 226, 10, 'cunha de apoio (folga 0,1)', GRAY)
lead_to(B, *pw_(0, 28), 226, 6, 'placa 76 × 8 × 140', GRAY)
dim_v(B, 0, H_LIP, 114, 0, 0, '16')
dim_v(B, 0, TE, 109, 0, 0, '3')
dim_h(B, 0, YBv, 98, 0, 0, fmt(YBv))
X0_, Y0_ = B.P(*pw_(-PT/2, 0))
c.setStrokeColor(ACC); c.setLineWidth(0.5); c.line(X0_, Y0_, X0_, Y0_ + 64*mm)
c.arc(X0_ - 56*mm, Y0_ - 56*mm, X0_ + 56*mm, Y0_ + 56*mm, 78, 12)
txt(X0_/mm + 3, Y0_/mm + 58, '12°', 8, 'DVB', ACC)
notes(236, 90, 'PLACA', [
    '• Entra ~12 mm na fenda.',
    '• Pressão só na espessura;',
    '  laterais com 0,3 mm.',
    '• Chanfro de 1 mm no pé',
    '  guia a entrada.'], size=7, lead=4.0)

w_, h_ = img_fit('teste.png', 108, 40, 66, 50)
view_label(108, 93, 'PEÇAS DE TESTE DE ENCAIXE', '')
txt(108, 88.5, 'folgas 0,10 / 0,15 / 0,20 mm – marcadas com 1, 2 e 3 entalhes', 6.5, col=GRAY)
c.showPage()

# ================= FOLHA 5 – PLACA / IMPRESSÃO =================
frame_page(5, 'Placa, adesivo e impressão 3D', 'Indicada')
Pv = View(22, 44, 0.8)
Pv.rect(0, 0, PL_W, PL_H, BLACK)
x0s, x1s = PL_W/2 - REC_W/2, PL_W/2 + REC_W/2
Pv.rect(x0s, REC_Z, x1s, REC_Z + REC_H, DARK, HexColor('#777777'), 0.3)
q0, q1 = LAYOUT['qr']; sq = q1 - q0
Pv.rect(PL_W/2 - sq/2, q0, PL_W/2 + sq/2, q1, colors.white, None)
m = (sq - 4) / NQ
c.setFillColor(HexColor('#111111'))
for r in range(NQ):
    for k in range(NQ):
        if QRR[r][k]:
            xa = PL_W/2 - sq/2 + 2 + k*m; zt = q1 - 2 - r*m
            (A0, B0), (A1, B1) = Pv.P(xa, zt - m), Pv.P(xa + m, zt)
            c.rect(A0, B0, A1 - A0 + 0.1, B1 - B0 + 0.1, fill=1, stroke=0)
for key, s_ in (('t1', 'CARDÁPIO'), ('t2', '– DIGITAL –'), ('l1', 'APONTE A CÂMERA'), ('l2', 'DO SEU CELULAR')):
    lz, em = LAYOUT[key]; X, Y = Pv.P(PL_W/2, lz); size = em*0.8*mm*0.98
    c.setFillColor(colors.white); c.setFont('DVB', size); c.drawCentredString(X, Y - size*0.36, s_)
Pv.rect(0, 0, PL_W, 12.4, None, ACC, 0.6, (2, 1.5))
view_label(22, 170, 'PLACA – FRENTE', 'ESC 1:1,25')
dim_h(Pv, 0, PL_W, 38, 0, 0, '76')
dim_h(Pv, x0s, x1s, 162, REC_Z + REC_H, REC_Z + REC_H, '68 (adesivo)')
dim_v(Pv, 0, PL_H, 17, 0, 0, '140')
dim_v(Pv, REC_Z, REC_Z + REC_H, 90, PL_W, PL_W, '122 (adesivo)')
dim_v(Pv, 0, REC_Z, 84, PL_W, PL_W, '14')
dim_v(Pv, q0, q1, 12, 0, 0, '50 (QR)')
txt(22, 34.5, 'Rebaixo de 0,4 mm para o adesivo. Tracejado vermelho = parte que entra na fenda.', 6.5, col=GRAY)

data = [['Arquivo STL', 'Peça', 'Medidas (mm)', 'Posição na mesa'],
        ['organizador.stl', 'Organizador', '224 × 110 × 85', 'fundo na mesa'],
        ['base_display.stl', 'Base do display', '92 × 70 × 111', 'fundo na mesa'],
        ['placa_cardapio.stl', 'Placa', '76 × 140 × 8', 'verso na mesa'],
        ['teste_encaixe_femea.stl', 'Teste (rasgos)', '90 × 30 × 14', 'fundo na mesa'],
        ['teste_encaixe_macho.stl', 'Teste (trilho)', '50 × 24 × 20', 'como no arquivo']]
tb = Table(data, colWidths=[40*mm, 26*mm, 26*mm, 26*mm])
tb.setStyle(TableStyle([
    ('FONT', (0, 0), (-1, 0), 'DVB', 7.2), ('FONT', (0, 1), (-1, -1), 'DV', 7),
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1c1c20')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('BACKGROUND', (0, 1), (-1, 3), HexColor('#eef0f6')),
    ('GRID', (0, 0), (-1, -1), 0.4, HexColor('#888888'))]))
txt(108, 181, 'ARQUIVOS PARA IMPRESSÃO', 9, 'DVB')
tw_, th_ = tb.wrapOn(c, 0, 0); tb.drawOn(c, 108*mm, 177*mm - th_)

st = ParagraphStyle('b', fontName='DV', fontSize=7.3, leading=9.3, spaceAfter=2.2)
hh = ParagraphStyle('h', fontName='DVB', fontSize=8.8, leading=10.5, spaceBefore=2.5, spaceAfter=1.2, textColor=ACC)
steps = [
 ('1. Imprima primeiro o teste de encaixe (≈ 30 min)', [
  'O bloco tem 3 rasgos e 3 fendas com folgas de <b>0,10</b> (1 entalhe), <b>0,15</b> (2) e <b>0,20 mm</b> (3). '
  'Encaixe o trilho e a lâmina de 8 mm em cada um. O ideal é entrar com pressão firme da mão, sem martelo.']),
 ('2. Se o encaixe ficar justo ou folgado', [
  'Os STL usam 0,15 mm no trilho e 0,10 mm na placa. Se o seu teste pedir outra folga, no Bambu Studio use '
  '<b>Qualidade › Compensação de contorno XY</b> só na base (ex.: −0,05 mm alarga os rasgos) ou me peça os STL com a nova folga.']),
 ('3. Configurações (Bambu Studio, bico 0,4)', [
  'PLA ou PETG · camada 0,2 mm · <b>4 paredes</b> (≈1,6 mm; a parede de 3 mm fica sólida) · 5 camadas de topo e fundo · '
  'preenchimento 15% gyroid · <b>sem suporte</b> · brim de 5 mm no organizador · '
  'desligue <b>"Elephant foot compensation"</b> só se o teste mostrar folga demais na base dos rasgos.']),
 ('4. Montagem', [
  'Desça a base por cima dos trilhos até o fundo encostar na mesa. Cole o adesivo no rebaixo da placa e '
  'empurre o pé da placa na fenda até encostar na cunha.']),
]
story = []
for t_, ps in steps:
    story.append(Paragraph(t_, hh))
    for p_ in ps: story.append(Paragraph(p_, st))
fr = Frame(108*mm, 38*mm, 178*mm, 177*mm - th_ - 44*mm, showBoundary=0, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
fr.addFromList(story, c)
if story: print('SOBROU', len(story))
c.showPage()
c.save(); print('ok')
