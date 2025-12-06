"""Quick test for Anthropic model"""

from agent import Agent, Message, Role, Model
from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    name="Anthropic Test",
    description="Testing Anthropic provider",
    model=Model.CLAUDE_SONNET
)

messages = [Message(Role.USER, "Say 'Hello from Claude!' and nothing else.")]
response = agent.run(messages)

print(f"Claude response: {response.content}")

