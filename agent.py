from typing import List, Callable
from enum import Enum

class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message:
    def __init__(self, role: Role, content: str):
        self.role = role
        self.content = content

class Tool:
    def __init__(self, function: Callable):
        self.function = function
        # TODO: Implement (name, description, parameters)


class Agent:
    def __init__(self, tools: List[Tool]):
        # TODO: Implement
        self.tools = tools

    def run(self, messages: List[Message]) -> Message:
        # TODO: Implement
        pass

