import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 获取API Key，如果没有则尝试从EMBED_API_KEY获取（兼容hello-agents配置）
api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("EMBED_API_KEY")

client = OpenAI(
    api_key="sk-aa4e8c45f44f4cd28c86b23e2895217e",  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 百炼服务的base_url
)

try:
    completion = client.embeddings.create(
        model="text-embedding-v4",  # 使用v4模型
        input='衣服的质量杠杠的，很漂亮，不枉我等了这么久啊，喜欢，以后还来这里买',
        dimensions=1024, # 指定向量维度（仅 text-embedding-v3及 text-embedding-v4支持该参数）
        encoding_format="float"
    )

    print(completion.model_dump_json())

except Exception as e:
    print(f"Error: {e}")
    if not api_key:
        print("\n提示: 请确保已设置 DASHSCOPE_API_KEY 环境变量。")
