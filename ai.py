import asyncio
from collections.abc import Awaitable, Callable

import aiohttp
import numpy as np
import ollama
from scipy.spatial import distance

type Fetcher = Callable[[aiohttp.ClientSession, str], Awaitable[list[str]]]


async def fetch_synonyms_datamuse(
    session: aiohttp.ClientSession,
    word: str,
) -> list[str]:
    url = f"https://api.datamuse.com/words?rel_syn={word}"
    async with session.get(url) as response:
        if response.status != 200:
            raise RuntimeError(response.status)

        data = await response.json()

        # filter words with a score too low, or no score at all
        data = [item for item in data if "score" in item]
        if not data:
            return []

        avg_score = sum(item["score"] for item in data) / len(data)
        data = [item for item in data if item["score"] > avg_score]

        return [item["word"] for item in data]


async def fetch_synonyms_dictionaryapi(
    session: aiohttp.ClientSession,
    word: str,
) -> list[str]:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    async with session.get(url) as response:
        if response.status != 200:
            raise RuntimeError(response.status)

        data = await response.json()
        if not data:
            return []

        synonyms = [
            synonym
            for entry in data
            for meaning in entry["meanings"]
            for synonym in meaning["synonyms"]
        ]
        synonyms += [
            synonym
            for entry in data
            for meaning in entry["meanings"]
            for definition in meaning["definitions"]
            for synonym in definition["synonyms"]
        ]

        return synonyms


async def fetch_synonyms_freedictionaryapi(
    session: aiohttp.ClientSession,
    word: str,
) -> list[str]:
    url = f"https://freedictionaryapi.com/api/v1/entries/en/{word}"
    async with session.get(url) as response:
        if response.status != 200:
            raise RuntimeError(response.status)

        data = await response.json()
        if not data:
            return []

        synonyms = [
            synonym for entry in data["entries"] for synonym in entry["synonyms"]
        ]
        synonyms += [
            synonym
            for entry in data["entries"]
            for sens in entry["senses"]
            for synonym in sens["synonyms"]
        ]

        return synonyms


DEFAULT_FETCHERS: list[Fetcher] = [
    fetch_synonyms_datamuse,
    fetch_synonyms_dictionaryapi,
    fetch_synonyms_freedictionaryapi,
]


async def fetcher_wrapper(
    session: aiohttp.ClientSession,
    word: str,
    fetcher: Fetcher,
) -> list[str]:
    try:
        return await fetcher(session, word)
    except RuntimeError:
        return []


async def get_all_synonyms(
    words: list[str],
    fetchers: list[Fetcher],
) -> set[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetcher_wrapper(session, word, fetcher)
            for fetcher in fetchers
            for word in words
        ]
        results = await asyncio.gather(*tasks)

        # using a set to de-duplicate
        return {word for words in results for word in words}


async def filter_synonyms(
    words: list[str],
    all_synonyms: set[str],
    threshold: float,
) -> list[tuple[str, float]]:
    base_vector, *vectors = ollama.embed(
        model="all-minilm",
        input=[" ".join(words), *all_synonyms],
    ).embeddings

    synonyms = []
    for synonym, vector in zip(all_synonyms, vectors, strict=True):
        # Filter multiple-word expressions
        if synonym.count(" ") > 3:
            continue

        vec = np.array(vector)

        similarity = distance.cosine(vec, base_vector)
        if similarity >= threshold:
            synonyms.append((synonym, similarity))

    return sorted(synonyms, key=lambda x: x[1], reverse=True)


async def get_synonyms(
    words: list[str],
    context: list[str],
    fetchers: list[Fetcher] | None = None,
    threshold: float = 0.0,
) -> list[tuple[str, float]]:
    if fetchers is None:
        fetchers = DEFAULT_FETCHERS

    all_synonyms = await get_all_synonyms(words, fetchers)

    return await filter_synonyms(words + context, all_synonyms, threshold)
