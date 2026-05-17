# Freepik Image Generation Setup

This guide documents how to use the Freepik Flux Pro v1.1 API for high-quality image generation in this workspace.

## API Configuration

The API uses the **Freepik Flux Pro v1.1** model.

- **Endpoint**: `https://api.freepik.com/v1/ai/text-to-image/flux-pro-v1-1`
- **Authentication**: `x-freepik-api-key` header.
- **Key Location**: Stored in `.env` as `FREEPIK_API_KEY`.

## Usage via CLI Script

A custom Node.js script has been created to handle the image generation process (Request -> Polling -> Downloading).

### Command
```bash
node scripts/freepik_image_gen.js "Your image prompt here" filename.png
```

## Setup Details
1. **API Key**: The key is retrieved from the project's `.env` file.
2. **Polling**: The script polls the Freepik API until the image is ready.
3. **Storage**: Images are saved directly to the project directory.

## Troubleshooting
- If you get a 401, check that the `FREEPIK_API_KEY` in `.env` is correct.
- If the task remains in `CREATED` or `PENDING` for too long, check the Freepik dashboard for service status.
