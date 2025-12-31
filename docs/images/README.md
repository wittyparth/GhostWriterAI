# Demo Assets

This folder contains demo assets for the README and documentation.

## Required Images

To complete the README, add the following images:

### 1. `demo.gif` - Main Demo Animation
A GIF showing the CLI in action:
- Running `python -m src.cli.main`
- Entering an idea
- Answering questions
- Viewing the generated post

**Recording tips:**
- Use [Terminalizer](https://terminalizer.com/) or [asciinema](https://asciinema.org/)
- Keep it under 30 seconds
- Show the full flow

### 2. `architecture.png` - System Architecture
The architecture diagram (already in README as ASCII)

### 3. `api-docs.png` - API Documentation Screenshot
Screenshot of `/docs` endpoint showing Swagger UI

## How to Create Demo GIF

### Option 1: Using Terminalizer

```bash
npm install -g terminalizer
terminalizer record demo
# Run your demo commands
# Press Ctrl+D to stop
terminalizer render demo -o demo.gif
```

### Option 2: Using Windows Terminal + ScreenToGif

1. Install [ScreenToGif](https://www.screentogif.com/)
2. Record your terminal
3. Export as GIF

### Option 3: Using LICEcap

1. Download [LICEcap](https://www.cockos.com/licecap/)
2. Position over terminal
3. Record demo
