import asyncio
import os
import signal
import subprocess

class Terminal:
    def __init__(self):
        self.process = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    async def run_command(self, command: str, timeout: int = 10) -> str:
        try:
            output, _ = await asyncio.wait_for(asyncio.to_thread(self._run_command, command), timeout=timeout)
            return output
        except asyncio.TimeoutError:
            return "Command timed out"

    def _run_command(self, command: str) -> str:
        self.process.stdin.write(command.encode('utf-8'))
        self.process.stdin.write(b'\n')
        self.process.stdin.flush()
        output = self.process.stdout.readline().decode('utf-8')
        return output.strip()

    async def force_stop(self):
        os.kill(self.process.pid, signal.SIGINT)
		# self.process.terminate()
        # await asyncio.to_thread(self.process.wait)