# Guardanapeiro Modular Organizador — contexto do projeto

Documento de handoff. Produto físico impresso em 3D **+** landing page com configurador 3D.
Tudo aqui foi gerado num chat anterior; este arquivo existe para retomar o trabalho sem perder contexto.

---

## 1. O produto

Organizador de mesa para bares/lanchonetes/restaurantes, com suporte de cardápio digital (QR Code).
Sistema **modular**: peça base + módulos que encaixam por pressão.

Estado atual (versão vigente = **v4 / módulos refinados**):

| Peça | Medidas (mm) | Arquivo |
|---|---|---|
| Organizador (peça base) | 228 × 110 × 85 | `stl/organizador_botoes.stl` |
| Base do display (cardápio) | 92 × 70 × 111 | `stl/base_display_botoes.stl` |
| Placa do cardápio (removível) | 76 × 140 × 8 | `stl/placa_cardapio.stl` |
| Módulo compartimentos — 1 / 2 / 3 vãos | 58,4 / 112,3 / 166,1 × 70 × 60 | `stl/modulo_compartimentos_1.stl` / `_2.stl` / `_3.stl` |
| Módulo suporte de celular/tablet | 66 × 70 × 92,5 | `stl/modulo_suporte_celular.stl` |
| Módulo porta-bisnaga 3 | 169,2 × 70 × 46 | `stl/modulo_porta_bisnaga_3.stl` |
| Módulo porta-bisnaga 6 | 169,2 × 114,8 × 46 | `stl/modulo_porta_bisnaga_6.stl` |
| Peças de teste do botão | 10 × 70 × 22 | `stl/teste_botao_macho.stl` / `_femea.stl` |

### Decisões de projeto já tomadas
- **Paredes externas 3 mm, internas 1,5 mm** (pedido do cliente na V1.1).
- **Encaixe por botão de pressão** (v3), substituiu a cauda-de-andorinha da V1.1 porque precisava ser
  discreto quando o módulo não está instalado: pescoço Ø6,0 / cabeça Ø6,8 passa por furo Ø6,2 num
  disco flexível de 1,3 mm, com alívio Ø8,6 atrás. 4 botões por interface (y = 18 e 52; z = 9 e 33).
  **`BTN_HEAD_D = 6,8 mm` já é o valor calibrado/definitivo** (`cad/parts.py`) — o cliente testou as
  3 cabeças e confirmou; não regerar com outro valor sem confirmação nova.
- **Placa do cardápio**: encaixe por pressão em fenda inclinada 12°, folga 0,10 mm/lado na espessura.
- **QR Code e textos em adesivo** (68 × 122 mm), não impressos em relevo — decisão da v2, mantida.
- **Profundidade padrão dos módulos = 70 mm**, para os botões ficarem sempre na mesma posição.
- Módulos se **encadeiam** entre si (cada um tem soquete numa face e botões na outra).
- **v4 — compartimentos com quantidade escolhível**: `module_compartimentos(n)` gera 1/2/3 vãos, cada
  um do **mesmo tamanho** dos compartimentos de sachê da peça base (`COMP_W`, derivado de `OW`/`N_COMP`
  em `parts.py`) — não é mais um módulo de tamanho fixo.
- **v4 — porta-bisnaga com corpo retangular**: paredes externas retas (não mais um bloco cilíndrico
  aparente) com furos internos cilíndricos; ver `module_bisnaga_grid()` em `parts.py`.
- **v4 — suporte de celular/tablet redesenhado**: pedestal vazado por um arco (`arch_poly`, auto-
  sustentado na impressão), painel a 26° com janela de alívio, rebordo de apoio (`LIP_*`) e passagem
  de cabo — inspirado em suportes de tablet/notebook de metal (referências do cliente).

### Pendências conhecidas
1. Opcional: versões decimadas dos STL do porta-bisnaga (~2,8 MB) para a web.
2. Regerar as pranchas técnicas em PDF (`docs/`) com a geometria v4 — as pranchas atuais ainda
   mostram os módulos da v3 (compartimentos de tamanho fixo, bisnaga "maciça", celular antigo).

---

## 2. CAD paramétrico (`cad/`)

**Não há Blender/OpenSCAD/trimesh neste projeto.** A geometria é gerada por um motor CSG próprio,
escrito do zero em Python puro.

| Arquivo | Papel |
|---|---|
| `csg.py` | Motor CSG (BSP, porte do csg.js): `union`, `subtract`, primitivas `box`/`prism`/`loft_x`, `to_mesh` (triangulação com vértice central, corrige T-junctions), `check_mesh` (valida malha fechada + volume), `write_stl` |
| `parts.py` | **Arquivo principal.** Todos os parâmetros e todas as peças |
| `assemble.py` | Transformações de montagem (ex.: `plate_world`) e teste de interferência |
| `raster.py` | Rasterizador z-buffer próprio (numpy) para renders isométricos |
| `views.py`, `mod_views*.py`, `ortho.py` | Cenas e renders (isométricos e vistas ortográficas) |
| `pdf*.py`, `head3.py`, `pages3.py` | Geração das pranchas técnicas em PDF (reportlab) — **desatualizados para a v4**, ver pendência #2 |
| `catalog_render.py` | Renders isométricos do catálogo-conceito (produto num balcão de bar estilizado, packshots, módulos isolados, paleta de cores) — usa o mesmo `raster.py` |
| `catalog_pdf.py` | Monta o catálogo-conceito em PDF a partir dos renders acima (reportlab) — ver seção 4 |

### Como regerar tudo
```bash
cd cad
python gerar_stl.py
```
(gera todos os STL de produção em `../stl/`, incluindo os 3 tamanhos de compartimentos, e valida
cada malha com `check_mesh`; ver também `check_modules.py` para o teste de interferência dos encaixes)

### Regras importantes ao mexer no CAD
- **Sempre validar com `check_mesh`**: `bad_edges` tem que ser `0`. Já apareceram dois bugs por
  causa disso — orientação invertida no `loft_x` espelhado (volume negativo) e círculos de 32 lados
  criando slivers no boolean (resolvido usando 24 lados).
- **Testar interferência** entre peças montadas (`check_modules.py`). O resultado esperado do botão
  encaixado é **0 mm³**: a interferência do snap existe só durante a inserção, não na posição final.
- `union_all` recebe **lista de sólidos**; `union` recebe dois sólidos. `button_pair` devolve lista
  de sólidos (uma armadilha que já causou erro).
- Dependências: `numpy`, `scipy` (KDTree para soldar vértices), `Pillow`, `reportlab`.

---

## 3. Site (`site-3d/`)

Landing page B2B + configurador 3D. Ver `site-3d/README.md` para o passo a passo completo.
**No ar em produção**: https://henri-rodrigues.github.io/guardanapeiro-modular/ (GitHub Pages,
deploy automático via `.github/workflows/pages.yml` a cada push em `main` que toque `site-3d/public/**`).
Repositório: https://github.com/henri-rodrigues/guardanapeiro-modular (público).

```bash
cd site-3d && npm install && npm start     # http://localhost:3000
# ou, sem Node:  python server.py
```

- `server.js` (Express) serve `public/`, os `.stl` com CORS liberado e o Three.js de
  `node_modules` em `/vendor/three` (funciona offline após o `npm install`). Em produção
  (GitHub Pages, sem servidor Node) o Three.js vem de `public/vendor/three` — **versionado no
  repo**, veja `index.html`: o import map é **estático** e os specifiers têm que começar com
  `./` (specifier "nu" tipo `vendor/...` é rejeitado pelo browser como bare specifier).
- `public/js/config.js` — **ponto de edição principal**: WhatsApp, lista de módulos (com
  `variantes` de quantidade — compartimentos 1/2/3, bisnaga 3/6), cores, posição das artes
  de marca (`ARTE.frente`/`ARTE.fundo`).
- `public/js/viewer.js` — cena Three.js. As coordenadas de montagem (`PXC = 268`, tilt 12°,
  `OFFSET_GLOBAL = 4`) vêm do CAD, então o 3D da web reproduz a montagem real. Módulos são
  encadeados por `ordem` (não mais pela ordem de declaração) e cada um guarda sua variante ativa.
- `public/js/marca.js` — **extrai a paleta de cor da logo enviada** (cores dominantes por matiz/
  saturação) e desenha as artes (faixa da frente + painel do fundo com número da mesa) em
  `<canvas>`, aplicadas como decalque na peça 3D e retematizando a própria página (CSS vars
  `--acc`/`--acc2`/...). Sem logo, usa a cor de peça escolhida (`paletaNeutra`).
- Os módulos da esquerda são encadeados pela `largura` da variante ativa; os dois porta-bisnaga
  são mutuamente exclusivos.

---

## 4. Documentação (`docs/`)

| PDF | Conteúdo |
|---|---|
| `Catalogo_Conceito_brasa_bar.pdf` | **Catálogo-conceito de vendas** (não técnico): produto em cena de balcão de bar, módulos, personalização por cor/logo, especificações — gerado por `cad/catalog_render.py` + `cad/catalog_pdf.py` com uma marca de demonstração (`MARCA` em `catalog_render.py`). Para gerar a versão de um cliente real, troque `MARCA` (nome/cores/mesa) e rode os dois scripts de novo. |
| `Projeto_Organizador_Cardapio_V1-1.pdf` | Pranchas da V1.1 (vistas, cotas, encaixes) |
| `Modulos_Extras.pdf` | Os 3 módulos com a interface antiga (cauda-de-andorinha) |
| `Encaixe_Botao_e_PortaBisnaga.pdf` | Botão de pressão + porta-bisnaga 3 e 6 (geometria v3) |
| `Projeto_Organizador_Cardapio_v2.pdf` | Variante descontinuada (≤ 240 mm / ≤ 45 g) |
| `Projeto_Organizador_Cardapio_Digital.pdf` | Projeto original com ímãs (histórico) |

> Atenção: as pranchas técnicas (`V1-1`, `Modulos_Extras`, `Encaixe_Botao_e_PortaBisnaga`) mostram
> geometria de versões anteriores (cauda-de-andorinha ou módulos v3). Só o catálogo-conceito e os
> STL em `stl/` refletem a v4 atual.

---

## 5. Histórico resumido das versões

1. **V1** — organizador + base + placa presas por **ímãs** Ø10×2.
2. **v2** — variante enxuta: peça única, ≤ 240 mm e ≤ 45 g (paredes 0,8 mm, janelas de alívio).
   Descontinuada, mas foi dela que veio a decisão do QR em adesivo.
3. **V1.1** — volta ao V1 com paredes 3/1,5 mm e ímãs trocados por **cauda-de-andorinha**.
4. **Módulos** — 3 módulos novos + trilhos nos dois lados do organizador.
5. **v3** — cauda-de-andorinha trocada por **botão de pressão** (discrição, `BTN_HEAD_D` calibrado
   em 6,8 mm) e porta-bisnaga em duas versões (3 e 6 lugares).
6. **v4 (atual)** — compartimentos extras com **quantidade escolhível** (mesmo tamanho de vão da
   peça base), porta-bisnaga com **corpo retangular** e furos cilíndricos, suporte de celular/tablet
   **redesenhado** (pedestal vazado + rebordo). Site publicado no GitHub Pages, com **tema e artes
   de marca extraídos automaticamente da logo do cliente**. Catálogo-conceito de vendas em PDF.
