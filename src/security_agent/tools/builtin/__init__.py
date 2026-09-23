"""Built-in security tools."""

from __future__ import annotations

from security_agent.core.base_tool import BaseTool, ToolInput, ToolOutput
from security_agent.sandbox.executor import CommandExecutor


class SandboxTool(BaseTool):
    """Base for all sandbox-executed tools."""

    def build_command(self, tool_input: ToolInput) -> str:
        tpl = self.config.command_template
        flags = tool_input.flags or self.config.default_flags
        return tpl.format(target=tool_input.target, flags=flags, **tool_input.extra).strip()

    async def execute(self, tool_input: ToolInput) -> ToolOutput:
        cmd = self.build_command(tool_input)
        executor = CommandExecutor()
        result = await executor.run(
            tool_id=self.config.tool_id,
            target=tool_input.target,
            flags=tool_input.flags or self.config.default_flags,
            command=cmd,
            timeout=self.config.timeout_seconds,
        )
        return ToolOutput(
            tool_id=self.config.tool_id,
            target=tool_input.target,
            command=result.command,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
            duration_seconds=result.duration_seconds,
            success=result.success,
        )


class NmapTool(SandboxTool):
    pass


class GobusterTool(SandboxTool):
    pass


class SqlmapTool(SandboxTool):
    pass


class NiktoTool(SandboxTool):
    pass


class WhoisTool(SandboxTool):
    pass


class CurlTool(SandboxTool):
    pass


class ShellTool(SandboxTool):
    pass
