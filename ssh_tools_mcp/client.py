"""SSH client implementation for MCP servers."""

import paramiko
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SSHClient:
    """A high-level SSH client for MCP servers."""
    
    def __init__(self, hostname: str, username: str, port: int = 22):
        """Initialize the SSH client.
        
        Args:
            hostname: The remote host to connect to
            username: The username to authenticate as
            port: The port to connect to (default: 22)
        """
        self.hostname = hostname
        self.username = username
        self.port = port
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
    def connect(self, password: Optional[str] = None, key_filename: Optional[str] = None) -> None:
        """Connect to the remote host.
        
        Args:
            password: The password to authenticate with
            key_filename: Path to private key file
        """
        try:
            self._client.connect(
                hostname=self.hostname,
                username=self.username,
                password=password,
                key_filename=key_filename,
                port=self.port
            )
            logger.info(f"Successfully connected to {self.hostname}")
        except Exception as e:
            logger.error(f"Failed to connect to {self.hostname}: {str(e)}")
            raise
            
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command on the remote host.
        
        Args:
            command: The command to execute
            
        Returns:
            Dict containing stdout, stderr and return code
        """
        try:
            stdin, stdout, stderr = self._client.exec_command(command)
            return {
                "stdout": stdout.read().decode(),
                "stderr": stderr.read().decode(),
                "return_code": stdout.channel.recv_exit_status()
            }
        except Exception as e:
            logger.error(f"Failed to execute command '{command}': {str(e)}")
            raise
            
    def close(self) -> None:
        """Close the SSH connection."""
        self._client.close()
        logger.info(f"Closed connection to {self.hostname}")
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()