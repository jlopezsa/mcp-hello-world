import asyncio
import os
from typing import Any

from dotenv import find_dotenv, load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

_ = load_dotenv(find_dotenv())

openai_api_key = os.environ["OPENAI_API_KEY"]
base_url = os.environ["ORCHESTATOR_BASE_URL"]
model_name = os.environ["ORCHESTATOR_MODEL"]

# Context7 server - provides access to library documentation
CONTEXT7_CONFIG = {
    "context7": {
        "url": "https://mcp.context7.com/mcp",  # Server endpoint
        "transport": "streamable_http",         # Communication protocol
    }
}

# Met Museum server - provides access to museum collection data
MET_MUSEUM_CONFIG = {
    "met-museum": {
        "command": "npx",                   # Node.js package runner    
        "args": ["-y", "metmuseum-mcp"],    # Install and run met museum MCP
        "transport": "stdio",               # Communication via stdin/stdout
    }
}


def print_tools(title: str, tools: list[Any]) -> None:
    print(f"\n{title}: {len(tools)}")
    for index, tool in enumerate(tools, start=1):
        tool_name = getattr(tool, "name", "<sin nombre>")
        tool_description = getattr(tool, "description", "")
        print(f"{index}. {tool_name}")
        if tool_description:
            print(f"   {tool_description}")

async def async_main() -> None:
    print("Init main function")

    context7_client = MultiServerMCPClient(CONTEXT7_CONFIG)
    met_museum_client = MultiServerMCPClient(MET_MUSEUM_CONFIG)
    client = MultiServerMCPClient({
        **CONTEXT7_CONFIG, 
        **MET_MUSEUM_CONFIG
    })

    # Initialize the OpenAI language model
    # This model will power the AI agent's reasoning and responses
    openai_model = ChatOpenAI(
        api_key=openai_api_key,
        base_url=base_url, 
        model=model_name
    )

    context7_tools = await context7_client.get_tools()
    met_museum_tools = await met_museum_client.get_tools()
    tools = await client.get_tools()

    print_tools("Tools de Context7", context7_tools)
    print_tools("Tools de Met Museum", met_museum_tools)
    print_tools("Tools combinadas", tools)

    # Set up conversation memory using InMemorySaver
    # This allows the agent to remember previous messages in the conversation
    checkpointer = InMemorySaver()

    # Configuration for conversation persistence
    # The thread_id ensures all messages in this session are grouped together
    config = {"configurable": {"thread_id": "conversation_id"}}

    # Create the ReAct agent with all components
    # ReAct = Reasoning + Acting (agent can reason about and use tools)
    agent = create_react_agent(
        model=openai_model,         # The language model to use 
        tools=tools,                # Available tools from MCP servers
        checkpointer=checkpointer,  # Memory system for conversation history
    )

    # Send initial message to introduce the agent and its capabilities
    response = await agent.ainvoke(
        {"messages": [
            # System message defines the agent's role and personality
            {
                "role": "system", 
                "content": "You are a smart, useful agent with tools to access code library documentation and the Met Museum collection."
            },
            # User message requests the agent to introduce itself
            {
                "role": "user", 
                "content": "Give a brief introduction of what you do and the tools you can access."
            },
        ]},
        config=config  # Use the conversation thread for memory persistence
    )

    # Print the agent's response (last message in the conversation)
    print("--- Agent response ---")
    print(response['messages'][-1].content)
    print("----------------------")

    # Main interaction loop - allows continuous conversation with the agent
    while True:
        # Display menu options to the user
        choice = input("""
            Menu:
            1. Ask the agent a question
            2. Quit
            Enter your choice (1 or 2): """
        )

        if choice == "1":
            # Get user's question
            print("Your question")
            query = input("> ")

            # Send the user's question to the agent
            # The agent will have access to the full conversation history
            response = await agent.ainvoke(
                {"messages": query},        # User's current question
                config=config              # Maintains conversation thread
            )
            # Display the agent's response
            print(response['messages'][-1].content)
        else:
            # Exit the program for any choice other than "1"
            print("Goodbye!")
            break

    print(f"Agent ready with {len(tools)} tools.")
    print(config)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
