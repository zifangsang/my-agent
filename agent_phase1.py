import random
from typing import TypedDict
from langgraph.graph import StateGraph, END

# ==========================================
# 1. 定义数据状态 (Agent 在整个流程中携带的档案)
# ==========================================
class AgentState(TypedDict):
    retry_count: int      # 重试次数
    image_path: str       # 当前生成的图片路径
    score: int            # 视觉模型打出的分数
    status: str           # 当前状态信息

# ==========================================
# 2. 模拟外部工具 (后续这里会替换成你真实的 API)
# ==========================================
def tool_generate_image(prompt: str) -> str:
    """模拟生图工具 (比如 Stable Diffusion)"""
    print(f"  🎨 [生图工具] 正在生成立面图... (提示词: {prompt})")
    # 假设生成了一张图片并保存在本地
    return "./output/facade_v1.png"

def tool_ask_image_qwen(image_path: str) -> int:
    """模拟 Qwen3.5/Gemini 视觉大模型进行质检"""
    print(f"  👁️ [视觉模型] 正在审视图片 {image_path}...")
    # 模拟 AI 打分：随机给一个 1 到 10 的分数
    # 实际应用中，这里会调用 Ollama 里的 Qwen3.5 或 Nano Banana 接口
    score = random.randint(3, 10) 
    print(f"  📝 [视觉模型] 质检完毕，打分为: {score}/10")
    return score

# ==========================================
# 3. 定义图的节点 (Agent 执行的具体动作)
# ==========================================
def node_generate(state: AgentState):
    print(f"\n▶️ [节点执行] 第 {state['retry_count'] + 1} 次尝试生成图片...")
    img_path = tool_generate_image("建筑正交立面图, 纯白背景")
    return {"image_path": img_path}

def node_qa_check(state: AgentState):
    print("\n▶️ [节点执行] 进入质量检测环节...")
    score = tool_ask_image_qwen(state["image_path"])
    return {"score": score}

# ==========================================
# 4. 定义条件分支 (大脑的判断逻辑)
# ==========================================
def check_score(state: AgentState) -> str:
    """判断分数是否达标，决定下一步去哪"""
    if state["score"] >= 7:
        print("  ✅ [条件判断] 分数达标 (>=7)，通过质检！")
        return "pass"
    else:
        print("  ❌ [条件判断] 分数不达标 (<7)，打回重画！")
        return "fail"

# ==========================================
# 5. 组装 LangGraph 工作流
# ==========================================
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("generate_image", node_generate)
workflow.add_node("qa_check", node_qa_check)

# 定义连线 (流程顺序)
workflow.set_entry_point("generate_image")         # 第一步：画图
workflow.add_edge("generate_image", "qa_check")    # 画完图后，交给质检

# 添加条件边 (根据质检结果决定是结束，还是循环)
workflow.add_conditional_edges(
    "qa_check",             # 判断的起点是 qa_check 节点
    check_score,            # 调用上面定义的判断函数
    {
        "pass": END,               # 如果函数返回 "pass"，流程结束 (进入下一阶段)
        "fail": "generate_image"   # 如果函数返回 "fail"，线连回 generate_image 重新画
    }
)

app = workflow.compile()

# ==========================================
# 6. 运行测试
# ==========================================
if __name__ == "__main__":
    print("🚀 启动 3D 资产生成 Agent (Phase 1 测试)...")
    
    # 初始状态
    initial_state = {
        "retry_count": 0,
        "image_path": "",
        "score": 0,
        "status": "初始化"
    }
    
    # 运行流程
    final_state = app.invoke(initial_state)
    print("\n🎉 最终结果:", final_state)