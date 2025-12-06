# Design Document: Tool-Calling Agent Library

## Agent Flow

The agent operates through an agentic loop in the `run()` method. When a user calls `run()` after creating their agent, we inject a system prompt containing the agent's name, description, custom prompt (if provided), and detailed descriptions of all available tools. This system prompt instructs the LLM on how to request tool calls using a specific XML-like format. We then enter a loop that runs for up to `max_iterations` times. In each iteration, we pass all message history to the LLM provider, which analyzes the context and decides whether to call a tool or return a final response. If the LLM outputs a tool call, we parse it, execute the corresponding function, append the result to the message history, and loop again. If the LLM outputs normal text (no tool call detected), we return that as the final response. This continues until either the agent decides it has enough information to answer, or we hit the iteration limit, at which point we force a final answer by replacing the system prompt with instructions to synthesize a response from available information without calling more tools.

## Classes

The library is built around three core classes. 
- `Agent` is the orchestrator that manages the agentic loop, routes to the appropriate LLM provider (OpenAI, Anthropic, or Gemini), and executes tools. It requires `name` and `description` parameters that define the agent's identity and purpose in its system prompt, while `tools`, `model`, `max_iterations`, `max_tokens`, and `demo` are optional with sensible defaults. The `model` parameter accepts a `Model` enum value that encapsulates both the model name and its provider through tuple values, with properties to access each. 
- `Tool` encapsulates a callable function along with metadata: a name, description, and parameters dictionary that specifies each parameter's type, whether it's required, and a description. This metadata is formatted into natural language for the system prompt so the LLM understands when and how to use each tool. 
- `Message` represents individual conversation turns, with a `Role` enum distinguishing between USER, ASSISTANT, SYSTEM, TOOL_CALL, and TOOL_RESULT messages. This role system allows us to track the full conversation flow including tool interactions, and each provider's `_call_*` method handles formatting these roles appropriately for that provider's API (e.g., Anthropic separates system prompts while OpenAI includes them in the messages array).

## Design Considerations

- **Missing information to answer the query**: The system prompt instructs the LLM to respond conversationally when it lacks information. The LLM will naturally ask clarifying questions (like "Which city?" if asked about weather without specifying a location) rather than attempting to call tools with incomplete context.

- **Missing necessary parameters for a tool**: The system prompt emphasizes using tools immediately when information is available, but asking users when required parameters are completely missing. In practice, the LLM typically asks for clarification before calling. If it does attempt a call with missing parameters, Python raises a TypeError, which our try/except block catches and feeds back to the LLM as an error message, allowing it to recover by requesting the missing information.

- **Deciding which tool to call**: Each tool's description and parameter specifications are included in the system prompt. The LLM uses semantic understanding to match user intent with tool capabilities, selecting the most appropriate tool based on these descriptions. Our prompt engineering emphasizes immediate tool use when queries clearly benefit from external data. The user's custom prompt can add additional instructions here as well.

- **Deciding when to stop calling tools**: The LLM naturally terminates the loop by outputting plain text instead of a tool call when it has sufficient information to answer. Our parser only detects tool calls in the specific `<tool_call>` format, so any other response is treated as final. The `max_iterations` parameter prevents infinite loops if the agent gets stuck; when reached, we modify the system prompt to force a conclusive answer based on information gathered so far. The user can set `max_iterations` at the `Agent` level; otherwise, it's set to 10 by default.

- **Handling errors from tool calls**: All tool execution is wrapped in try/except blocks. Any exception is caught, converted to a descriptive string (e.g., "Error executing tool 'divide': division by zero"), and fed back to the LLM as a TOOL_RESULT message. The LLM sees this error as conversational context and can retry with corrected parameters, ask the user for help, explain limitations, or suggest alternatives.

- **Handling tool responses**: Tool outputs are converted to strings and added as TOOL_RESULT messages in the conversation history. When formatting messages for provider APIs, these are treated as user-role messages since they represent input to the LLM. The LLM receives tool results as context and synthesizes them into natural language responses for the user.

## Demo

The `chat.py` file demonstrates a Travel Assistant agent with four tools: `get_weather`, `get_flight_prices`, `get_currency_exchange`, and `divide_by_secret_number` (which intentionally causes errors). The demo runs ten scenarios with maintained conversation history:

- **"What do you do?"** - Agent describes its capabilities without needing tools
- **"What's the weather in Tokyo?"** - Single tool call to get_weather
- **"What's the weather in my favorite city?"** - Agent asks for clarification (missing information)
- **"My favorite city is New York"** - Continues conversation with context from previous turn
- **"How much is a flight from NYC to Paris"** - Missing 1/3 paramaters (date), agent asks for it
- **"It's June 15?"** - Agent uses context to complete the flight price query
- **"I want to go from London to Tokyo next month..."** - Two tool calls at once (weather and flights)
- **"Plan a trip from NYC to Paris..."** - Uses all three main tools (weather, flights, currency)
- **"Tell me the weather in Australia, Belarus, Caribbean..."** - Queries many locations to demonstrate hitting max_iterations limit
- **"Divide 17 by the secret number!"** - Triggers division by zero to demonstrate error handling

All tools use mock data (deterministic weather based on first letter, random prices/rates) so reviewers don't need additional API keys.

(*Note: Demo mode, enabled in chat.py, outputs tool usage for demonstration purposes)

## File Structure and Usage

```
agent.py           - Core Agent, Tool, Message classes
config.py          - Model/Provider enums and system prompt templates  
mock_tools.py      - Example tool function implementations
chat.py            - Demo with Travel Assistant scenarios
test_gemini.py     - Gemini provider connectivity test
test_anthropic.py  - Anthropic provider connectivity test
requirements.txt   - Dependencies (openai, anthropic, google-generativeai, python-dotenv)
.env.example       - API key template
```

**Usage**: Create an `.env` file with API keys, install dependencies with `pip install -r requirements.txt`, then run `python chat.py` to see the demo. Users can create their own agents by defining tool functions, wrapping them in `Tool` objects with metadata, and passing them to `Agent(name, description, tools=tools)`.
