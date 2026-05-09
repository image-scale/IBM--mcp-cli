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
- [ ] EnvVar enum defines environment variable names (MCP_TOOL_TIMEOUT, LLM_PROVIDER, etc.)
- [ ] get_env(EnvVar) returns the environment variable value or None if not set
- [ ] get_env(EnvVar, default) returns default when variable not set
- [ ] set_env(EnvVar, value) sets the environment variable
- [ ] unset_env(EnvVar) removes the environment variable
- [ ] is_set(EnvVar) returns True if variable is set, False otherwise
- [ ] get_env_int(EnvVar) returns integer value or None if not set/invalid
- [ ] get_env_float(EnvVar) returns float value or None if not set/invalid
- [ ] get_env_bool(EnvVar) returns boolean (True for "1", "true", "yes", "on")
- [ ] get_env_list(EnvVar) returns comma-separated values as list
