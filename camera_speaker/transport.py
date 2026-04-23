import sys

import paramiko


class Transport:
    def __init__(self, host: str, user: str, port: int):
        self.host = host
        self.user = user
        self.port = port
        self._client = None

    def _connect(self):
        if self._client is not None:
            return
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self._client.connect(self.host, port=self.port, username=self.user)
        except Exception as e:
            print(f"Error: Cannot connect to {self.host}: {e}", file=sys.stderr)
            sys.exit(1)

    def ssh_exec(self, command: str) -> tuple[str, str]:
        """Execute command on camera, return (stdout, stderr)."""
        self._connect()
        _, stdout, stderr = self._client.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()

    def scp_upload(self, local_path: str, remote_path: str):
        """Upload file to camera via SFTP."""
        self._connect()
        sftp = self._client.open_sftp()
        try:
            sftp.put(local_path, remote_path)
        finally:
            sftp.close()

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
