# Kimi K2.5 Model Integration Issue Documentation

## Problem Summary
- **Issue**: API Error: 400 {"error":{"message":"thinking is enabled but reasoning_content is missing in assistant tool call message at index 4","type":"invalid_request_error"}}

## Root Cause Analysis

### Primary Issue
The Kimi K2.5 model requires specific message formatting that Claude Code's standard implementation wasn't providing.

### Technical Details
- Kimi's API requires assistant messages containing tool calls to include 'reasoning_content' field
- The error occurs because Kimi's API has specific requirements for message structure that differ from standard Anthropic API implementation

## Solution Implemented

### Environment Configuration
Set environment variables to properly configure Claude Code for Kimi:
```
export ENABLE_TOOL_SEARCH=false
```

This setting disables the tool search discovery step that Kimi's API doesn't support, which resolves the compatibility issue.

## Key Points About the Fix

### What This Fix Does NOT Do
- Does NOT remove Kimi's reasoning capabilities
- Does NOT affect model selection in Jan
- Does NOT impact Jan's core functionality
- Does NOT remove any model features

### What This Fix DOES
- Fixes the API compatibility issue between Claude Code and Kimi model
- Preserves all Kimi model capabilities while fixing message formatting
- Maintains full Jan integration functionality

The error you were encountering was due to the fact that the Kimi model requires specific message formatting that Claude Code wasn't providing by default. By setting the proper environment variables, the API compatibility issue is resolved while preserving all model capabilities.