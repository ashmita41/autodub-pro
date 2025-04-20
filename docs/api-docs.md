# API Documentation

This document provides detailed information about the APIs used in AutoDub Pro and how to integrate with them.

## Overview

AutoDub Pro offers several ways to interact with its functionality programmatically:

1. **Internal Python API** - Use AutoDub Pro's modules in your Python code
2. **Command Line Interface (CLI)** - Automate dubbing tasks from shell scripts
3. **Third-party Service Integration** - Configure external AI services

## Internal Python API

### Core Modules

```python
from autodub_pro.subtitle import SubtitleProcessor
from autodub_pro.audio import AudioProcessor
from autodub_pro.video import VideoProcessor
from autodub_pro.translation import Translator
```

### SubtitleProcessor

The `SubtitleProcessor` class handles subtitle extraction, parsing, and generation.

```python
subtitle_processor = SubtitleProcessor()

# Load subtitles from a file
subtitles = subtitle_processor.load_from_file("input.srt")

# Generate subtitles from audio
subtitles = subtitle_processor.generate_from_audio("audio.mp3", language="en")

# Save subtitles to a file
subtitle_processor.save_to_file(subtitles, "output.srt")
```

#### Key Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `load_from_file(path)` | Load subtitles from a file | `path`: Path to subtitle file |
| `generate_from_audio(audio_path, language)` | Generate subtitles from audio | `audio_path`: Path to audio file, `language`: Language code |
| `save_to_file(subtitles, path)` | Save subtitles to a file | `subtitles`: Subtitle object, `path`: Output path |
| `extract_from_video(video_path)` | Extract embedded subtitles | `video_path`: Path to video file |

### AudioProcessor

The `AudioProcessor` class handles audio extraction, processing, and synthesis.

```python
audio_processor = AudioProcessor()

# Generate speech from text
audio_processor.generate_speech("Hello world", voice_id="default", output_path="output.mp3")

# Extract audio from video
audio_processor.extract_from_video("input.mp4", "output.mp3")

# Merge audio tracks
audio_processor.merge_tracks(["background.mp3", "speech.mp3"], "output.mp3")
```

#### Key Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `generate_speech(text, voice_id, output_path)` | Generate speech audio | `text`: Text to convert, `voice_id`: Voice to use, `output_path`: Output file |
| `extract_from_video(video_path, output_path)` | Extract audio from video | `video_path`: Input video, `output_path`: Output audio |
| `merge_tracks(tracks, output_path)` | Merge multiple audio tracks | `tracks`: List of audio files, `output_path`: Output file |

### VideoProcessor

The `VideoProcessor` class handles video loading, processing, and export.

```python
video_processor = VideoProcessor()

# Load a video
video = video_processor.load("input.mp4")

# Replace audio track
video_processor.replace_audio(video, "dubbed_audio.mp3")

# Export final video
video_processor.export(video, "output.mp4", format="mp4")
```

#### Key Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `load(path)` | Load a video file | `path`: Path to video file |
| `replace_audio(video, audio_path)` | Replace video's audio | `video`: Video object, `audio_path`: New audio |
| `export(video, output_path, format)` | Export processed video | `video`: Video object, `output_path`: Output path, `format`: Output format |

### Translator

The `Translator` class handles text translation between languages.

```python
translator = Translator(provider="openai")

# Translate text
translated = translator.translate("Hello world", source_lang="en", target_lang="es")

# Translate subtitles
translated_subs = translator.translate_subtitles(subtitles, target_lang="fr")
```

#### Key Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `translate(text, source_lang, target_lang)` | Translate text | `text`: Source text, `source_lang`: Source language, `target_lang`: Target language |
| `translate_subtitles(subtitles, target_lang)` | Translate subtitles | `subtitles`: Subtitle object, `target_lang`: Target language |

## Command Line Interface (CLI)

AutoDub Pro can be used from the command line for automation and batch processing.

### Basic Usage

```bash
# Display help
autodub --help

# Process a single video
autodub process --input video.mp4 --output dubbed.mp4 --target-lang es

# Batch process multiple videos
autodub batch --input-dir ./videos --output-dir ./dubbed --target-lang fr
```

### Key Commands

| Command | Description | Options |
|---------|-------------|---------|
| `process` | Process a single video | `--input`, `--output`, `--target-lang`, `--voice-id` |
| `batch` | Process multiple videos | `--input-dir`, `--output-dir`, `--target-lang` |
| `extract-subtitles` | Extract subtitles only | `--input`, `--output`, `--format` |
| `translate-subtitles` | Translate subtitles | `--input`, `--output`, `--target-lang` |

## Third-party Service Integration

AutoDub Pro integrates with several external APIs for various functionalities.

### Required API Services

#### Speech Recognition APIs

Configure in `.env` file:

```
# AWS Transcribe
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1

# Alternative: Google Speech-to-Text
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

#### Translation APIs

Configure in `.env` file:

```
# OpenAI (GPT)
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4

# Alternative: Google Cloud Translation
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

#### Text-to-Speech APIs

Configure in `.env` file:

```
# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=default_voice_id

# Alternative: AWS Polly
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
```

### API Fallback Chain

AutoDub Pro implements a fallback chain for each service category. If the primary service fails, it will attempt to use the next configured service in the chain.

Configure service priorities in `.env`:

```
SPEECH_RECOGNITION_SERVICES=aws,google,local
TRANSLATION_SERVICES=openai,google,azure
TTS_SERVICES=elevenlabs,aws,google
```

## Advanced Integration

### Webhooks

AutoDub Pro can trigger webhooks on process completion:

```python
from autodub_pro import AutoDubProcessor

processor = AutoDubProcessor()
processor.set_webhook_url("https://your-server.com/webhook")
processor.process_video("input.mp4", "output.mp4", target_lang="es")
```

### Custom Voice Models

You can use custom voice models by providing the model path:

```python
from autodub_pro.audio import VoiceModel

# Load a custom model
voice_model = VoiceModel.load_from_file("custom_voice.model")

# Use in audio processing
audio_processor = AudioProcessor()
audio_processor.set_voice_model(voice_model)
audio_processor.generate_speech("Hello world", output_path="output.mp3")
```

## Error Handling

All API methods raise specific exceptions that can be caught and handled:

```python
from autodub_pro.exceptions import SubtitleError, AudioError, VideoError, TranslationError

try:
    subtitle_processor.load_from_file("non_existent.srt")
except SubtitleError as e:
    print(f"Subtitle error: {e}")
```

## Rate Limiting and Quotas

When using external APIs, be aware of rate limits and quotas. You can configure throttling behavior:

```python
from autodub_pro import config

# Set rate limits for API calls
config.set_rate_limit("openai", max_requests=60, per_minute=True)
config.set_rate_limit("elevenlabs", max_requests=30, per_minute=True)
```

## Further Resources

- [API Examples Repository](https://github.com/yourusername/autodub-pro-examples)
- [API Changelog](./api-changelog.md)
- [Service Provider Documentation](#third-party-service-integration) 