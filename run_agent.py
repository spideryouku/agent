from dotenv import load_dotenv
load_dotenv()


from hello_agents import HelloAgentsLLM, SimpleAgent

# 自动检测provider（推荐）
llm = HelloAgentsLLM()

# 创建Agent
agent = SimpleAgent("AI助手", llm)
response = agent.run("你好！")
print(response)
