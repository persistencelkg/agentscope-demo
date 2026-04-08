"""Data models for insurance agent."""

from __future__ import annotations

from dataclasses import Field
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel


class IntentType(str, Enum):
    """Insurance intent types."""

    PRODUCT_COMPARE = "product_compare"
    PRODUCT_INTRO = "product_intro"
    SURRENDER = "surrender"
    UNKNOWN = "unknown"


class ExtractMethod(str, Enum):
    """Information extraction methods."""

    EXACT = "exact"
    FUZZY = "fuzzy"
    VECTOR = "vector"


class IntentAnalysis(BaseModel):
    """Intent analysis result."""

    intent: IntentType = Field(description="The detected user intent")
    confidence: float = Field(description="Confidence score 0-1", ge=0, le=1)
    extract_method: ExtractMethod = Field(description="Method used for extraction")
    products: list[str] = Field(
        default_factory=list, description="Extracted product names"
    )
    entities: dict[str, Any] = Field(
        default_factory=dict, description="Other extracted entities"
    )
    raw_query: str = Field(description="Original user query")


class ProductInfo(BaseModel):
    """Product information."""

    id: str
    name: str
    category: str
    premium: float
    coverage: list[str]
    features: list[str]
    exclusions: list[str]
    waiting_period: str
    term: str


class CompareResult(BaseModel):
    """Product comparison result."""

    products: list[ProductInfo]
    comparison_table: dict[str, list[Any]]
    recommendation: str


class IntroResult(BaseModel):
    """Product introduction result."""

    product: ProductInfo
    highlights: list[str]
    target_audience: str
    scenarios: list[str]


class SurrenderResult(BaseModel):
    """Surrender calculation result."""

    policy_id: str
    policy_name: str
    premium_paid: float
    surrender_value: float
    loss_amount: float
    loss_percentage: float
    notes: list[str]


class CardType(str, Enum):
    """Frontend card types."""

    PRODUCT_COMPARE = "product_compare"
    PRODUCT_INTRO = "product_intro"
    SURRENDER = "surrender"
    TEXT = "text"


class CardPayload(BaseModel):
    """Card payload for frontend rendering."""

    card_type: CardType
    data: dict[str, Any]
    timestamp: str = ""


class ChatMessage(BaseModel):
    """Chat message model."""

    role: Literal["user", "assistant", "system"]
    content: str
    cards: list[CardPayload] = Field(default_factory=list)


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    """Chat response model."""

    message: str
    cards: list[CardPayload] = Field(default_factory=list)
    intent: IntentAnalysis | None = None
    session_id: str
