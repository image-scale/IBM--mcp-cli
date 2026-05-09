# Acceptance Criteria

## Task 1: Configuration defaults and enums

### Acceptance Criteria
- [ ] DEFAULT_TOOL_EXECUTION_TIMEOUT equals 120.0 seconds
- [ ] DEFAULT_SERVER_INIT_TIMEOUT equals 120.0 seconds
- [ ] DEFAULT_STREAMING_CHUNK_TIMEOUT equals 45.0 seconds
- [ ] DEFAULT_PROVIDER equals "openai"
- [ ] DEFAULT_MODEL equals "gpt-4o-mini"
- [ ] DEFAULT_THEME equals "default"
- [ ] TimeoutType enum has values for streaming, tool, server, and HTTP timeouts
- [ ] TokenBackend enum includes AUTO, KEYCHAIN, WINDOWS, ENCRYPTED, VAULT options
- [ ] ServerStatus enum includes CONFIGURED, CONNECTED, DISCONNECTED, ERROR states
- [ ] ConfigSource enum has CLI, ENV, FILE, DEFAULT priority values
- [ ] ConversationAction enum has SHOW, CLEAR, SAVE, LOAD actions
- [ ] TokenAction enum includes LIST, SET, GET, DELETE, CLEAR actions
- [ ] OutputFormat enum has JSON, TABLE, TEXT, TREE formats
- [ ] All enums are string enums (can be used as string values)
