from typing import Any, Dict, List

from pydantic import BaseModel, Field

from src.llm.base import BaseLLMCaller
from src.prompts import prompt


# 1. 定义总经理的拆任务字典
class SubTask(BaseModel):
    task_id: int
    worker_type: str = Field(description="负责该任务的专家类型，可选: 'REFUND' 或 'TRAVEL'")
    task_content: str = Field(description="具体分派给该专家的任务文本")


class TaskPlan(BaseModel):
    thought: str = Field(description="总经理拆解任务的思考过程")
    plan_list: List[SubTask] = Field(description="拆解出来的子任务列表")


class TaskResultSummary(BaseModel):
    final_reply_to_user: str = Field(description="汇总所有专家结果后，返回给用户的最终答复")


# 2. 核心调度器类
class MultiAgentOrchestrator(BaseLLMCaller):
    ORCHESTRATOR_SYSTEM_PROMPT = prompt("""
        你是一个多专家调度器。
        你的职责：
        1. 拆解用户问题
        2. 为每个子任务选择合适专家
        3. 汇总专家结果
        4. 严格输出符合指定 schema 的 JSON
    """)

    def __init__(self, workers: Dict[str, Any]):
        super().__init__(system_prompt=self.ORCHESTRATOR_SYSTEM_PROMPT)
        self.workers = workers  # 传入你之前写好的专家实例字典，如 {'REFUND': refund_agent, 'TRAVEL': travel_agent}

    def dispatch(self, user_query: str):
        print("====== 🚀 [总经理] 开始拆解复合任务 ======")

        # 让大模型严格按照 TaskPlan 结构输出 JSON (2026年标准的结构化路由)
        # 这里的 call_llm_with_pydantic 是我们在 Week 4 学的底层方法
        plan_output = self.call_llm_with_pydantic(user_query, response_model=TaskPlan)
        print(f"思考过程: {plan_output.thought}\n")

        # 准备一个收集箱，收集各个专家的汇报
        reports = []

        # 3. 内部拆实例运行（落实你的直觉！）
        for sub_task in plan_output.plan_list:
            worker_type = sub_task.worker_type
            content = sub_task.task_content

            print(f"👉 正在指派任务 [{sub_task.task_id}] 给 [{worker_type}] 专家，任务内容: {content}")

            if worker_type in self.workers:
                # 调动对应的专家实例运行，并拿到专家的 Observation/Final Answer
                worker_result = self.workers[worker_type].run(content)
                reports.append(f"任务 {sub_task.task_id} 汇报: {worker_result}")
            else:
                reports.append(f"任务 {sub_task.task_id} 失败: 找不到对应的专家类型 {worker_type}")

        # 4. 总经理统一组织语言汇总汇报
        print("\n====== 📊 [总经理] 开始聚合结果并统一回复 ======")
        final_summary_prompt = prompt(f"""
            原始用户需求: {user_query}
            专家执行汇报: {chr(10).join(reports)}
            请统一组织语言回复用户。
        """)

        # 这里调用我们刚刚定义的 TaskResultSummary 模型
        final_response = self.call_llm_with_pydantic(
            final_summary_prompt,
            response_model=TaskResultSummary,
        )
        return final_response.final_reply_to_user
