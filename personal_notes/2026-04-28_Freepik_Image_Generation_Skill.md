# Freepik API Image Generation Skill

## Overview
This skill enables AI agents to generate images using the Freepik API's Flux Pro v1.1 model.

## Setup Instructions

### 1. API Key Configuration
The Freepik API key is already stored in the project's `.env` file:
```
FREEPIK_API_KEY=FPSX085db71e358da992e9ecca7c74725864
```

### 2. Usage
To use this skill, agents can call the Freepik API to generate images from text prompts.

### 3. API Endpoint
```
POST https://api.freepik.com/v1/ai/text-to-image/flux-pro-v1-1
```

### 4. Request Format
```json
{
  "prompt": "string",
  "prompt_upsampling": false,
  "seed": 123,
  "aspect_ratio": "square_1_1",
  "safety_tolerance": 2,
  "output_format": "jpeg"
}
```

### 5. Response Format
```json
{
  "data": {
    "task_id": "046b6c7f-0b8a-43b9-b35d-6489e6daee91",
    "status": "CREATED"
  }
}
```

## Implementation Example

### Python Implementation
```python
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_image(prompt, aspect_ratio="square_1_1", safety_tolerance=2):
    url = "https://api.freepik.com/v1/ai/text-to-image/flux-pro-v1-1"
    
    headers = {
        "x-freepik-api-key": os.getenv("FREEPIK_API_KEY"),
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "prompt_upsampling": False,
        "aspect_ratio": aspect_ratio,
        "safety_tolerance": safety_tolerance,
        "output_format": "jpeg"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Example usage
result = generate_image("A beautiful landscape with mountains and a lake")
print(result)
```

## Parameters

### Required
- `prompt` (string): The text prompt for image generation

### Optional
- `prompt_upsampling` (boolean): Whether to perform upsampling on the prompt (default: false)
- `seed` (integer): Optional seed for reproducibility
- `aspect_ratio` (string): Image aspect ratio. Options: 
  - square_1_1
  - classic_4_3
  - traditional_3_4
  - widescreen_16_9
  - social_story_9_16
  - standard_3_2
  - portrait_2_3
  - horizontal_2_1
  - vertical_1_2
  - social_post_4_5
  - (default: square_1_1)
- `safety_tolerance` (integer): Tolerance level for input/output moderation (0-6, default: 2)
- `output_format` (string): Format of output image. Options: jpeg, png
- `webhook_url` (string): Optional callback URL for asynchronous notifications

## Response Handling
The API returns a task ID which can be used to check the status of the image generation:

```json
{
  "data": {
    "task_id": "046b6c7f-0b8a-43b9-b35d-6489e6daee91",
    "status": "CREATED"
  }
}
```

## Error Handling
Common error responses:
- 401: Invalid API key
- 400: Invalid request parameters
- 429: Rate limiting
- 500: Server errors

## Best Practices

1. Always check the .env file for the API key before making requests
2. Handle rate limiting with exponential backoff
3. Validate prompts for safety before sending to the API
4. Store generated image task IDs for later retrieval
5. Implement proper error handling for failed requests
6. Cache successful image generations when possible

## Example Agent Integration

```python
class FreepikImageGenerator:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("FREEPIK_API_KEY")
        if not self.api_key:
            raise ValueError("FREEPIK_API_KEY not found in environment variables")
    
    def generate_image(self, prompt, **kwargs):
        url = "https://api.freepik.com/v1/ai/text-to-image/flux-pro-v1-1"
        
        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            **kwargs
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
```

This documentation should be updated in the personal notes directory with the implementation details for using the Freepik API for image generation.