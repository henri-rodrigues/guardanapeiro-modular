# Guardanapeiro Modular — Landing Page com Configurador 3D

Landing page B2B com visualizador 3D (Three.js + STLLoader + OrbitControls),
troca de módulos/cores em tempo real, simulação de logo e orçamento via WhatsApp.

---

## 1. Estrutura de pastas

```
site-3d/
├── server.js              ← servidor Node/Express (recomendado)
├── server.py              ← alternativa em Python (sem dependências)
├── package.json
├── iniciar.bat            ← Windows: copia STL + instala + sobe o servidor
├── iniciar.sh             ← Linux/macOS
└── public/
    ├── index.html
    ├── css/estilo.css
    ├── js/
    │   ├── config.js      ← número do WhatsApp, módulos, cores  ← EDITE AQUI
    │   ├── viewer.js      ← cena Three.js, luzes, sombras, encaixes
    │   └── app.js         ← painel, estado e link do WhatsApp
    └── modelos/           ← arquivos .STL servidos por HTTP
        ├── organizador_botoes.stl          (peça base — sempre visível)
        ├── base_display_botoes.stl         (cardápio digital)
        ├── placa_cardapio.stl              (placa do QR)
        ├── modulo_compartimentos_extras.stl
        ├── modulo_suporte_celular.stl
        ├── modulo_porta_bisnaga_3.stl
        └── modulo_porta_bisnaga_6.stl
```

> Os STL do projeto **já estão** em `public/modelos/`. Para usar outros, copie da sua pasta:
> `C:\Users\eletrica2\Desktop\Projetos Henri\Site modelo 3d\Modelos` → `public\modelos\`
> (o `iniciar.bat` faz essa cópia automaticamente).

---

## 2. Rodando com Node.js (recomendado)

Pré-requisito: **Node.js 18+** (https://nodejs.org).

```bash
cd site-3d
npm install      # instala express + three
npm start        # sobe em http://localhost:3000
```

No Windows, dê dois cliques em **`iniciar.bat`**: ele copia os STL, roda o `npm install`,
sobe o servidor e já abre o navegador.

Com o Node, o Three.js é servido de `node_modules` em `/vendor/three` — ou seja,
**depois do `npm install` a página funciona sem internet**.

---

## 3. Rodando com Python (sem instalar nada)

```bash
cd site-3d
python server.py          # http://localhost:3000
python server.py 8080     # outra porta
```

Nesse modo o Three.js vem do CDN (unpkg), então é preciso estar **online**.
A página detecta isso sozinha e troca a origem do Three.js automaticamente.

---

## 4. Testando

Abra `http://localhost:3000` e confira:

| O que testar | Esperado |
|---|---|
| Girar/zoom | Arrastar gira, rolagem aproxima, botão direito move |
| Ligar "Compartimentos extras" | Módulo aparece encaixado na lateral esquerda |
| Ligar os dois porta-bisnaga | O segundo desliga o primeiro (são alternativos) |
| Trocar a cor | Todas as peças mudam juntas, na hora |
| Enviar uma logo PNG | Aparece aplicada na face frontal |
| Botão do WhatsApp | Abre o `wa.me` com a mensagem preenchida |

Endpoint auxiliar: `http://localhost:3000/api/modelos` lista os STL encontrados na pasta.

---

## 5. O que editar antes de publicar

**`public/js/config.js`**

```js
export const WHATSAPP = {
  numero: '5516999999999',   // ← DDI + DDD + número, só dígitos
  saudacao: 'Olá! Gostaria de um orçamento para o Guardanapeiro Modular'
};
```

Para acrescentar um módulo novo, basta colocar o `.stl` em `public/modelos/`
e adicionar um item em `MODULOS_ESQUERDA`:

```js
{
  id: 'paliteiro',
  nome: 'Paliteiro',
  descricao: 'Compartimento dedicado para palitos',
  arquivo: '/modelos/modulo_paliteiro.stl',
  largura: 40,               // largura em mm (define o encaixe em fila)
  medidas: '40 × 70 × 45 mm'
}
```

A `largura` é o que posiciona a peça: os módulos são encadeados à esquerda,
um encostando no outro, exatamente como no encaixe real.

---

## 6. Publicando

O conteúdo de `public/` é estático — dá para subir em qualquer hospedagem
(Vercel, Netlify, Hostinger, S3). Só duas observações:

1. Se publicar **sem** Node, remova a pasta `/vendor` do caminho — a página já cai no CDN sozinha.
2. Arquivos `.STL` precisam ser servidos com `Content-Type` que não seja `text/html`;
   em servidores Apache/Nginx, adicione `model/stl` ao mime.types se necessário.

---

## 7. Observações técnicas

- **Posicionamento dos módulos:** as coordenadas em `config.js` (`PLACA`, `BASE_CARDAPIO_X`,
  `OFFSET_GLOBAL`) vêm da montagem real do CAD, então o que aparece na tela é a montagem de verdade,
  não uma aproximação visual.
- **Performance:** os STL do porta-bisnaga têm ~2,8 MB (malha curva). Se a página ficar lenta em
  máquinas fracas, gere versões decimadas (Blender → *Decimate*) para uso exclusivo na web.
- **Sombras:** `PCFSoftShadowMap` com plano receptor invisível (`ShadowMaterial`), para as peças
  "pousarem" na cena sem um chão aparente.
- **Logo:** é uma simulação em plano com textura. Para gravação real em relevo seria preciso
  converter o logo em geometria — posso fazer isso se virar um requisito.
