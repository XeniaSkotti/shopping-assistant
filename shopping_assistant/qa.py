from __future__ import annotations
import dataclasses
from pathlib import Path
import logging
from typing import List

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.callbacks import BaseCallbackHandler
from langchain_ollama import ChatOllama

from shopping_assistant.tools import calculator

# Module logger
logger = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    project_root = Path(__file__).resolve().parents[1]
    prompt_path = project_root / "prompts" / "system.txt"
    try:
        return prompt_path.read_text(encoding="utf-8")
    except Exception:
        return ""


@dataclasses.dataclass
class QAAgent:
    llm: BaseChatModel = dataclasses.field(default_factory=lambda: ChatOllama(model="llama3.1"))
    system_prompt: str = dataclasses.field(default_factory=_load_system_prompt)
    messages: List[BaseMessage] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        tools = [calculator]
        default_system = (
            "You are a helpful conversational assistant. "
            "Use the calculator tool for any arithmetic or numeric computation. "
            "Answer concisely and do not reveal your internal reasoning."
        )
        prompt_instruction = self.system_prompt or default_system

        self.app = create_agent(model=self.llm, tools=tools, system_prompt=prompt_instruction)

    # Simple console logger to confirm tool usage
    class _ConsoleToolLogger(BaseCallbackHandler):
        def on_tool_start(self, tool, input_str, **kwargs):  # type: ignore[override]
            try:
                name = getattr(tool, "name", str(tool))
            except Exception:
                name = str(tool)
            logger.info("[tool:start] %s | input=%s", name, input_str)

        def on_tool_end(self, output, **kwargs):  # type: ignore[override]
            logger.info("[tool:end] output=%s", output)

    def ask(self, question: str) -> str:
        # Route all questions through the agent; calculator usage is governed by the system prompt
        self.messages.append(HumanMessage(content=question))
        result = self.app.invoke(
            {"messages": self.messages},
            config={"callbacks": [QAAgent._ConsoleToolLogger()]},
        )
        answer = result["messages"][-1].content
        self.messages.append(AIMessage(content=answer))
        return answer

    def stream(self, question: str):
        self.messages.append(HumanMessage(content=question))
        for state in self.app.stream(
            {"messages": self.messages},
            stream_mode="values",
            config={"callbacks": [QAAgent._ConsoleToolLogger()]},
        ):
            msg = state["messages"][-1]
            yield (msg.type, msg.content)
        self.messages.append(AIMessage(content=msg.content))
