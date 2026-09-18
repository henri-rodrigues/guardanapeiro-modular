#!/usr/bin/env bash
# Guardanapeiro Modular - configurador 3D (Linux/macOS)
set -e
cd "$(dirname "$0")"
echo "[1/2] Instalando dependências..."
npm install --no-fund --no-audit
echo "[2/2] Subindo servidor em http://localhost:3000"
npm start
