"""
Utility to capture print() statements from existing Phase 1/2/3 code
and redirect them to WebSocket for live frontend updates
"""
import sys
import io
from typing import Callable, Optional
from contextlib import contextmanager


class LogCapture:
    """Captures stdout and redirects to callback function"""

    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        """
        Args:
            callback: Function to call with each captured line
        """
        self.callback = callback
        self.captured_lines = []
        self._original_stdout = None
        self._string_io = None

    def __enter__(self):
        """Start capturing stdout"""
        self._original_stdout = sys.stdout
        self._string_io = io.StringIO()
        sys.stdout = self._TeeOutput(self._original_stdout, self._string_io, self._on_write)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing stdout"""
        sys.stdout = self._original_stdout
        return False

    def _on_write(self, text: str):
        """Called whenever something is written to stdout"""
        if text and text.strip():
            self.captured_lines.append(text.strip())
            if self.callback:
                self.callback(text.strip())

    def get_lines(self) -> list:
        """Get all captured lines"""
        return self.captured_lines

    class _TeeOutput:
        """Tee output to both original stdout and string buffer"""

        def __init__(self, original, string_io, on_write_callback):
            self.original = original
            self.string_io = string_io
            self.on_write_callback = on_write_callback
            self._line_buffer = ""

        def write(self, text):
            # Write to original stdout (console)
            self.original.write(text)
            self.original.flush()

            # Write to string buffer
            self.string_io.write(text)

            # Buffer lines and call callback on newline
            self._line_buffer += text
            if '\n' in self._line_buffer:
                lines = self._line_buffer.split('\n')
                for line in lines[:-1]:  # All complete lines
                    if line.strip():
                        self.on_write_callback(line)
                self._line_buffer = lines[-1]  # Keep incomplete line in buffer

        def flush(self):
            self.original.flush()
            self.string_io.flush()


@contextmanager
def capture_logs(callback: Optional[Callable[[str], None]] = None):
    """
    Context manager to capture print() statements

    Usage:
        with capture_logs(lambda line: websocket.send(line)) as logger:
            # Any print() statements here will be captured
            print("This will be sent to websocket")
    """
    logger = LogCapture(callback)
    try:
        yield logger
    finally:
        pass
