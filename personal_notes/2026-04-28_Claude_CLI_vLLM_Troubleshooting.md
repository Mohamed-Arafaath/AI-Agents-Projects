# Claude CLI & vLLM Troubleshooting

## Issue: `claude --enable-auto-tool-choice` Fails / Tool Calling Disabled

When running the Claude CLI, you might encounter an error indicating that tool calling is disabled or the `--enable-auto-tool-choice` flag fails. 

**Root Cause:**
The error isn't coming from the `claude` CLI itself—it's actually coming from the backend server that your Claude CLI is connected to (which appears to be running vLLM to serve the model). When you run `claude`, it sends a request to your vLLM server to use tools. However, your vLLM server currently has tool-calling disabled. Because the `claude` CLI tool doesn't recognize those flags on its end, trying to run `claude --enable-auto-tool-choice` fails.

## How to Fix This

You need to restart your backend vLLM server (wherever the model is actually being hosted) and add specific flags to the server startup command, NOT the client command.

### 1. If starting vLLM via Terminal/CLI:
Add the following flags to your startup command:

```bash
python -m vllm.entrypoints.openai.api_server \
    --model <your-model-name> \
    --enable-auto-tool-choice \
    --tool-call-parser hermes # (or mistral, openai, pythonic depending on the model)
```

### 2. If running vLLM via Docker or a Cloud Host:
Add these environment variables to that server:

```bash
VLLM_ENABLE_AUTO_TOOL_CHOICE=true
VLLM_TOOL_CALL_PARSER=hermes
```

Once your backend server is restarted with those flags enabled, your normal `claude` CLI command (just running `claude` without any extra flags) will start working perfectly!
