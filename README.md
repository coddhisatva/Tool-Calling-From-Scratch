# AI Tool Calling from Scratch   

## Overview

Imagine you just built the world's first chat bot, and now you want to add tool calling to it. The goal of this coding challenge is to create a simple library for defining and running AI agents that can use tool calling. This should take around 2-3 hours to complete.

Your implementation can roughly follow the interface defined in `agent.py`.

## Use Case

A user should be able to define any arbitrary agent with any arbitrary tools, and then execute the agent with any arbitrary query. For example, someone may want to define an agent that can answer questions about the weather:

```python
agent = Agent(
    tools=[Tool(name="get_current_weather", ...)]
)

agent.run(messages=[Message(role=Role.USER, content="What is the weather in Tokyo?")])
```

or an agent that can make and manage calendar events.

```python
agent = Agent(
    tools=[
        Tool(name="create_calendar_event", ...),
        Tool(name="get_calendar_events", ...),
        Tool(name="delete_calendar_event", ...),
    ]
)

agent.run(messages=[Message(role=Role.USER, content="Create a calendar event for tomorrow at 10am")])
```

## Rules

- The only non-standard libraries you can use are strictly for LLM api calls. You can use any LLM api you want, but **it must be text only**. You cannot use any libraries' prebuilt tool calling capabilities (because that is exactly what you're making from scratch).
- Everything else must be implemented through your own code. This includes any prompt engineering, agentic logic, state management, response parsing, etc.
- The `Agent` skeleton in `agent.py` is just a starting point. Feel free to change/add any methods/classes, create helper classes, etc. The implementation of `Tool`, `Message`, and `Role` is up to you.

## Design Considerations

- What should the agent do if it doesn't have all the information it needs to answer the query?
- What should the agent do if it doesn't have the necessary parameters it needs to call a tool?
- How should the agent decide which tool to call?
- How should the agent decide when to stop calling tools?
- How should the agent handle errors from tool calls?
- How should the agent handle the response from tool calls?

## Requirements

- Implement the `Agent` class in `agent.py`.
- Implement the `Tool` class in `agent.py`.
- Implement an example use case in `chat.py` file to demonstrate how to use your `Agent` and `Tool` classes.
- Anything beyond these requirements is totally up to you.

## Submission

- Submit a zip file containing the `agent.py` and `chat.py` files.
- Show an example of an agent in action.
- Give a brief explanation of your design decisions and how you implemented the agent.