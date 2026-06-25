from typing import TypedDict, List, Dict, Annotated
import time
from langgraph.graph import StateGraph, START, END

# ==========================================
# 1. 状态工程：DevOps 状态字典
# ==========================================
def append_logs(old_logs: List[str], new_logs: List[str]) -> List[str]:
    return (old_logs or []) + new_logs

class DevOpsPipelineState(TypedDict):
    issue_id: str                              # 缺陷 ID
    target_file: str                           # 目标修复文件
    source_code_snippet: str                   # 漏洞源码片段
    generated_patch: str                       # 🛠️ Agent 编写的修复补丁
    test_result_stdout: str                    # 🧪 E2B 沙箱测试输出结果
    is_test_passed: bool                       # 测试门禁状态
    retry_count: int                           # 修复重试计数器
    pipeline_logs: Annotated[List[str], append_logs]

# ==========================================
# 2. 模拟 Redis 分布式锁机制
# ==========================================
class MockRedisLockManager:
    """模拟企业级 Redis 分布式锁"""
    def __init__(self):
        self.active_locks = set()

    def acquire_lock(self, file_path: str, agent_name: str) -> bool:
        if file_path in self.active_locks:
            print(f"   [Redis 锁拒绝] 🚨 文件 {file_path} 目前被其他流水线锁定中！ {agent_name} 必须原地排队等待...")
            return False
        self.active_locks.add(file_path)
        print(f"   [Redis 锁成功] 🔒 成功为 {agent_name} 锁定文件: {file_path}")
        return True

    def release_lock(self, file_path: str):
        if file_path in self.active_locks:
            self.active_locks.remove(file_path)
            print(f"   [Redis 锁释放] 🔓 文件 {file_path} 锁已释放，允许下个 Agent 竞争。")

# 初始化全局锁管理器
redis_lock_server = MockRedisLockManager()

# ==========================================
# 3. 节点定义 (Nodes)
# ==========================================

def issue_triage_bot(state: DevOpsPipelineState):
    """缺陷分发器"""
    print(f"\n[Node: 📋 Issue Triage Bot] 监测到 GitHub 新 Issue: #{state['issue_id']}")
    return {
        "target_file": "src/auth/payment.py",
        "source_code_snippet": "def process_payment(amount):\n    # ❌ 漏洞：未做金额负数防御校验\n    account.balance -= amount",
        "pipeline_logs": ["【缺陷解析】成功将 Issue 转化为待修复任务，目标文件: src/auth/payment.py"]
    }

def code_searcher(state: DevOpsPipelineState):
    """源码检索与并发控制（引入 Redis 锁）"""
    target = state["target_file"]
    print(f"\n[Node: 🔍 Code Searcher] 正在分析 AST 依赖图，并尝试锁定目标文件: {target} ...")
    
    # 尝试去 Redis 获取分布式锁
    lock_acquired = False
    while not lock_acquired:
        lock_acquired = redis_lock_server.acquire_lock(target, "DevOps_Agent_#99")
        if not lock_acquired:
            time.sleep(0.5)  # 模拟在分布式网关中排队等待
            
    return {
        "pipeline_logs": [f"【源码加锁】已利用 Redis 分布式锁锁定 {target}，防止并发代码合并冲突。"]
    }

def patch_developer(state: DevOpsPipelineState):
    """补丁编写员"""
    current_retry = state.get("retry_count", 0)
    print(f"\n[Node: 🛠️ Patch Developer] 正在编写代码修复补丁... (第 {current_retry + 1} 次尝试)")
    
    # 模拟 Agent 的行为：第一次它粗心大意，写的补丁里带有语法错误
    if current_retry == 0:
        patch = "def process_payment(amount):\n    if amount <= 0: raise ValueError('Invalid Amount')\n    account.balance -= amount"
        # 故意少些了一个闭合括号或变量未定义（模拟测试失败）
        patch_code = patch + "\n    # 故意注入错误：print(undefined_var)"
        logs = ["【补丁开发】编写了第一版修复补丁，但引入了未定义变量。"]
    else:
        # 第二次重试时，AI 拿到了报错堆栈，写出了完美补丁
        patch_code = "def process_payment(amount):\n    if amount <= 0:\n        raise ValueError('Amount must be positive')\n    account.balance -= amount"
        logs = ["【补丁开发】结合报错 Traceback 重新对齐，编写了完美的确定性防御补丁！"]
        
    return {
        "generated_patch": patch_code,
        "retry_count": current_retry + 1,
        "pipeline_logs": logs
    }

def cicd_reviewer(state: DevOpsPipelineState):
    """终审门禁：E2B 沙箱测试节点"""
    patch = state["generated_patch"]
    current_retry = state["retry_count"]
    print(f"\n[Node: 🧪 CI/CD Reviewer] 启动 E2B 安全沙箱隔离舱，开始运行 pytest 单元测试...")
    
    # 模拟沙箱内执行测试代码
    if "undefined_var" in patch:
        print("   ❌ 沙箱运行结果: NameError: name 'undefined_var' is not defined (测试失败)")
        return {
            "is_test_passed": False,
            "test_result_stdout": "NameError: name 'undefined_var' is not defined at line 4",
            "pipeline_logs": ["【自动化测试】沙箱反馈单元测试失败！捕获异常堆栈，拒绝上报主分支。"]
        }
    else:
        print("   ✅ 沙箱运行结果: pytest passed 100% (测试成功)")
        # 测试通过，释放 Redis 锁
        redis_lock_server.release_lock(state["target_file"])
        return {
            "is_test_passed": True,
            "test_result_stdout": "All tests passed successfully.",
            "pipeline_logs": ["【自动化测试】沙箱反馈全单测通过！释放 Redis 锁，准备触发正式 CI/CD 部署！"]
        }

# ==========================================
# 4. 路由决策与图拓扑编排
# ==========================================
def gate_router(state: DevOpsPipelineState):
    """门禁条件路由"""
    if state["is_test_passed"]:
        return "deploy_and_end"
    
    if state["retry_count"] >= 3:
        print("🚨 [安全熔断] 连续多次补丁测试失败，可能涉及底层重构，移交人类开发介入！")
        redis_lock_server.release_lock(state["target_file"]) # 熔断也必须记得释放锁
        return "human_fallback"
        
    return "fix_failed_retry"

# 初始化图
devops_workflow = StateGraph(DevOpsPipelineState)

# 注册节点
devops_workflow.add_node("issue_triage_bot", issue_triage_bot)
devops_workflow.add_node("code_searcher", code_searcher)
devops_workflow.add_node("patch_developer", patch_developer)
devops_workflow.add_node("cicd_reviewer", cicd_reviewer)

# 串行依赖流转
devops_workflow.add_edge(START, "issue_triage_bot")
devops_workflow.add_edge("issue_triage_bot", "code_searcher")
devops_workflow.add_edge("code_searcher", "patch_developer")
devops_workflow.add_edge("patch_developer", "cicd_reviewer")

# 条件网关：决定是通过还是重新被打回
devops_workflow.add_conditional_edges(
    "cicd_reviewer",
    gate_router,
    {
        "deploy_and_end": END,                   # 成功，流水线终结
        "human_fallback": END,                   # 熔断，交由人类
        "fix_failed_retry": "patch_developer"    # 🧪 测试没过，直接带着报错堆栈单向打回给开发节点！
    }
)

app_devops = devops_workflow.compile()


if __name__ == "__main__":
    initial_input = {
        "issue_id": "1024",
        "retry_count": 0,
        "is_test_passed": False,
        "pipeline_logs": []
    }
    
    print("=== 🎬 启动企业级 AI-Driven DevOps 闭环自动修复平台 ===")
    config = {"configurable": {"thread_id": "pipeline_run_001"}}
    
    final_output = app_devops.invoke(initial_input, config)
    
    print("\n==================================================")
    print("📜 最终全链路生产级追踪日志（DevOps Audit Trail）：")
    for idx, log in enumerate(final_output["pipeline_logs"], 1):
        print(f"{idx}. {log}")
    print("==================================================")