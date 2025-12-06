"""Quick test for Gemini model"""

from agent import Agent, Message, Role, Model
from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    name="Gemini Test",
    description="Testing Gemini provider",
    model=Model.GEMINI_2_5_FLASH
)

messages = [Message(Role.USER, "Say 'Hello from Gemini!' and nothing else.")]
response = agent.run(messages)

print(f"Gemini response: {response.content}")

