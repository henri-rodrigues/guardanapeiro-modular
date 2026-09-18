import json
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

pdfmetrics.registerFont(TTFont('DV', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
VOL = json.load(open('mod_vols.json'))
PW_, PH_ = landscape(A4)
BLACK = HexColor('#1c1c20'); ACC = HexColor('#c8102e'); GRAY = HexColor('#555555')
C_M1 = HexColor('#3a5a78'); C_M2 = HexColor('#3a6b4a'); C_M3 = HexColor('#7a4a2e')
c = canvas.Canvas('/mnt/user-data/outputs/Modulos_Extras.pdf', pagesize=(PW_, PH_))
c.setTitle('Módulos extras – sistema modular do organizador')

def frame(n, title, total=3):
    c.setStrokeColor(colors.black); c.setLineWidth(1.2)
    c.rect(8*mm, 8*mm, PW_-16*mm, PH_-16*mm)
    c.setFont('DVB', 15); c.setFillColor(colors.black); c.drawString(14*mm, PH_-18*mm, title)
    c.setStrokeColor(ACC); c.setLineWidth(1.5); c.line(14*mm, PH_-20.5*mm, 62*mm, PH_-20.5*mm)
    x0, y0, w, h = PW_-8*mm-90*mm, 8*mm, 90*mm, 16*mm
    c.setStrokeColor(colors.black); c.setLineWidth(0.8); c.setFillColor(colors.white)
    c.rect(x0, y0, w, h, fill=1)
    c.setFont('DVB', 9); c.drawString(x0+3*mm, y0+10*mm, 'MÓDULOS EXTRAS — ORGANIZADOR + CARDÁPIO DIGITAL')
    c.setFont('DV', 7); c.drawString(x0+3*mm, y0+3*mm, f'Folha {n}/{total}   ·   16/09/2026   ·   PLA/PETG preto   ·   mm')

def txt(x, y, s, size=8, font='DV', col=colors.black, center=False):
    c.setFont(font, size); c.setFillColor(col)
    (c.drawCentredString if center else c.drawString)(x*mm, y*mm, s)

def img_fit(path, x, y, w, hmax=None):
    im = ImageReader(path); iw, ih = im.getSize(); h = w*ih/iw
    if hmax and h > hmax: h = hmax; w = h*iw/ih
    c.drawImage(im, x*mm, y*mm, w*mm, h*mm, mask='auto'); return w, h

def swatch(x, y, color, label):
    c.setFillColor(color); c.setStrokeColor(colors.black); c.setLineWidth(0.4)
    c.rect(x*mm, y*mm-1.2*mm, 6*mm, 3.4*mm, fill=1)
    txt(x+8, y, label, 7.3, col=colors.black)

# ================= FOLHA 1 – VISÃO GERAL DO SISTEMA =================
frame(1, 'Sistema modular — visão geral')
img_fit('chain_demo.png', 16, 46, 175, 132)
view_x = 16
txt(16, 40, 'ORGANIZADOR + 3 MÓDULOS ENCADEADOS NA LATERAL ESQUERDA', 9.5, 'DVB')
txt(16, 35.5, 'da esquerda p/ direita: porta-bisnaga · suporte de celular · compartimentos extras · organizador · base + placa', 7, col=GRAY)
swatch(16, 27, C_M3, 'Porta-bisnaga'); swatch(66, 27, C_M2, 'Suporte de celular'); swatch(130, 27, C_M1, 'Compartimentos extras')

bx = 200
c.setFillColor(HexColor('#f3f3f5')); c.setStrokeColor(HexColor('#999999')); c.setLineWidth(0.5)
c.roundRect(bx*mm, 46*mm, 88*mm, 140*mm, 2*mm, fill=1)
txt(bx+4, 178, 'COMO FUNCIONA A INTERFACE', 10, 'DVB')
txt(bx+4, 172, 'Todos os módulos usam o mesmo encaixe cauda-de-andorinha já', 7.6)
txt(bx+4, 168, 'validado entre organizador e base (6→9 mm, folga 0,15 mm).', 7.6)
txt(bx+4, 161, '• O organizador agora tem trilhos macho nos DOIS lados: o', 7.6)
txt(bx+8, 157, 'direito continua com a base do cardápio; o esquerdo é', 7.6)
txt(bx+8, 153, 'livre para qualquer módulo novo.', 7.6)
txt(bx+4, 146, '• Cada módulo tem um rasgo fêmea na face que encosta no', 7.6)
txt(bx+8, 142, 'organizador (ou no módulo anterior) — e um trilho macho', 7.6)
txt(bx+8, 138, 'na face de fora, para encaixar mais um módulo em fila.', 7.6)
txt(bx+4, 131, '• Montagem: cada peça desce por cima (vertical), como a', 7.6)
txt(bx+8, 127, 'base já fazia com o organizador.', 7.6)
txt(bx+4, 118, 'PROFUNDIDADE PADRÃO', 9, 'DVB')
txt(bx+4, 113, 'Todo módulo tem 70 mm de profundidade (y), a mesma da', 7.6)
txt(bx+4, 109, 'base do display, com os trilhos nas mesmas posições', 7.6)
txt(bx+4, 105, '(y = 18 e 52 mm). Isso garante que qualquer combinação', 7.6)
txt(bx+4, 101, 'de módulos encaixa sem redesenhar nada.', 7.6)
txt(bx+4, 92, 'ARQUIVOS ATUALIZADOS', 9, 'DVB')
txt(bx+4, 87, 'organizador_v2_trilhos_2_lados.stl substitui o', 7.6)
txt(bx+4, 83, 'organizador.stl da versão anterior (agora com trilho', 7.6)
txt(bx+4, 79, 'também do lado esquerdo). As demais peças (base,', 7.6)
txt(bx+4, 75, 'placa) continuam as mesmas.', 7.6)
txt(bx+4, 66, 'ENCAIXE', 9, 'DVB')
txt(bx+4, 61, 'Mesma folga já testada na V1.1 (0,15 mm). Se seu', 7.6)
txt(bx+4, 57, 'teste de encaixe (folha anterior) pediu outra folga,', 7.6)
txt(bx+4, 53, 'me avise para eu regerar os STL com o valor certo.', 7.6)
c.showPage()

# ================= FOLHA 2 – 3 MÓDULOS (specs) =================
frame(2, 'Especificação dos 3 módulos novos')
cols = [(16, 'modulo_compartimentos_extras', 'mod_compartimentos_alone.png', C_M1,
         'MÓDULO 1 — COMPARTIMENTOS EXTRAS',
         [('Largura × profundidade × altura', '44 × 70 × 60 mm'),
          ('Compartimentos', '2 × 18,25 × 64 mm'),
          ('Paredes / divisória', '3 mm / 1,5 mm'),
          ('Volume sólido', f'{VOL["modulo_compartimentos_extras"]:.1f} cm³')],
         ['Bandeja simples com 2 vãos abertos — adoçante, canudo,',
          'palito ou um sachê extra. Mesma altura da parede frontal',
          'do organizador (60 mm), para ficar visualmente alinhada.']),
        (108, 'modulo_suporte_celular', 'mod_celular_alone.png', C_M2,
         'MÓDULO 2 — SUPORTE DE CELULAR/TABLET',
         [('Largura × profundidade × altura', '64 × 70 × 84 mm'),
          ('Inclinação do painel', '28° da vertical'),
          ('Bolso (funda) altura × profundidade', '11 × 15 mm'),
          ('Volume sólido', f'{VOL["modulo_suporte_celular"]:.1f} cm³')],
         ['Painel de 4 mm apoiado num bolso frontal que segura a',
          'borda do aparelho; ranhura central de 10 mm para o cabo',
          'de carga passar por trás. Ajuste o ângulo (TILT2) no script',
          'se preferir mais ou menos reclinado.']),
        (200, 'modulo_porta_bisnaga', 'mod_bisnaga_alone.png', C_M3,
         'MÓDULO 3 — PORTA-BISNAGA',
         [('Largura × profundidade × altura', '60 × 70 × 46 mm'),
          ('Diâmetro interno do copo', '52 mm'),
          ('Furo de dreno', 'Ø 8 mm'),
          ('Volume sólido', f'{VOL["modulo_porta_bisnaga"]:.1f} cm³')],
         ['Copo cilíndrico com 2 recortes laterais para tirar a',
          'bisnaga com os dedos, e furo de dreno no fundo.',
          'Ajuste BOTTLE_D no script para o diâmetro da sua',
          'embalagem antes de imprimir.'])]
for x, key, img, col, title, specs, desc in cols:
    img_fit(img, x, 118, 84, 62)
    swatch(x, 112, col, title)
    y = 104
    for k, v in specs:
        txt(x, y, k, 6.8, col=GRAY); txt(x, y-4.2, v, 8.2, 'DVB'); y -= 11
    y -= 2
    for line in desc:
        txt(x, y, line, 7.2); y -= 4.3
c.showPage()

# ================= FOLHA 3 – IMPRESSÃO =================
frame(3, 'Impressão e montagem')
img_fit('mod_compartimentos_fl.png', 16, 118, 68, 64)
img_fit('mod_celular_fl.png', 90, 118, 68, 64)
img_fit('mod_bisnaga_fl.png', 164, 118, 68, 64)
txt(16, 114, 'Compartimentos', 8.5, 'DVB'); txt(90, 114, 'Suporte de celular', 8.5, 'DVB'); txt(164, 114, 'Porta-bisnaga', 8.5, 'DVB')

data = [['Arquivo STL', 'Medidas (mm)', 'Posição na mesa', 'Sem suporte?'],
        ['organizador_v2_trilhos_2_lados.stl', '228 × 110 × 85', 'fundo na mesa', 'sim'],
        ['modulo_compartimentos_extras.stl', '48 × 70 × 60', 'fundo na mesa', 'sim'],
        ['modulo_suporte_celular.stl', '68 × 70 × 84', 'fundo na mesa', 'sim (painel apoiado)'],
        ['modulo_porta_bisnaga.stl', '64 × 70 × 46', 'fundo na mesa', 'sim']]
tb = Table(data, colWidths=[62*mm, 32*mm, 34*mm, 38*mm])
tb.setStyle(TableStyle([
    ('FONT', (0,0), (-1,0), 'DVB', 7.5), ('FONT', (0,1), (-1,-1), 'DV', 7.2),
    ('BACKGROUND', (0,0), (-1,0), BLACK), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('BACKGROUND', (0,1), (-1,-1), HexColor('#eef0f6')),
    ('GRID', (0,0), (-1,-1), 0.4, HexColor('#888888'))]))
txt(16, 100, 'ARQUIVOS PARA IMPRESSÃO', 9.5, 'DVB')
tw_, th_ = tb.wrapOn(c, 0, 0); tb.drawOn(c, 16*mm, 96*mm - th_)

st = ParagraphStyle('s', fontName='DV', fontSize=7.6, leading=9.8, spaceAfter=2.5)
hh = ParagraphStyle('h', fontName='DVB', fontSize=9.2, leading=11, spaceBefore=3, spaceAfter=1.5, textColor=ACC)
story = [Paragraph('COMO USAR', hh)] + [Paragraph(t, st) for t in [
    '<b>1.</b> Se você já imprimiu o organizador da V1.1, troque só pelo novo '
    '<b>organizador_v2_trilhos_2_lados.stl</b> — o resto do conjunto (base, placa) não muda.',
    '<b>2.</b> Escolha 1, 2 ou os 3 módulos e imprima com as mesmas configurações da V1.1: '
    'PLA/PETG, 4 paredes, 5 camadas de topo/fundo, 15% de preenchimento, sem suporte.',
    '<b>3.</b> Encaixe o primeiro módulo por cima da lateral esquerda do organizador, '
    'deslizando para baixo até o fundo. Para encadear outro, repita o mesmo movimento '
    'encostando na face externa do módulo já encaixado.',
    '<b>4.</b> A ordem dos módulos é livre — organize como preferir. Se algum ficar muito justo '
    'ou muito solto, ajuste a folga (mesma peça de teste da V1.1 serve para calibrar).',
]]
fr = Frame(16*mm, 16*mm, 130*mm, 40*mm, showBoundary=0, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
fr.addFromList(story, c)
c.showPage(); c.save(); print('ok')
