# Guardanapeiro Modular Organizador — contexto do projeto

Documento de handoff. Produto físico impresso em 3D **+** landing page com configurador 3D.
Tudo aqui foi gerado num chat anterior; este arquivo existe para retomar o trabalho sem perder contexto.

---

## 1. O produto

Organizador de mesa para bares/lanchonetes/restaurantes, com suporte de cardápio digital (QR Code).
Sistema **modular**: peça base + módulos que encaixam por pressão.

Estado atual (versão vigente = **v3 / encaixe por botão**):

| Peça | Medidas (mm) | Arquivo |
|---|---|---|
| Organizador (peça base) | 228 × 110 × 85 | `stl/organizador_botoes.stl` |
| Base do display (cardápio) | 92 × 70 × 111 | `stl/base_display_botoes.stl` |
| Placa do cardápio (removível) | 76 × 140 × 8 | `stl/placa_cardapio.stl` |
| Módulo compartimentos extras | 48 × 70 × 60 | `stl/modulo_compartimentos_extras.stl` |
| Módulo suporte de celular | 68 × 70 × 84 | `stl/modulo_suporte_celular.stl` |
| Módulo porta-bisnaga 3 | 169 × 70 × 46 | `stl/modulo_porta_bisnaga_3.stl` |
| Módulo porta-bisnaga 6 | 169 × 111,5 × 46 | `stl/modulo_porta_bisnaga_6.stl` |
| Peças de teste do botão | 10 × 70 × 22 | `stl/teste_botao_macho.stl` / `_femea.stl` |

### Decisões de projeto já tomadas
- **Paredes externas 3 mm, internas 1,5 mm** (pedido do cliente na V1.1).
- **Encaixe por botão de pressão** (v3), substituiu a cauda-de-andorinha da V1.1 porque precisava ser
  discreto quando o módulo não está instalado: pescoço Ø6,0 / cabeça Ø6,8 passa por furo Ø6,2 num
  disco flexível de 1,3 mm, com alívio Ø8,6 atrás. 4 botões por interface (y = 18 e 52; z = 9 e 33).
- **Placa do cardápio**: encaixe por pressão em fenda inclinada 12°, folga 0,10 mm/lado na espessura.
- **QR Code e textos em adesivo** (68 × 122 mm), não impressos em relevo — decisão da v2, mantida.
- **Profundidade padrão dos módulos = 70 mm**, para os botões ficarem sempre na mesma posição.
- Módulos se **encadeiam** entre si (cada um tem soquete numa face e botões na outra).

### Pendências conhecidas
1. **Calibração do botão**: o cliente precisa imprimir `teste_botao_macho/femea.stl` (3 cabeças:
   6,6 / 6,8 / 7,0 mm, marcadas com 1/2/3 entalhes) e dizer qual travou melhor. Depois disso,
   **regerar todos os STL** com esse `BTN_HEAD_D` em `cad/parts.py`.
2. Melhorar o **módulo de compartimentos** e o **suporte de celular** (conteúdo interno; já estão
   convertidos para o botão, mas não foram revisados).
3. No site: trocar o número do WhatsApp (placeholder em `site-3d/public/js/config.js`).
4. Opcional: versões decimadas dos STL do porta-bisnaga (~2,8 MB) para a web.

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
| `pdf*.py`, `head3.py`, `pages3.py` | Geração das pranchas técnicas em PDF (reportlab) |

### Como regerar tudo
```bash
cd cad
python -c "
from parts import *
for nome, fn in (('organizador_botoes', organizer_v2), ('base_display_botoes', base),
                 ('placa_cardapio', plate), ('modulo_compartimentos_extras', module_compartimentos),
                 ('modulo_suporte_celular', module_celular),
                 ('modulo_porta_bisnaga_3', module_bisnaga_3),
                 ('modulo_porta_bisnaga_6', module_bisnaga_6)):
    T = to_mesh(fn()); T = T - T.reshape(-1,3).min(0)
    print(nome, check_mesh(T))
    write_stl(T, f'../stl/{nome}.stl', nome)
"
```

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

```bash
cd site-3d && npm install && npm start     # http://localhost:3000
# ou, sem Node:  python server.py
```

- `server.js` (Express) serve `public/`, os `.stl` com CORS liberado e o Three.js de
  `node_modules` em `/vendor/three` (funciona offline após o `npm install`).
- `public/js/config.js` — **ponto de edição principal**: WhatsApp, lista de módulos, cores.
- `public/js/viewer.js` — cena Three.js. As coordenadas de montagem (`PXC = 268`, tilt 12°,
  `OFFSET_GLOBAL = 4`) vêm do CAD, então o 3D da web reproduz a montagem real.
- Os módulos da esquerda são encadeados pela `largura` de cada um; os dois porta-bisnaga são
  mutuamente exclusivos.

---

## 4. Documentação (`docs/`)

| PDF | Conteúdo |
|---|---|
| `Projeto_Organizador_Cardapio_V1-1.pdf` | Pranchas da V1.1 (vistas, cotas, encaixes) |
| `Modulos_Extras.pdf` | Os 3 módulos com a interface antiga (cauda-de-andorinha) |
| `Encaixe_Botao_e_PortaBisnaga.pdf` | **Mais atual**: botão de pressão + porta-bisnaga 3 e 6 |
| `Projeto_Organizador_Cardapio_v2.pdf` | Variante descontinuada (≤ 240 mm / ≤ 45 g) |
| `Projeto_Organizador_Cardapio_Digital.pdf` | Projeto original com ímãs (histórico) |

> Atenção: as pranchas da V1.1 e do `Modulos_Extras` ainda mostram a **cauda-de-andorinha**.
> Se for atualizar a documentação, regerar com o encaixe de botão.

---

## 5. Histórico resumido das versões

1. **V1** — organizador + base + placa presas por **ímãs** Ø10×2.
2. **v2** — variante enxuta: peça única, ≤ 240 mm e ≤ 45 g (paredes 0,8 mm, janelas de alívio).
   Descontinuada, mas foi dela que veio a decisão do QR em adesivo.
3. **V1.1** — volta ao V1 com paredes 3/1,5 mm e ímãs trocados por **cauda-de-andorinha**.
4. **Módulos** — 3 módulos novos + trilhos nos dois lados do organizador.
5. **v3 (atual)** — cauda-de-andorinha trocada por **botão de pressão** (discrição) e porta-bisnaga
   em duas versões (3 e 6 lugares).
