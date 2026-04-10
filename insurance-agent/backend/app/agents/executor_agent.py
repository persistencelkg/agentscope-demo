"""Insurance executor agent for handling tool calls."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.app.models.schemas import (
    CardPayload,
    CardType,
    IntentAnalysis,
    IntentType,
    IntroResult,
    SurrenderResult,
)
from backend.app.tools.product_compare import (
    PRODUCT_DB,
    _build_comparison,
    _find_product,
)


class InsuranceExecutorAgent:
    """Agent for executing insurance-related tasks."""

    async def execute(self, intent: IntentAnalysis) -> dict[str, Any]:
        """Execute task based on intent analysis."""
        try:
            if intent.intent == IntentType.PRODUCT_COMPARE:
                return await self._handle_compare(intent)
            elif intent.intent == IntentType.PRODUCT_INTRO:
                return await self._handle_intro(intent)
            elif intent.intent == IntentType.SURRENDER:
                return await self._handle_surrender(intent)
            else:
                return {
                    "response": "抱歉，我无法理解您的意图。请尝试以下方式：\n- 对比产品：帮我对比平安福和国寿福\n- 产品介绍：介绍百万医疗险\n- 退保咨询：我要退保",
                    "card": None,
                }
        except Exception as e:
            print(f"Executor error: {e}")
            import traceback

            traceback.print_exc()
            return {
                "response": f"处理请求时发生错误: {str(e)}",
                "card": None,
            }

    async def _handle_compare(self, intent: IntentAnalysis) -> dict[str, Any]:
        """Handle product comparison."""
        products = []
        for name in intent.products:
            product = _find_product(name)
            if product:
                products.append(product)

        if len(products) < 2:
            return {
                "response": f"抱歉，未找到足够的产品进行对比。您提到的产品: {', '.join(intent.products)}\n可用产品: {', '.join(PRODUCT_DB.keys())}",
                "card": None,
            }

        result = _build_comparison(products)
        card = CardPayload(
            card_type=CardType.PRODUCT_COMPARE,
            data=result.model_dump(),
            timestamp=datetime.now().isoformat(),
        )

        return {
            "response": f"已为您对比 {' 和 '.join([p.name for p in products])}，请查看下方对比卡片。",
            "card": card.model_dump(),
        }

    async def _handle_intro(self, intent: IntentAnalysis) -> dict[str, Any]:
        """Handle product introduction."""
        if not intent.products:
            return {
                "response": "请告诉我您想了解哪个产品的信息。\n可用产品: "
                + ", ".join(PRODUCT_DB.keys()),
                "card": None,
            }

        product = _find_product(intent.products[0])
        if not product:
            return {
                "response": f"抱歉，未找到产品 '{intent.products[0]}'。\n可用产品: {', '.join(PRODUCT_DB.keys())}",
                "card": None,
            }

        highlights = product.features[:3] if product.features else []

        if product.category == "重疾险":
            target_audience = (
                "适合0-55岁人群，特别是家庭经济支柱，建议保额为年收入的3-5倍"
            )
            scenarios = [
                "确诊重大疾病时获得一次性赔付",
                "弥补收入损失和康复费用",
                "家庭财务安全垫",
            ]
        elif product.category == "医疗险":
            target_audience = "适合所有年龄段人群，可作为社保补充，建议与重疾险搭配购买"
            scenarios = ["住院医疗费用报销", "门诊手术费用报销", "特殊门诊治疗费用"]
        else:
            target_audience = "适合有保障需求的人群"
            scenarios = ["提供基本保障"]

        result = IntroResult(
            product=product,
            highlights=highlights,
            target_audience=target_audience,
            scenarios=scenarios,
        )

        card = CardPayload(
            card_type=CardType.PRODUCT_INTRO,
            data=result.model_dump(),
            timestamp=datetime.now().isoformat(),
        )

        return {
            "response": f"以下是 {product.name} 的详细介绍。",
            "card": card.model_dump(),
        }

    async def _handle_surrender(self, intent: IntentAnalysis) -> dict[str, Any]:
        """Handle surrender calculation."""
        if not intent.products:
            return {
                "response": "请告诉我您想退保哪个产品。\n可用产品: "
                + ", ".join(PRODUCT_DB.keys()),
                "card": None,
            }

        product = _find_product(intent.products[0])
        if not product:
            return {
                "response": f"抱歉，未找到产品 '{intent.products[0]}'。\n可用产品: {', '.join(PRODUCT_DB.keys())}",
                "card": None,
            }

        # 默认投保3年
        policy_years = 3

        total_premium = product.premium * policy_years

        if policy_years <= 1:
            ratio = 0.3
        elif policy_years <= 2:
            ratio = 0.5
        elif policy_years <= 5:
            ratio = 0.7
        else:
            ratio = 0.85

        surrender_value = total_premium * ratio
        loss_amount = total_premium - surrender_value
        loss_percentage = (loss_amount / total_premium) * 100

        result = SurrenderResult(
            policy_id=f"POL-{product.id}-{policy_years}",
            policy_name=product.name,
            premium_paid=total_premium,
            surrender_value=surrender_value,
            loss_amount=loss_amount,
            loss_percentage=loss_percentage,
            notes=[
                f"您已缴纳保费 {total_premium:.2f} 元",
                f"当前退保可获得 {surrender_value:.2f} 元",
                f"损失金额 {loss_amount:.2f} 元（损失率 {loss_percentage:.1f}%）",
                "犹豫期内退保可全额返还",
                "建议咨询客服了解详细退保流程",
            ],
        )

        card = CardPayload(
            card_type=CardType.SURRENDER,
            data=result.model_dump(),
            timestamp=datetime.now().isoformat(),
        )

        return {
            "response": f"以下是 {product.name} 的退保计算结果。",
            "card": card.model_dump(),
        }
