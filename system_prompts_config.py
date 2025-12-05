# ─── SYSTEM PROMPTS CONFIGURATION ────────────────────────
# Users can edit these prompts to customize agent behavior

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

DEFAULT_CUSTOM_SYSTEM_PROMPT = """
"Your goal is to be as helpful as possible to the user."
"""
