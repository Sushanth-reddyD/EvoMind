"""Security and resource policies for sandbox execution."""

from dataclasses import dataclass
from typing import Set


@dataclass
class ResourcePolicy:
    """Resource limits for sandbox execution."""

    cpu_time_limit: int = 30  # seconds
    wall_time_limit: int = 60  # seconds
    memory_limit_mb: int = 512
    disk_limit_mb: int = 100
    max_processes: int = 1
    max_file_size_mb: int = 10

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "cpu_time_limit": self.cpu_time_limit,
            "wall_time_limit": self.wall_time_limit,
            "memory_limit_mb": self.memory_limit_mb,
            "disk_limit_mb": self.disk_limit_mb,
            "max_processes": self.max_processes,
            "max_file_size_mb": self.max_file_size_mb
        }


@dataclass
class SecurityPolicy:
    """Security constraints for sandbox execution."""

    network_enabled: bool = False
    allowed_hosts: Set[str] = None
    filesystem_readonly: bool = True
    allowed_write_paths: Set[str] = None
    allow_subprocess: bool = False
    allow_imports: Set[str] = None

    def __post_init__(self):
        if self.allowed_hosts is None:
            self.allowed_hosts = set()
        if self.allowed_write_paths is None:
            self.allowed_write_paths = {"/tmp"}
        if self.allow_imports is None:
            self.allow_imports = {
                "json", "re", "math", "datetime",
                "typing", "dataclasses", "collections"
            }

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "network_enabled": self.network_enabled,
            "allowed_hosts": list(self.allowed_hosts),
            "filesystem_readonly": self.filesystem_readonly,
            "allowed_write_paths": list(self.allowed_write_paths),
            "allow_subprocess": self.allow_subprocess,
            "allow_imports": list(self.allow_imports)
        }


@dataclass
class SandboxPolicy:
    """Combined sandbox policy."""

    resource: ResourcePolicy = None
    security: SecurityPolicy = None

    def __post_init__(self):
        if self.resource is None:
            self.resource = ResourcePolicy()
        if self.security is None:
            self.security = SecurityPolicy()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "resource": self.resource.to_dict(),
            "security": self.security.to_dict()
        }
