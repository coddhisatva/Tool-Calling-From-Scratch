# Design Document: Tool-Calling Agent Library

## Overview

This library implements an AI agent system with tool-calling capabilities from scratch, without using pre-built tool-calling features from LLM SDKs. The agent can intelligently decide when to use external tools to answer user queries, execute those tools, and synthesize responses based on the results.

## Architecture

### High-Level Flow

```
User Query
    ↓
Agent.run()
    ↓
Add system prompt with tool descriptions
    ↓
┌─── Agentic Loop (max_iterations) ───┐
│                                      │
│  Call LLM with message history       │
│           ↓                          │
│  Parse response for tool calls       │
│           ↓                          │
│  Tool call found?                    │
│    YES → Execute tool                │
│         → Add result to history      │
│         → Loop back                  │
│    NO  → Return final response       │
│                                      │
└──────────────────────────────────────┘
```

### Core Components

**1. Agent**
- Manages the agentic loop
- Routes to appropriate LLM provider
- Handles tool execution
- Maintains conversation state

**2. Tool**
- Encapsulates a callable function
- Includes metadata (name, description, parameters)
- Provides self-documentation for the LLM

**3. Message**
- Represents conversation turns
- Supports multiple roles (USER, ASSISTANT, SYSTEM, TOOL_CALL, TOOL_RESULT)

**4. Provider/Model System**
- Supports OpenAI, Anthropic, and Google Gemini
- Provider-specific message formatting
- Unified interface across providers

## Implementation Details

### Tool Calling Mechanism

Since we cannot use built-in tool calling, we implement it through prompt engineering:

1. **System Prompt Generation**: Tools are formatted into natural language descriptions and injected into the system prompt, along with instructions for a specific XML-like format to request tool calls.

2. **Tool Call Format**: The LLM is instructed to output:
   ```
   <tool_call>
   {"name": "tool_name", "parameters": {"param": "value"}}
   </tool_call>
   ```

3. **Parsing**: Regular expressions extract the JSON from tool call tags.

4. **Execution**: The tool function is called with extracted parameters, and results are fed back as conversation context.

### Multi-Provider Support

Each provider has different API requirements:

**OpenAI**:
- System messages included in messages array
- Uses `max_completion_tokens` parameter
- Simple role/content format

**Anthropic**:
- System prompt is separate parameter (list of objects)
- Uses `max_tokens` parameter
- Standard role/content format

**Gemini**:
- No native system role (prepended to first user message)
- Uses chat history + current message pattern
- Uses `max_output_tokens` in GenerationConfig

The `_call_llm()` method routes to provider-specific implementations that handle these differences.

### Message Flow

Messages accumulate through the conversation:

1. User message added
2. System prompt injected (if tools exist)
3. LLM generates response
4. If tool call detected:
   - TOOL_CALL message added (contains request)
   - TOOL_RESULT message added (contains output)
   - Loop continues
5. If no tool call: return as final response

## Design Considerations

### 1. Missing Information to Answer Query

**Approach**: The system prompt instructs the LLM to respond naturally when it lacks information.

**Outcome**: The LLM will ask clarifying questions without calling tools, maintaining a conversational flow. For example, if asked "What's the weather?" it will ask "Which city?"

### 2. Missing Tool Parameters

**Approach**: System prompt tells LLM to use tools immediately when information is available, and to ask users only when required parameters are completely missing.

**Outcome**: The LLM typically asks for clarification before attempting a tool call. If it does call with missing parameters, Python raises TypeError, which is caught and fed back to the LLM for recovery.

### 3. Deciding Which Tool to Call

**Approach**: Each tool includes a detailed description and parameter specifications in the system prompt. The LLM uses semantic understanding to match user intent with tool capabilities.

**Outcome**: The LLM analyzes the query and selects the most appropriate tool based on descriptions. Our prompt engineering emphasizes immediate tool use when relevant.

### 4. Deciding When to Stop

**Approach**: The LLM outputs either:
- A tool call (loop continues)
- Normal text (loop terminates)

A `max_iterations` safeguard prevents infinite loops. If reached, a modified system prompt forces a final answer.

**Outcome**: The agent naturally terminates when the LLM has sufficient information to answer without more tools.

### 5. Handling Tool Errors

**Approach**: All tool execution is wrapped in try/except. Errors are caught and converted to descriptive strings, then fed back to the LLM as tool results.

**Outcome**: The LLM sees error messages and can:
- Retry with corrected parameters
- Ask the user for clarification
- Apologize and explain limitations
- Suggest alternatives

### 6. Handling Tool Responses

**Approach**: Tool outputs are converted to strings and added as TOOL_RESULT messages. These are formatted as user messages in provider APIs, since they represent input to the LLM.

**Outcome**: The LLM receives tool results as conversational context and synthesizes them into natural language responses.

## Configuration System

The library separates configuration into `config.py`:

**Model Configuration**:
- Provider enum (OPENAI, GEMINI, ANTHROPIC)
- Model enum with tuples of (model_name, provider)
- Properties for accessing name and provider

**System Prompts**:
- Generic system prompt template
- Tool instructions template
- Max iterations prompt

**Design Rationale**: This separation allows users to see all available models in one place and modify prompt templates without touching core agent logic.

## Agent Parameters

The Agent class is instantiated with:

**Required**:
- `name`: Agent's identity
- `description`: Agent's purpose

**Optional**:
- `custom_system_prompt`: Override default behavioral instructions
- `tools`: List of Tool objects
- `model`: Which LLM to use (default: GPT-5-mini)
- `max_iterations`: Loop limit (default: 10)
- `max_tokens`: Response length limit (default: 4096)
- `demo`: Enable tool call logging (default: False)

**Design Rationale**: Name and description are required because they define the agent's identity and purpose, which are fundamental to its system prompt. Everything else has sensible defaults.

## Demo: chat.py

The demo showcases a Travel Assistant agent with three tools:

**Tools**:
1. `get_weather(location)` - Returns mock weather data
2. `get_flight_prices(origin, destination, date)` - Returns mock flight prices
3. `get_currency_exchange(from_currency, to_currency, amount)` - Returns mock exchange rates
4. `divide_by_secret_number(numerator)` - Intentionally errors to demonstrate error handling

**Scenarios**:

1. **"What do you do?"** - No tools needed, agent describes capabilities
2. **"Where should I travel this summer?"** - General advice, no external data needed
3. **"What's the weather in Tokyo?"** - Single tool call (get_weather)
4. **"How much does a flight from NYC to Paris cost on June 15?"** - Single tool call (get_flight_prices)
5. **"If I have 1000 USD, how much is that in EUR?"** - Single tool call (get_currency_exchange)
6. **"I want to go from London to Tokyo next month..."** - Multiple tool calls (get_weather, get_flight_prices)
7. **"Plan a trip from NYC to Paris..."** - Multiple tool calls (all three tools)
8. **"Tell me the weather in Australia, Belarus..."** - Exceeds max_iterations, demonstrates loop limit
9. **"Divide 17 by the secret number!"** - Tool error (division by zero), demonstrates error handling

The demo maintains conversation history across scenarios, showing how context builds through multiple interactions.

## Error Handling Strategy

**API Key Validation**: On Agent initialization, we verify the required API key exists for the selected provider. This fails fast with a clear error message.

**Tool Execution Errors**: Caught and returned as descriptive strings. The LLM can then respond appropriately rather than crashing the entire agent.

**Max Iterations**: Prevents infinite loops by forcing a final answer after N tool calls, ensuring the agent always returns something useful.

**Provider Errors**: Let SDK exceptions propagate naturally, as they contain useful debugging information.

## Testing

Two test files verify provider functionality:
- `test_gemini.py` - Verifies Gemini API integration
- `test_anthropic.py` - Verifies Anthropic API integration

These simple scripts ensure basic connectivity and parameter compatibility with each provider.

## Trade-offs and Decisions

**Why text-based tool calling instead of structured?**
- Assignment requirement: build from scratch
- More portable across providers
- Easier to debug (human-readable)

**Why mock tools instead of real APIs?**
- Reviewers don't need additional API keys
- Deterministic demo results
- Focus on tool-calling mechanism, not API integration

**Why multiple providers?**
- Demonstrates abstraction and flexibility
- Real-world libraries support multiple providers
- Shows understanding of provider differences

**Why maintain message history in demo?**
- Shows agent can maintain context
- Enables follow-up questions
- More realistic conversation flow

## File Structure

```
tool-calling-from-scratch/
├── agent.py           # Core Agent, Tool, Message classes
├── config.py          # Model configurations and system prompts
├── mock_tools.py      # Example tool implementations
├── chat.py            # Demo script with scenarios
├── test_gemini.py     # Gemini provider test
├── test_anthropic.py  # Anthropic provider test
├── requirements.txt   # Dependencies
└── .env.example       # API key template
```

## Conclusion

This implementation demonstrates a fully functional tool-calling agent built from first principles. The system uses prompt engineering to guide LLM behavior, handles errors gracefully, supports multiple providers, and provides a clean API for users to create custom agents with arbitrary tools.

