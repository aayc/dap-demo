#!/usr/bin/env python3

import json
import socket
import subprocess
import sys
import time


class DAPClient:
    def __init__(self) -> None:
        self.debug_port: int = 5678
        self.socket: socket.socket | None = None
        self.seq: int = 1

    def send_request(
        self,
        command: str,
        arguments: dict | None = None,
        wait_for_response: bool = True,
    ) -> dict | None:
        request = {
            "seq": self.seq,
            "type": "request",
            "command": command,
            "arguments": arguments or {},
        }
        self.seq += 1

        message = json.dumps(request)
        content_length = len(message.encode("utf-8"))

        full_message = f"Content-Length: {content_length}\r\n\r\n{message}"
        print(f"Sending: {command}")
        self.socket.send(full_message.encode("utf-8"))

        if not wait_for_response:
            return None

        # For requests, keep reading until we get the response (not events)
        while True:
            response = self.read_response()
            print(
                f"Received: {response.get('type')} - {response.get('command', response.get('event'))}"
            )
            if (
                response.get("type") == "response"
                and response.get("command") == command
            ):
                return response
            # Skip events during request/response cycle

    def read_response(self) -> dict:
        # Read headers
        headers = b""
        while b"\r\n\r\n" not in headers:
            headers += self.socket.recv(1)

        # Parse content length
        header_str = headers.decode("utf-8")
        content_length = int(header_str.split("Content-Length: ")[1].split("\r\n")[0])

        # Read body
        body = b""
        while len(body) < content_length:
            body += self.socket.recv(content_length - len(body))

        return json.loads(body.decode("utf-8"))

    def connect(self, host: str, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        print(f"Connected to debug server at {host}:{port}")

    def initialize_session(self) -> None:
        """Handle the DAP initialization handshake"""
        # Initialize debug session
        print("Initializing debug session...")
        self.send_request(
            "initialize",
            {
                "clientID": "dap-demo",
                "clientName": "DAP Demo Client",
                "adapterID": "python",
                "pathFormat": "path",
                "linesStartAt1": True,
                "columnsStartAt1": True,
                "supportsVariableType": True,
                "supportsVariablePaging": True,
                "supportsRunInTerminalRequest": True,
            },
        )

        # Send attach request to trigger initialized event (don't wait for response)
        print("Sending attach request...")
        self.send_request(
            "attach",
            {
                "connect": {"host": "localhost", "port": self.debug_port},
                "pathMappings": [],
                "justMyCode": False,
            },
            wait_for_response=False,
        )

        # Wait for initialized event
        print("Waiting for initialized event...")
        while True:
            response = self.read_response()
            print(f"Event received: {response}")
            if (
                response.get("type") == "event"
                and response.get("event") == "initialized"
            ):
                print("Got initialized event!")
                break

    def set_breakpoints(self, file_path: str, lines: list[int]) -> dict:
        """Set breakpoints at specified lines in a file"""
        import os

        abs_path = os.path.abspath(file_path)
        breakpoints = [{"line": line} for line in lines]

        return self.send_request(
            "setBreakpoints", {"source": {"path": abs_path}, "breakpoints": breakpoints}
        )

    def configuration_done(self) -> dict:
        """Signal that configuration is complete and execution can start"""
        return self.send_request("configurationDone")

    def get_stack_trace(self, thread_id: int) -> dict:
        """Get the stack trace for a thread"""
        return self.send_request("stackTrace", {"threadId": thread_id})

    def get_scopes(self, frame_id: int) -> dict:
        """Get the scopes (local, global variables) for a frame"""
        return self.send_request("scopes", {"frameId": frame_id})

    def get_variables(self, variables_reference: int) -> dict:
        """Get variables for a given scope reference"""
        return self.send_request(
            "variables", {"variablesReference": variables_reference}
        )


class DAPDebugger:
    def __init__(self) -> None:
        self.debug_port: int = 5678
        self.client: DAPClient = DAPClient()

    def start_debug_session(self) -> None:
        print("Starting Debug Adapter Protocol session...")

        # Start the target script with debugpy
        print(f"Starting demo/main.py with debugpy on port {self.debug_port}")
        target_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "debugpy",
                "--listen",
                f"localhost:{self.debug_port}",
                "--wait-for-client",
                "demo/main.py",
            ]
        )

        # Give the process time to start
        time.sleep(2)

        try:
            # Connect to debug server
            print(f"Connecting to debug session on port {self.debug_port}")
            self.client.connect("localhost", self.debug_port)

            # Initialize the DAP session
            self.client.initialize_session()

            # Set breakpoint at line 99 (quality check with hidden variables)
            print("Setting breakpoint at demo/main.py:99")
            self.client.set_breakpoints("demo/main.py", [99])

            # Start the program
            print("Starting program execution...")
            self.client.configuration_done()

            # Wait for breakpoint to be hit
            print("Waiting for breakpoint to be hit...")
            while True:
                response = self.client.read_response()
                if (
                    response.get("type") == "event"
                    and response.get("event") == "stopped"
                ):
                    print("\n=== BREAKPOINT HIT ===")
                    break

            # Get stack trace
            stack_response = self.client.get_stack_trace(response["body"]["threadId"])
            frame_id = stack_response["body"]["stackFrames"][0]["id"]

            # Get scopes (local, global variables)
            scopes_response = self.client.get_scopes(frame_id)

            for scope in scopes_response["body"]["scopes"]:
                print(f"\n{scope['name']} variables:")
                vars_response = self.client.get_variables(scope["variablesReference"])

                for var in vars_response["body"]["variables"]:
                    print(f"  {var['name']}: {var['value']}")

                    # Look for interesting hidden variables
                    secret_vars = [
                        "SECRET_PIPELINE_CONFIG",
                        "internal_batch_id",
                        "quality_threshold",
                        "pipeline_start_time",
                        "admin_override_enabled",
                        "encryption_keys",
                        "DB_SECRETS",
                        "SECRET_CONFIG_KEYS",
                        "LOGGING_SECRETS",
                        "app_config",
                    ]

                    if var["name"] in secret_vars:
                        print(
                            f"\n🔍 Found secret variable: {var['name']} = {var['value']}"
                        )
                    elif var["name"] == "processing_stats" and "hidden_config" in str(
                        var["value"]
                    ):
                        print(
                            f"\n🔍 Found processing stats with hidden config: {var['name']}"
                        )
                    elif var["name"] == "advanced_results" and "secret_params" in str(
                        var["value"]
                    ):
                        print(
                            f"\n🔍 Found advanced results with secret parameters: {var['name']}"
                        )
                    elif var["name"] == "db_manager" and hasattr(
                        var.get("value"), "get_cluster_status"
                    ):
                        print(
                            f"\n🔍 Found database manager with cluster secrets: {var['name']}"
                        )
                    elif var[
                        "name"
                    ] == "secure_logger" and "sensitive_data_cache" in str(
                        var["value"]
                    ):
                        print(
                            f"\n🔍 Found secure logger with sensitive cache: {var['name']}"
                        )

        except Exception as e:
            print(f"Debug session error: {e}")
        finally:
            if self.client.socket:
                self.client.socket.close()
            target_process.terminate()
            target_process.wait()


def main() -> None:
    debugger = DAPDebugger()
    debugger.start_debug_session()


if __name__ == "__main__":
    main()
