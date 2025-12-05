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
    def __init__(
        self,
        tools: List[Tool] = None,
        model: Model = Model.GPT_5_MINI,
        max_iterations: int = 10,
        max_tokens: int = 4096,
        temperature: float = 0.4
    ):
        self.tools = tools or []
        self.model = model
        self.max_iterations = max_iterations
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize clients based on provider
        if model.provider == Provider.OPENAI:
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif model.provider == Provider.ANTHROPIC:
            self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        elif model.provider == Provider.GEMINI:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.gemini_model = genai.GenerativeModel(model.model_name)

    def _call_llm(self, messages: List[Message]) -> str:
        """Route to appropriate provider based on model."""
        if self.model.provider == Provider.OPENAI:
            return self._call_openai(messages)
        elif self.model.provider == Provider.GEMINI:
            return self._call_gemini(messages)
        elif self.model.provider == Provider.ANTHROPIC:
            return self._call_anthropic(messages)
        else:
            raise ValueError(f"Unsupported provider: {self.model.provider}")

    def _call_openai(self, messages: List[Message]) -> str:
        """Call OpenAI API with message conversion."""
        formatted = []
        for m in messages:
            if m.role in [Role.USER, Role.ASSISTANT, Role.SYSTEM]:
                formatted.append({"role": m.role.value, "content": m.content})
            elif m.role == Role.TOOL_CALL:
                formatted.append({"role": "assistant", "content": m.content})
            elif m.role == Role.TOOL_RESULT:
                formatted.append({"role": "user", "content": f"Tool result from {m.tool_name}:\n{m.content}"})
        
        response = self.openai_client.chat.completions.create(
            model=self.model.model_name,
            messages=formatted,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def _call_anthropic(self, messages: List[Message]) -> str:
        """Call Anthropic API with message conversion."""
        # Extract system messages (Anthropic uses separate system param)
        system_messages = [m.content for m in messages if m.role == Role.SYSTEM]
        system_prompt = "\n\n".join(system_messages) if system_messages else None
        
        # Convert non-system messages
        formatted = []
        for m in messages:
            if m.role in [Role.USER, Role.ASSISTANT]:
                formatted.append({"role": m.role.value, "content": m.content})
            elif m.role == Role.TOOL_CALL:
                formatted.append({"role": "assistant", "content": m.content})
            elif m.role == Role.TOOL_RESULT:
                formatted.append({"role": "user", "content": f"Tool result from {m.tool_name}:\n{m.content}"})
        
        response = self.anthropic_client.messages.create(
            model=self.model.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=formatted
        )
        return response.content[0].text

    def _call_gemini(self, messages: List[Message]) -> str:
        """Call Gemini API with message conversion."""
        history = []
        last_message = None
        
        # Prepend system messages to first user message
        system_messages = [m.content for m in messages if m.role == Role.SYSTEM]
        system_prefix = "\n\n".join(system_messages) + "\n\n" if system_messages else ""
        system_prepended = False
        
        for i, m in enumerate(messages):
            is_last = (i == len(messages) - 1)
            
            # Map role to Gemini format
            if m.role == Role.USER:
                gemini_role = "user"
                content = m.content
                # Prepend system to first user message
                if not system_prepended and system_prefix:
                    content = system_prefix + content
                    system_prepended = True
            elif m.role in [Role.ASSISTANT, Role.TOOL_CALL]:
                gemini_role = "model"
                content = m.content
            elif m.role == Role.TOOL_RESULT:
                gemini_role = "user"
                content = f"Tool result from {m.tool_name}:\n{m.content}"
            else:
                continue  # Skip SYSTEM (already handled)
            
            # Add to history or set as last message
            if is_last:
                last_message = content
            else:
                history.append({"role": gemini_role, "parts": [content]})
        
        chat = self.gemini_model.start_chat(history=history)
        response = chat.send_message(
            last_message or "",
            generation_config=genai.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature
            )
        )
        return response.text

    def run(self, messages: List[Message]) -> Message:
        """Main agent loop: calls LLM, executes tools, returns final response."""
        # Copy messages to avoid mutating user's list
        internal_messages = messages.copy()
        
        # Add system prompt if tools exist
        if self.tools:
            system_msg = Message(Role.SYSTEM, self._build_system_prompt())
            internal_messages.insert(0, system_msg)
        
        # Agent loop
        response_text = ""
        for iteration in range(self.max_iterations):
            # Call LLM
            response_text = self._call_llm(internal_messages)
            
            # Check for tool call
            tool_call = self._parse_tool_call(response_text)
            
            if tool_call:
                # Add tool call to history
                internal_messages.append(
                    Message(Role.TOOL_CALL, response_text, tool_call["name"])
                )
                
                # Execute tool
                result = self._execute_tool(tool_call)
                
                # Add result to history
                internal_messages.append(
                    Message(Role.TOOL_RESULT, result, tool_call["name"])
                )
                
                # Continue loop to let LLM process result
                continue
            else:
                # No tool call - this is the final answer
                return Message(Role.ASSISTANT, response_text)
        
        # Max iterations reached - replace system prompt and force final answer
        final_messages = [m for m in internal_messages if m.role != Role.SYSTEM]
        final_messages.insert(0, Message(
            Role.SYSTEM,
            "You have reached the maximum number of tool calls. The conversation contains all the tool results gathered so far. "
            "Based on the information available in the conversation history, provide the best final answer you can to the user's question. "
            "Do NOT attempt to call any more tools. Just synthesize the information you have and respond directly."
        ))
        final_response = self._call_llm(final_messages)
        return Message(Role.ASSISTANT, final_response)

