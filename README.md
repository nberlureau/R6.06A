# GlossAI

Une application en Python **FastAPI** permettant d'implémenter les fonctionnalités intelligentes du LLM.

## Installation

Téléchargez la [dernière version](https://github.com/embeddings-but3-2025-AIpagnan/GlossAI/releases/latest).

**Linux**: double-cliquez sur le fichier téléchargé pour lancer l'application.  
**Windows**: lancez le fichier téléchargé puis suivez les instructions pour installer l'application.

## Développement

### Prérequis
- [Python 3.9+](https://www.python.org/downloads/), ainsi que pip et venv
- [Node.js 18.17.1+](https://nodejs.org/en/download)
- [Rust](https://rust-lang.org/tools/install/)
- Tauri-cli:
  - [Prérequis](https://v2.tauri.app/start/prerequisites/)
  - Puis lancer `cargo install tauri-cli --version "^2.0.0" --locked`
- [Ollama](https://ollama.com/download)

Sur Windows (il faut nécéssairement utiliser Powershell):
- Autoriser l'exécution des scripts avec la commande `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned`

### Linux
```bash
git clone https://github.com/embeddings-but3-2025-AIpagnan/GlossAI.git
cd GlossAI
python3 -m venv .venv
source .venv/bin/activate
npm install
pip install -r backend/requirements.txt
npm run dev
```

### Windows
```bash
git clone https://github.com/embeddings-but3-2025-AIpagnan/GlossAI.git
cd GlossAI
python3 -m venv .venv
.venv/Scripts/Activate.ps1
npm install
pip install -r backend/requirements.txt
npm run dev
```
