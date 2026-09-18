/**
 * Servidor local do configurador 3D.
 *   node server.js          → http://localhost:3000
 *   PORT=8080 node server.js
 *
 * Serve:
 *   /                → public/index.html
 *   /modelos/*.stl   → public/modelos  (com CORS liberado)
 *   /vendor/three/*  → node_modules/three  (Three.js sem depender de CDN)
 */
const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');
const MODELS_DIR = path.join(PUBLIC_DIR, 'modelos');

// CORS liberado (evita bloqueio ao carregar .stl via fetch/XHR)
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

// .stl precisa de um mime-type que o navegador não tente interpretar como texto
express.static.mime.define({ 'model/stl': ['stl'] });

app.use(express.static(PUBLIC_DIR, { extensions: ['html'] }));
app.use('/modelos', express.static(MODELS_DIR, {
  setHeaders: (res) => res.setHeader('Cache-Control', 'public, max-age=3600')
}));

// Three.js servido localmente (não depende de internet depois do npm install)
const threeDir = path.join(__dirname, 'node_modules', 'three');
if (fs.existsSync(threeDir)) {
  app.use('/vendor/three', express.static(threeDir));
} else {
  console.warn('[aviso] node_modules/three não encontrado — rode "npm install".');
}

// Lista os STLs disponíveis (o front-end usa para saber o que existe na pasta)
app.get('/api/modelos', (req, res) => {
  fs.readdir(MODELS_DIR, (err, files) => {
    if (err) return res.status(500).json({ erro: 'Não foi possível ler a pasta de modelos.' });
    const stls = files.filter((f) => f.toLowerCase().endsWith('.stl'));
    res.json(stls.map((nome) => {
      const { size } = fs.statSync(path.join(MODELS_DIR, nome));
      return { nome, url: `/modelos/${nome}`, tamanhoKB: Math.round(size / 1024) };
    }));
  });
});

app.listen(PORT, () => {
  console.log('\n  Guardanapeiro Modular — configurador 3D');
  console.log(`  Servidor no ar:  http://localhost:${PORT}`);
  console.log(`  Modelos STL em:  ${MODELS_DIR}`);
  console.log('  Ctrl+C para parar.\n');
});
