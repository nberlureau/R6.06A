import os
import signal
from collections import Counter

import uvicorn
from ai import get_synonyms
from dossier_parser import analyser_dossier
from fastapi import FastAPI, HTTPException
from parser import analyze_file
from pydantic import BaseModel

app = FastAPI(title="GlossAI")


class SynonymRequest(BaseModel):
    glossary_name: str
    glossary_description: str
    term: str
    definition: str | None
    synonyms: list[str]
    context: list[str]


class SynonymResponse(BaseModel):
    synonyms: list[str]


@app.post("/api/suggest", response_model=SynonymResponse)
async def suggest_synonyms(request: SynonymRequest) -> SynonymResponse:
    try:
        # Appeler la fonction get_synonyms avec le terme et le contexte
        synonyms = await get_synonyms(
            glossary_name=request.glossary_name,
            glossary_description=request.glossary_description,
            word=request.term,
            definition=request.definition,
            synonyms=request.synonyms,
            context=request.context,
        )

        return SynonymResponse(synonyms=synonyms)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération des suggestions: {e!s}",
        )


class FileAnalyzeResponse(BaseModel):
    names: dict[str, int]


@app.get("/api/analyze/file")
async def analyze_file_route(path: str) -> FileAnalyzeResponse:
    result = analyze_file(path, return_data=True)
    return FileAnalyzeResponse(names=Counter(result["names_list"]))


class FolderAnalyzeResponse(BaseModel):
    files: dict[str, FileAnalyzeResponse]
    names: dict[str, int]


@app.get("/api/analyze/folder")
async def analyze_folder_route(path: str) -> FolderAnalyzeResponse:
    result = analyser_dossier(path, return_data=True)
    print(result["resultats_fichiers"][0])
    return FolderAnalyzeResponse(
        files={
            x["fichier"]: FileAnalyzeResponse(names=Counter(x["data"]["names_list"]))
            for x in result["resultats_fichiers"]
        },
        names=result["compteur_global"],
    )


@app.post("/shutdown")
async def shutdown() -> None:
    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)
