"""Core validation logic for dotguard."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

SENSITIVE_PATTERNS = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|auth|credential|private[_-]?key"
    r"|access[_-]?key|signing[_-]?key|encryption[_-]?key|jwt|oauth|cert|ssl)",
    re.IGNORECASE,
)

W = r"[\w-]+"

PLACEHOLDER_PATTERNS = re.compile(
    rf"^("
    rf"your[_-]?{W}[_-]?here"
    rf"|your[_-]{W}"
    rf"|changeme|change[_-]me|replace[_-]me"
    rf"|placeholder|example[_-]{W}|example"
    rf"|todo|fixme|xxx+"
    rf"|<[^>]+>|\[[^\]]+\]"
    rf"|sk-\.\.\.|pk-\.\.\.|{W}\.\.\."
    rf"|\.{{3,}}"
    rf"|insert[_-]{W}|add[_-]your[_-]{W}"
    rf"|test[_-]?(key|secret|token|password)"
    rf")$",
    re.IGNORECASE,
)

class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

@dataclass
class Issue:
    severity: Severity
    key: str
    message: str
    def __str__(self):
        return f"[{self.severity.value}] {self.key}: {self.message}"

@dataclass
class ValidationResult:
    issues: list[Issue] = field(default_factory=list)
    @property
    def errors(self):
        return [i for i in self.issues if i.severity == Severity.ERROR]
    @property
    def warnings(self):
        return [i for i in self.issues if i.severity == Severity.WARNING]
    @property
    def passed(self):
        return len(self.errors) == 0
    def add(self, severity, key, message):
        self.issues.append(Issue(severity=severity, key=key, message=message))

def parse_env_file(path):
    env = {}
    with path.open(encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, raw_value = line.partition("=")
            key = key.strip()
            if not key:
                continue
            env[key] = _strip_inline_comment(raw_value)
    return env

def _strip_inline_comment(raw):
    raw = raw.strip()
    if not raw:
        return ""
    if raw[0] in ('"', "'"):
        q = raw[0]
        end = raw.find(q, 1)
        return raw[1:end] if end != -1 else raw[1:]
    return raw.split("#")[0].rstrip()

def is_sensitive(key):
    return bool(SENSITIVE_PATTERNS.search(key))

def is_placeholder_for_key(key, value):
    if not value:
        return False
    if PLACEHOLDER_PATTERNS.match(value.strip()):
        return True
    return value.upper() == key.upper()

def validate(env_path, example_path):
    result = ValidationResult()
    env = parse_env_file(env_path)
    example = parse_env_file(example_path)
    for key in sorted(set(example) - set(env)):
        result.add(Severity.ERROR, key, "missing from .env (required by .env.example)")
    for key in sorted(set(env) - set(example)):
        result.add(Severity.WARNING, key, "present in .env but not in .env.example")
    for key in sorted(set(example) & set(env)):
        value = env[key]
        if value is None or value == "":
            if is_sensitive(key):
                result.add(Severity.ERROR, key, "sensitive key has no value (passwords/tokens must not be blank)")
            else:
                result.add(Severity.WARNING, key, "value is empty")
        elif is_placeholder_for_key(key, value):
            if is_sensitive(key):
                result.add(Severity.ERROR, key, f"sensitive key has a placeholder value ({value!r}) — looks like AI-generated or template code")
            else:
                result.add(Severity.WARNING, key, f"value looks like a placeholder ({value!r}) — replace with a real value before deploying")
    return result
