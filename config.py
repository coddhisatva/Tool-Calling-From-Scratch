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

DEFAULT_MODEL = Model.GPT_5_MINI
DEFAULT_TEMPERATURE = 0.4
DEFAULT_MAX_TOKENS = 4096
DEFAULT_MAX_ITERATIONS = 10
DEFAULT_AGENT_NAME = "AI Assistant"
DEFAULT_AGENT_DESCRIPTION = "A helpful AI assistant."
DEFAULT_CUSTOM_SYSTEM_PROMPT = "Your goal is to be as helpful as possible to the user."


# ─── SYSTEM PROMPTS ───────────────────────────────────────

GENERIC_SYSTEM_PROMPT = """You are {agent_name}. {agent_description}

{custom_prompt}"""

TOOL_INSTRUCTIONS = """
You have access to the following tools that you MAY use when particularly relevant:

{tool_descriptions}

To call a tool, respond with EXACTLY this format:
<tool_call>
{{"name": "tool_name", "parameters": {{"param1": "value1", "param2": "value2"}}}}
</tool_call>

Important guidelines:
- Only use tools when they are specifically relevant and necessary to answer the user's question
- You can respond directly without using any tools if you already have sufficient information
- Only call ONE tool at a time and wait for its result before deciding the next step
- If you need more information from the user to use a tool effectively, ask them first
"""

MAX_ITERATIONS_PROMPT = """
You have reached the maximum number of tool calls for this conversation.
The conversation history contains all the tool results gathered so far.
Based on the information available, provide the best final answer you can to the user's question.
Do NOT attempt to call any more tools. Just synthesize the information you have and respond directly.
"""

