"""
axioma_criterion_engine/v4_2/semantic_matcher.py

Semantic matching for risk patterns.
- Local backend: sentence-transformers (e.g., all-MiniLM-L6-v2)
- OpenAI backend: embeddings via official openai-python client

Design goals:
- Deterministic normalization
- Explainable evidence: anchor + similarity score
- Safe fallback: if local deps are missing, fail loudly (or use SimpleToken matcher if enabled)

References:
- Official OpenAI Python SDK :contentReference[oaicite:1]{index=1}
- Embeddings + encoding_format gotcha :contentReference[oaicite:2]{index=2}
- Cookbook embeddings usage patterns :contentReference[oaicite:3]{index=3}
"""

from __future__ import annotations

import json
import math
import os
import re
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple, Literal, Any


BackendName = Literal["off", "local", "openai", "simple_tokens"]


@dataclass(frozen=True)
class SemanticHit:
    pattern_id: str
    similarity: float
    anchor: str
    backend: BackendName
    threshold: float

    def evidence_string(self) -> str:
        return f"semantic:{self.similarity:.3f}>=th:{self.threshold:.3f} -> '{self.anchor}' (backend={self.backend})"


@dataclass(frozen=True)
class PatternSemanticSpec:
    pattern_id: str
    anchors: List[str]
    threshold: float


# ----------------------------
# Normalization
# ----------------------------

_WS_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^0-9a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s]+")

def normalize_text(s: str) -> str:
    """
    Normalize text to improve semantic + token matching.
    Keeps Spanish accents (we don't strip diacritics) because they can carry meaning.
    """
    s = (s or "").strip().lower()
    s = _NON_ALNUM_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


# ----------------------------
# Vector utilities
# ----------------------------

def cosine_similarity(a: List[float], b: List[float]) -> float:
    # Robust cosine (handles zero vectors)
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


# ----------------------------
# Cache (optional disk)
# ----------------------------

class EmbeddingCache:
    """
    Tiny JSON cache:
    key = f"{backend}:{model}:{normalized_text}"
    value = embedding vector (list[float])
    """
    def __init__(self, cache_path: Optional[str] = None):
        self.cache_path = cache_path
        self._data: Dict[str, List[float]] = {}

        if self.cache_path:
            self._load()

    def _load(self) -> None:
        try:
            if os.path.exists(self.cache_path):
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    if isinstance(raw, dict):
                        # Only accept list[float] values
                        for k, v in raw.items():
                            if isinstance(k, str) and isinstance(v, list) and v and isinstance(v[0], (int, float)):
                                self._data[k] = [float(x) for x in v]
        except Exception:
            # Silent fail: cache is a perf optimization only
            self._data = {}

    def flush(self) -> None:
        if not self.cache_path:
            return
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f)
        except Exception:
            pass

    def get(self, key: str) -> Optional[List[float]]:
        return self._data.get(key)

    def set(self, key: str, value: List[float]) -> None:
        self._data[key] = value


# ----------------------------
# Base matcher
# ----------------------------

class SemanticMatcherBase:
    backend: BackendName = "off"

    def best_hit(
        self,
        text: str,
        specs: List[PatternSemanticSpec],
        *,
        top_k_anchors: int = 1,
    ) -> Optional[SemanticHit]:
        """
        Return the best semantic hit across all patterns (or None).
        For deterministic behavior we pick the highest similarity; in ties, first seen.
        """
        raise NotImplementedError


# ----------------------------
# Simple token fallback (optional)
# ----------------------------

def jaccard_token_similarity(a: str, b: str) -> float:
    ta = set(normalize_text(a).split())
    tb = set(normalize_text(b).split())
    if not ta or not tb:
        return 0.0
    inter = len(ta.intersection(tb))
    union = len(ta.union(tb))
    return inter / union if union else 0.0


class SimpleTokenSemanticMatcher(SemanticMatcherBase):
    """
    Super cheap fallback (not true semantics).
    Useful for baseline testing when you don't want external deps.
    """
    backend: BackendName = "simple_tokens"

    def best_hit(self, text: str, specs: List[PatternSemanticSpec], *, top_k_anchors: int = 1) -> Optional[SemanticHit]:
        t = normalize_text(text)
        best: Optional[SemanticHit] = None
        for spec in specs:
            for anchor in spec.anchors:
                sim = jaccard_token_similarity(t, anchor)
                if sim >= spec.threshold:
                    hit = SemanticHit(
                        pattern_id=spec.pattern_id,
                        similarity=sim,
                        anchor=anchor,
                        backend=self.backend,
                        threshold=spec.threshold,
                    )
                    if (best is None) or (hit.similarity > best.similarity):
                        best = hit
        return best


# ----------------------------
# Local backend (sentence-transformers)
# ----------------------------

class LocalSentenceTransformerMatcher(SemanticMatcherBase):
    backend: BackendName = "local"

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        *,
        cache_path: Optional[str] = None,
    ):
        self.model_name = model_name
        self.cache = EmbeddingCache(cache_path=cache_path)

        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "Local semantic matcher requires 'sentence-transformers'. "
                "Install it (and torch) or switch backend to 'openai' or 'simple_tokens'."
            ) from e

        self._model = SentenceTransformer(self.model_name)

    def _embed(self, text: str) -> List[float]:
        norm = normalize_text(text)
        key = f"{self.backend}:{self.model_name}:{norm}"
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        vec = self._model.encode([norm], normalize_embeddings=True)[0]  # returns numpy-like
        emb = [float(x) for x in vec]
        self.cache.set(key, emb)
        return emb

    def best_hit(self, text: str, specs: List[PatternSemanticSpec], *, top_k_anchors: int = 1) -> Optional[SemanticHit]:
        q = self._embed(text)
        best: Optional[SemanticHit] = None
        for spec in specs:
            # compute similarities vs anchors
            for anchor in spec.anchors:
                a = self._embed(anchor)
                sim = cosine_similarity(q, a)  # embeddings normalized, but still ok
                if sim >= spec.threshold:
                    hit = SemanticHit(
                        pattern_id=spec.pattern_id,
                        similarity=sim,
                        anchor=anchor,
                        backend=self.backend,
                        threshold=spec.threshold,
                    )
                    if (best is None) or (hit.similarity > best.similarity):
                        best = hit

        # Persist cache occasionally (cheap)
        self.cache.flush()
        return best


# ----------------------------
# OpenAI backend (embeddings)
# ----------------------------

class OpenAISemanticMatcher(SemanticMatcherBase):
    backend: BackendName = "openai"

    def __init__(
        self,
        *,
        embedding_model: str = "text-embedding-3-large",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        cache_path: Optional[str] = None,
        timeout_s: float = 30.0,
    ):
        """
        Uses official openai-python client:
        from openai import OpenAI; client = OpenAI()
        client.embeddings.create(model=..., input=[...], encoding_format="float")
        :contentReference[oaicite:4]{index=4}
        """
        self.embedding_model = embedding_model
        self.timeout_s = timeout_s
        self.cache = EmbeddingCache(cache_path=cache_path)

        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "OpenAI semantic matcher requires 'openai' package. Install openai-python."
            ) from e

        client_kwargs: Dict[str, Any] = {}
        if api_key:
            client_kwargs["api_key"] = api_key
        if base_url:
            client_kwargs["base_url"] = base_url

        self._client = OpenAI(**client_kwargs)

    def _embed(self, text: str) -> List[float]:
        norm = normalize_text(text)
        key = f"{self.backend}:{self.embedding_model}:{norm}"
        cached = self.cache.get(key)
        if cached is not None:
            return cached

        # encoding_format="float" to reliably get list[float]
        resp = self._client.embeddings.create(
            model=self.embedding_model,
            input=[norm],
            encoding_format="float",
        )
        emb = resp.data[0].embedding
        emb_list = [float(x) for x in emb]
        self.cache.set(key, emb_list)
        return emb_list

    def best_hit(self, text: str, specs: List[PatternSemanticSpec], *, top_k_anchors: int = 1) -> Optional[SemanticHit]:
        q = self._embed(text)
        best: Optional[SemanticHit] = None
        for spec in specs:
            for anchor in spec.anchors:
                a = self._embed(anchor)
                sim = cosine_similarity(q, a)
                if sim >= spec.threshold:
                    hit = SemanticHit(
                        pattern_id=spec.pattern_id,
                        similarity=sim,
                        anchor=anchor,
                        backend=self.backend,
                        threshold=spec.threshold,
                    )
                    if (best is None) or (hit.similarity > best.similarity):
                        best = hit

        self.cache.flush()
        return best


# ----------------------------
# Factory
# ----------------------------

def build_semantic_matcher(
    backend: BackendName,
    *,
    cache_dir: str = ".cache/axioma",
    local_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    openai_embedding_model: str = "text-embedding-3-large",
) -> SemanticMatcherBase:
    os.makedirs(cache_dir, exist_ok=True)

    if backend == "off":
        # Intentionally disabled: caller should skip semantic matching
        return SimpleTokenSemanticMatcher()  # harmless placeholder
    if backend == "simple_tokens":
        return SimpleTokenSemanticMatcher()
    if backend == "local":
        return LocalSentenceTransformerMatcher(
            model_name=local_model_name,
            cache_path=os.path.join(cache_dir, "embeddings_local.json"),
        )
    if backend == "openai":
        return OpenAISemanticMatcher(
            embedding_model=openai_embedding_model,
            cache_path=os.path.join(cache_dir, "embeddings_openai.json"),
        )

    raise ValueError(f"Unknown semantic backend: {backend}")


# ----------------------------
# Helper to convert dict->specs
# ----------------------------

def specs_from_config(pattern_cfg: Dict[str, Dict[str, Any]]) -> List[PatternSemanticSpec]:
    """
    pattern_cfg example:
    {
      "REL_BABY_SAVE_REL": {"anchors": [...], "threshold": 0.82},
      "MNY_QUIT_NO_PLAN": {"anchors": [...], "threshold": 0.80},
    }
    """
    out: List[PatternSemanticSpec] = []
    for pid, cfg in pattern_cfg.items():
        anchors = list(cfg.get("anchors", []) or [])
        thr = float(cfg.get("threshold", 0.0))
        if not anchors or thr <= 0.0:
            continue
        out.append(PatternSemanticSpec(pattern_id=pid, anchors=anchors, threshold=thr))
    return out
