# GlossAI

[![CI](https://img.shields.io/github/actions/workflow/status/embeddings-but3-2025-AIpagnan/GlossAI/publish.yml?branch=main&label=CI&logo=github&style=for-the-badge)](https://github.com/embeddings-but3-2025-AIpagnan/GlossAI/actions)
[![Release](https://img.shields.io/github/v/release/embeddings-but3-2025-AIpagnan/GlossAI?label=version&style=for-the-badge)](https://github.com/embeddings-but3-2025-AIpagnan/GlossAI/releases)
[![Stars](https://img.shields.io/github/stars/embeddings-but3-2025-AIpagnan/GlossAI?style=for-the-badge)](https://github.com/embeddings-but3-2025-AIpagnan/GlossAI/stargazers)

Une solution simple et élégante pour explorer et enrichir des glossaires avec des embeddings et des outils d'IA modernes. GlossAI accélère la création, la recherche et la visualisation de termes spécialisés pour les équipes produit, documentation et recherche.

---

## Aperçu



## Installation

Linux: téléchargez le fichier .AppImage, puis double-cliquez dessus pour lancer l'application.

Windows: téléchargez le fichier .msi, lancez-le puis suivez les instructions d'installation standard.

MacOS : téléchargez le fichier .dmg, lancez-le puis suivez les instructions d'installation standard. Avant de lancer l'application, il faut taper la commande "OLLAMA_HOST=http://127.0.0.1:51824 ollama serve" dans le terminal pour changer le port par défaut  pour pouvoir faire fonctionner le back-end.

Trouvez la dernière version ici : [ici](https://github.com/embeddings-but3-2025-AIpagnan/GlossAI/releases/latest).


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
Sur les pc de L'IUT, il faut utiliser la VM Debian_12_Dev pour avoir les droits administrateur.
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
## 📝 File Formats

### Markdown (Table Format)
```markdown
# My Glossary
### Description
### Export Date:
### Number of Terms:

| Word | Definition | Synonyms |
| --- | --- | --- |
| Example | A representative form | sample, illustration |
```

### JSON Format
```json
{
  "glossary": {
    "name": "Scrabble game",
    "description": "A board game where you use tiles to write words to earn the most points",
    "exportDate": "2025-12-08T13:18:06.794Z",
    "termCount": 6
  },
  "headers": [
    "Word",
    "Definition",
    "Synonyms"
  ],
  "data": [
    [
      "Gameboard",
      "A piece of cardboard painted for the pieces to be played onto it.",
      [
        "board"
      ]
    ],
  ]
}
```
