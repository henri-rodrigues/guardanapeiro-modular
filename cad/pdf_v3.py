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
INFO = json.load(open('v3_info.json'))
PW_, PH_ = landscape(A4)
DARK = HexColor('#1c1c20'); ACC = HexColor('#c8102e'); GRAY = HexColor('#555555')
c = canvas.Canvas('/mnt/user-data/outputs/Encaixe_Botao_e_PortaBisnaga.pdf', pagesize=(PW_, PH_))
c.setTitle('Encaixe por botão + porta-bisnaga 3 e 6')

def frame(n, title, total=2):
    c.setStrokeColor(colors.black); c.setLineWidth(1.2)
    c.rect(8*mm, 8*mm, PW_-16*mm, PH_-16*mm)
    c.setFont('DVB', 15); c.setFillColor(colors.black); c.drawString(14*mm, PH_-18*mm, title)
    c.setStrokeColor(ACC); c.setLineWidth(1.5); c.line(14*mm, PH_-20.5*mm, 62*mm, PH_-20.5*mm)
    c.setFont('DV', 7.5); c.setFillColor(GRAY)
    c.drawRightString(PW_-14*mm, PH_-18*mm, f'Folha {n}/{total}  ·  16/09/2026  ·  mm  ·  PLA/PETG')

def txt(x, y, s, size=8, font='DV', col=colors.black):
    c.setFont(font, size); c.setFillColor(col); c.drawString(x*mm, y*mm, s)

def img(path, x, y, w, hmax=None):
    im = ImageReader(path); iw, ih = im.getSize(); h = w*ih/iw
    if hmax and h > hmax: h = hmax; w = h*iw/ih
    c.drawImage(im, x*mm, y*mm, w*mm, h*mm, mask='auto'); return w, h

# ---------- FOLHA 1 – novo encaixe ----------
frame(1, 'Novo encaixe: botão de pressão (substitui o trilho)')
img('v3_org_sem_modulo.png', 14, 96, 128, 86)
txt(16, 91, 'ORGANIZADOR SEM NENHUM MÓDULO', 9.5, 'DVB')
txt(16, 86.5, 'só 4 botões de Ø6,8 mm em cada lateral — quase invisíveis de longe', 7.2, col=GRAY)
img('v3_botao_teste.png', 150, 100, 120, 70)
txt(152, 95, 'PEÇAS DE TESTE DO BOTÃO', 9.5, 'DVB')
txt(152, 90.5, 'macho (3 cabeças: 6,6 / 6,8 / 7,0 mm) e fêmea — 1, 2 e 3 entalhes', 7.2, col=GRAY)

txt(16, 76, 'COMO FUNCIONA', 10, 'DVB')
linhas = [
 'O pino tem pescoço de Ø6,0 mm e cabeça abaulada de Ø6,8 mm. Ele entra num furo de Ø6,2 mm',
 'feito num disco fino de 1,3 mm, que flexiona na hora do encaixe e volta atrás da cabeça, travando.',
 'Depois do disco há um alívio de Ø8,6 mm, onde a cabeça se acomoda sem forçar.',
 'São 4 botões por interface, num retângulo de 34 × 24 mm (y = 18 e 52; z = 9 e 33), o que segura',
 'o módulo contra giro e contra tombamento — mesmo sem trilho contínuo.',
 '',
 'Vantagem em relação ao trilho: quando não há módulo instalado, a lateral fica lisa, com 4 pontinhos',
 'discretos, em vez de um trilho de 24 mm de altura aparecendo na peça.',
 '',
 'Montagem: empurre o módulo de lado contra o organizador até ouvir/sentir o clique (antes era preciso',
 'descer o módulo por cima).',
]
y = 71
for l in linhas:
    txt(16, y, l, 7.6); y -= 4.3
txt(16, 16, 'IMPORTANTE: imprima as duas peças de teste antes dos módulos — elas definem a cabeça certa', 7.6, 'DVB', ACC)
txt(16, 11.5, 'para a sua impressora. Me diga qual das 3 (6,6 / 6,8 / 7,0) travou melhor e eu regero os STL.', 7.6, 'DVB', ACC)
c.showPage()

# ---------- FOLHA 2 – porta-bisnaga ----------
frame(2, 'Porta-bisnaga: versões de 3 e 6 bisnagas')
img('v3_bisnaga3_alone.png', 14, 120, 110, 62)
txt(16, 115, 'VERSÃO A — 3 BISNAGAS EM LINHA', 9.5, 'DVB')
txt(16, 110.5, '165 × 70 × 46 mm  ·  volume sólido ' + f"{INFO['modulo_porta_bisnaga_3']['vol']:.0f} cm³", 7.4, col=GRAY)
img('v3_bisnaga6_alone.png', 150, 120, 110, 62)
txt(152, 115, 'VERSÃO B — 6 BISNAGAS (3 × 2)', 9.5, 'DVB')
txt(152, 110.5, '165 × 111,5 × 46 mm  ·  volume sólido ' + f"{INFO['modulo_porta_bisnaga_6']['vol']:.0f} cm³", 7.4, col=GRAY)

txt(16, 101, 'DETALHES DOS DOIS', 9.5, 'DVB')
for i, l in enumerate([
  '• Copo de Ø52 mm interno e 46 mm de altura — ajuste BOTTLE_D no script se a sua bisnaga for diferente.',
  '• Copos vizinhos compartilham parede de 1,5 mm (centros a 53,5 mm), o que economiza material e espaço.',
  '• Furo de dreno de Ø8 mm no fundo de cada copo.',
  '• Versão A tem recortes laterais para tirar a bisnaga com os dedos; na versão B os copos do meio ficam',
  '   cercados, então a retirada é por cima.',
  '• Ambas têm a mesma interface de botão, então trocam de lugar com qualquer outro módulo.']):
    txt(16, 96 - i*4.3, l, 7.6)

data = [['Arquivo STL', 'Medidas (mm)', 'Observação'],
        ['organizador_botoes.stl', '228 × 110 × 85', 'substitui o da versão anterior'],
        ['base_display_botoes.stl', '92 × 70 × 111', 'bloco de encaixe mais alto (38 mm)'],
        ['placa_cardapio.stl', '76 × 140 × 8', 'não mudou'],
        ['modulo_compartimentos_extras.stl', '48 × 70 × 60', 'agora com botão'],
        ['modulo_suporte_celular.stl', '68 × 70 × 84', 'agora com botão'],
        ['modulo_porta_bisnaga_3.stl', '169 × 70 × 46', 'novo — 3 bisnagas'],
        ['modulo_porta_bisnaga_6.stl', '169 × 111,5 × 46', 'novo — 6 bisnagas'],
        ['teste_botao_macho.stl / femea.stl', '10 × 70 × 22', 'imprima primeiro']]
tb = Table(data, colWidths=[74*mm, 34*mm, 72*mm])
tb.setStyle(TableStyle([
    ('FONT', (0,0), (-1,0), 'DVB', 7.4), ('FONT', (0,1), (-1,-1), 'DV', 7.2),
    ('BACKGROUND', (0,0), (-1,0), DARK), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('BACKGROUND', (0,1), (-1,-1), HexColor('#eef0f6')),
    ('GRID', (0,0), (-1,-1), 0.4, HexColor('#888888'))]))
txt(16, 64, 'ARQUIVOS', 9.5, 'DVB')
tw, th = tb.wrapOn(c, 0, 0); tb.drawOn(c, 16*mm, 60*mm - th)
c.showPage(); c.save(); print('ok')
