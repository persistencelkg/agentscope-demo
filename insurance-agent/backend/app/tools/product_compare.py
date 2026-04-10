"""Insurance product comparison tool."""

from __future__ import annotations

from datetime import datetime

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse
from backend.app.models.schemas import (
    CardPayload,
    CardType,
    CompareResult,
    ProductInfo,
)

from backend import app

# Mock product database
PRODUCT_DB: dict[str, ProductInfo] = {
    "平安福": ProductInfo(
        id="PAF001",
        name="平安福2024",
        category="重疾险",
        premium=8000.0,
        coverage=["重疾", "中症", "轻症", "身故"],
        features=[
            "120种重疾保障",
            "20种中症保障",
            "40种轻症保障",
            "身故赔付保额",
            "可附加医疗险",
        ],
        exclusions=["既往症", "战争", "核辐射"],
        waiting_period="90天",
        term="终身",
    ),
    "国寿福": ProductInfo(
        id="GSF001",
        name="国寿福盛典版",
        category="重疾险",
        premium=7500.0,
        coverage=["重疾", "症", "轻症", "身故"],
        features=[
            "120种重疾保障",
            "25种症保障",
            "50种轻症保障",
            "身故赔付保额",
            "特定疾病额外赔",
        ],
        exclusions=["既往症", "战争", "故意犯罪"],
        waiting_period="90天",
        term="终身",
    ),
    "百万医疗": ProductInfo(
        id="BWYL001",
        name="百万医疗险",
        category="医疗险",
        premium=500.0,
        coverage=["住院医疗", "门诊手术", "特殊门诊"],
        features=[
            "保额400万",
            "1万免赔额",
            "100%报销",
            "质子重离子保障",
        ],
        exclusions=["既往症", "整形美容", "牙科"],
        waiting_period="30天",
        term="1年",
    ),
    "好医保": ProductInfo(
        id="HBY001",
        name="好医保长期医疗",
        category="医疗险",
        premium=450.0,
        coverage=["住院医疗", "门诊手术", "特殊门诊"],
        features=[
            "保额400万",
            "1万免赔额",
            "100%报销",
            "保证续保20年",
        ],
        exclusions=["既往症", "整形美容", "牙科"],
        waiting_period="30天",
        term="20年",
    ),
}

# Product index for O(1) lookup by normalized name
_PRODUCT_INDEX: dict[str, ProductInfo] = {}
for product in PRODUCT_DB.values():
    _PRODUCT_INDEX[product.name.lower()] = product
    _PRODUCT_INDEX[product.id.lower()] = product
    for alt in [
        product.name.replace("2024", "").replace("盛典版", "").replace("长期医疗", "")
    ]:
        if alt and alt != product.name:
            _PRODUCT_INDEX[alt.lower()] = product


async def compare_products(
    product_names: str,
    aspects: str = "",
) -> ToolResponse:
    """Compare multiple insurance products.

    Args:
        product_names: Product names separated by comma, e.g., "平安福,国寿福".
        aspects: Specific aspects to compare, separated by comma.
                 Options: 保障范围,保费,保额,理赔,免责,等待期.
                 Leave empty to compare all aspects.
    """
    # Parse product names
    names = [n.strip() for n in product_names.split(",") if n.strip()]

    if len(names) < 2:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text="请提供至少两个产品名称进行对比，用逗号分隔。",
                )
            ]
        )

    # Find products
    products: list[ProductInfo] = []
    not_found: list[str] = []

    for name in names:
        product = _find_product(name)
        if product:
            products.append(product)
        else:
            not_found.append(name)

    if not_found:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"未找到以下产品: {', '.join(not_found)}。"
                    f"可用产品: {', '.join(PRODUCT_DB.keys())}",
                )
            ]
        )

    # Build comparison
    result = _build_comparison(products, aspects)

    # Create card payload
    card = CardPayload(
        card_type=CardType.PRODUCT_COMPARE,
        data=result.model_dump(),
        timestamp=datetime.now().isoformat(),
    )

    return ToolResponse(
        content=[
            TextBlock(
                type="text",
                text=f"已为您对比 {len(products)} 个产品，请查看对比卡片。",
            )
        ],
        metadata={"card": card.model_dump()},
    )


async def get_product_intro(
    product_name: str,
) -> ToolResponse:
    """Get detailed introduction of an insurance product.

    Args:
        product_name: The name of the product to introduce.
    """
    product = _find_product(product_name)

    if not product:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"未找到产品 '{product_name}'。"
                    f"可用产品: {', '.join(PRODUCT_DB.keys())}",
                )
            ]
        )

    # Build introduction
    highlights = product.features[:3] if product.features else []
    target_audience = _get_target_audience(product)
    scenarios = _get_scenarios(product)

    from backend.app.models.schemas import IntroResult

    result = IntroResult(
        product=product,
        highlights=highlights,
        target_audience=target_audience,
        scenarios=scenarios,
    )

    # Create card payload
    card = CardPayload(
        card_type=CardType.PRODUCT_INTRO,
        data=result.model_dump(),
        timestamp=datetime.now().isoformat(),
    )

    return ToolResponse(
        content=[
            TextBlock(
                type="text",
                text=f"以下是 {product.name} 的详细介绍。",
            )
        ],
        metadata={"card": card.model_dump()},
    )


async def calculate_surrender(
    product_name: str,
    policy_years: int = 1,
) -> ToolResponse:
    """Calculate surrender value for a policy.

    Args:
        product_name: The name of the product.
        policy_years: How many years the policy has been in force.
    """
    product = _find_product(product_name)

    if not product:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"未找到产品 '{product_name}'。"
                    f"可用产品: {', '.join(PRODUCT_DB.keys())}",
                )
            ]
        )

    # Calculate surrender value (simplified formula)
    total_premium = product.premium * policy_years

    # Surrender value ratio decreases with earlier surrender
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

    from backend.app.models.schemas import SurrenderResult

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

    # Create card payload
    card = CardPayload(
        card_type=CardType.SURRENDER,
        data=result.model_dump(),
        timestamp=datetime.now().isoformat(),
    )

    return ToolResponse(
        content=[
            TextBlock(
                type="text",
                text=f"以下是 {product.name} 的退保计算结果。",
            )
        ],
        metadata={"card": card.model_dump()},
    )


def _find_product(name: str) -> ProductInfo | None:
    """Find product using O(1) index lookup with fallback for fuzzy matching."""
    if not name:
        return None

    name_lower = name.lower()

    # O(1) lookup from index
    if name_lower in _PRODUCT_INDEX:
        return _PRODUCT_INDEX[name_lower]

    # Partial match fallback (rare case)
    for key, product in PRODUCT_DB.items():
        if name in key or key in name:
            return product
        if name_lower in key.lower():
            return product

    return None


def _build_comparison(products: list[ProductInfo], aspects: str = "") -> CompareResult:
    """Build comparison table."""
    aspect_list = (
        [a.strip() for a in aspects.split(",") if a.strip()]
        if aspects
        else ["保障范围", "保费", "特点", "免责", "等待期"]
    )

    comparison_table: dict[str, list] = {}

    for aspect in aspect_list:
        values: list[str] = []
        for product in products:
            if aspect in ("保障范围", "coverage"):
                values.append(", ".join(product.coverage))
            elif aspect in ("保费", "premium"):
                values.append(f"¥{product.premium:,.0f}/年")
            elif aspect in ("特点", "features"):
                values.append("; ".join(product.features[:3]))
            elif aspect in ("免责", "exclusions"):
                values.append(", ".join(product.exclusions))
            elif aspect in ("等待期", "waiting"):
                values.append(product.waiting_period)
            else:
                values.append("-")
        comparison_table[aspect] = values

    # Generate recommendation
    cheapest = min(products, key=lambda p: p.premium)
    most_coverage = max(products, key=lambda p: len(p.coverage))
    recommendation = (
        f"如果注重性价比，推荐 {cheapest.name}（年保费 ¥{cheapest.premium:,.0f}）；"
        f"如果注重保障全面，推荐 {most_coverage.name}"
        f"（覆盖 {len(most_coverage.coverage)} 类保障）。"
    )

    return CompareResult(
        products=products,
        comparison_table=comparison_table,
        recommendation=recommendation,
    )


def _get_target_audience(product: ProductInfo) -> str:
    """Determine target audience based on product type."""
    if product.category == "重疾险":
        return "适合0-55岁人群，特别是家庭经济支柱，建议保额为年收入的3-5倍"
    elif product.category == "医疗险":
        return "适合所有年龄段人群，可作为社保补充，建议与重疾险搭配购买"
    else:
        return "适合有保障需求的人群"


def _get_scenarios(product: ProductInfo) -> list[str]:
    """Get applicable scenarios."""
    if product.category == "重疾险":
        return [
            "确诊重大疾病时获得一次性赔付",
            "弥补收入损失和康复费用",
            "家庭财务安全垫",
        ]
    elif product.category == "医疗险":
        return [
            "住院医疗费用报销",
            "门诊手术费用报销",
            "特殊门诊治疗费用",
        ]
    else:
        return ["提供基本保障"]
