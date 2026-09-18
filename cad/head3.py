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

