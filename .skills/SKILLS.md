# Project Skills

Skills are instructions for the AI agent. Each skill defines a specific workflow
the agent must follow when the trigger condition is met.

## Available Skills

| Skill | Trigger | SKILL.md |
|---|---|---|
| `sync-docs` | Any code change that affects public interfaces, config, CLI, or project structure | [.skills/sync-docs/SKILL.md](.skills/sync-docs/SKILL.md) |
| `security` | Any new code handling files, user input, secrets, or external data | [.skills/security/SKILL.md](.skills/security/SKILL.md) |
| `best-practices` | Any new or refactored Python code | [.skills/best-practices/SKILL.md](.skills/best-practices/SKILL.md) |
| `testing` | Any code change — service, pipeline, parser, or CLI | [.skills/testing/SKILL.md](.skills/testing/SKILL.md) |
| `code-review` | Before finalising any feature, fix, or refactor | [.skills/code-review/SKILL.md](.skills/code-review/SKILL.md) |

## Folder Structure

```
.skills/
├── SKILLS.md                          # this file
├── sync-docs/
│   ├── SKILL.md                       # when and how to update docs
│   └── references/
│       └── doc-map.md                 # maps every documented item to its code location
├── security/
│   ├── SKILL.md                       # security rules and checklist
│   └── references/
│       └── threat-model.md            # known threats and mitigations
├── best-practices/
│   ├── SKILL.md                       # Python and RAG coding standards
│   └── references/
│       └── rag-patterns.md            # chunking, embedding, retrieval patterns
├── testing/
│   ├── SKILL.md                       # how to write tests for each type of change
│   └── scripts/
│       └── run_tests.ps1              # PowerShell script to run full test suite
└── code-review/
    ├── SKILL.md                       # review checklist and report template
    └── references/
        └── review-examples.md         # real before/after examples from this project
```

## How the Agent Uses Skills

When making any code change, the agent should:
1. Apply **best-practices** while writing the code
2. Apply **security** for any file, input, or config handling
3. Apply **testing** to write or update test cases
4. Apply **sync-docs** if any public interface, config, or CLI changed
5. Apply **code-review** before declaring the change done
