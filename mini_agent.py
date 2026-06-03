import re
import zai
import os
from zai import ZhipuAiClient


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
        
        # 构建完整的系统提示词
        tool_descriptions = self._build_tool_description(tools)
        self.system_prompt = self._build_system_prompt(system_prompt, tool_descriptions)
        self.messages = [{"role": "system", "content": self.system_prompt}]
    
    def _build_tool_description(self, tools):
        """构建工具描述文本"""
        descriptions = []
        for name, func in tools.items():
            doc = func.__doc__ or "无描述"
            descriptions.append(f"- `{name}`: {doc}")
        return "\n".join(descriptions)
    
    def _build_system_prompt(self, base_prompt, tool_descriptions):
        """构建完整的系统提示词"""
        return f"""{base_prompt}

## 可用工具
{tool_descriptions}

## 重要规则（必须严格遵守）
1. **你只输出 Thought 和 Action**，绝对不要输出 Observation
2. Observation 是系统执行工具后自动返回的，不是你生成的
3. 每次只输出一轮 Thought + Action，然后等待系统返回 Observation
4. 收到 Observation 后，再决定下一步行动
5. 只有在获得足够信息后才能输出 Final Answer

## 回复格式
 Thought: 分析当前情况，规划下一步
Action: 工具名 (参数)

（然后等待系统返回 Observation）

重复以上步骤直到完成任务，最后输出：
Final Answer: 给用户的最终答案

## 禁止行为
❌ 严禁编造 Observation 数据
❌ 严禁一次性输出多轮 Thought-Action-Observation
❌ 严禁在没有工具支持的情况下编造信息

## 注意事项
1. 必须通过工具获取信息，不能编造
2. 如果工具调用失败，分析原因并尝试其他方法
3. 只有在获得足够信息后才能输出 Final Answer
"""

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
                temperature=0.7
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
                temperature=0
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
            return f"用户已选择继续。报错原因可能是：{str(original_error)}。请根据此反馈重新规划路径。"

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
            print(f"\n{'='*50}")
            print(f"[Step {step + 1}/{self.max_steps}]")
            print(f"{'='*50}")
            
            # 1. 让模型思考
            response = self.call_llm(self.messages)
            print(f"\n[LLM Response]:\n{response}")
            print(f"\n[Debug] 尝试匹配 Action 正则表达式...")
            
            # 2. 检查是否已经是最终答案
            if "Final Answer:" in response:
                print(f"\n[✓] 任务完成")
                return response

            # 3. 捕捉 Action
            action_match = re.search(r"Action:\s*(\w+)\((.*)\)", response)
            print(f"[Debug] action_match 结果：{action_match}")
            
            if action_match:
                func_name = action_match.group(1)
                args = action_match.group(2)
                print(f"\n[Action] 调用工具：{func_name}({args})")
                print(f"[Debug] 可用工具列表：{list(self.tools.keys())}")
                print(f"[Debug] func_name='{func_name}', in tools={func_name in self.tools}")
                
                # 4. 执行工具并处理异常
                try:
                    if func_name not in self.tools:
                        raise KeyError(f"工具 '{func_name}' 不存在，可用工具：{list(self.tools.keys())}")
                    
                    # 解析参数：如果 args 为空字符串，则不传参数；否则尝试解析
                    print(f"[Debug] 原始 args: '{args}'")
                    if args.strip() == "":
                        # 无参数调用
                        observation = self.tools[func_name]()
                    else:
                        # 有参数调用，直接传入字符串
                        observation = self.tools[func_name](args)
                    
                    print(f"[Observation] 结果：{observation}")
                except Exception as e:
                    print(f"[Error] 工具执行失败：{e}")
                    import traceback
                    traceback.print_exc()
                    observation = self.handle_error_with_user(e)
                    if observation == "STOP":
                        print(f"\n[✗] 用户选择停止")
                        break
                
                # 5. 喂回观察结果
                self.messages.append({"role": "assistant", "content": response})
                self.messages.append({"role": "user", "content": f"Observation: {observation}"})
            else:
                print(f"\n[Warning] 回复格式不正确，引导模型")
                self.messages.append({"role": "assistant", "content": response})
                self.messages.append({
                    "role": "user", 
                    "content": "你的回复格式不正确。请使用以下格式：\nAction: 工具名 (参数)\n或者\nFinal Answer: 你的最终答案"
                })
        
        print(f"\n[✗] 达到最大循环次数，未能完成任务")
        return "达到最大循环次数，未能完成任务"

