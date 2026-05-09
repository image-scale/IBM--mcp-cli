# Todo

## Plan
Build the CLI infrastructure in dependency order: configuration system first (constants, enums, environment helpers), then data models for tools and servers, then command infrastructure, then context management, and finally the main entry point. Each task delivers testable functionality that subsequent tasks build upon.

## Tasks
- [ ] Task 1: Implement configuration defaults and enums (config/defaults.py, config/enums.py + tests)
- [ ] Task 2: Implement environment variable helpers (config/env_vars.py + tests)
- [ ] Task 3: Implement configuration models with Pydantic (config/models.py + tests)
- [ ] Task 4: Implement runtime configuration with override resolution (config/runtime.py + tests)
- [ ] Task 5: Implement tool and server data models (tools/models.py + tests)
- [ ] Task 6: Implement command base classes and registry (commands/base.py, commands/registry.py + tests)
- [ ] Task 7: Implement context management (context/context_manager.py + tests)
- [ ] Task 8: Implement tool filtering and validation utilities (tools/filter.py, tools/validation.py + tests)
- [ ] Task 9: Implement display formatting utilities (display/formatters.py + tests)
- [ ] Task 10: Implement main CLI entry point with Typer (main.py + tests)
