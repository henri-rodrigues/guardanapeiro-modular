/* =====================================================================
   Configuração do produto — ajuste aqui sem mexer no resto do código.
   As posições vêm da montagem real do projeto (mm, mesmas do CAD).
   ===================================================================== */
export const WHATSAPP = {
  // Troque pelo número da empresa: DDI + DDD + número, só dígitos.
  numero: '5516997700883',
  saudacao: 'Olá! Gostaria de um orçamento para o Guardanapeiro Modular'
};

// Deslocamento global: o organizador tem os botões de encaixe saindo em x = -4 mm,
// e todos os STL foram exportados com o canto na origem.
export const OFFSET_GLOBAL = 4;

export const PECA_BASE = {
  id: 'organizador',
  nome: 'Organizador (peça base)',
  arquivo: 'modelos/organizador_botoes.stl',
  largura: 228
};

/* Módulos que encaixam na LATERAL ESQUERDA (empilham em fila).
   'ordem' define a sequência do encadeamento: os módulos menores ficam
   junto da peça base e os maiores na ponta, que é o arranjo mais estável.
   Em cada variante, 'largura' é a do corpo, sem a ponta dos botões. */
export const MODULOS_ESQUERDA = [
  {
    id: 'compartimentos',
    nome: 'Compartimentos extras',
    descricao: 'Vãos do mesmo tamanho dos compartimentos de sachê da peça base',
    rotulo: 'Quantidade de vãos',
    ordem: 1,
    padrao: 1,
    variantes: [
      { valor: 1, texto: '1 vão',  arquivo: 'modelos/modulo_compartimentos_1.stl', largura: 58.375,  medidas: '58,4 × 70 × 60 mm' },
      { valor: 2, texto: '2 vãos', arquivo: 'modelos/modulo_compartimentos_2.stl', largura: 112.25,  medidas: '112,3 × 70 × 60 mm' },
      { valor: 3, texto: '3 vãos', arquivo: 'modelos/modulo_compartimentos_3.stl', largura: 166.125, medidas: '166,1 × 70 × 60 mm' }
    ]
  },
  {
    id: 'celular',
    nome: 'Suporte de celular/tablet',
    descricao: 'Pedestal vazado com painel a 26°, rebordo de apoio e passagem de cabo',
    ordem: 2,
    padrao: 1,
    variantes: [
      { valor: 1, texto: 'Único', arquivo: 'modelos/modulo_suporte_celular.stl', largura: 66, medidas: '66 × 70 × 92,5 mm' }
    ]
  },
  {
    id: 'bisnaga',
    nome: 'Porta-bisnaga',
    descricao: 'Corpo retangular com furos cilíndricos, dreno e entalhe de pegada',
    rotulo: 'Quantidade de lugares',
    ordem: 3,
    padrao: 3,
    variantes: [
      { valor: 3, texto: '3 lugares', arquivo: 'modelos/modulo_porta_bisnaga_3.stl', largura: 169.2, medidas: '169,2 × 70 × 46 mm' },
      { valor: 6, texto: '6 lugares', arquivo: 'modelos/modulo_porta_bisnaga_6.stl', largura: 169.2, medidas: '169,2 × 114,8 × 46 mm' }
    ]
  }
];

/* Conjunto do cardápio digital: encaixa na lateral DIREITA.
   A placa é posicionada pela mesma matriz da montagem real (inclinada 12°). */
export const MODULO_CARDAPIO = {
  id: 'cardapio',
  nome: 'Suporte de cardápio digital (QR Code)',
  descricao: 'Base + placa removível de 76 × 140 mm para o QR',
  medidas: '92 × 70 × 111 mm',
  pecas: [
    { arquivo: 'modelos/base_display_botoes.stl', tipo: 'base' },
    { arquivo: 'modelos/placa_cardapio.stl', tipo: 'placa' }
  ]
};

// Constantes da montagem da placa (iguais às do CAD)
export const PLACA = {
  PXC: 268,        // centro x da placa no conjunto
  Y0: 10,          // pivô y
  Z0: 3.8316,      // pivô z
  TILT: 12 * Math.PI / 180,
  ESPESSURA: 8,
  LARGURA: 76
};

export const BASE_CARDAPIO_X = 220;  // x original onde a base começa

/* Onde as artes da marca são aplicadas no organizador (mm, coordenadas do STL).
   O corpo ocupa x de 4 a 224, a parede frontal fica em y = 0 e a do fundo em
   y = 110, com 85 mm de altura. */
export const ARTE = {
  frente: { cx: 114, cz: 32, y: -0.35, largura: 160, altura: 34, normal: [0, -1, 0] },
  fundo:  { cx: 114, cz: 46, y: 110.35, largura: 160, altura: 60, normal: [0, 1, 0] }
};

export const CORES = [
  { id: 'preto',    nome: 'Preto fosco', hex: 0x2b2b30, css: '#2b2b30', rug: 0.85 },
  { id: 'branco',   nome: 'Branco',      hex: 0xe8e8e6, css: '#e8e8e6', rug: 0.7 },
  { id: 'vermelho', nome: 'Vermelho',    hex: 0xb3161f, css: '#b3161f', rug: 0.55 },
  { id: 'amarelo',  nome: 'Amarelo',     hex: 0xe0a300, css: '#e0a300', rug: 0.55 },
  { id: 'cinza',    nome: 'Cinza',       hex: 0x8a8d93, css: '#8a8d93', rug: 0.7 }
];
