import sys
from api import HelloAgentsLLM
from ReflectionAgent import ReflectionAgent

if __name__ == "__main__":
    # 1. 初始化 LLM
    llm = HelloAgentsLLM()

    # 2. 初始化 Reflection 智能体
    agent = ReflectionAgent(llm_client=llm)

    # 3. 获取任务 (优先从命令行参数获取，否则使用默认任务)
    if len(sys.argv) > 1:
        task = sys.argv[1]
    else:
        # 默认任务：找素数（这是一个经典的可以被反复优化的算法题）
        #task = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"
        task = "海南三亚旅游攻略"

    # 4. 运行智能体
    agent.run(task)
