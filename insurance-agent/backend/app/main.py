"""FastAPI application for insurance agent."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import HTTPException, FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from backend.app.agents.intent_agent import IntentAgent
from backend.app.models.schemas import (
    CardPayload,
    ChatRequest,
    ChatResponse,
    IntentType,
)

from backend.app.agents.executor_agent import InsuranceExecutorAgent



# Global agents
intent_agent: IntentAgent | None = None
executor_agent: InsuranceExecutorAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global intent_agent, executor_agent

    # Initialize agents on startup
    print("Initializing insurance agents...")
    intent_agent = IntentAgent()
    executor_agent = InsuranceExecutorAgent()
    print("Insurance agents initialized.")

    yield

    # Cleanup on shutdown
    print("Shutting down insurance agents...")


# Create FastAPI app
app = FastAPI(
    title="Insurance Agent API",
    description="AI-powered insurance assistant using AgentScope",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "message": "Insurance Agent API is running"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat message."""
    if not intent_agent or not executor_agent:
        raise HTTPException(
            status_code=500,
            detail="Agents not initialized",
        )

    try:
        # Step 1: Analyze intent
        intent = await intent_agent.analyze(request.message)
        print(f"Detected intent: {intent.intent} (confidence: {intent.confidence})")

        # Step 2: Execute based on intent
        if intent.intent == IntentType.UNKNOWN:
            return ChatResponse(
                message="抱歉，我没有理解您的意图。请尝试以下方式：\n"
                "- 对比产品：帮我对比平安福和国寿福\n"
                "- 产品介绍：介绍百万医疗险\n"
                "- 退保咨询：我要退保",
                cards=[],
                intent=intent,
                session_id=request.session_id,
            )

        # Step 3: Execute the task
        result = await executor_agent.execute(intent)

        # Step 4: Build response
        cards: list[CardPayload] = []
        if result.get("card"):
            cards.append(CardPayload(**result["card"]))

        return ChatResponse(
            message=result.get("response", "任务执行完成"),
            cards=cards,
            intent=intent,
            session_id=request.session_id,
        )

    except Exception as e:
        print(f"Error processing chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}",
        )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Process a chat message with streaming response."""
    if not intent_agent or not executor_agent:
        raise HTTPException(
            status_code=500,
            detail="Agents not initialized",
        )

    async def generate():
        try:
            # Step 1: Analyze intent
            yield '{"type": "status", "message": "正在分析您的意图..."}\n'
            intent = await intent_agent.analyze(request.message)

            yield f'{{"type": "intent", "data": {intent.model_dump_json()}}}\n'

            # Step 2: Execute
            yield '{"type": "status", "message": "正在处理您的请求..."}\n'
            result = await executor_agent.execute(intent)

            # Step 3: Send result
            if result.get("card"):
                import json

                card_json = json.dumps(result["card"], ensure_ascii=False)
                yield f'{{"type": "card", "data": {card_json}}}\n'

            response_text = result.get("response", "任务执行完成")
            yield f'{{"type": "message", "content": "{response_text}"}}\n'

        except Exception as e:
            yield f'{{"type": "error", "message": "{str(e)}"}}\n'

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@app.get("/api/intents")
async def get_intents() -> dict[str, list[dict[str, str]]]:
    """Get available intent types."""
    return {
        "intents": [
            {
                "type": IntentType.PRODUCT_COMPARE.value,
                "name": "产品对比",
                "description": "对比多个保险产品的优劣",
                "example": "帮我对比平安福和国寿福",
            },
            {
                "type": IntentType.PRODUCT_INTRO.value,
                "name": "产品介绍",
                "description": "获取保险产品的详细介绍",
                "example": "介绍一下百万医疗险",
            },
            {
                "type": IntentType.SURRENDER.value,
                "name": "退保咨询",
                "description": "计算退保金额和损失",
                "example": "我要退保，能退多少钱",
            },
        ],
    }


@app.get("/api/products")
async def get_products() -> dict[str, list[str]]:
    """Get available products."""
    from backend.app.tools.product_compare import PRODUCT_DB

    return {
        "products": list(PRODUCT_DB.keys()),
    }
