"""
Main FastAPI application module.
Provides endpoints for synonym suggestions and file/folder analysis.
"""
import os
import signal
from collections import Counter
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Fix for W4901: Deprecated module 'parser'
# We import the local parser module as code_parser
try:
    sys.path.insert(0, str(Path(__file__).parent))
    # pylint: disable=deprecated-module
    import parser as code_parser
except ImportError:
    # Fallback or error handling if necessary
    pass

from ai import get_synonyms, Glossary
from dossier_parser import analyser_dossier
from security import validate_path


app = FastAPI(title="GlossAI")


class SynonymRequest(BaseModel):
    """Request model for synonym suggestion."""
    # pylint: disable=too-few-public-methods
    glossary_name: str
    glossary_description: str
    term: str
    definition: str | None
    synonyms: list[str]
    context: list[str]


class SynonymResponse(BaseModel):
    """Response model for synonym suggestion."""
    # pylint: disable=too-few-public-methods
    synonyms: list[str]


@app.post("/api/suggest", response_model=SynonymResponse)
async def suggest_synonyms(request: SynonymRequest) -> SynonymResponse:
    """
    Generate synonyms for a given term based on context and glossary.
    """
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
        ) from e


class FileAnalyzeResponse(BaseModel):
    """Response model for file analysis."""
    # pylint: disable=too-few-public-methods
    names: dict[str, int]


@app.get("/api/analyze/file")
async def analyze_file_route(path: str) -> FileAnalyzeResponse:
    """
    Analyze a single file and return name occurrences.
    """
    try:
        validated_path = validate_path(path)
        # Utilisation de code_parser au lieu de l'import direct pour éviter W4901
        result = code_parser.analyze_file(validated_path, return_data=True)
        return FileAnalyzeResponse(names=Counter(result["names_list"]))
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


class FolderAnalyzeResponse(BaseModel):
    """Response model for folder analysis."""
    # pylint: disable=too-few-public-methods
    files: dict[str, FileAnalyzeResponse]
    names: dict[str, int]


@app.get("/api/analyze/folder")
async def analyze_folder_route(path: str) -> FolderAnalyzeResponse:
    """
    Analyze a folder recursively and return stats.
    """
    try:
        validated_path = validate_path(path)
        result = analyser_dossier(validated_path, return_data=True)
        # Le format de retour de analyser_dossier est un dictionnaire complet
        # Nous devons extraire ce qui correspond au modèle FolderAnalyzeResponse
        return FolderAnalyzeResponse(
            files={
                x["fichier"]: FileAnalyzeResponse(
                    names=Counter(x["data"]["names_list"])
                )
                for x in result["resultats_fichiers"]
            },
            names=result["compteur_global"],
        )
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/shutdown")
async def shutdown() -> None:
    """
    Shutdown the server.
    """
    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":
    # Fix W1508: default should be string
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="127.0.0.1", port=port)
