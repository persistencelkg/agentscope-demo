# 保险智能助手 - 基于 AgentScope 构建

这是一个基于 AgentScope 框架开发的保险智能助手，支持产品对比、产品介绍、退保咨询等功能。

## 架构设计

```
insurance-agent/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── agents/            # Agent 实现
│   │   │   ├── intent_agent.py    # 意图识别 Agent
│   │   │   └── executor_agent.py  # 执行 Agent
│   │   ├── tools/             # 工具函数
│   │   │   └── product_compare.py # 保险产品工具
│   │   ├── models/            # 数据模型
│   │   │   └── schemas.py
│   │   ├── services/          # 业务服务
│   │   │   └── intent_service.py  # 意图识别服务
│   │   └── main.py           # FastAPI 入口
│   ├── requirements.txt
│   └── .env.example
└── frontend/                  # 前端应用
    ├── src/
    │   ├── components/
    │   │   ├── Chat/          # 聊天组件
    │   │   └── Cards/         # 卡片组件
    │   ├── services/          # API 服务
    │   └── types/             # TypeScript 类型
    └── package.json
```

## 核心功能

### 1. 意图识别（Intent Recognition）

支持三种提取方式：
- **精确提取（Exact）**：基于正则表达式模式匹配
- **模糊提取（Fuzzy）**：基于字符串相似度匹配
- **向量提取（Vector）**：基于 TF-IDF 和余弦相似度

### 2. 工具调用（Tool Calling）

使用 AgentScope 的 Toolkit 管理工具：
- `compare_products` - 产品对比
- `get_product_intro` - 产品介绍
- `calculate_surrender` - 退保计算

### 3. 卡片渲染（Card Rendering）

工具执行结果以卡片形式展示：
- 产品对比卡片
- 产品介绍卡片
- 退保计算卡片

## 快速开始

### 后端启动

```bash
cd insurance-agent/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 DASHSCOPE_API_KEY

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd insurance-agent/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000 即可使用。

## 使用示例

### 产品对比
```
用户：帮我对比平安福和国寿福
助手：已为您对比 2 个产品，请查看对比卡片。
[展示产品对比卡片]
```

### 产品介绍
```
用户：介绍一下百万医疗险
助手：以下是 百万医疗险 的详细介绍。
[展示产品介绍卡片]
```

### 退保咨询
```
用户：我要退保，投保了3年
助手：以下是 平安福 的退保计算结果。
[展示退保计算卡片]
```

## API 接口

### POST /api/chat
处理聊天消息

**请求体：**
```json
{
  "message": "帮我对比平安福和国寿福",
  "session_id": "session-123"
}
```

**响应：**
```json
{
  "message": "已为您对比 2 个产品",
  "cards": [...],
  "intent": {...},
  "session_id": "session-123"
}
```

### POST /api/chat/stream
流式处理聊天消息

### GET /api/intents
获取可用意图类型

### GET /api/products
获取可用产品列表

## 技术栈

### 后端
- **AgentScope** - AI Agent 框架
- **FastAPI** - Web 框架
- **Pydantic** - 数据验证
- **scikit-learn** - 机器学习（向量匹配）

### 前端
- **React** - UI 框架
- **TypeScript** - 类型安全
- **TailwindCSS** - 样式框架
- **Vite** - 构建工具

## 扩展指南

### 添加新产品
编辑 `backend/app/tools/product_compare.py` 中的 `PRODUCT_DB` 字典。

### 添加新意图
1. 在 `IntentType` 枚举中添加新类型
2. 在 `INTENT_PATTERNS` 中添加匹配模式
3. 在 `INTENT_TRAINING_DATA` 中添加训练数据
4. 创建对应的工具函数
5. 在 `executor_agent.py` 中注册工具

### 添加新卡片
1. 在 `CardType` 枚举中添加新类型
2. 创建对应的 Card 组件
3. 在 `ChatMessage.tsx` 中添加渲染逻辑

## License

MIT
