import json
import os
import re
from typing import Type

from pydantic import BaseModel
from zai import ZhipuAiClient

from src.prompts import prompt


class BaseLLMCaller:
    """封装通用的 LLM 调用、system prompt 注入与 Pydantic 结构化解析能力"""

    def __init__(self, system_prompt: str | None = None):
        self.client = ZhipuAiClient(api_key=os.getenv("ZAI_API_KEY"))
        self.system_prompt = system_prompt

    def _extract_json_text(self, text: str) -> str:
        """从模型回复中提取 JSON 文本"""
        stripped = text.strip()

        if stripped.startswith("```"):
            code_block_match = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, re.DOTALL)
            if code_block_match:
                return code_block_match.group(1).strip()

        return stripped

    def build_messages(
        self,
        user_input: str | None = None,
        messages=None,
        extra_system_prompts: list[str] | None = None,
    ):
        """统一构造消息列表，并在需要时自动注入 system prompt"""
        system_messages = []
        if self.system_prompt:
            system_messages.append({"role": "system", "content": self.system_prompt})
        if extra_system_prompts:
            system_messages.extend(
                {"role": "system", "content": prompt}
                for prompt in extra_system_prompts
            )

        if messages is not None:
            if messages and messages[0].get("role") == "system":
                return [*system_messages, *messages[1:]] if system_messages else messages
            return [*system_messages, *messages] if system_messages else messages

        result = [*system_messages]
        if user_input is not None:
            result.append({"role": "user", "content": user_input})
        return result

    def call_llm(self, messages, temperature: float = 0, response_format: dict | None = None) -> str:
        """调用 LLM，返回原始文本内容"""
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("ZAI_MODEL"),
                messages=self.build_messages(messages=messages),
                temperature=temperature,
                response_format=response_format,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    def _build_structured_output_prompt(self, response_model: Type[BaseModel]) -> str:
        """构造结构化输出约束，并注入到 system prompt"""
        schema = response_model.model_json_schema()
        schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
        return prompt(f"""
            你必须严格输出一个合法的 JSON 对象。
            不要输出 Markdown、代码块、额外解释或 JSON 之外的任何内容。
            输出内容必须完全符合下面的 JSON Schema。

            JSON Schema:
            {schema_json}
        """)

    def call_llm_with_pydantic(self, prompt_or_messages, response_model: Type[BaseModel]):
        """调用 LLM，并通过 system prompt 注入 schema 后解析为指定的 Pydantic 模型"""
        structured_prompt = self._build_structured_output_prompt(response_model)

        if isinstance(prompt_or_messages, str):
            messages = self.build_messages(
                user_input=prompt_or_messages,
                extra_system_prompts=[structured_prompt],
            )
        else:
            messages = self.build_messages(
                messages=prompt_or_messages,
                extra_system_prompts=[structured_prompt],
            )

        response_text = self.call_llm(
            messages,
            temperature=0,
            response_format={"type": "json_object"},
        )
        json_text = self._extract_json_text(response_text)
        return response_model.model_validate_json(json_text)
