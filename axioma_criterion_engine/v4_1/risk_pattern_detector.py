# axioma_criterion_engine/v4_1/risk_pattern_detector.py
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from .risk_patterns_v4_1 import RISK_PATTERNS_V41, RiskPattern

_SEVERITY_TO_RISK_DELTA = {
    "low": 0.10,
    "medium": 0.20,
    "high": 0.35,
}

import re
import unicodedata

def _strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))

def _norm(s: str) -> str:
    s = (s or "").strip().lower()
    s = _strip_accents(s)
    # deja solo letras/numeros/espacios
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _tokens(s: str) -> List[str]:
    s = _norm(s)
    return [t for t in s.split(" ") if t]

def _match_phrase_tokens(text_norm: str, phrase: str) -> bool:
    """
    True si TODAS las palabras significativas del trigger están en el texto.
    """
    p_tokens = _tokens(phrase)
    if not p_tokens:
        return False

    # opcional: ignora palabras muy comunes
    stop = {"de", "la", "el", "una", "un", "que", "yo", "mi", "mas", "mucho", "muchas", "tener", "quiero", "debo"}
    key_tokens = [t for t in p_tokens if t not in stop]

    # si se quedaron muy pocas, usa todas
    use_tokens = key_tokens if len(key_tokens) >= 2 else p_tokens

    return all(t in text_norm for t in use_tokens)

def _collect_text(obj: Dict[str, Any]) -> str:
    parts: List[str] = []
    parts.append(str(obj.get("original_statement", "")))
    f = obj.get("foundation", {}) or {}
    c = obj.get("context", {}) or {}
    p = obj.get("principle", {}) or {}
    parts.append(str(f.get("facts_key", "")))
    parts.append(str(c.get("current_situation", "")))
    parts.append(str(p.get("declared_purpose", "")))
    return _norm("\n".join([x for x in parts if x]))

def detect_risk_patterns(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retorna:
    {
      "signals": [ {pattern_id, domain, title, severity, observed_risks, missing_critical_data, followup_questions, evidence_hits} ],
      "risk_delta": float,              # suma (cap 1.0)
      "missing_context_count": int,     # total variables críticas mencionadas por patrones activados
    }
    """
    text = _collect_text(obj)
    if not text:
        return {"signals": [], "risk_delta": 0.0, "missing_context_count": 0}

    signals: List[Dict[str, Any]] = []
    risk_delta = 0.0
    missing_count = 0

    for pat in RISK_PATTERNS_V41:
        hits: List[str] = []
        for phrase in pat.get("trigger_phrases", []):
            if _match_phrase_tokens(text, phrase):
                hits.append(phrase)

        if not hits:
            continue

        sev = pat.get("severity", "medium")
        risk_delta += float(_SEVERITY_TO_RISK_DELTA.get(sev, 0.2))
        missing = pat.get("missing_critical_data", [])
        missing_count += len(missing)

        signals.append(
            {
                "pattern_id": pat.get("id", ""),
                "domain": pat.get("domain", "relationships"),
                "title": pat.get("title", ""),
                "severity": sev,
                "observed_risks": pat.get("observed_risks", []),
                "missing_critical_data": missing,
                "followup_questions": pat.get("followup_questions", []),
                "evidence_hits": hits[:5],
            }
        )

    return {
        "signals": signals,
        "risk_delta": min(risk_delta, 1.0),
        "missing_context_count": int(missing_count),
    }
