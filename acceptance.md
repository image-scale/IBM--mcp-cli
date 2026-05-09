# Acceptance Criteria

## Task 1: Configuration defaults and enums

### Acceptance Criteria
- [x] DEFAULT_TOOL_EXECUTION_TIMEOUT equals 120.0 seconds
- [x] DEFAULT_SERVER_INIT_TIMEOUT equals 120.0 seconds
- [x] DEFAULT_STREAMING_CHUNK_TIMEOUT equals 45.0 seconds
- [x] DEFAULT_PROVIDER equals "openai"
- [x] DEFAULT_MODEL equals "gpt-4o-mini"
- [x] DEFAULT_THEME equals "default"
- [x] TimeoutType enum has values for streaming, tool, server, and HTTP timeouts
- [x] TokenBackend enum includes AUTO, KEYCHAIN, WINDOWS, ENCRYPTED, VAULT options
- [x] ServerStatus enum includes CONFIGURED, CONNECTED, DISCONNECTED, ERROR states
- [x] ConfigSource enum has CLI, ENV, FILE, DEFAULT priority values
- [x] ConversationAction enum has SHOW, CLEAR, SAVE, LOAD actions
- [x] TokenAction enum includes LIST, SET, GET, DELETE, CLEAR actions
- [x] OutputFormat enum has JSON, TABLE, TEXT, TREE formats
- [x] All enums are string enums (can be used as string values)

## Task 2: Environment variable helpers

### Acceptance Criteria
- [x] EnvVar enum defines environment variable names (MCP_TOOL_TIMEOUT, LLM_PROVIDER, etc.)
- [x] get_env(EnvVar) returns the environment variable value or None if not set
- [x] get_env(EnvVar, default) returns default when variable not set
- [x] set_env(EnvVar, value) sets the environment variable
- [x] unset_env(EnvVar) removes the environment variable
- [x] is_set(EnvVar) returns True if variable is set, False otherwise
- [x] get_env_int(EnvVar) returns integer value or None if not set/invalid
- [x] get_env_float(EnvVar) returns float value or None if not set/invalid
- [x] get_env_bool(EnvVar) returns boolean (True for "1", "true", "yes", "on")
- [x] get_env_list(EnvVar) returns comma-separated values as list

## Task 3: Configuration models with Pydantic

### Acceptance Criteria
- [x] TimeoutConfig model has fields for all timeout types with proper defaults
- [x] TimeoutConfig.get(TimeoutType) returns the timeout value by enum
- [x] TimeoutConfig is immutable (frozen=True)
- [x] ToolConfig model has include_tools, exclude_tools, confirm_tools, max_concurrency fields
- [x] ConfigOverride model captures CLI argument overrides (provider, model, api_base, etc.)
- [x] MCPConfig model can load from JSON file with server definitions
- [x] MCPConfig supports both sync and async loading
- [x] All config models have proper validation (e.g., timeouts must be positive)

## Task 4: Runtime configuration with override resolution

### Acceptance Criteria
- [ ] RuntimeConfig combines MCPConfig with ConfigOverride
- [ ] CLI overrides take precedence over file configuration
- [ ] Environment variable overrides are supported
- [ ] RuntimeConfig.provider returns resolved provider value
- [ ] RuntimeConfig.model returns resolved model value
- [ ] RuntimeConfig.get_timeout(TimeoutType) returns resolved timeout
- [ ] ResolvedValue tracks the source of each config value (CLI, ENV, FILE, DEFAULT)
- [ ] get_server_timeout returns server-specific timeout if set, else global
