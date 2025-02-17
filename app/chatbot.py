# Most of the code taken from the CDP Agentkit Chatbot Example: https://github.com/coinbase/agentkit/blob/master/python/examples/cdp-langchain-chatbot/chatbot.py

import json
import os
import sys
import time

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import CDP Agentkit Langchain Extension.
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

from cdp import Wallet, WalletData

# Configure a file to persist the agent's CDP MPC Wallet Data.
wallet_data_file = "wallet_data.txt"

# Global vars to store the agent executor and config.
agent_executor = None
agent_config = None
cdp_toolkit = None


def get_wallet_address():
    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            try:
                json_data = json.loads(f.read())
                return json_data["default_address_id"]
            except:
                return "no address"
    return "no address"


def get_wallet_balance(address_id, asset_id):
    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            try:
                wallet_data = WalletData.from_dict(json.loads(f.read()))
                wallet = Wallet.import_wallet(wallet_data)
                for address in wallet.addresses:
                    if address.address_id == address_id:
                        return "{}".format(address.balance(asset_id))
                return "no such address in wallet"
            except Exception as e:
                print("Error in get_wallet_balance(): {}".format(e))
                return "no address"
    return "no address"


def get_network():
    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            try:
                json_data = json.loads(f.read())
                return json_data["network_id"]
            except:
                return "no network"
    return "no network"


def initialize_agent(cdp_api_key_name, cdp_api_key_private_key, openai_api_key):
    """Initialize the agent with CDP Agentkit."""
    # Initialize LLM.
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)

    wallet_data = None

    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            wallet_data = f.read()

    # Configure CDP Agentkit Langchain Extension.
    values = {
        "cdp_api_key_name": cdp_api_key_name,
        "cdp_api_key_private_key": cdp_api_key_private_key,
    }
    if wallet_data is not None:
        # If there is a persisted agentic wallet, load it and pass to the CDP Agentkit Wrapper.
        values["cdp_wallet_data"] = wallet_data

    agentkit = CdpAgentkitWrapper(**values)

    # persist the agent's CDP MPC Wallet Data.
    wallet_data = agentkit.export_wallet()
    with open(wallet_data_file, "w") as f:
        f.write(wallet_data)

    # Initialize CDP Agentkit Toolkit and get tools.
    global cdp_toolkit
    cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
    tools = cdp_toolkit.get_tools()

    # Store buffered conversation history in memory.
    memory = MemorySaver()

    global agent_config
    agent_config = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    global agent_executor
    agent_executor = create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=(
            "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. "
            "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
            "them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
            "details and request funds from the user. Before executing your first action, get the wallet details "
            "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
            "again later. If someone asks you to do something you can't do with your currently available tools, "
            "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
            "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
            "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
        ),
    )
    return agent_executor, agent_config


def get_agent_response(message: str):
    responses = []
    if agent_executor is None or agent_config is None:
        print("Agent not initialized. Please run initialize_agent() first.")
        return responses

    for chunk in agent_executor.stream(
        {"messages": [HumanMessage(content=message)]}, agent_config
    ):
        if "agent" in chunk and chunk["agent"]["messages"][0].content != "":
            responses.append(chunk["agent"]["messages"][0].content)
    return responses


# Autonomous Mode
def run_autonomous_mode(agent_executor, config, interval=10):
    """Run the agent autonomously with specified intervals."""
    print("Starting autonomous mode...")
    while True:
        try:
            # Provide instructions autonomously
            thought = (
                "Be creative and do something interesting on the blockchain. "
                "Choose an action or set of actions and execute it that highlights your abilities."
            )

            # Run agent in autonomous mode
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=thought)]}, config
            ):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

            # Wait before the next action
            time.sleep(interval)

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


# Chat Mode
def run_chat_mode(agent_executor, config):
    """Run the agent interactively based on user input."""
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nPrompt: ")
            if user_input.lower() == "exit":
                break

            # Run agent with the user's input in chat mode
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=user_input)]}, config
            ):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


# Mode Selection
def choose_mode():
    """Choose whether to run in autonomous or chat mode based on user input."""
    while True:
        print("\nAvailable modes:")
        print("1. chat    - Interactive chat mode")
        print("2. auto    - Autonomous action mode")

        choice = input("\nChoose a mode (enter number or name): ").lower().strip()
        if choice in ["1", "chat"]:
            return "chat"
        elif choice in ["2", "auto"]:
            return "auto"
        print("Invalid choice. Please try again.")


def main():
    """Start the chatbot agent."""
    agent_executor, config = initialize_agent()

    mode = choose_mode()
    if mode == "chat":
        run_chat_mode(agent_executor=agent_executor, config=config)
    elif mode == "auto":
        run_autonomous_mode(agent_executor=agent_executor, config=config)


def test():
    print(get_wallet_balance("0x3Fa331F48d1cbc59cc28d28ea1ac7CdAe24959e0", "eth"))


if __name__ == "__main__":
    # print("Starting Agent...")
    # main()
    test()
