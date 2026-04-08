"""Intent recognition agent using AgentScope."""

from __future__ import annotations

import os

from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit
from backend.app.models.schemas import ExtractMethod, IntentAnalysis, IntentType
from backend.app.services.intent_service import IntentService
from pydantic import BaseModel, Field


class IntentOutput(BaseModel):
    """Structured output for intent recognition."""

    intent: str = Field(
        description=(
            "用户意图，必须是以下之一: "
            "product_compare(产品对比), "
            "product_intro(产品介绍), "
            "surrender(退保), "
            "unknown(未知)"
        )
    )
    products: list[str] = Field(
        default_factory=list,
        description="提取的产品名称列表",
    )
    confidence: float = Field(
        description="置信度 0-1",
        ge=0,
        le=1,
    )
    reasoning: str = Field(
        description="推理过程说明",
    )


class IntentAgent:
    """Agent for recognizing user intent."""

    def __init__(self) -> None:
        self._intent_service = IntentService()

        api_key = os.getenv("DASHSCOPE_API_KEY", "your-api-key")
        model_name = os.getenv("MODEL_NAME", "qwen-max")

        self._agent = ReActAgent(
            name="IntentAnalyzer",
            sys_prompt=self._build_sys_prompt(),
            model=DashScopeChatModel(
                model_name=model_name,
                api_key=api_key,
                stream=False,
            ),
            formatter=DashScopeChatFormatter(),
            memory=InMemoryMemory(),
            toolkit=Toolkit(),
        )

    def _build_sys_prompt(self) -> str:
        """Build system prompt for intent recognition."""
        return """你是一个保险意图识别专家。你的任务是分析用户的查询，识别用户的真实意图。

可识别的意图类型：
1. product_compare - 用户想要对比多个保险产品
   触发词：对比、比较、区别、差异、哪个好、选哪个
   
2. product_intro - 用户想要了解某个产品的详情
   触发词：介绍、了解、详情、说明、什么是、怎么样
   
3. surrender - 用户想要退保或了解退保信息
   触发词：退保、解约、取消保单、退掉、不想要了
   
4. unknown - 无法识别的意图

请仔细分析用户的查询，提取出：
- 意图类型
- 提到的产品名称（如有）
- 置信度（0-1之间的浮点数）

使用中文进行推理说明。"""

    async def analyze(self, query: str) -> IntentAnalysis:
        """Analyze user query using both rule-based and LLM methods."""
        # First, use rule-based analysis
        rule_result = self._intent_service.analyze(query)

        # If confidence is high enough, return rule-based result
        if rule_result.confidence >= 0.7:
            return rule_result

        # Otherwise, use LLM for more accurate analysis
        llm_result = await self._llm_analyze(query)

        # Merge results
        return self._merge_results(rule_result, llm_result, query)

    async def _llm_analyze(self, query: str) -> IntentOutput:
        """Use LLM for intent analysis."""
        prompt = f"""请分析以下用户查询的意图，以JSON格式返回：
用户查询："{query}"

请返回JSON格式，包含以下字段：
- intent: 意图类型，必须是 "product_compare"、"product_intro"、"surrender" 或 "unknown" 之一
- products: 产品名称列表
- confidence: 置信度(0-1)
- reasoning: 推理过程

示例输出：
{{"intent": "product_compare", "products": ["平安福", "国寿福"], "confidence": 0.9, "reasoning": "用户想要对比两个产品"}}"""

        msg = Msg(name="user", role="user", content=prompt)

        try:
            response = await self._agent(msg, structured_model=IntentOutput)

            if hasattr(response, "metadata") and response.metadata:
                return IntentOutput(**response.metadata)
        except Exception as e:
            print(f"LLM analysis failed: {e}")

        # Fallback if structured output fails
        return IntentOutput(
            intent="unknown",
            products=[],
            confidence=0.5,
            reasoning="无法解析结构化输出",
        )

    def _merge_results(
        self,
        rule_result: IntentAnalysis,
        llm_result: IntentOutput,
        query: str,
    ) -> IntentAnalysis:
        """Merge rule-based and LLM results."""
        # Prefer LLM result if its confidence is higher
        if llm_result.confidence > rule_result.confidence:
            intent = (
                IntentType(llm_result.intent)
                if llm_result.intent in [t.value for t in IntentType]
                else IntentType.UNKNOWN
            )
            return IntentAnalysis(
                intent=intent,
                confidence=llm_result.confidence,
                extract_method=ExtractMethod.VECTOR,
                products=llm_result.products,
                entities={"reasoning": llm_result.reasoning},
                raw_query=query,
            )

        # Use rule result but merge products
        rule_result.products = list(set(rule_result.products + llm_result.products))
        return rule_result
