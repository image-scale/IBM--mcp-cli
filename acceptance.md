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
- [x] RuntimeConfig combines MCPConfig with ConfigOverride
- [x] CLI overrides take precedence over file configuration
- [x] Environment variable overrides are supported
- [x] RuntimeConfig.provider returns resolved provider value
- [x] RuntimeConfig.model returns resolved model value
- [x] RuntimeConfig.get_timeout(TimeoutType) returns resolved timeout
- [x] ResolvedValue tracks the source of each config value (CLI, ENV, FILE, DEFAULT)
- [x] get_server_timeout returns server-specific timeout if set, else global

## Task 5: Tool and server data models

### Acceptance Criteria
- [x] ToolInfo model has name, namespace, description, parameters fields
- [x] ToolInfo.fully_qualified_name returns "namespace.name" format
- [x] ToolInfo.to_llm_format() converts to OpenAI function calling format
- [x] ServerInfo model has id, name, status, tool_count, capabilities fields
- [x] ServerInfo.is_healthy checks status and connected state
- [x] ToolCallResult model tracks success, result, error, execution_time
- [x] ConversationMessage model supports user, assistant, system, tool roles
- [x] ValidationResult model has is_valid, error_message, warnings fields

## Task 6: Command base classes and registry

### Acceptance Criteria
- [x] CommandMode flag enum has CHAT, CLI, INTERACTIVE, ALL values
- [x] CommandParameter model defines name, type, default, required, help fields
- [x] CommandResult model has success, output, data, error, should_exit fields
- [x] UnifiedCommand abstract base class defines name, description, execute method
- [x] UnifiedCommand has aliases, modes, parameters, and hidden properties
- [x] CommandRegistry can register and lookup commands by name or alias
- [x] CommandRegistry.get_commands_for_mode filters by CommandMode
- [x] Commands can validate their parameters before execution
