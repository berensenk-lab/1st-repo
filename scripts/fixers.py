"""
Specialized fixers for different issue categories.
Extensible design for adding new fixes.
"""

import subprocess
from pathlib import Path
from typing import Callable, List


class DockerFixer:
    """Fixes Docker/container-related issues."""

    @staticmethod
    def optimize_dockerfile(workspace: Path) -> bool:
        """Apply Docker best practices."""
        dockerfile = workspace / "Dockerfile"
        if not dockerfile.exists():
            return False

        content = dockerfile.read_text()

        # Example: Add .dockerignore if missing
        dockerignore = workspace / ".dockerignore"
        if not dockerignore.exists():
            default_ignores = """
.git
.gitignore
.dockerignore
.env
node_modules
__pycache__
.pytest_cache
.venv
build
dist
*.egg-info
.vscode
.idea
"""
            dockerignore.write_text(default_ignores.strip())
            return True

        return False


class SecurityFixer:
    """Fixes security-related issues."""

    @staticmethod
    def remove_hardcoded_secrets(workspace: Path) -> int:
        """Scan and report hardcoded secrets."""
        try:
            result = subprocess.run(
                ["git", "secrets", "--scan"],
                cwd=workspace,
                capture_output=True,
                timeout=30,
            )
            return result.returncode
        except:
            return 1


class ConfigFixer:
    """Fixes configuration issues."""

    @staticmethod
    def add_docker_compose_healthcheck(compose_file: Path) -> bool:
        """Add health checks to docker-compose.yml if missing."""
        import yaml

        try:
            with open(compose_file) as f:
                config = yaml.safe_load(f)

            if not config or "services" not in config:
                return False

            modified = False
            for service_name, service in config.get("services", {}).items():
                if "healthcheck" not in service and service.get("image"):
                    # Add basic healthcheck
                    service["healthcheck"] = {
                        "test": ["CMD", "curl", "-f", "http://localhost/ || exit 1"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                        "start_period": "40s",
                    }
                    modified = True

            if modified:
                with open(compose_file, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)
                return True
        except:
            pass

        return False


class FixerRegistry:
    """Registry of available fixers."""

    fixers: dict = {
        "docker": DockerFixer,
        "security": SecurityFixer,
        "config": ConfigFixer,
    }

    @classmethod
    def get_fixer(cls, category: str):
        """Get fixer for a category."""
        return cls.fixers.get(category)

    @classmethod
    def register(cls, category: str, fixer_class: type):
        """Register a new fixer."""
        cls.fixers[category] = fixer_class
