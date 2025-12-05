from typing import List, Callable, Optional
from enum import Enum
import os
import re
import json
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai


# ─── ENUMS ───────────────────────────────────────────────

class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


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


# ─── MESSAGE ─────────────────────────────────────────────

class Message:
    def __init__(self, role: Role, content: str, tool_name: Optional[str] = None):
        self.role = role
        self.content = content
        self.tool_name = tool_name


# ─── TOOL ────────────────────────────────────────────────

class Tool:
    def __init__(self, name: str, description: str, parameters: dict, function: Callable):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function


class Agent:
    def __init__(self, tools: List[Tool]):
        # TODO: Implement
        self.tools = tools

    def run(self, messages: List[Message]) -> Message:
        # TODO: Implement
        pass

