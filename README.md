# AutoDub Pro

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.9%2B-green)](https://doc.qt.io/qtforpython-6/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 📌 Overview

AutoDub Pro is a powerful automated video dubbing solution that transforms your videos for international audiences. Using cutting-edge AI technologies, the application streamlines the entire dubbing workflow from subtitle extraction to voice generation.

## 🚀 Key Features

- **Automatic Subtitle Extraction** - Extract subtitles from videos using AWS Transcribe
- **AI Translation & Refinement** - Translate and refine subtitles using OpenAI's GPT models
- **Natural Voice Generation** - Create lifelike voiceovers with ElevenLabs text-to-speech API
- **Subtitle Synchronization** - Fine-tune subtitle timings with the built-in editor
- **Video Preview & Export** - Preview and export your professionally dubbed videos
- **Google Drive Integration** - Seamlessly sync your projects with Google Drive

## 🛠️ Technologies

- **Python** - Core programming language
- **PySide6** - Modern Qt-based UI framework
- **AWS Transcribe** - Speech-to-text for subtitle extraction
- **OpenAI GPT** - AI translation and correction 
- **ElevenLabs** - State-of-the-art TTS for natural-sounding voiceovers
- **FFmpeg** - Audio and video processing

## 📋 Prerequisites

- Python 3.9 or higher
- FFmpeg installed and added to PATH
- AWS, OpenAI, and ElevenLabs API keys
- Google Drive API credentials (optional, for cloud sync)

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/autodub-pro.git
   cd autodub-pro
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Configure your API credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## 🚀 Usage

1. Start the application:
   ```bash
   python -m autodub_pro
   ```

2. Load a video file using the "Load Video" button

3. Extract subtitles using AWS Transcribe

4. Edit and refine subtitles as needed

5. Generate voiceovers with ElevenLabs

6. Export the dubbed video using the "Export" button

## ⚙️ Configuration

Configure API keys and default settings by editing the `.env` file:

```
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region

# OpenAI Credentials
OPENAI_API_KEY=your_openai_key

# ElevenLabs Credentials
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_default_voice_id

# Google Drive (optional)
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
```

## 🔍 Project Structure

```
autodub_pro/
├── autodub_pro/               # Main package
│   ├── __init__.py
│   ├── main.py                # Application entry point
│   ├── config.py              # Configuration management
│   ├── ui/                    # UI components
│   │   ├── __init__.py
│   │   ├── main_window.py     # Main application window
│   │   ├── video_player.py    # Video playback components
│   │   └── subtitle_editor.py # Subtitle editing interface
│   ├── services/              # External service integrations
│   │   ├── __init__.py
│   │   ├── aws.py             # AWS Transcribe integration
│   │   ├── openai_service.py  # OpenAI integration
│   │   ├── elevenlabs.py      # ElevenLabs TTS integration
│   │   └── gdrive.py          # Google Drive integration
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── subtitle.py        # Subtitle processing utilities
│   │   ├── audio.py           # Audio processing 
│   │   └── video.py           # Video editing & export
│   └── utils/                 # Helper utilities
│       ├── __init__.py
│       └── helpers.py         # Common utility functions
├── assets/                    # Static assets
│   └── icons/
├── data/                      # Local data storage
├── tests/                     # Unit tests
├── docs/                      # Documentation
├── .env.example               # Environment variables template
├── setup.py                   # Installation script
├── requirements.txt           # Dependencies
├── LICENSE                    # License file
└── README.md                  # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [FFmpeg](https://ffmpeg.org/) - The powerful multimedia framework
- [AWS Transcribe](https://aws.amazon.com/transcribe/) - For speech-to-text capabilities
- [OpenAI](https://openai.com/) - For AI translation capabilities
- [ElevenLabs](https://elevenlabs.io/) - For the realistic text-to-speech API
- [Qt for Python (PySide6)](https://www.qt.io/qt-for-python) - For the GUI framework
