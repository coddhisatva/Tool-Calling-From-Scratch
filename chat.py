"""
Demo script: Travel Assistant with Tool Calling

This demonstrates the Agent's tool-calling capabilities through various scenarios:
- No tool usage (general questions)
- Single tool usage (weather, flights, currency)
- Multiple tool usage (combined queries)
"""

from agent import Agent, Tool, Message, Role, Model
from mock_tools import get_weather, get_flight_prices, get_currency_exchange, divide_by_secret_number
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
    ),
    Tool(
        name="divide_by_secret_number",
        description="Divides a number by a secret number and returns the result",
        parameters={
            "numerator": {
                "type": "number",
                "required": True,
                "description": "The number to be divided"
            }
        },
        function=divide_by_secret_number
    )
]


# ─── CREATE AGENT ─────────────────────────────────────────

agent = Agent(
    name="Travel Assistant",
    description="A helpful travel planning assistant that can check weather, find flight prices, and convert currencies.",
    tools=tools,
    demo=True
)


# ─── DEMO SCENARIOS ───────────────────────────────────────

scenarios = [
    # No tools
    "What do you do?",
    # One tool
    "What's the weather in Tokyo?",
    # Needs more information
    "What's the weather in my favorite city?",
    # More information given
    "My favorite city is New York",
    # Different tool, one of three parameters missing
    "How much is a flight from NYC to Paris",
    # Now has all 3 parameters
    "It's June 15?",
    # Two tools at once
    "I want to go from London to Tokyo next month. What's the weather like and how much will a flight cost?",
    # All 3 tools
    "Plan a trip from NYC to Paris - tell me the weather, flight cost for July 1st, and tell me how much French money I can get with $500.",
    # Too many tool calls (above default max_iterations of 10)
    "Tell me the weather in Australia, Belarus, the Carribean, Delaware, Edison NJ, Frankfurt Germany, Georgia USA, Himalayin mountains, Inter-national waters, Jersey City, King's County NY, and most importantly, Westeros",
    # How does agent handle error?
    "Divide 17 by the secret number!",
]


def chat():
    """Run through all demo scenarios."""
    print("\n" + "="*70)
    print("TOOL-CALLING AGENT DEMO: Travel Assistant")
    print("="*70)
    print("\nTo showcase our tool calling library, we have created a travel")
    print("agent can use tools to fetch weather, flight prices, and currency")
    print("exchange rates, or respond directly when tools aren't needed.\n")
    
    # Maintain conversation history across all scenarios
    messages = []
    
    for i, question in enumerate(scenarios, 1):
        print("\n" + "─"*70)
        print(f"SCENARIO {i}")
        print("─"*70)
        print(f"User: {question}")
        print()
        
        # Add user message to ongoing conversation
        messages.append(Message(Role.USER, question))
        
        try:
            response = agent.run(messages)
            
            # Add response to ongoing conversation
            messages.append(response)
            
            print(f"Agent: {response.content}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print()
    
    print("="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    chat()
