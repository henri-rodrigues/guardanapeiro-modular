"""Monta o catálogo-conceito em PDF a partir dos renders de catalog_render.py.

É um material de apresentação para o time de vendas: mostra o produto
montado num cenário de bar, as opções de módulo, a personalização por
cor/logo e as especificações técnicas — com a marca de demonstração
definida em catalog_render.MARCA (troque por um cliente real e rode os
dois scripts de novo para gerar a versão personalizada dele).

Uso:  python catalog_render.py && python catalog_pdf.py
Saída: ../docs/Catalogo_Conceito_<marca>.pdf
"""
import os
import re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

from catalog_render import MARCA, CORES, OUT, FONT_BOLD, FONT_REG
from parts import (OW, OD, H_FRONT, H_BACK, TE, TI, N_COMP, M2_W, BTN_HEAD_D,
                    m1_width, module_bisnaga_grid)

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, '..', 'docs')
os.makedirs(DOCS, exist_ok=True)

# ---------------------------------------------------------------------
# fontes (TTF do Windows, para acentuação correta; cai pro Helvetica padrão
# do reportlab se não achar nenhuma)
# ---------------------------------------------------------------------
FONT, FONTB = 'Helvetica', 'Helvetica-Bold'
if FONT_REG and FONT_BOLD:
    try:
        pdfmetrics.registerFont(TTFont('Corpo', FONT_REG))
        pdfmetrics.registerFont(TTFont('CorpoB', FONT_BOLD))
        FONT, FONTB = 'Corpo', 'CorpoB'
    except Exception:
        pass

PW, PH = landscape(A4)

PRIM = HexColor(MARCA['primaria'])
SEC = HexColor(MARCA['secundaria'])
INK = HexColor('#1c1c20')
PAPER = HexColor('#f6f4ef')
GRAY = HexColor('#6b6b72')
LINE = HexColor('#d8d5cc')

slug = re.sub(r'[^a-z0-9]+', '_', MARCA['nome'].lower()).strip('_')
OUT_PDF = os.path.join(DOCS, f'Catalogo_Conceito_{slug}.pdf')
c = canvas.Canvas(OUT_PDF, pagesize=(PW, PH))
c.setTitle(f"Catálogo Conceito — Guardanapeiro Modular ({MARCA['nome']})")
c.setAuthor('Guardanapeiro Modular')

def asset(nome):
    return os.path.join(OUT, nome)

def img_fit(path, x, y, w, h, align='center'):
    """desenha a imagem inteira dentro da caixa (x,y,w,h), sem distorcer."""
    im = ImageReader(path); iw, ih = im.getSize()
    k = min(w / iw, h / ih)
    dw, dh = iw * k, ih * k
    dx = x + (w - dw) / 2 if align == 'center' else x
    dy = y + (h - dh) / 2
    c.drawImage(im, dx, dy, dw, dh, mask='auto')
    return dx, dy, dw, dh

def img_cover(path, x, y, w, h):
    """preenche a caixa inteira, cortando o excesso (fundo/hero full-bleed)."""
    im = ImageReader(path); iw, ih = im.getSize()
    k = max(w / iw, h / ih)
    dw, dh = iw * k, ih * k
    c.saveState()
    p = c.beginPath(); p.rect(x, y, w, h); c.clipPath(p, stroke=0, fill=0)
    c.drawImage(im, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, mask='auto')
    c.restoreState()

def texto(x, y, s, size=9, font=FONT, col=INK, leading=None, w=None, align='left'):
    c.setFont(font, size); c.setFillColor(col)
    if w is None:
        (c.drawString if align == 'left' else c.drawCentredString if align == 'center' else c.drawRightString)(
            x, y, s)
        return y
    words = s.split(); linhas, cur = [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if c.stringWidth(t, font, size) <= w:
            cur = t
        else:
            linhas.append(cur); cur = wd
    if cur: linhas.append(cur)
    ld = leading or size * 1.4
    for i, l in enumerate(linhas):
        c.drawString(x, y - i * ld, l)
    return y - len(linhas) * ld

def rotulo(x, y, s, size=8.5, col=PRIM):
    c.setFillColor(col); c.setFont(FONTB, size)
    c.drawString(x, y, s.upper())
    c.setLineWidth(1.1); c.setStrokeColor(col)
    w = c.stringWidth(s.upper(), FONTB, size)
    c.line(x, y - 3.2, x + min(w, 26 * mm), y - 3.2)

def rodape(pagina, total=7):
    c.setFont(FONT, 7); c.setFillColor(GRAY)
    c.drawString(12 * mm, 8 * mm, 'Guardanapeiro Modular — catálogo conceito para apresentação')
    c.drawRightString(PW - 12 * mm, 8 * mm, f'{pagina:02d} / {total:02d}')

def fundo(cor=PAPER):
    c.setFillColor(cor); c.rect(0, 0, PW, PH, fill=1, stroke=0)

# =======================================================================
# 1) CAPA
# =======================================================================
fundo(SEC)
img_cover(asset('hero_balcao.png'), 0, 0, PW, PH)
c.setFillColor(colors.Color(0, 0, 0, alpha=0.42))
c.rect(0, 0, PW, PH, fill=1, stroke=0)
c.setFillColor(colors.Color(0, 0, 0, alpha=0.55))
c.rect(0, 0, PW, 66 * mm, fill=1, stroke=0)

c.setFillColor(PRIM); c.setFont(FONTB, 10.5)
c.drawString(14 * mm, 52 * mm, f"PERSONALIZADO PARA {MARCA['nome']}".upper())
c.setFillColor(colors.white); c.setFont(FONTB, 34)
c.drawString(14 * mm, 38 * mm, 'GUARDANAPEIRO MODULAR')
c.setFont(FONT, 13)
c.drawString(14 * mm, 28 * mm, 'Catálogo conceito — organizador de mesa com cardápio digital')
c.setFont(FONT, 9.5); c.setFillColor(HexColor('#d8d8dc'))
c.drawString(14 * mm, 20 * mm, 'Sistema modular · encaixe por botão de pressão · impresso em 3D · PLA/PETG')
c.setFont(FONT, 8.5); c.setFillColor(HexColor('#b8b8be'))
c.drawString(14 * mm, 13 * mm, 'Material de apoio para equipe de vendas — exemplo de personalização com a marca do cliente')
c.showPage()

# =======================================================================
# 2) SUMÁRIO + SOBRE
# =======================================================================
fundo()
c.setFillColor(INK); c.setFont(FONTB, 26)
c.drawString(14 * mm, PH - 24 * mm, 'SUMÁRIO')
itens = [
    ('01', 'Sobre o produto', 'Sistema modular e como funciona'),
    ('02', 'O produto em uso', 'Visualização no ambiente de bar/restaurante'),
    ('03', 'Módulos disponíveis', 'Compartimentos, celular e porta-bisnaga'),
    ('04', 'Personalização', 'Cores, logo do cliente e número da mesa'),
    ('05', 'Especificações', 'Medidas, materiais e o encaixe por botão'),
    ('06', 'Como pedir', 'Configurador online e contato comercial'),
]
y = PH - 46 * mm
for num, tit, desc in itens:
    c.setFont(FONTB, 20); c.setFillColor(PRIM); c.drawString(14 * mm, y, num)
    c.setFont(FONTB, 12.5); c.setFillColor(INK); c.drawString(26 * mm, y + 3.2 * mm, tit)
    c.setFont(FONT, 8.8); c.setFillColor(GRAY); c.drawString(26 * mm, y - 2 * mm, desc)
    c.setStrokeColor(LINE); c.setLineWidth(0.6); c.line(14 * mm, y - 6 * mm, 100 * mm, y - 6 * mm)
    y -= 15 * mm

rotulo(120 * mm, PH - 24 * mm, 'Sobre o produto')
sobre = (
    "O Guardanapeiro Modular organiza a mesa do bar ou restaurante e ainda serve de suporte "
    "para o cardápio digital via QR Code. É um sistema modular: a peça base já resolve "
    "guardanapos e sachês, e o cliente escolhe quais módulos fazem sentido para a operação — "
    "compartimentos extras, suporte de celular/tablet ou porta-bisnaga."
)
y2 = texto(120 * mm, PH - 34 * mm, sobre, size=9.3, w=176 * mm, leading=13.2, col=INK)
sobre2 = (
    "Os módulos encaixam por pressão, num botão discreto que só aparece como 4 pontinhos "
    "quando não há módulo instalado — sem trilhos ou peças salientes à mostra. Toda a peça "
    "pode sair na cor e com a logo do estabelecimento, incluindo o número da mesa no fundo."
)
texto(120 * mm, y2 - 6 * mm, sobre2, size=9.3, w=176 * mm, leading=13.2, col=INK)

img_fit(asset('modulo_bisnaga_3.png'), 120 * mm, 16 * mm, 56 * mm, 46 * mm)
img_fit(asset('modulo_celular.png'), 180 * mm, 16 * mm, 56 * mm, 46 * mm)
img_fit(asset('modulo_compartimentos_2.png'), 240 * mm, 16 * mm, 56 * mm, 46 * mm)
rodape(2)
c.showPage()

# =======================================================================
# 3) O PRODUTO EM USO (hero full-bleed + callouts)
# =======================================================================
fundo(SEC)
img_cover(asset('hero_balcao_alt.png'), 0, 0, PW, PH)
c.setFillColor(colors.Color(0, 0, 0, alpha=0.28)); c.rect(0, 0, PW, PH, fill=1, stroke=0)
rotulo(14 * mm, PH - 18 * mm, 'O produto em uso', col=PRIM)
c.setFont(FONTB, 20); c.setFillColor(colors.white)
c.drawString(14 * mm, PH - 28 * mm, 'Feito para o balcão — não só para a mesa')
texto(14 * mm, PH - 36 * mm, 'Compacto, resistente à limpeza diária e discreto quando nenhum módulo extra está instalado.',
      size=9.5, w=110 * mm, col=HexColor('#e8e6e0'), leading=13)
rodape(3)
c.showPage()

# =======================================================================
# 4) MÓDULOS DISPONÍVEIS (grade tipo "spec sheet")
# =======================================================================
fundo()
rotulo(14 * mm, PH - 18 * mm, 'Módulos disponíveis')
c.setFont(FONTB, 22); c.setFillColor(INK)
c.drawString(14 * mm, PH - 28 * mm, 'Cada operação escolhe os seus')
texto(14 * mm, PH - 36 * mm,
      'Todos os módulos usam a mesma interface de botão de pressão e podem ser combinados livremente.',
      size=9.3, w=180 * mm, col=GRAY)

W3, W6 = module_bisnaga_grid(3, 1)[1], module_bisnaga_grid(3, 2)[1]
CARDS = [
    ('modulo_compartimentos_1.png', 'Compartimentos extras', '1, 2 ou 3 vãos', f'{m1_width(1):.0f}–{m1_width(3):.0f} × 70 × 60 mm',
     'Mesmo tamanho de vão dos compartimentos de sachê da peça base — a quantidade é escolhida pelo cliente.'),
    ('modulo_celular.png', 'Suporte de celular/tablet', 'tamanho único', f'{M2_W:.0f} × 70 × 92,5 mm',
     'Pedestal vazado com painel a 26°, rebordo de apoio e passagem de cabo para carregar sem tirar o aparelho.'),
    ('modulo_bisnaga_3.png', 'Porta-bisnaga · 3 lugares', '1 fileira', f'{W3:.0f} × 70 × 46 mm',
     'Corpo retangular com furos cilíndricos, dreno no fundo e entalhe para retirar a bisnaga com os dedos.'),
    ('modulo_bisnaga_6.png', 'Porta-bisnaga · 6 lugares', '3 × 2', f'{W6:.0f} × 114,8 × 46 mm',
     'Mesma peça em dobro — para bares com mais variedade de molhos por mesa.'),
]
cx0, cy0, cw, gap = 14 * mm, PH - 52 * mm, 62 * mm, 7 * mm
for i, (png, nome, tam, medidas, desc) in enumerate(CARDS):
    x = cx0 + i * (cw + gap)
    c.setFillColor(colors.white); c.setStrokeColor(LINE); c.setLineWidth(0.7)
    c.roundRect(x, 14 * mm, cw, cy0 - 6 * mm, 3 * mm, fill=1, stroke=1)
    img_fit(asset(png), x + 3 * mm, cy0 - 44 * mm, cw - 6 * mm, 40 * mm)
    c.setFont(FONTB, 10.2); c.setFillColor(INK)
    texto(x + 4 * mm, cy0 - 49 * mm, nome, size=10.2, font=FONTB, w=cw - 8 * mm, leading=12)
    c.setFont(FONT, 8); c.setFillColor(PRIM)
    c.drawString(x + 4 * mm, cy0 - 58 * mm, tam)
    c.setFont(FONT, 7.6); c.setFillColor(GRAY)
    c.drawString(x + 4 * mm, cy0 - 63 * mm, medidas)
    texto(x + 4 * mm, cy0 - 69 * mm, desc, size=7.6, w=cw - 8 * mm, leading=9.6, col=INK)
rodape(4)
c.showPage()

# =======================================================================
# 5) PERSONALIZAÇÃO — cores, logo, número da mesa
# =======================================================================
fundo()
rotulo(14 * mm, PH - 18 * mm, 'Personalização')
c.setFont(FONTB, 22); c.setFillColor(INK)
c.drawString(14 * mm, PH - 28 * mm, 'A cor e a logo do seu bar, sem custo extra de projeto')
texto(14 * mm, PH - 36 * mm,
      f"Exemplo abaixo com a marca demonstrativa “{MARCA['nome']}” — no configurador do site, "
      "basta o cliente enviar a logo: o próprio sistema escolhe as cores e o estilo da arte automaticamente.",
      size=9.3, w=184 * mm, col=GRAY, leading=12.6)

img_fit(asset('packshot_marca.png'), 14 * mm, 16 * mm, 118 * mm, 138 * mm)
img_fit(asset('verso_mesa_logo.png'), 138 * mm, 22 * mm, 82 * mm, 128 * mm)
texto(138 * mm, 18 * mm, 'Fundo da peça: logo + número da mesa (demonstrativo)', size=7.6, col=GRAY, w=82 * mm)

rotulo(228 * mm, PH - 46 * mm, 'Cores de linha', size=8, col=PRIM)
yy = PH - 54 * mm
for nome, hx in CORES.items():
    if nome == 'marca':
        continue
    c.setFillColor(HexColor(hx)); c.setStrokeColor(LINE); c.setLineWidth(0.6)
    c.roundRect(228 * mm, yy - 8 * mm, 10 * mm, 10 * mm, 2 * mm, fill=1, stroke=1)
    c.setFont(FONT, 8.6); c.setFillColor(INK)
    c.drawString(241 * mm, yy - 4 * mm, nome.capitalize())
    yy -= 14 * mm
texto(228 * mm, yy - 4 * mm, 'Também sai em qualquer cor RAL equivalente ao filamento disponível.',
      size=7.4, w=54 * mm, col=GRAY, leading=9.4)
rodape(5)
c.showPage()

# =======================================================================
# 6) ESPECIFICAÇÕES TÉCNICAS
# =======================================================================
fundo()
rotulo(14 * mm, PH - 18 * mm, 'Especificações')
c.setFont(FONTB, 22); c.setFillColor(INK)
c.drawString(14 * mm, PH - 28 * mm, 'Feito para durar no dia a dia do salão')

esp = [
    ('Peça base', f'{OW:.0f} × {OD:.0f} × {H_BACK:.0f} mm'),
    ('Paredes', f'{TE:.1f} mm externas · {TI:.1f} mm internas'),
    ('Compartimentos de sachê', f'{N_COMP} vãos na peça base'),
    ('Encaixe dos módulos', f'botão de pressão, cabeça Ø{BTN_HEAD_D:.1f} mm — 4 pontos por interface'),
    ('Cardápio digital', 'placa removível 76 × 140 × 8 mm, inclinada 12°'),
    ('Material', 'PLA ou PETG, impresso em 3D'),
    ('Acabamento', 'QR Code e textos em adesivo (não impressos em relevo)'),
    ('Personalização', 'cor de linha, cor sob medida ou logo do cliente'),
]
y = PH - 42 * mm
for k, v in esp:
    c.setFont(FONTB, 9); c.setFillColor(PRIM); c.drawString(14 * mm, y, k.upper())
    c.setFont(FONT, 9.3); c.setFillColor(INK); c.drawString(80 * mm, y, v)
    c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(14 * mm, y - 4 * mm, 176 * mm, y - 4 * mm)
    y -= 11 * mm

img_fit(asset('cor_preto.png'), 190 * mm, PH - 80 * mm, 48 * mm, 48 * mm)
img_fit(asset('cor_branco.png'), 190 * mm, PH - 130 * mm, 48 * mm, 48 * mm)
img_fit(asset('cor_vermelho.png'), 242 * mm, PH - 80 * mm, 48 * mm, 48 * mm)
img_fit(asset('cor_amarelo.png'), 242 * mm, PH - 130 * mm, 48 * mm, 48 * mm)

rotulo(14 * mm, y - 4 * mm, 'Por que o botão de pressão', size=8, col=PRIM)
bullets = [
    'Discreto: sem módulo instalado, a lateral fica lisa — só 4 pontinhos de Ø6,8 mm em vez de um trilho aparente.',
    'Firme: 4 botões por interface travam contra giro e contra tombamento do módulo.',
    'Modular de verdade: qualquer módulo encaixa em qualquer lateral, na mesma posição padrão.',
]
yb = y - 12 * mm
for b in bullets:
    c.setFillColor(PRIM); c.circle(15.2 * mm, yb + 1.3 * mm, 0.9 * mm, fill=1, stroke=0)
    yb = texto(19 * mm, yb, b, size=8.4, w=155 * mm, col=INK, leading=11) - 3 * mm
rodape(6)
c.showPage()

# =======================================================================
# 7) COMO PEDIR (contracapa)
# =======================================================================
fundo(SEC)
c.setFillColor(colors.white); c.setFont(FONTB, 26)
c.drawCentredString(PW / 2, PH - 46 * mm, 'PRONTO PARA PERSONALIZAR')
c.setFont(FONT, 11); c.setFillColor(HexColor('#d8d8dc'))
c.drawCentredString(PW / 2, PH - 56 * mm,
                     'Monte a configuração no site — cor, módulos e logo — e envie o orçamento pelo WhatsApp.')

box_w, box_h = 150 * mm, 60 * mm
bx, by = (PW - box_w) / 2, PH - 140 * mm
c.setFillColor(colors.white); c.roundRect(bx, by, box_w, box_h, 4 * mm, fill=1, stroke=0)
c.setFillColor(PRIM); c.setFont(FONTB, 10)
c.drawString(bx + 8 * mm, by + box_h - 12 * mm, 'CONFIGURADOR 3D')
c.setFillColor(INK); c.setFont(FONT, 9.3)
c.drawString(bx + 8 * mm, by + box_h - 20 * mm, 'henri-rodrigues.github.io/guardanapeiro-modular')
c.setFillColor(PRIM); c.setFont(FONTB, 10)
c.drawString(bx + 8 * mm, by + box_h - 34 * mm, 'CONTATO COMERCIAL')
c.setFillColor(INK); c.setFont(FONT, 9.3)
c.drawString(bx + 8 * mm, by + box_h - 42 * mm, 'WhatsApp: +55 16 99770-0883')
c.setFillColor(GRAY); c.setFont(FONT, 8)
c.drawString(bx + 8 * mm, by + 6 * mm, 'Amostras físicas e prazos sob consulta — peças impressas sob encomenda.')

c.setFillColor(HexColor('#b8b8be')); c.setFont(FONT, 8)
c.drawCentredString(PW / 2, 12 * mm, 'Guardanapeiro Modular · catálogo conceito · uso interno da equipe de vendas')
c.showPage()

c.save()
print('PDF gerado em', OUT_PDF)
