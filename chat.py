"""
Demo script: Travel Assistant with Tool Calling

This demonstrates the Agent's tool-calling capabilities through various scenarios:
- No tool usage (general questions)
- Single tool usage (weather, flights, currency)
- Multiple tool usage (combined queries)
"""

from agent import Agent, Tool, Message, Role, Model
from mock_tools import get_weather, get_flight_prices, get_currency_exchange
from dotenv import load_dotenv

# Load API keys
load_dotenv()


# ─── DEFINE TOOLS ─────────────────────────────────────────

tools = [
    Tool(
        name="get_weather",
        description="Get current weather conditions for any location",
        parameters={
            "location": {
                "type": "string",
                "required": True,
                "description": "The location to get weather for"
            }
        },
        function=get_weather
    ),
    Tool(
        name="get_flight_prices",
        description="Get flight prices between two locations for a specific date",
        parameters={
            "origin": {
                "type": "string",
                "required": True,
                "description": "The departure location"
            },
            "destination": {
                "type": "string",
                "required": True,
                "description": "The arrival location"
            },
            "date": {
                "type": "string",
                "required": True,
                "description": "The flight date (e.g., 'June 15', 'next month')"
            }
        },
        function=get_flight_prices
    ),
    Tool(
        name="get_currency_exchange",
        description="Convert an amount from one currency to another",
        parameters={
            "from_currency": {
                "type": "string",
                "required": True,
                "description": "The source currency code (e.g., 'USD', 'EUR')"
            },
            "to_currency": {
                "type": "string",
                "required": True,
                "description": "The target currency code (e.g., 'USD', 'EUR')"
            },
            "amount": {
                "type": "number",
                "required": True,
                "description": "The amount to convert"
            }
        },
        function=get_currency_exchange
    )
]


# ─── CREATE AGENT ─────────────────────────────────────────

agent = Agent(
    name="Travel Assistant",
    description="A helpful travel planning assistant that can check weather, find flight prices, and convert currencies.",
    tools=tools
)


# ─── DEMO SCENARIOS ───────────────────────────────────────

scenarios = [
    "What do you do?",
    
    "Where should I travel this summer?",
    
    "What's the weather in Tokyo?",
    
    "How much does a flight from NYC to Paris cost on June 15?",
    
    "If I have 1000 USD, how much is that in EUR?",
    
    "I want to go from London to Tokyo next month. What's the weather like and how much will a flight cost?",
    
    "Plan a trip from NYC to Paris - tell me the weather, flight cost for July 1st, and convert $500 to EUR.",
]


def chat():
    """Run through all demo scenarios."""
    print("\n" + "="*70)
    print("TOOL-CALLING AGENT DEMO: Travel Assistant")
    print("="*70)
    print("\nTo showcase our tool calling library, we have created a travel")
    print("agent can use tools to fetch weather, flight prices, and currency")
    print("exchange rates, or respond directly when tools aren't needed.\n")
    
    for i, question in enumerate(scenarios, 1):
        print("\n" + "─"*70)
        print(f"SCENARIO {i}")
        print("─"*70)
        print(f"User: {question}")
        print()
        
        # Create fresh message list for each scenario
        messages = [Message(Role.USER, question)]
        
        try:
            response = agent.run(messages)
            print(f"Agent: {response.content}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print()
    
    print("="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    chat()
