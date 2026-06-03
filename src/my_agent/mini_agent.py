import inspect
import json
import os
import re
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter, ValidationError
from zai import ZhipuAiClient


class ToolCallPayload(BaseModel):
    """工具调用输出结构"""

    type: Literal["tool_call"]
    thought: str = Field(min_length=1)
    action: str = Field(min_length=1)
    action_input: dict[str, Any] = Field(default_factory=dict)


class FinalAnswerPayload(BaseModel):
    """最终答案输出结构"""

    type: Literal["final_answer"]
    thought: str = Field(min_length=1)
    final_answer: str = Field(min_length=1)


AgentPayload = Annotated[Union[ToolCallPayload, FinalAnswerPayload], Field(discriminator="type")]


class MiniAgent:
    """
    一个简单的 Agent 类，实现 ReAct 模式（Reasoning + Acting）
    """

    def __init__(self, system_prompt, tools):
        """
        初始化 Agent

        Args:
            system_prompt: 系统提示词，定义 Agent 的角色和任务
            tools: 工具字典，格式如 {"工具名": 函数}
        """
        self.tools = tools
        self.max_steps = 5
        self.client = ZhipuAiClient(api_key=os.getenv("ZAI_API_KEY"))
        self.response_adapter = TypeAdapter[Any](AgentPayload)

        # 构建完整的系统提示词
        tool_descriptions = self._build_tool_description(tools)
        self.system_prompt = self._build_system_prompt(system_prompt, tool_descriptions)
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def _build_tool_description(self, tools):
        """构建工具描述文本"""
        descriptions = []
        for name, func in tools.items():
            doc = inspect.getdoc(func) or "无描述"
            signature = inspect.signature(func)
            descriptions.append(f"- `{name}{signature}`: {doc}")
        return "\n".join(descriptions)

    def _build_system_prompt(self, base_prompt, tool_descriptions):
        """构建完整的系统提示词"""
        return f"""{base_prompt}

## 可用工具
{tool_descriptions}

## 重要规则（必须严格遵守）
1. 你每次只能输出一个 JSON 对象
2. 不要输出 Markdown、代码块、额外解释或 Observation
3. 如果要调用工具，必须输出 `type=tool_call`
4. 如果任务已完成，必须输出 `type=final_answer`
5. `action_input` 必须是 JSON 对象，key 必须与工具参数名一致
6. 只有在获得足够信息后才能输出 `final_answer`

## JSON 输出格式
### 工具调用
{{
  "type": "tool_call",
  "thought": "简要分析当前情况",
  "action": "工具名",
  "action_input": {{
    "参数名": "参数值"
  }}
}}

### 最终答案
{{
  "type": "final_answer",
  "thought": "简要说明结论依据",
  "final_answer": "给用户的最终答案"
}}

## 禁止行为
❌ 严禁编造 Observation 数据
❌ 严禁一次性输出多轮推理过程
❌ 严禁输出无法解析的自由文本
❌ 严禁传入与工具签名不匹配的参数名

## 注意事项
1. 必须通过工具获取信息，不能编造
2. 如果工具调用失败，根据返回的 Observation 调整下一步
3. 输出必须是合法 JSON
"""

    def _extract_json_text(self, text):
        """从模型回复中提取 JSON 文本"""
        stripped = text.strip()

        if stripped.startswith("```"):
            code_block_match = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, re.DOTALL)
            if code_block_match:
                return code_block_match.group(1).strip()

        return stripped

    def _parse_agent_response(self, response_text):
        """解析并校验 Agent 输出"""
        json_text = self._extract_json_text(response_text)
        data = json.loads(json_text)
        return self.response_adapter.validate_python(data)

    def _normalize_observation(self, observation):
        """规范化 Observation，便于回灌给模型"""
        if isinstance(observation, str):
            return observation

        return json.dumps(observation, ensure_ascii=False, indent=2)

    # ========== LLM 调用方法 ==========

    def call_llm_simple(self, prompt):
        """
        简单调用 LLM（用于错误处理等简单场景）

        Args:
            prompt: 简单的文本提示

        Returns:
            LLM 的文本响应
        """
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("ZAI_MODEL"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={ "type": "json_object" }
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM 调用失败：{e}"

    def call_llm(self, messages):
        """
        完整调用 LLM（用于主对话循环，支持上下文）

        Args:
            messages: 消息列表，包含对话历史

        Returns:
            LLM 的文本响应
        """
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("ZAI_MODEL"),
                messages=messages,
                temperature=0,
                response_format={ "type": "json_object" }
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    # ========== 错误处理方法 ==========

    def handle_error_with_user(self, original_error):
        """
        人性化处理工具执行错误，与用户交互

        Args:
            original_error: 原始异常对象

        Returns:
            "STOP" 或包含用户反馈的字符串
        """
        # 第一步：错误发给 LLM 进行转换
        prompt = f"系统报错：{str(original_error)}。请你向用户解释这个错误，并询问是 [继续] 还是 [停止]。请说人话。"
        human_explanation = self.call_llm_simple(prompt)

        # 第二步：打印 LLM 返回的结果
        print(f"\n[Agent 状态反馈]: {human_explanation}")

        # 第三步：获取用户真实的意图
        choice = input("你的选择 (C:继续 / S:停止): ")

        if choice.lower() == 's':
            return "STOP"
        else:
            return {
                "status": "error",
                "message": "用户已选择继续",
                "original_error": str(original_error)
            }

    # ========== 主循环方法 ==========

    def run(self, user_input):
        """
        运行 Agent 主循环

        Args:
            user_input: 用户输入的指令

        Returns:
            最终答案或错误信息
        """
        self.messages.append({"role": "user", "content": user_input})

        for step in range(self.max_steps):
            print(f"\n{'=' * 50}")
            print(f"[Step {step + 1}/{self.max_steps}]")
            print(f"{'=' * 50}")

            # 1. 让模型思考
            response = self.call_llm(self.messages)
            print(f"\n[LLM Response]:\n{response}")

            # 2. 解析结构化输出
            try:
                payload = self._parse_agent_response(response)
                print(f"\n[Parsed Payload]:\n{payload.model_dump_json(indent=2)}")
            except (json.JSONDecodeError, ValidationError) as e:
                print(f"\n[Warning] 输出格式不正确：{e}")
                self.messages.append({"role": "assistant", "content": response})
                self.messages.append({
                    "role": "user",
                    "content": (
                        "你的上一条回复无法通过 JSON/Pydantic 校验。"
                        "请严格输出一个合法 JSON 对象，且必须符合 system prompt 中定义的 schema。"
                    )
                })
                continue

            # 3. 检查是否已经是最终答案
            if isinstance(payload, FinalAnswerPayload):
                print("\n[✓] 任务完成")
                self.messages.append({"role": "assistant", "content": response})
                return payload.final_answer

            # 4. 执行工具并处理异常
            func_name = payload.action
            action_input = payload.action_input
            print(f"\n[Action] 调用工具：{func_name}({action_input})")
            print(f"[Debug] 可用工具列表：{list(self.tools.keys())}")

            try:
                if func_name not in self.tools:
                    raise KeyError(f"工具 '{func_name}' 不存在，可用工具：{list(self.tools.keys())}")

                observation = self.tools[func_name](**action_input)
                observation = self._normalize_observation(observation)
                print(f"[Observation] 结果：{observation}")
            except Exception as e:
                print(f"[Error] 工具执行失败：{e}")
                import traceback
                traceback.print_exc()
                observation = self.handle_error_with_user(e)
                if observation == "STOP":
                    print("\n[✗] 用户选择停止")
                    break
                observation = self._normalize_observation(observation)

            # 5. 喂回观察结果
            self.messages.append({"role": "assistant", "content": response})
            self.messages.append({
                "role": "user",
                "content": f"Observation: {observation}"
            })

        print("\n[✗] 达到最大循环次数，未能完成任务")
        return "达到最大循环次数，未能完成任务"
