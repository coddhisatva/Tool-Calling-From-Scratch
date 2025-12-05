# Example Usage
from agent import Agent, Tool, Message, Role

tools = [Tool(...), Tool(...), Tool(...)]

agent = Agent(tools=tools)

def chat():
    messages = []
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        messages.append(Message(role=Role.USER, content=user_input))
        response = agent.run(messages=messages)
        messages.append(response)
        print(f"AI: {response.content}")


if __name__ == "__main__":
    chat()
