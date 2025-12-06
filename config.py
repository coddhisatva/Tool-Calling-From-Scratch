from enum import Enum

# ─── MODEL CONFIGURATION ──────────────────────────────────

class Provider(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


class Model(Enum):
    # OpenAI - GPT
    GPT_5_1 = ("gpt-5.1", Provider.OPENAI)
    GPT_5 = ("gpt-5", Provider.OPENAI)
    GPT_5_MINI = ("gpt-5-mini", Provider.OPENAI)
    GPT_5_NANO = ("gpt-5-nano", Provider.OPENAI)
    
    # OpenAI - Reasoning
    O4_MINI = ("o4-mini", Provider.OPENAI)
    O3 = ("o3", Provider.OPENAI)
    O3_MINI = ("o3-mini", Provider.OPENAI)
    O1 = ("o1", Provider.OPENAI)
    
    # Gemini
    GEMINI_3_PRO = ("gemini-3-pro-preview", Provider.GEMINI)
    GEMINI_2_5_PRO = ("gemini-2.5-pro", Provider.GEMINI)
    GEMINI_2_5_FLASH = ("gemini-2.5-flash", Provider.GEMINI)
    GEMINI_2_FLASH = ("gemini-2.0-flash", Provider.GEMINI)
    
    # Anthropic
    CLAUDE_SONNET = ("claude-sonnet-4-20250514", Provider.ANTHROPIC)
    CLAUDE_HAIKU = ("claude-haiku-4-20250514", Provider.ANTHROPIC)

    @property
    def model_name(self):
        return self.value[0]
    
    @property
    def provider(self):
        return self.value[1]


# ─── DEFAULT VALUES ───────────────────────────────────────

DEFAULT_CUSTOM_SYSTEM_PROMPT = "Your goal is to be as helpful as possible to the user."

# ─── SYSTEM PROMPTS ───────────────────────────────────────

GENERIC_SYSTEM_PROMPT = """You are {agent_name}. {agent_description}

{custom_prompt}"""

TOOL_INSTRUCTIONS = """
You have access to the following tools:

{tool_descriptions}

To call a tool, respond with EXACTLY this format:
<tool_call>
{{"name": "tool_name", "parameters": {{"param1": "value1", "param2": "value2"}}}}
</tool_call>

Important guidelines:
- When the user's question can be answered by using a tool, USE IT immediately with the information provided
- Don't ask for clarification unless a REQUIRED parameter is completely missing
- Use tools when they help answer the question, even if some details are ambiguous
- After receiving a tool result, use it to answer the user's question
- You can respond directly without tools if the question doesn't need external data
"""

MAX_ITERATIONS_PROMPT = """
IMPORTANT: You have reached the maximum number of tool calls allowed for this conversation.
Due to this limit, you were unable to complete all requested tool calls.
Please clearly state that you ran out of tool calls and explain which information you were unable to retrieve.
Then provide the best answer you can based on the tool results you did receive.
Do NOT attempt to call any more tools.
"""

