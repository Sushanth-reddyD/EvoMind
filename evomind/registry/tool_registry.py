"""Tool registry for managing and discovering tools."""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""
    
    id: str
    name: str
    version: str
    description: str
    owner: str = "system"
    io_spec: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    network_scopes: List[str] = field(default_factory=list)
    fs_scopes: List[str] = field(default_factory=list)
    cpu_limit: int = 30
    memory_limit_mb: int = 512
    tests: List[Dict[str, Any]] = field(default_factory=list)
    success_rate: float = 1.0
    usage_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    deprecated: bool = False
    deprecation_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "owner": self.owner,
            "io_spec": self.io_spec,
            "dependencies": self.dependencies,
            "network_scopes": self.network_scopes,
            "fs_scopes": self.fs_scopes,
            "cpu_limit": self.cpu_limit,
            "memory_limit_mb": self.memory_limit_mb,
            "tests": self.tests,
            "success_rate": self.success_rate,
            "usage_count": self.usage_count,
            "created_at": self.created_at,
            "deprecated": self.deprecated,
            "deprecation_date": self.deprecation_date,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolMetadata":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


class ToolRegistry:
    """Registry for storing and discovering tools.
    
    Implements:
    - Tool storage with versioning
    - Metadata indexing
    - Search and discovery
    - Lifecycle management
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".evomind" / "registry"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.tools: Dict[str, ToolMetadata] = {}
        self.artifacts: Dict[str, Dict[str, Any]] = {}
        
        self._load_registry()
    
    def register(
        self,
        artifact: Dict[str, Any],
        metadata: Dict[str, Any],
        version: str
    ) -> str:
        """Register a new tool.
        
        Args:
            artifact: Tool artifact (code, etc.)
            metadata: Tool metadata
            version: Semantic version
        
        Returns:
            Tool ID
        """
        tool_id = f"{metadata.get('name', 'tool')}_{version}"
        
        # Create metadata
        meta = ToolMetadata(
            id=tool_id,
            name=metadata.get("name", ""),
            version=version,
            description=metadata.get("description", ""),
            io_spec=metadata.get("io_spec", {}),
            tags=metadata.get("tags", [])
        )
        
        # Store
        self.tools[tool_id] = meta
        self.artifacts[tool_id] = artifact
        
        # Persist
        self._save_tool(tool_id, meta, artifact)
        
        logger.info(f"Registered tool: {tool_id}")
        return tool_id
    
    def search(
        self,
        query: str,
        io_spec: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for tools.
        
        Args:
            query: Search query (intent/description)
            io_spec: Input/output specification to match
            limit: Maximum results
        
        Returns:
            List of matching tools
        """
        results = []
        
        query_lower = query.lower()
        
        for tool_id, meta in self.tools.items():
            if meta.deprecated:
                continue
            
            # Simple text matching
            score = 0.0
            
            if query_lower in meta.name.lower():
                score += 0.5
            
            if query_lower in meta.description.lower():
                score += 0.3
            
            for tag in meta.tags:
                if query_lower in tag.lower():
                    score += 0.2
            
            if score > 0:
                artifact = self.artifacts.get(tool_id, {})
                results.append({
                    "id": tool_id,
                    "metadata": meta.to_dict(),
                    "artifact": artifact,
                    "score": score,
                    "tool_id": tool_id,
                    "code": artifact.get("code", "")
                })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Found {len(results)} tools for query: {query}")
        return results[:limit]
    
    def get(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool by ID."""
        meta = self.tools.get(tool_id)
        if not meta:
            return None
        
        artifact = self.artifacts.get(tool_id, {})
        
        return {
            "id": tool_id,
            "metadata": meta.to_dict(),
            "artifact": artifact,
            "tool_id": tool_id,
            "code": artifact.get("code", "")
        }
    
    def update_stats(self, tool_id: str, success: bool) -> None:
        """Update tool usage statistics."""
        meta = self.tools.get(tool_id)
        if meta:
            meta.usage_count += 1
            if success:
                # Update success rate using exponential moving average
                alpha = 0.1
                meta.success_rate = alpha * 1.0 + (1 - alpha) * meta.success_rate
            else:
                alpha = 0.1
                meta.success_rate = alpha * 0.0 + (1 - alpha) * meta.success_rate
            
            self._save_tool(tool_id, meta, self.artifacts.get(tool_id, {}))
    
    def deprecate(self, tool_id: str, reason: Optional[str] = None) -> bool:
        """Deprecate a tool."""
        meta = self.tools.get(tool_id)
        if meta:
            meta.deprecated = True
            meta.deprecation_date = datetime.utcnow().isoformat()
            self._save_tool(tool_id, meta, self.artifacts.get(tool_id, {}))
            logger.info(f"Deprecated tool: {tool_id}")
            return True
        return False
    
    def list_all(self, include_deprecated: bool = False) -> List[Dict[str, Any]]:
        """List all tools."""
        results = []
        for tool_id, meta in self.tools.items():
            if not include_deprecated and meta.deprecated:
                continue
            
            results.append({
                "id": tool_id,
                "metadata": meta.to_dict()
            })
        
        return results
    
    def _save_tool(
        self,
        tool_id: str,
        metadata: ToolMetadata,
        artifact: Dict[str, Any]
    ) -> None:
        """Save tool to storage."""
        tool_dir = self.storage_path / tool_id
        tool_dir.mkdir(exist_ok=True)
        
        # Save metadata
        meta_path = tool_dir / "metadata.json"
        meta_path.write_text(json.dumps(metadata.to_dict(), indent=2))
        
        # Save artifact
        artifact_path = tool_dir / "artifact.json"
        artifact_path.write_text(json.dumps(artifact, indent=2))
    
    def _load_registry(self) -> None:
        """Load registry from storage."""
        if not self.storage_path.exists():
            return
        
        for tool_dir in self.storage_path.iterdir():
            if not tool_dir.is_dir():
                continue
            
            try:
                # Load metadata
                meta_path = tool_dir / "metadata.json"
                if meta_path.exists():
                    meta_data = json.loads(meta_path.read_text())
                    meta = ToolMetadata.from_dict(meta_data)
                    self.tools[meta.id] = meta
                
                # Load artifact
                artifact_path = tool_dir / "artifact.json"
                if artifact_path.exists():
                    artifact = json.loads(artifact_path.read_text())
                    self.artifacts[meta.id] = artifact
                
                logger.debug(f"Loaded tool: {meta.id}")
            
            except Exception as e:
                logger.error(f"Error loading tool from {tool_dir}: {e}")
        
        logger.info(f"Loaded {len(self.tools)} tools from registry")
