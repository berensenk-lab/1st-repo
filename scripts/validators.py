"""
Validators to ensure fixes don't break anything.
"""

import subprocess
from pathlib import Path
from typing import Tuple


class Validator:
    """Base validator class."""

    def validate(self) -> Tuple[bool, str]:
        """Run validation. Returns (success, message)."""
        raise NotImplementedError


class PythonValidator(Validator):
    """Validates Python code changes."""

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def validate(self) -> Tuple[bool, str]:
        """Run Python tests and linting."""
        try:
            # Check syntax
            result = subprocess.run(
                ["python", "-m", "py_compile"]
                + [str(f) for f in self.workspace.rglob("*.py")],
                capture_output=True,
                timeout=30,
            )

            if result.returncode != 0:
                return False, "Python syntax errors detected"

            # Run tests if pytest exists
            result = subprocess.run(
                ["pytest", str(self.workspace), "-v"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                return False, f"Tests failed:\n{result.stdout}"

            return True, "Python validation passed"
        except FileNotFoundError:
            return True, "Python validators not available"
        except Exception as e:
            return False, f"Validation error: {str(e)}"


class JavaScriptValidator(Validator):
    """Validates JavaScript/Node code changes."""

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def validate(self) -> Tuple[bool, str]:
        """Run JavaScript tests."""
        if not (self.workspace / "package.json").exists():
            return True, "No JavaScript project found"

        try:
            # Run tests if available
            result = subprocess.run(
                ["npm", "test"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                return False, f"Tests failed:\n{result.stdout}"

            return True, "JavaScript validation passed"
        except FileNotFoundError:
            return True, "npm not available"
        except Exception as e:
            return False, f"Validation error: {str(e)}"


class DockerValidator(Validator):
    """Validates Docker configuration changes."""

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def validate(self) -> Tuple[bool, str]:
        """Validate Docker configuration."""
        try:
            dockerfile = self.workspace / "Dockerfile"
            if dockerfile.exists():
                # Build image to check for errors
                result = subprocess.run(
                    [
                        "docker",
                        "build",
                        "-f",
                        str(dockerfile),
                        "-t",
                        "validator:latest",
                        str(self.workspace),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=180,
                )

                if result.returncode != 0:
                    return False, f"Docker build failed:\n{result.stderr}"

            # Validate docker-compose
            compose_file = self.workspace / "docker-compose.yml"
            if compose_file.exists():
                result = subprocess.run(
                    ["docker", "compose", "-f", str(compose_file), "config"],
                    cwd=self.workspace,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    return False, f"Docker Compose validation failed:\n{result.stderr}"

            return True, "Docker validation passed"
        except FileNotFoundError:
            return True, "Docker not available for validation"
        except Exception as e:
            return False, f"Validation error: {str(e)}"


class ValidatorChain:
    """Runs multiple validators."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.validators = [
            PythonValidator(workspace),
            JavaScriptValidator(workspace),
            DockerValidator(workspace),
        ]

    def validate_all(self) -> Tuple[bool, list]:
        """Run all validators. Returns (all_passed, results)."""
        results = []
        all_passed = True

        for validator in self.validators:
            try:
                passed, message = validator.validate()
                results.append(
                    {
                        "validator": validator.__class__.__name__,
                        "passed": passed,
                        "message": message,
                    }
                )
                if not passed:
                    all_passed = False
            except Exception as e:
                results.append(
                    {
                        "validator": validator.__class__.__name__,
                        "passed": False,
                        "message": f"Error: {str(e)}",
                    }
                )
                all_passed = False

        return all_passed, results
