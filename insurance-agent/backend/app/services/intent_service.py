"""Intent recognition service with multiple extraction methods."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

import numpy as np
from backend.app.models.schemas import ExtractMethod, IntentAnalysis, IntentType
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Intent patterns for exact matching
INTENT_PATTERNS: dict[IntentType, list[str]] = {
    IntentType.PRODUCT_COMPARE: [
        r"对比|比较|区别|差异|哪个好|选哪个|vs|versus",
        r"比对.*?和|.*?与.*?的区别|.*?和.*?哪个",
        r"产品.*?对比|产品.*?比较",
    ],
    IntentType.PRODUCT_INTRO: [
        r"介绍|了解|详情|说明|什么是|怎么样",
        r"产品.*?介绍|.*?产品.*?详情",
        r"告诉我.*?产品|讲解.*?产品",
    ],
    IntentType.SURRENDER: [
        r"退保|解约|取消保单|退掉|不想要了",
        r"怎么退保|如何退保|退保流程",
        r"退保.*?多少钱|能退多少",
    ],
}

# Pre-compiled regex patterns for performance
_COMPILED_INTENT_PATTERNS: dict[IntentType, list[re.Pattern]] = {}
for intent, patterns in INTENT_PATTERNS.items():
    _COMPILED_INTENT_PATTERNS[intent] = [re.compile(p, re.IGNORECASE) for p in patterns]

# Product name patterns
PRODUCT_PATTERNS = [
    r"产品\s*([A-Za-z0-9\u4e00-\u9fa5]+)",
    r"([A-Za-z]+)\s*产品",
    r"(平安福|国寿福|金佑人生|康宁保|百万医疗|e享护|好医保|尊享e生)",
    r"([A-Za-z0-9]+(?:版|Pro|Plus|旗舰版|尊享版)?)",
]

# Pre-compiled product patterns
_COMPILED_PRODUCT_PATTERNS = [re.compile(p, re.IGNORECASE) for p in PRODUCT_PATTERNS]

# Keyword extraction pattern
_KEYWORD_PATTERN = re.compile(r"[\u4e00-\u9fa5]+|[a-zA-Z]+")

# Sample products for fuzzy and vector matching
PRODUCT_DATABASE = [
    "平安福",
    "国寿福",
    "金佑人生",
    "康宁保",
    "百万医疗",
    "e享护",
    "好医保",
    "尊享e生",
    "平安福2024",
    "国寿福盛典版",
    "金佑人生2023",
]

# Intent training data for vector matching
INTENT_TRAINING_DATA: dict[IntentType, list[str]] = {
    IntentType.PRODUCT_COMPARE: [
        "我想对比一下这两个产品",
        "帮我比较A产品和B产品的区别",
        "哪个产品更好一些",
        "这两个产品有什么不同",
        "产品对比分析",
        "比较一下保障范围",
        "看看哪个更划算",
    ],
    IntentType.PRODUCT_INTRO: [
        "介绍一下这个产品",
        "这个产品怎么样",
        "产品详情是什么",
        "我想了解产品信息",
        "有什么特点和优势",
        "保障内容是什么",
        "产品介绍",
    ],
    IntentType.SURRENDER: [
        "我要退保",
        "怎么退保",
        "退保能退多少钱",
        "我想取消保单",
        "不想继续投保了",
        "退保流程是什么",
        "退保损失多少",
    ],
}


class IntentService:
    """Service for intent recognition and entity extraction."""

    def __init__(self) -> None:
        self._vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
        )
        self._intent_vectors: dict[IntentType, Any] = {}
        self._train_vectorizer()

    def _train_vectorizer(self) -> None:
        """Train the vectorizer with intent training data."""
        all_texts: list[str] = []
        intent_indices: dict[IntentType, list[int]] = {}

        idx = 0
        for intent, texts in INTENT_TRAINING_DATA.items():
            intent_indices[intent] = list(range(idx, idx + len(texts)))
            all_texts.extend(texts)
            idx += len(texts)

        if all_texts:
            self._vectorizer.fit(all_texts)
            vectors = self._vectorizer.transform(all_texts)

            for intent, indices in intent_indices.items():
                self._intent_vectors[intent] = vectors[indices]

    def analyze(self, query: str) -> IntentAnalysis:
        """Analyze user query to extract intent and entities.

        Uses three extraction methods:
        1. Exact: Regex pattern matching
        2. Fuzzy: String similarity matching
        3. Vector: TF-IDF cosine similarity
        """
        # Try exact matching first
        exact_result = self._exact_match(query)
        if exact_result.confidence >= 0.8:
            products = self._extract_products(query, ExtractMethod.EXACT)
            exact_result.products = products
            return exact_result

        # Try fuzzy matching
        fuzzy_result = self._fuzzy_match(query)
        if fuzzy_result.confidence >= 0.6:
            products = self._extract_products(query, ExtractMethod.FUZZY)
            fuzzy_result.products = products
            return fuzzy_result

        # Fall back to vector matching
        vector_result = self._vector_match(query)
        products = self._extract_products(query, ExtractMethod.VECTOR)
        vector_result.products = products
        return vector_result

    def _exact_match(self, query: str) -> IntentAnalysis:
        """Exact pattern matching using pre-compiled regex."""
        best_intent = IntentType.UNKNOWN
        best_score = 0.0

        for intent, compiled_patterns in _COMPILED_INTENT_PATTERNS.items():
            score = 0.0
            for pattern in compiled_patterns:
                if pattern.search(query):
                    score += 1.0

            if compiled_patterns:
                score = score / len(compiled_patterns)
                if score > best_score:
                    best_score = score
                    best_intent = intent

        return IntentAnalysis(
            intent=best_intent,
            confidence=best_score,
            extract_method=ExtractMethod.EXACT,
            raw_query=query,
        )

    # Pre-extracted keywords for fuzzy matching (computed once at module level)
    _FUZZY_KEYWORDS: dict[IntentType, list[str]] = {}
    for intent, patterns in INTENT_PATTERNS.items():
        keywords = set()
        for pattern in patterns:
            keywords.update(_KEYWORD_PATTERN.findall(pattern))
        _FUZZY_KEYWORDS[intent] = list(keywords)

    def _fuzzy_match(self, query: str) -> IntentAnalysis:
        """Fuzzy string matching using pre-extracted keywords."""
        best_intent = IntentType.UNKNOWN
        best_score = 0.0

        for intent, keywords in self._FUZZY_KEYWORDS.items():
            max_similarity = 0.0
            for keyword in keywords:
                similarity = SequenceMatcher(None, query, keyword).ratio()
                max_similarity = max(max_similarity, similarity)

            if max_similarity > best_score:
                best_score = max_similarity
                best_intent = intent

        return IntentAnalysis(
            intent=best_intent,
            confidence=best_score,
            extract_method=ExtractMethod.FUZZY,
            raw_query=query,
        )

    def _vector_match(self, query: str) -> IntentAnalysis:
        """Vector-based matching using TF-IDF and cosine similarity."""
        if not self._intent_vectors:
            return IntentAnalysis(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                extract_method=ExtractMethod.VECTOR,
                raw_query=query,
            )

        query_vector = self._vectorizer.transform([query])

        best_intent = IntentType.UNKNOWN
        best_score = 0.0

        for intent, intent_vectors in self._intent_vectors.items():
            similarities = cosine_similarity(query_vector, intent_vectors)
            max_similarity = float(np.max(similarities))

            if max_similarity > best_score:
                best_score = max_similarity
                best_intent = intent

        return IntentAnalysis(
            intent=best_intent,
            confidence=best_score,
            extract_method=ExtractMethod.VECTOR,
            raw_query=query,
        )

    def _extract_products(self, query: str, method: ExtractMethod) -> list[str]:
        """Extract product names from query using pre-compiled patterns."""
        products: list[str] = []

        # Try regex extraction with pre-compiled patterns
        for pattern in _COMPILED_PRODUCT_PATTERNS:
            matches = pattern.findall(query)
            products.extend(matches)

        # Clean and deduplicate
        products = [p.strip() for p in products if p.strip()]
        products = list(dict.fromkeys(products))

        # If no products found and method is fuzzy/vector, try fuzzy matching
        if not products and method in (
            ExtractMethod.FUZZY,
            ExtractMethod.VECTOR,
        ):
            for product in PRODUCT_DATABASE:
                for word in query.split():
                    similarity = SequenceMatcher(None, word, product).ratio()
                    if similarity > 0.6:
                        products.append(product)

        return products

    def extract_entities(self, query: str, intent: IntentType) -> dict[str, Any]:
        """Extract additional entities based on intent."""
        entities: dict[str, Any] = {}

        if intent == IntentType.PRODUCT_COMPARE:
            # Extract comparison aspects
            aspects = re.findall(
                r"保障范围|保费|保额|理赔|免责|等待期|缴费期",
                query,
            )
            if aspects:
                entities["compare_aspects"] = aspects

        elif intent == IntentType.SURRENDER:
            # Extract policy ID if present
            policy_id = re.search(r"保单号[：:]\s*(\w+)", query)
            if policy_id:
                entities["policy_id"] = policy_id.group(1)

            # Extract time period
            period = re.search(r"(\d+)\s*[年月]", query)
            if period:
                entities["period"] = period.group(0)

        return entities
