# Agent logic for handling prompts and tools
import os
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()

from langchain_community.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from tools import CheckAvailabilityTool, CreateEventTool, GetEventDetailsTool

llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.2,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

tools_list = [
    CheckAvailabilityTool(),
    CreateEventTool(),
    GetEventDetailsTool()
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools_list,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    memory=memory
)

def run_agent(prompt: str) -> str:
    """Run the agent with the given prompt and return the response."""
    try:
        logging.info(f"Agent received prompt: {prompt}")
        return agent.run(prompt)
    except AttributeError:
        response = agent.invoke(prompt)
        return response.content
    except Exception as e:
        logging.error(f"Agent error: {e}")
        raise