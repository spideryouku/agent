import unittest
from typing import List, Any
from ReActAgent import ReActAgent
from tools import ToolExecutor, calculator

# Mock LLM Client
class MockLLM:
    def __init__(self, responses: List[str]):
        self.responses = responses
        self.call_count = 0

    def think(self, messages: List[Any], temperature: float = 1) -> str:
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            return resp
        return "Action: Finish[No more mock responses]"

class TestReActAgent(unittest.TestCase):
    def setUp(self):
        self.executor = ToolExecutor()
        self.executor.registerTool("Calculator", "Math calculator", calculator)

    def test_calculator_logic(self):
        # Test basic calculation
        result = calculator("(10 + 20) * 3")
        self.assertEqual(result, "90")
        
        # Test complex calculation
        result = calculator("(123 + 456) * 789 / 12")
        # (579 * 789) / 12 = 456831 / 12 = 38069.25
        self.assertEqual(result, "38069.25")

        # Test error handling
        result = calculator("1 / 0")
        self.assertEqual(result, "错误: 除数不能为零。")
        
        result = calculator("invalid syntax")
        self.assertTrue("错误" in result)

    def test_agent_success(self):
        # Mock responses for a successful run
        responses = [
            "Thought: I need to calculate the expression.\nAction: Calculator[(123 + 456) * 789 / 12]",
            "Thought: I have the result.\nAction: Finish[38069.25]"
        ]
        llm = MockLLM(responses)
        agent = ReActAgent(llm_client=llm, tool_executor=self.executor)
        
        answer = agent.run("Calculate (123 + 456) * 789 / 12")
        self.assertEqual(answer, "38069.25")

    def test_failure_guidance_mechanism(self):
        # Mock responses that trigger failures
        # 1. Invalid Action Format (First failure)
        # 2. Unknown Tool (Second failure -> Should trigger guidance)
        # 3. Valid Tool (Success -> Should reset)
        responses = [
            "Thought: Invalid format\nAction: InvalidFormat",
            "Thought: Wrong tool\nAction: UnknownTool[123]", 
            "Thought: Correct now\nAction: Calculator[1+1]",
            "Thought: Done\nAction: Finish[2]"
        ]
        llm = MockLLM(responses)
        agent = ReActAgent(llm_client=llm, tool_executor=self.executor)
        
        agent.run("Test failure handling")
        
        # Verify history
        # History index 0: Invalid Format
        # History index 1: Unknown Tool (Should have guidance)
        
        print("\n--- History Inspection ---")
        for i, h in enumerate(agent.history):
            print(f"Step {i}: {h}")
            
        self.assertTrue(len(agent.history) >= 2)
        
        # Check Step 1 (Index 0) - No guidance yet (consecutive=1)
        self.assertNotIn("系统引导", agent.history[0])
        
        # Check Step 2 (Index 1) - Guidance should appear (consecutive=2)
        self.assertIn("系统引导", agent.history[1])
        self.assertIn("连续 2 次", agent.history[1])

if __name__ == '__main__':
    unittest.main()
