"""
Module providing AI functionality for synonym generation using Ollama.
"""
import asyncio
from dataclasses import dataclass
import ollama
from ollama import AsyncClient

# OCP pas respecté si l'objectif est de pouvoir modifier le modèle.
MODEL = "qwen3:0.6b"


@dataclass
class Glossary:
    """Dataclass representing glossary information."""
    name: str
    description: str


async def get_synonyms(
    glossary: Glossary,
    word: str,
    definition: str | None,
    synonyms: list[str],
    context: list[str],
) -> list[str]:
    """
    Generate synonyms for a word using the provided glossary context.

    Args:
        glossary: The glossary information containing name and description.
        word: The word to find synonyms for.
        definition: The definition of the word, or None.
        synonyms: List of already known synonyms.
        context: List of context words.

    Returns:
        List of suggested synonyms.
    """
    try:
        ollama.show(MODEL)
    except Exception:
        ollama.pull(MODEL)

    word = word.strip().lower()
    synonyms = [synonym.strip().lower() for synonym in synonyms if synonym.strip()]

    description_text = (
        "> " + "\n > ".join(glossary.description.split("\n"))
        if glossary.description else "No description"
    )

    definition_text = (
        f" as defined by:\n> {'\n > '.join(definition.split('\n'))}"
        if definition else "."
    )

    known_synonyms_text = (
        f"Already known synonyms for the correct sense of the word: {', '.join(synonyms)}"
        if synonyms else ""
    )

    prompt = f"""
In a ubiquitous language glossary named "{glossary.name}" and with the following description:
{description_text}

The glossary currently contains the following words: {", ".join(context)}

Find synonyms of the word "{word}"{definition_text}

{known_synonyms_text}

Your response MUST be in the original word's language.
Respond ONLY with the synonyms, separated by commas. Do not include any other text in your response.
"""

    response = (
        await AsyncClient().generate(
            model=MODEL,
            prompt=prompt,
            think=False,
        )
    ).response
    response = response.replace('"', "").replace("'", "").replace(".", "")

    return list(
        {
            term.strip().lower()
            for term in response.split(",")
            if term.strip().lower() not in [word, *synonyms]
            and term.strip().lower().removesuffix("s") not in [word, *synonyms]
        },
    )


async def main() -> None:
    """
    Main function for testing the synonym generation.
    """
    print(
        await get_synonyms(
            Glossary(
                "Chess",
                "The game of chess",
            ),
            "pawn",
            "A pawn",
            [],
            ["board"],
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
