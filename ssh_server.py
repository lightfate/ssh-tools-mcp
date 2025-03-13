from mcp.server.fastmcp import FastMCP
import paramiko
from dataclasses import dataclass
from typing import Optional
import json

# Create an MCP server
mcp = FastMCP("SSH Tools")

class SSHConnection:
    def __init__(self, hostname: str, password: str, username: str = "root", port: int = 22):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.client = None

    def connect(self):
        if self.client is not None:
            return
            
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=self.hostname,
            username=self.username,
            password=self.password,
            port=self.port
        )

    def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None

    def execute_command(self, command: str) -> str:
        if not self.client:
            self.connect()
            
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if error:
            return f"Error: {error}"
        return output

@dataclass
class SSHConnectionInfo:
    hostname: str
    password: str
    username: str = "root"
    port: int = 22

# Global connection storage
current_connection: Optional[SSHConnection] = None

@mcp.tool()
def connect_ssh(hostname: str, password: str, username: str = "root", port: int = 22) -> str:
    """Connect to a remote server via SSH
    
    Args:
        hostname: The IP address or hostname of the server
        password: The SSH password
        username: The SSH username (default: root)
        port: The SSH port (default: 22)
    """
    global current_connection
    
    try:
        if current_connection:
            current_connection.disconnect()
            
        connection = SSHConnection(hostname, password, username, port)
        connection.connect()
        current_connection = connection
        return "Successfully connected to the server!"
    except Exception as e:
        return f"Failed to connect: {str(e)}"

@mcp.tool()
def run_command(command: str) -> str:
    """Run a command on the connected SSH server
    
    Args:
        command: The command to execute
    """
    global current_connection
    
    if not current_connection:
        return "Error: Not connected to any server. Please connect first using connect_ssh."
        
    try:
        return current_connection.execute_command(command)
    except Exception as e:
        return f"Failed to execute command: {str(e)}"

@mcp.tool()
def disconnect_ssh() -> str:
    """Disconnect from the current SSH server"""
    global current_connection
    
    if current_connection:
        current_connection.disconnect()
        current_connection = None
        return "Successfully disconnected from the server!"
    return "Not connected to any server."

if __name__ == "__main__":
    mcp.run() 