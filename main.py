from typing import TypedDict
from langgraph.graph import StateGraph, END

# 1. 定义 Agent 的“记忆”（状态）
# 这就是流程图中贯穿始终的数据，我们先放两个最的
class AgentState(TypedDict):
    session_id: str
    retry_count: int

# 2. 定义一个简单的动作节点（相当于 Agent 的第一步）
def test_node(state: AgentState):
    print("\n🤖 Agent: '我醒了！环境配置完美，随时可以开始生成 3D 资产！'")
    
    # 模拟干了一次活，让计数器加 1
    current_count = state.get("retry_count", 0)
    return {"retry_count": current_count + 1}

# 3. 把节点连成“流程图”
workflow = StateGraph(AgentState)
workflow.add_node("start", test_node) # 添加节点
workflow.set_entry_point("start")     # 设置起点
workflow.add_edge("start", END)       # 执行完起点，直接结束

# 4. 编译成可执行的程序
app = workflow.compile()

# 如果直接运行这个文件，就会执行下面的代码
if __name__ == "__main__":
    # 给 Agent 喂入初始数据
    initial_state = {"session_id": "test_001", "retry_count": 0}
    
    print("⏳ 开始运行 Agent 工作流...")
    # 启动！
    result = app.invoke(initial_state)
    
    print(f"\n✅ 运行结束，Agent 最终记住的状态是: {result}")