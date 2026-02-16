"""
Specialized detectors for different issue categories.
Extensible design for adding new detectors.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class DetectionResult:
    category: str
    found: bool
    count: int
    details: Dict[str, Any]
    severity: str


class DockerDetector:
    """Detects Docker/container-related issues."""

    @staticmethod
    def detect_docker_best_practices(workspace: Path) -> DetectionResult:
        """Check for Docker best practices."""
        issues = {
            "multi_stage": False,
            "layer_caching": False,
            "security_scan": False,
        }

        dockerfile = workspace / "Dockerfile"
        if dockerfile.exists():
            content = dockerfile.read_text()
            issues["multi_stage"] = "FROM" in content and content.count("FROM") > 1
            issues["layer_caching"] = "RUN" in content

        return DetectionResult(
            category="docker",
            found=True,
            count=sum(not v for v in issues.values()),
            details=issues,
            severity="medium",
        )


class GitDetector:
    """Detects Git-related issues."""

    @staticmethod
    def detect_commit_quality(workspace: Path) -> DetectionResult:
        """Check git commit message quality."""
        try:
            result = subprocess.run(
                ["git", "log", "--format=%s", "-n", "10"],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=10,
            )

            commits = result.stdout.split("\n")
            issues = sum(1 for c in commits if len(c) > 72 or c.startswith("Merge"))

            return DetectionResult(
                category="git",
                found=issues > 0,
                count=issues,
                details={"bad_commits": issues, "total_checked": len(commits)},
                severity="low",
            )
        except:
            return DetectionResult(
                category="git", found=False, count=0, details={}, severity="low"
            )


class ConfigDetector:
    """Detects configuration file issues."""

    @staticmethod
    def detect_config_issues(workspace: Path) -> List[DetectionResult]:
        """Check common configuration files."""
        results = []

        # Check docker-compose.yml
        compose_file = workspace / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            issues = {
                "missing_healthcheck": "healthcheck" not in content,
                "missing_resource_limits": "deploy" not in content,
                "hardcoded_passwords": any(
                    p in content
                    for p in ["password:", "MYSQL_ROOT_PASSWORD", "POSTGRES_PASSWORD"]
                ),
            }
            results.append(
                DetectionResult(
                    category="docker-compose",
                    found=any(issues.values()),
                    count=sum(issues.values()),
                    details=issues,
                    severity="high" if issues["hardcoded_passwords"] else "medium",
                )
            )

        return results
