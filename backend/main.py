import os
import signal
from collections import Counter

import uvicorn
from ai import get_synonyms, Glossary
from dossier_parser import analyser_dossier
from fastapi import FastAPI, HTTPException
from parser import analyze_file
from security import validate_path
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
            glossary=Glossary(
                name=request.glossary_name,
                description=request.glossary_description,
            ),
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
    try:
        validated_path = validate_path(path)
        result = analyze_file(validated_path, return_data=True)
        return FileAnalyzeResponse(names=Counter(result["names_list"]))
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))


class FolderAnalyzeResponse(BaseModel):
    files: dict[str, FileAnalyzeResponse]
    names: dict[str, int]


@app.get("/api/analyze/folder")
async def analyze_folder_route(path: str) -> FolderAnalyzeResponse:
    try:
        validated_path = validate_path(path)
        result = analyser_dossier(validated_path, return_data=True)
        # print(result["resultats_fichiers"][0]) # Debug
        return FolderAnalyzeResponse(
            files={
                x["fichier"]: FileAnalyzeResponse(names=Counter(x["data"]["names_list"]))
                for x in result["resultats_fichiers"]
            },
            names=result["compteur_global"],
        )
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/shutdown")
async def shutdown() -> None:
    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)
