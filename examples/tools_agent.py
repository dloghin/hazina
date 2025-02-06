from pprint import pprint
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

class SearchInput(BaseModel):
    location: str = Field(description="location to search for")

@tool(args_schema=SearchInput)
def check_weather(location: str) -> str:
    '''Return the weather forecast for the specified location.'''
    return f"It's always sunny in {location}"

@tool
def magic_function(input: int) -> int:
    """Applies a magic function to an input."""
    return input + 2

tools = [magic_function, check_weather]

# *** Ollama
model = ChatOllama(model="llama3-groq-tool-use")
# model = ChatOllama(model="MFDoom/deepseek-r1-tool-calling")

# *** OpenAI
# model = ChatOpenAI(model="gpt-4o")

# query = "what is the weather in Paris?"
query = "what is the value of magic_function(3)?"

agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

agent = create_tool_calling_agent(model, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

resp = agent_executor.invoke({"input": query})

pprint(resp)