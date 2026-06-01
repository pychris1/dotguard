<p align="center">
  <img src="logo.png" alt="dotguard logo" width="160" />
</p>

<h1 align="center">.dot Guard</h1>

<p align="center">Validate your <code>.env</code> file against <code>.env.example</code> before you deploy.</p>

---

## Why dotguard?

In the age of AI-generated code, developers are shipping placeholder credentials and misconfigured environments to production every day. dotguard catches it before you deploy.

## What it catches

| Check | Severity |
|---|---|
| Key in .env.example but missing from .env | ERROR |
| Sensitive key with empty value | ERROR |
| Sensitive key with a placeholder value | ERROR |
| .env file tracked or staged in git | ERROR |
| Non-sensitive key with a placeholder value | WARNING |
| Key in .env but not in .env.example | WARNING |
| Non-sensitive key with empty value | WARNING |

## Install

pip install dotguard

## Usage

dotguard                        validate .env against .env.example
dotguard --strict               treat warnings as errors
dotguard --no-extras            treat extra keys as errors
dotguard --no-git-check         skip git tracking check
dotguard --quiet                silent, exit code only
dotguard init                   generate .env.example from .env
dotguard init --force           overwrite existing .env.example

## Exit codes

0 = All checks passed
1 = One or more errors
2 = File not found

## License

MIT
