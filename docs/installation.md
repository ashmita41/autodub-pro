# Installation Guide

This guide explains how to install AutoDub Pro and its dependencies.

## Prerequisites

Before installing AutoDub Pro, ensure you have the following:

1. **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
2. **FFmpeg** - Required for audio and video processing

### Installing FFmpeg

#### Windows
1. Download FFmpeg from [the official website](https://ffmpeg.org/download.html) or use a package manager like [Chocolatey](https://chocolatey.org/):
   ```
   choco install ffmpeg
   ```
2. Add FFmpeg to your system PATH.

#### macOS
Using Homebrew:
```
brew install ffmpeg
```

#### Linux
Using apt (Ubuntu/Debian):
```
sudo apt update
sudo apt install ffmpeg
```

Using dnf (Fedora):
```
sudo dnf install ffmpeg
```

## Installing AutoDub Pro

### Method 1: From PyPI (Recommended)

```bash
pip install autodub-pro
```

### Method 2: From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/autodub-pro.git
   cd autodub-pro
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Configuration

1. Copy the example environment file and configure your API keys:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your API keys:
   - AWS credentials (for speech-to-text)
   - OpenAI API key (for translation)
   - ElevenLabs API key (for voice generation)

For detailed API setup instructions, see the [API Keys Setup](api-keys.md) guide.

## Verifying Installation

After installation, you can verify that AutoDub Pro is working correctly:

```bash
autodub --version
```

Or run the application:

```bash
autodub
```

## Troubleshooting

If you encounter problems during installation, check the [Troubleshooting](troubleshooting.md) guide. 