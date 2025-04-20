# User Guide

This guide provides instructions on how to use AutoDub Pro effectively.

## Getting Started

### Launching the Application

After [installing](installation.md) AutoDub Pro, you can launch it:

```bash
autodub
```

### Interface Overview

The AutoDub Pro interface consists of:

1. **Main Toolbar** - Contains options for file operations, settings, and help
2. **Video Player** - For playback and preview of videos
3. **Subtitle Editor** - For viewing and editing subtitles
4. **Translation Panel** - For managing translations
5. **Voice Selection** - For choosing and customizing voice profiles
6. **Progress Panel** - Shows current processing status

## Basic Workflow

### 1. Loading a Video

1. Click **File → Open Video** or use the shortcut `Ctrl+O`
2. Select your video file from the file dialog
3. The video will load in the player, and if subtitles are embedded, they will appear in the subtitle editor

### 2. Working with Subtitles

#### Loading Subtitles
If your video doesn't have embedded subtitles, you can:
1. Click **File → Import Subtitles** (`Ctrl+I`)
2. Select a subtitle file (supports .srt, .vtt, .sub formats)

#### Generating Subtitles
To auto-generate subtitles:
1. Click **Tools → Generate Subtitles**
2. Select the source language
3. Wait for the speech recognition process to complete

#### Editing Subtitles
1. Click on any subtitle in the list to edit its text
2. Adjust timing using the start/end time controls
3. Add new subtitles with the **+** button
4. Remove subtitles with the **-** button

### 3. Translating Content

1. In the Translation Panel, select the target language
2. Click **Translate** to process all subtitles
3. Review and edit the translations as needed

### 4. Voice Selection

1. Choose a preset voice from the dropdown menu, or
2. Create a custom voice by clicking **Custom Voice**
3. Adjust voice parameters (speed, pitch, emphasis)
4. Preview the voice by clicking **Preview**

### 5. Generating Dubbed Audio

1. Click **Generate Dub** to start processing
2. The Progress Panel will show the status of each step
3. You can cancel the process at any time by clicking **Cancel**

### 6. Exporting the Result

When dubbing is complete:
1. Click **File → Export** (`Ctrl+E`)
2. Choose your preferred export format:
   - **Video with Dubbed Audio**
   - **Dubbed Audio Only**
   - **Translated Subtitles**
3. Select destination and file name
4. Click **Export**

## Advanced Features

### Batch Processing

Process multiple videos at once:
1. Click **File → Batch Process**
2. Add videos to the queue
3. Configure settings for all videos
4. Click **Start Processing**

### Voice Profile Management

Save and reuse voice settings:
1. Configure a voice to your liking
2. Click **Save Profile**
3. Name your profile
4. Access saved profiles from the **Voice Profiles** dropdown

### Project Files

Save your work to continue later:
1. Click **File → Save Project** (`Ctrl+S`)
2. This saves all your settings, translations, and progress
3. Reopen with **File → Open Project** (`Ctrl+P`)

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Video | `Ctrl+O` |
| Import Subtitles | `Ctrl+I` |
| Save Project | `Ctrl+S` |
| Open Project | `Ctrl+P` |
| Export | `Ctrl+E` |
| Play/Pause Video | `Space` |
| Next Subtitle | `Down Arrow` |
| Previous Subtitle | `Up Arrow` |
| Jump Forward 5s | `Right Arrow` |
| Jump Backward 5s | `Left Arrow` |
| Help | `F1` |

## Tips and Best Practices

- For better translation quality, ensure original subtitles are accurate
- Preview voices before generating the full dub to save time
- Break long sentences in subtitles for more natural speech
- Use the batch processing feature for multiple episodes of a series
- Save voice profiles for consistency across projects 