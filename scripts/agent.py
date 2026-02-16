#!/usr/bin/env python3
"""
Auto-Fix Agent: Detects and automatically fixes common issues in projects.
Supports code quality, formatting, dependencies, and security scanning.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from colorama import Fore, Style, init

init(autoreset=True)

@dataclass
class Issue:
    issue_type: str
    severity: str  # critical, high, medium, low
    file: str
    line: int
    message: str
    fixable: bool
    fix_command: str = None

class IssueDetector:
    """Detects various types of issues in the codebase."""

    def __init__(self, workspace: str = "."):
        self.workspace = Path(workspace)
        self.issues: List[Issue] = []

    def detect_formatting_issues(self) -> List[Issue]:
        """Detect code formatting issues using Black and isort."""
        issues = []

        try:
            # Check Python formatting with Black
            result = subprocess.run(
                ["black", "--check", "--quiet", self.workspace],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                issues.append(Issue(
                    issue_type="formatting",
                    severity="low",
                    file="(multiple)",
                    line=0,
                    message="Code not formatted according to Black standards",
                    fixable=True,
                    fix_command=f"black {self.workspace}"
                ))

            # Check import sorting with isort
            result = subprocess.run(
                ["isort", "--check-only", "--quiet", self.workspace],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                issues.append(Issue(
                    issue_type="imports",
                    severity="low",
                    file="(multiple)",
                    line=0,
                    message="Imports not sorted correctly",
                    fixable=True,
                    fix_command=f"isort {self.workspace}"
                ))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Formatting check failed: {e}{Style.RESET_ALL}")

        return issues

    def detect_security_issues(self) -> List[Issue]:
        """Detect security issues using Bandit."""
        issues = []

        try:
            result = subprocess.run(
                ["bandit", "-r", str(self.workspace), "-f", "json", "-q"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.stdout:
                data = json.loads(result.stdout)
                for issue in data.get("results", []):
                    issues.append(Issue(
                        issue_type="security",
                        severity=issue.get("severity", "medium").lower(),
                        file=issue.get("filename", "unknown"),
                        line=issue.get("line_number", 0),
                        message=issue.get("issue_text", "Security issue detected"),
                        fixable=False  # Security issues usually need manual review
                    ))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Security check failed: {e}{Style.RESET_ALL}")

        return issues

    def detect_linting_issues(self) -> List[Issue]:
        """Detect linting issues using pylint."""
        issues = []

        try:
            py_files = list(self.workspace.rglob("*.py"))
            if not py_files:
                return issues

            result = subprocess.run(
                ["pylint"] + [str(f) for f in py_files[:10]],  # Limit to first 10 files
                capture_output=True,
                text=True,
                timeout=60
            )

            # Parse pylint output (simplified - just count issues)
            output = result.stdout + result.stderr
            if "error" in output.lower() or "warning" in output.lower():
                issues.append(Issue(
                    issue_type="linting",
                    severity="medium",
                    file="(multiple)",
                    line=0,
                    message="Linting issues detected",
                    fixable=True,
                    fix_command=f"pylint --rcfile=/dev/null {self.workspace} --fix-imports=y"
                ))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Linting check failed: {e}{Style.RESET_ALL}")

        return issues

    def detect_dependency_issues(self) -> List[Issue]:
        """Detect outdated or vulnerable dependencies."""
        issues = []

        # Check Python requirements
        req_files = list(self.workspace.glob("requirements*.txt"))
        for req_file in req_files:
            try:
                result = subprocess.run(
                    ["pip", "list", "--outdated", "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.stdout:
                    outdated = json.loads(result.stdout)
                    if outdated:
                        issues.append(Issue(
                            issue_type="dependencies",
                            severity="medium",
                            file=str(req_file),
                            line=0,
                            message=f"{len(outdated)} outdated dependencies found",
                            fixable=True,
                            fix_command=f"pip install --upgrade pip && pip install -r {req_file} --upgrade"
                        ))
            except Exception as e:
                pass

        # Check package.json
        package_json = self.workspace / "package.json"
        if package_json.exists():
            try:
                result = subprocess.run(
                    ["npm", "outdated", "--json"],
                    cwd=self.workspace,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.stdout and result.stdout != "{}":
                    issues.append(Issue(
                        issue_type="npm-dependencies",
                        severity="medium",
                        file="package.json",
                        line=0,
                        message="Outdated npm packages found",
                        fixable=True,
                        fix_command="npm update"
                    ))
            except Exception as e:
                pass

        return issues

    def run_all_detectors(self) -> List[Issue]:
        """Run all issue detectors."""
        print(f"{Fore.CYAN}🔍 Starting issue detection...{Style.RESET_ALL}\n")

        all_issues = []
        all_issues.extend(self.detect_formatting_issues())
        all_issues.extend(self.detect_linting_issues())
        all_issues.extend(self.detect_security_issues())
        all_issues.extend(self.detect_dependency_issues())

        self.issues = all_issues
        return all_issues

class IssueFixer:
    """Applies fixes to detected issues."""

    def __init__(self, workspace: str = "."):
        self.workspace = Path(workspace)
        self.fixed_count = 0

    def fix_formatting(self) -> bool:
        """Fix code formatting issues."""
        try:
            print(f"{Fore.BLUE}🔧 Fixing code formatting...{Style.RESET_ALL}")
            subprocess.run(["black", str(self.workspace)], check=True, timeout=60)
            subprocess.run(["isort", str(self.workspace)], check=True, timeout=60)
            self.fixed_count += 2
            print(f"{Fore.GREEN}✓ Formatting fixed{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Formatting fix failed: {e}{Style.RESET_ALL}")
            return False

    def fix_dependencies(self) -> bool:
        """Update dependencies."""
        try:
            print(f"{Fore.BLUE}🔧 Updating dependencies...{Style.RESET_ALL}")

            # Python
            req_files = list(self.workspace.glob("requirements*.txt"))
            for req_file in req_files:
                subprocess.run(
                    ["pip", "install", "-r", str(req_file), "--upgrade"],
                    check=True,
                    timeout=120
                )

            # Node.js
            if (self.workspace / "package.json").exists():
                subprocess.run(["npm", "update"], cwd=self.workspace, check=True, timeout=120)

            self.fixed_count += 1
            print(f"{Fore.GREEN}✓ Dependencies updated{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Dependency update failed: {e}{Style.RESET_ALL}")
            return False

    def apply_fixes(self, issues: List[Issue]) -> int:
        """Apply all fixable issues."""
        print(f"\n{Fore.CYAN}🛠 Applying fixes...{Style.RESET_ALL}\n")

        # Group issues by type
        formatting_issues = [i for i in issues if i.issue_type in ["formatting", "imports"]]
        dep_issues = [i for i in issues if i.issue_type in ["dependencies", "npm-dependencies"]]

        if formatting_issues:
            self.fix_formatting()

        if dep_issues:
            self.fix_dependencies()

        return self.fixed_count

class WorkflowOrchestrator:
    """Orchestrates the full auto-fix workflow."""

    def __init__(self, workspace: str = "."):
        self.workspace = workspace
        self.detector = IssueDetector(workspace)
        self.fixer = IssueFixer(workspace)

    def run(self) -> bool:
        """Run the complete auto-fix workflow."""
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Auto-Fix Workflow Agent{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        # Detect issues
        issues = self.detector.run_all_detectors()

        if not issues:
            print(f"\n{Fore.GREEN}✓ No issues detected!{Style.RESET_ALL}\n")
            return True

        # Report findings
        print(f"\n{Fore.YELLOW}Found {len(issues)} issue(s):{Style.RESET_ALL}\n")
        for issue in issues:
            icon = "🔴" if issue.severity == "critical" else "🟠" if issue.severity == "high" else "🟡"
            fixable = "✓ fixable" if issue.fixable else "⚠ requires review"
            print(f"{icon} [{issue.issue_type}] {issue.message} ({fixable})")

        # Apply fixes
        fixed_count = self.fixer.apply_fixes(issues)

        # Summary
        print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Workflow Complete: {fixed_count} fix(es) applied{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")

        return True

if __name__ == "__main__":
    workspace = os.getenv("GITHUB_WORKSPACE", ".")
    orchestrator = WorkflowOrchestrator(workspace)
    success = orchestrator.run()
    sys.exit(0 if success else 1)
