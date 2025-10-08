"""Sandbox executor for safe code execution."""

import logging
import subprocess
import tempfile
import os
import signal
from typing import Dict, Any, Optional
from pathlib import Path
import json

from evomind.sandbox.policies import SandboxPolicy, ResourcePolicy, SecurityPolicy

logger = logging.getLogger(__name__)


class SandboxExecutor:
    """Executor for running code in isolated sandbox.
    
    Implements isolation using subprocess with resource limits.
    In production: use gVisor, nsjail, or Firecracker for stronger isolation.
    """
    
    def __init__(
        self,
        default_policy: Optional[SandboxPolicy] = None,
        work_dir: Optional[Path] = None
    ):
        self.default_policy = default_policy or SandboxPolicy()
        self.work_dir = work_dir or Path(tempfile.gettempdir()) / "evomind_sandbox"
        self.work_dir.mkdir(exist_ok=True)
    
    def execute(
        self,
        tool: Dict[str, Any],
        args: Dict[str, Any],
        policy: Optional[SandboxPolicy] = None
    ) -> Dict[str, Any]:
        """Execute tool in sandbox.
        
        Args:
            tool: Tool artifact with code
            args: Execution arguments
            policy: Optional override policy
        
        Returns:
            Execution result
        """
        policy = policy or self.default_policy
        
        logger.info(f"Executing tool {tool.get('tool_id', 'unknown')} in sandbox")
        
        try:
            # Prepare execution environment
            exec_dir = self._prepare_environment(tool)
            
            # Create execution script
            script_path = self._create_exec_script(tool, args, exec_dir)
            
            # Execute with limits
            result = self._execute_with_limits(script_path, policy)
            
            # Cleanup
            self._cleanup(exec_dir)
            
            return result
            
        except Exception as e:
            logger.error(f"Sandbox execution error: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "stdout": "",
                "stderr": str(e)
            }
    
    def _prepare_environment(self, tool: Dict[str, Any]) -> Path:
        """Prepare isolated execution environment."""
        # Create temporary directory for this execution
        exec_dir = Path(tempfile.mkdtemp(dir=self.work_dir))
        
        # Write tool code
        code = tool.get("artifact", {}).get("code", tool.get("code", ""))
        code_path = exec_dir / "tool_code.py"
        code_path.write_text(code)
        
        logger.debug(f"Prepared environment at {exec_dir}")
        return exec_dir
    
    def _create_exec_script(
        self,
        tool: Dict[str, Any],
        args: Dict[str, Any],
        exec_dir: Path
    ) -> Path:
        """Create execution script."""
        script = f"""
import sys
import json

# Load tool code
with open('tool_code.py', 'r') as f:
    exec(f.read(), globals())

# Load arguments
args = {json.dumps(args)}

# Execute tool
try:
    # Find the main function (avoid iteration issues)
    tool_func = None
    all_names = list(globals().keys())
    for name in all_names:
        obj = globals()[name]
        if callable(obj) and not name.startswith('_'):
            tool_func = obj
            break
    
    if tool_func:
        result = tool_func(args)
        print(json.dumps({{"status": "success", "result": result}}))
    else:
        print(json.dumps({{"status": "error", "error": "No executable function found"}}))
except Exception as e:
    import traceback
    print(json.dumps({{"status": "error", "error": str(e), "traceback": traceback.format_exc()}}))
"""
        
        script_path = exec_dir / "exec_script.py"
        script_path.write_text(script)
        return script_path
    
    def _execute_with_limits(
        self,
        script_path: Path,
        policy: SandboxPolicy
    ) -> Dict[str, Any]:
        """Execute script with resource limits."""
        resource_policy = policy.resource
        
        # Build command
        cmd = [
            "python3",
            str(script_path)
        ]
        
        try:
            # Set resource limits (simplified version)
            # In production: use cgroups, rlimits properly
            
            process = subprocess.Popen(
                cmd,
                cwd=script_path.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=self._set_limits(resource_policy)
            )
            
            # Wait with timeout
            try:
                stdout, stderr = process.communicate(timeout=resource_policy.wall_time_limit)
                returncode = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return {
                    "status": "timeout",
                    "error": "Execution timed out",
                    "stdout": stdout,
                    "stderr": stderr
                }
            
            # Parse result
            if returncode == 0 and stdout:
                try:
                    result_data = json.loads(stdout.strip())
                    return result_data
                except json.JSONDecodeError:
                    return {
                        "status": "success",
                        "result": {"output": stdout},
                        "stdout": stdout,
                        "stderr": stderr
                    }
            else:
                return {
                    "status": "error",
                    "error": f"Process exited with code {returncode}",
                    "stdout": stdout,
                    "stderr": stderr
                }
        
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _set_limits(self, policy: ResourcePolicy):
        """Return function to set resource limits."""
        def limits():
            try:
                import resource
                # Set CPU time limit
                resource.setrlimit(
                    resource.RLIMIT_CPU,
                    (policy.cpu_time_limit, policy.cpu_time_limit)
                )
                # Set memory limit
                mem_bytes = policy.memory_limit_mb * 1024 * 1024
                resource.setrlimit(
                    resource.RLIMIT_AS,
                    (mem_bytes, mem_bytes)
                )
            except Exception as e:
                logger.warning(f"Could not set resource limits: {e}")
        
        return limits
    
    def _cleanup(self, exec_dir: Path) -> None:
        """Cleanup execution directory."""
        try:
            import shutil
            shutil.rmtree(exec_dir)
            logger.debug(f"Cleaned up {exec_dir}")
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
