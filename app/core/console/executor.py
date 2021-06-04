import asyncio
import collections
import shlex
import uuid
import os.path
from dataclasses import dataclass, field
from typing import AsyncIterable, Optional, Awaitable, Callable, Any, Union
from .base import BaseCommandExecution, BaseCommandExecutor


class CommandExecution(BaseCommandExecution):
    def __init__(self) -> None:
        self._process: asyncio.subprocess.Process = None
        self._output: str = ""

    async def execute(
        self, command: str, *, stdin: Optional[bytes] = None, cwd: Optional[str] = None
    ) -> None:
        self._process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd or ...,
        )
        if stdin is not None and self._process.stdin is not None:
            self._process.stdin.write(stdin)

    def current_output(self) -> str:
        return self._output

    @property
    def return_code(self) -> Optional[int]:
        return self._process.returncode

    async def output(self) -> AsyncIterable[str]:
        if self._process.stdout is None:
            return
        async for output in self._process.stdout:
            self._output += output.decode("utf8", errors="ignore")
            yield self._output


AsyncStrCallback = Callable[[str], Awaitable[None]]
AsyncCallback = Callable[[], Awaitable[None]]


@dataclass
class ExecutionData:
    execution: CommandExecution = field(default_factory=CommandExecution)
    callback_data: dict[AsyncStrCallback, asyncio.Event] = field(default_factory=dict)


class CommandExecutor(BaseCommandExecutor):
    def __init__(self) -> None:
        self._executions: dict[uuid.UUID, ExecutionData] = {}
        self.__filter_exec: dict[uuid.UUID, uuid.UUID] = {}
        self.__exec_filter: dict[uuid.UUID, uuid.UUID] = {}

    async def execute(
        self,
        command: Union[list[str], str],
        *,
        filter_id: Optional[uuid.UUID] = None,
        stdin: Optional[bytes] = None,
        cwd: Optional[str] = None,
    ) -> uuid.UUID:
        execution_id = uuid.uuid4()
        if filter_id is not None:
            if filter_id in self.__filter_exec:
                raise PermissionError(
                    f"A process with filter={filter_id} is already running"
                )
            self.__filter_exec[filter_id] = execution_id
            self.__exec_filter[execution_id] = filter_id

        self._executions[execution_id] = ExecutionData()
        command_text = command if isinstance(command, str) else shlex.join(command)
        await self._executions[execution_id].execution.execute(
            command_text, stdin=stdin, cwd=cwd
        )
        asyncio.create_task(self._run_execution(execution_id))

        return execution_id

    @staticmethod
    def __get_command_log_path(command_id: uuid.UUID) -> str:
        return os.path.join("data", "logs", f"{command_id}.log")

    async def _run_execution(self, execution_id: uuid.UUID) -> None:
        execution_data = self._executions[execution_id]
        output_update = ""
        async for output_update in execution_data.execution.output():
            for callback in list(execution_data.callback_data):
                try:
                    await callback(output_update)
                except Exception:
                    execution_data.callback_data[callback].set()
                    del execution_data.callback_data[callback]

        return_value = execution_data.execution.return_code or -1

        with open(self.__get_command_log_path(execution_id), mode="w") as file:
            file.write(f"{return_value}\n")
            file.write(output_update)

        for callback in execution_data.callback_data:
            execution_data.callback_data[callback].set()

        del self._executions[execution_id]
        if execution_id in self.__exec_filter:
            filter_id = self.__exec_filter[execution_id]
            del self.__filter_exec[filter_id]
            del self.__exec_filter[execution_id]

    def __contains__(self, execution_id: Union[uuid.UUID, Any]) -> bool:
        if not isinstance(execution_id, uuid.UUID):
            return False
        return execution_id in self._executions or self.finished(execution_id)

    def finished(self, execution_id: uuid.UUID) -> bool:
        return os.path.isfile(self.__get_command_log_path(execution_id))

    def result(self, execution_id: uuid.UUID) -> Optional[tuple[int, str]]:
        if not self.finished(execution_id):
            return None

        with open(self.__get_command_log_path(execution_id), mode="r") as file:
            return_code, file_content = file.read().split("\n", maxsplit=1)
            return int(return_code), file_content

    async def listen(self, callback: AsyncStrCallback, execution_id: uuid.UUID) -> None:
        execution = self._executions[execution_id]
        execution.callback_data[callback] = asyncio.Event()
        await callback(execution.execution.current_output())
        await execution.callback_data[callback].wait()