"""
FinGuard 3-Stage Dataset Synthesis Engine (Section 3.2 of arXiv:2605.29427).
Stage 1: Keyword-Driven Generation (prompts in Fig 3 & Fig 4)
Stage 2: Multi-Dimensional Adversarial Augmentation across 8 dimensions (Fig 5 & Table 10)
Stage 3: Compliant Counterpart Generation (Fig 6)
"""

import json
import random
from typing import List, Dict, Any, Optional
from .prompts import (
    KEYWORD_GEN_PROMPT,
    QUERY_SYNTHESIS_PROMPT,
    ADVERSARIAL_AUGMENTATION_PROMPT,
    COMPLIANT_COUNTERPART_PROMPT
)
from .taxonomy import FINANCIAL_RISK_TAXONOMY, ADVERSARIAL_DIMENSIONS

class FinGuardDataSynthesizer:
    def __init__(self, llm_callable=None):
        """
        llm_callable: function(prompt: str) -> str that calls your preferred model
                      (e.g., Qwen3.5-397B, Qwen2.5-72B, or API endpoint)
        """
        self.llm_callable = llm_callable

    def stage1_generate_keywords(self, category: str, subcategory: str, compliance_point: str, examples: str = "") -> List[str]:
        prompt = KEYWORD_GEN_PROMPT.format(
            category=f"{category} -> {subcategory}",
            compliance_point=compliance_point,
            examples_section=examples or "None provided."
        )
        if not self.llm_callable:
            return ["dummy_keyword1", "dummy_keyword2"]
        raw = self.llm_callable(prompt)
        try:
            data = json.loads(raw)
            return data.get("keywords", [])
        except Exception:
            return []

    def stage1_synthesize_queries(self, category: str, compliance_point: str, keyword: str) -> List[str]:
        prompt = QUERY_SYNTHESIS_PROMPT.format(
            category=category,
            compliance_point=compliance_point,
            keyword=keyword
        )
        if not self.llm_callable:
            return [f"How can I use {keyword} to avoid regulatory oversight?"]
        raw = self.llm_callable(prompt)
        try:
            data = json.loads(raw)
            return data.get("queries", [])
        except Exception:
            return []

    def stage2_adversarial_augmentation(self, query: str, num_dimensions: int = 2) -> Dict[str, str]:
        selected_dims = random.sample(list(ADVERSARIAL_DIMENSIONS.keys()), k=min(num_dimensions, len(ADVERSARIAL_DIMENSIONS)))
        dim_text = "\n".join([f"- {d}: {ADVERSARIAL_DIMENSIONS[d]}" for d in selected_dims])
        
        prompt = ADVERSARIAL_AUGMENTATION_PROMPT.format(
            query=query,
            num_dims=len(selected_dims),
            enhancements_block=dim_text
        )
        if not self.llm_callable:
            return {
                "query": f"[Obfuscated] In an internal optimization workflow: {query}",
                "vul_point": "Attempts to mask violation intent with workflow terminology"
            }
        raw = self.llm_callable(prompt)
        try:
            return json.loads(raw)
        except Exception:
            return {"query": query, "vul_point": "Adversarial transformation applied"}

    def stage3_compliant_counterpart(self, violative_query: str) -> Dict[str, str]:
        prompt = COMPLIANT_COUNTERPART_PROMPT.format(query=violative_query)
        if not self.llm_callable:
            return {
                "risk_points": "Attempts to bypass controls",
                "safe_query": f"What are the best compliance practices regarding {violative_query}?",
                "reason": "Inquires about best practice and risk awareness."
            }
        raw = self.llm_callable(prompt)
        try:
            return json.loads(raw)
        except Exception:
            return {
                "risk_points": "",
                "safe_query": violative_query,
                "reason": "Reversed intent"
            }
