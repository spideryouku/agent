import re
from typing import Optional, Tuple
from api import HelloAgentsLLM
from tools import ToolExecutor

# --- ReAct 提示词模板 ---
REACT_PROMPT_TEMPLATE = """
你是一个强大的智能助手，可以使用工具与外界交互。

你可以使用以下工具:
{tools}

请按照以下格式进行思考和行动:

Question: 需要回答的问题
Thought: 思考当前需要做什么。
Action: 采取的行动，格式为 ToolName[Input]。例如: Search[Python latest version]
Observation: 行动的结果 (由系统提供)。
... (重复 Thought/Action/Observation N 次)
Thought: 我已经收集了足够的信息。
Action: Finish[最终答案]

开始!

Question: {question}
{history}
"""

class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def _parse_output(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析LLM的输出，提取Thought和Action。"""
        thought_match = re.search(r"Thought: (.*)", text)
        action_match = re.search(r"Action: (.*)", text)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析Action字符串，提取工具名称和输入。"""
        match = re.match(r"(\w+)\[(.*)\]", action_text)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def run(self, question: str):
        """
        运行ReAct智能体来回答一个问题。
        """
        self.history = [] # 每次运行时重置历史记录
        current_step = 0
        consecutive_failures = 0  # 连续失败计数器

        while current_step < self.max_steps:
            current_step += 1
            print(f"--- 第 {current_step} 步 ---")

            # 1. 格式化提示词
            tools_desc = self.tool_executor.getAvailableTools()
            print(f"{current_step}--- 提示词 {tools_desc}  ---")
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )

            # 2. 调用LLM进行思考
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)
            print(f"{current_step}--- prompt: {prompt}  ---")
            
            if not response_text:
                print("错误:LLM未能返回有效响应。")
                # 这种情况通常是网络或API问题，可以选择重试或终止，这里暂时终止
                break

            # 3. 解析LLM的输出
            thought, action = self._parse_output(response_text)
            
            if thought:
                print(f"思考: {thought}")

            # 处理 Action 解析失败的情况
            if not action:
                print("警告:未能解析出有效的Action。")
                consecutive_failures += 1
                observation = "系统提示: 你的输出格式不正确。请务必包含 'Action: ToolName[Input]'，或者如果是最终答案请使用 'Action: Finish[答案]'。"
                
                # 记录这次失败的尝试
                step_record = f"Thought: {thought or 'None'}\nObservation: {observation}"
                self.history.append(step_record)
                
                # 检查是否需要引导
                if consecutive_failures >= 2:
                    self.history[-1] += f"\n(系统引导: 你已经连续失败 {consecutive_failures} 次。请严格遵守 Action 格式，并检查可用工具列表: {tools_desc})"
                
                continue

            # 4. 执行Action
            if action.startswith("Finish"):
                # 如果是Finish指令，提取最终答案并结束
                final_answer_match = re.match(r"Finish\[(.*)\]", action)
                final_answer = final_answer_match.group(1) if final_answer_match else action
                print(f"🎉 最终答案: {final_answer}")
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)
            
            # 处理 Action 格式错误 (例如 Action: Search without brackets)
            if not tool_name or not tool_input:
                print(f"警告: 无效的 Action 格式 '{action}'")
                consecutive_failures += 1
                observation = f"系统提示: Action '{action}' 格式无效。正确格式为 ToolName[Input]。"
            else:
                print(f"🎬 行动: {tool_name}[{tool_input}]")
                
                tool_function = self.tool_executor.getTool(tool_name)
                if not tool_function:
                    consecutive_failures += 1
                    observation = f"错误:未找到名为 '{tool_name}' 的工具。请检查可用工具列表。"
                else:
                    observation = tool_function(tool_input) # 调用真实工具
                    # 检查工具执行结果是否包含错误信息
                    if observation.startswith("错误") or "Error" in observation:
                        consecutive_failures += 1
                    else:
                        consecutive_failures = 0 # 成功执行，重置计数器
            
            print(f"👀 观察: {observation}")
            
            # 失败引导机制
            if consecutive_failures >= 2:
                guidance = f"\n(系统引导: 检测到连续 {consecutive_failures} 次操作失败或无效。请仔细阅读工具定义，确保输入参数正确，且工具名称存在。可用工具: {tools_desc})"
                observation += guidance
                print(f"💡 触发系统引导: {guidance}")

            # 将本轮的Action和Observation添加到历史记录中
            step_record = f"Thought: {thought}\nAction: {action}\nObservation: {observation}"
            self.history.append(step_record)

        # 循环结束
        print("已达到最大步数，流程终止。")
        return None
