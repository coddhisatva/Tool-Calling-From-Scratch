from typing import List, Callable, Optional
import os
import re
import json
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from config import (
    Provider,
    Model,
    DEFAULT_CUSTOM_SYSTEM_PROMPT,
    GENERIC_SYSTEM_PROMPT,
    TOOL_INSTRUCTIONS,
    MAX_ITERATIONS_PROMPT
)


# ─── ENUMS ───────────────────────────────────────────────

from enum import Enum

class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


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
        name: str,
        description: str,
        custom_system_prompt: str = DEFAULT_CUSTOM_SYSTEM_PROMPT,
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
        self.agent_name = name
        self.agent_description = description
        self.custom_system_prompt = custom_system_prompt
        
        # Validate API key exists for chosen provider
        if model.provider == Provider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found in environment. "
                    "Please add it to your .env file or set it as an environment variable."
                )
            self.openai_client = OpenAI(api_key=api_key)
        elif model.provider == Provider.ANTHROPIC:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not found in environment. "
                    "Please add it to your .env file or set it as an environment variable."
                )
            self.anthropic_client = Anthropic(api_key=api_key)
        elif model.provider == Provider.GEMINI:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY not found in environment. "
                    "Please add it to your .env file or set it as an environment variable."
                )
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel(model.model_name)

    def _build_system_prompt(self) -> str:
        """Build system prompt with agent info and optional tool descriptions."""
        # Build base prompt
        base_prompt = GENERIC_SYSTEM_PROMPT.format(
            agent_name=self.agent_name,
            agent_description=self.agent_description,
            custom_prompt=self.custom_system_prompt
        ).strip()
        
        if not self.tools:
            return base_prompt
        
        # Add tool instructions
        tool_descriptions = "\n\n".join([self._format_tool_description(t) for t in self.tools])
        tool_section = TOOL_INSTRUCTIONS.format(tool_descriptions=tool_descriptions)
        
        return base_prompt + "\n\n" + tool_section

    def _format_tool_description(self, tool: Tool) -> str:
        """Format a single tool's description for the system prompt."""
        params_desc = []
        for param_name, param_info in tool.parameters.items():
            required = "(required)" if param_info["required"] else "(optional)"
            param_type = param_info["type"]
            param_desc = param_info.get("description", "")
            params_desc.append(f"    - {param_name} ({param_type}, {required}): {param_desc}")
        
        params_str = "\n".join(params_desc) if params_desc else "    (no parameters)"
        
        return f"""  {tool.name}: {tool.description}
    Parameters:
{params_str}"""

    def _parse_tool_call(self, response: str) -> Optional[dict]:
        """Extract tool call from response text, or None if no tool call."""
        match = re.search(r'<tool_call>\s*(.*?)\s*</tool_call>', response, re.DOTALL)
        if not match:
            return None
        
        try:
            tool_call = json.loads(match.group(1))
            # Validate structure
            if "name" not in tool_call:
                return None
            return tool_call
        except json.JSONDecodeError:
            return None

    def _execute_tool(self, tool_call: dict) -> str:
        """Execute a tool and return result (or error message)."""
        tool_name = tool_call.get("name")
        params = tool_call.get("parameters", {})
        
        # Find the tool
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"
        
        # Execute the tool
        try:
            result = tool.function(**params)
            return str(result)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"

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
            GENERIC_SYSTEM_PROMPT + "\n\n" + MAX_ITERATIONS_PROMPT
        ))
        final_response = self._call_llm(final_messages)
        return Message(Role.ASSISTANT, final_response)

