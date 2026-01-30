from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.agents import ChatAgent
from camel.toolkits import SearchToolkit
import os
from dotenv import load_dotenv

load_dotenv()

# Map local env vars to what CAMEL expects or use them directly
if os.getenv("LLM_API_KEY") and not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY") or ""
    # Also set base URL if it's not default OpenAI
    if os.getenv("LLM_BASE_URL"):
        os.environ["OPENAI_API_BASE"] = os.getenv("LLM_BASE_URL") or ""

# Since the user's code explicitly requested GPT-4o, but our env has DeepSeek,
# we might run into model availability issues if we point to DeepSeek API but ask for GPT-4o.
# However, the user's request is to "Run the following Python code". 
# I should try to honor the code structure but make it work with the available credentials.
# If I use ModelPlatformType.OPENAI, it expects OpenAI-compatible API.
# DeepSeek is OpenAI compatible.
# But `model_type=ModelType.GPT_4O` might be rejected by DeepSeek API if they validate model names strictly 
# and don't map "gpt-4o" to their model.
# DeepSeek usually expects "deepseek-chat" or "deepseek-coder".
#
# Let's try to adjust the model_type if we are using the LLM_BASE_URL from .env which is deepseek.

try:
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"Using API Key: {api_key[:5] if api_key else 'None'}...")
    print(f"Using Base URL: {os.getenv('OPENAI_API_BASE')}")

    # Use the model defined in .env if available, otherwise fallback to user's requested GPT-4o
    # But for ModelFactory with OPENAI platform, we pass the model type enum or string.
    # Let's see if we can pass a string directly or if we must use the enum.
    # The user code uses `ModelType.GPT_4O`. 
    
    # Check if we should override model type for DeepSeek
    # DeepSeek isn't in ModelType, so we need a workaround or use STUB/DEFAULT if possible.
    # However, ModelFactory.create() usually validates against ModelType if provided.
    # But if we use ModelPlatformType.OPENAI_COMPATIBILITY_MODEL, maybe we can pass a string?
    
    # If we look at ModelPlatformType, there is OPENAI_COMPATIBILITY_MODEL.
    # Let's try to use that if we are on DeepSeek.
    
    model_type = ModelType.GPT_4O
    platform = ModelPlatformType.OPENAI
    
    if "deepseek" in (os.getenv("LLM_BASE_URL") or ""):
         # Use OpenAI Compatibility platform
         platform = ModelPlatformType.OPENAI_COMPATIBILITY_MODEL
         # And we might need to set the model config to point to deepseek-chat
         # But ModelType needs to be passed.
         # If we pass ModelType.GPT_4O to OPENAI_COMPATIBILITY_MODEL, does it just use the value "gpt-4o"?
         # Yes, typically.
         # So we need to change the model type to something that resolves to "deepseek-chat".
         # Since "deepseek-chat" is not in ModelType, we can't use ModelType enum directly for it.
         # But maybe we can mock it or use ModelType.STUB and override?
         # Or maybe we can just rely on the fact that we are mocking OpenAI but the server is DeepSeek.
         # If DeepSeek rejects "gpt-4o", we must send "deepseek-chat".
         
         # Hack: Enum members can be accessed by value? No.
         # Can we pass a string "deepseek-chat" to ModelFactory? 
         # Type hint says ModelType, but runtime might accept string if not strictly checked.
         # Let's try passing the string "deepseek-chat" directly.
         model_type = "deepseek-chat" 
    
    model = ModelFactory.create(
      model_platform=platform,
      model_type=model_type,
      model_config_dict={"temperature": 0.0},
      url=os.getenv("LLM_BASE_URL"), # Pass the base URL if supported or rely on env var
    )

    # Note: SearchToolkit needs SERPAPI_API_KEY or similar? 
    # The user code uses `SearchToolkit().search_duckduckgo`. 
    # DuckDuckGo usually doesn't need an API key.

    search_tool = SearchToolkit().search_duckduckgo

    # Create a system message
    from camel.messages import BaseMessage
    sys_msg = BaseMessage.make_assistant_message(role_name="Assistant", content="You are a helpful assistant.")

    # It seems we need to wrap the function in OpenAIFunction
    from camel.toolkits import OpenAIFunction
    
    search_func = SearchToolkit().search_duckduckgo
    search_tool = OpenAIFunction(search_func)
    
    agent = ChatAgent(
        model=model, 
        tools=[search_tool], 
        system_message=sys_msg
    )

    # ChatAgent.step expects a BaseMessage, not a string.
    from camel.messages import BaseMessage
    from camel.types import RoleType

    print("--- Step 1: What is CAMEL-AI? ---")
    msg1 = BaseMessage.make_user_message(role_name="User", content="What is CAMEL-AI?")
    response_1 = agent.step(msg1)
    print(response_1.msgs[0].content)

    print("\n--- Step 2: Github link? ---")
    msg2 = BaseMessage.make_user_message(role_name="User", content="What is the Github link to CAMEL framework?")
    response_2 = agent.step(msg2)
    print(response_2.msgs[0].content)

except Exception as e:
    print(f"An error occurred: {e}")
