# Troubleshooting Guide

This guide provides solutions to common issues you might encounter while using AutoDub Pro.

## Installation Issues

### Application Won't Install

- **Error: "Missing dependencies"**
  - Make sure your system meets the minimum requirements
  - Install any missing system dependencies mentioned in the error message
  - For Windows: Update Visual C++ Redistributable packages
  - For macOS: Install Rosetta 2 if using an M1/M2 Mac

- **Error: "Permission denied"**
  - Run the installer as Administrator (Windows) or with sudo (Linux)
  - Check if your antivirus is blocking the installation
  - Verify you have sufficient disk space

### Crashes on Startup

- **Application immediately closes**
  - Check system logs for error details
  - Reinstall the application
  - Update your graphics drivers
  - Disable hardware acceleration in settings

- **Stuck on loading screen**
  - Clear the application cache: `%AppData%\AutoDubPro\cache` (Windows) or `~/Library/Application Support/AutoDubPro/cache` (macOS)
  - Verify your internet connection if initial setup requires online verification
  - Run in compatibility mode if using older operating systems

## API Connection Problems

### API Keys Not Working

- **Authentication errors**
  - Verify you've entered the correct API keys
  - Check if your API subscription is active
  - Ensure your account has sufficient credit/quota
  - Check if the API service is experiencing downtime

- **Connection timeout**
  - Check your internet connection
  - Verify your firewall isn't blocking the application
  - Try a different network connection
  - Contact support if persistent

## Video Import Issues

### Video Won't Import

- **Unsupported format**
  - Convert your video to a supported format (MP4, AVI, MKV, MOV, WebM)
  - Use a converter like HandBrake or FFmpeg
  - Check if the video is corrupted

- **File too large**
  - Compress the video before importing
  - Split large videos into smaller segments
  - Upgrade to a higher tier plan for larger file support

### Poor Quality After Import

- **Video appears pixelated**
  - Check your original video quality
  - Ensure you haven't enabled any compression during import
  - Verify display settings in preferences

## Subtitle Issues

### Auto-Generation Failures

- **No speech detected**
  - Ensure your video has clear audio
  - Check if the audio language is supported
  - Manually adjust audio levels if too quiet

- **Incorrect timestamps**
  - Manually adjust subtitle timing
  - Check for audio sync issues in the original video
  - Use the "Reset Timing" option and try again

### Import Problems

- **Subtitle file not recognized**
  - Verify the file format is supported (.SRT, .VTT, .SUB)
  - Check if the file is corrupted
  - Try converting to a different subtitle format

## Translation Problems

### Inaccurate Translations

- **Context errors**
  - Manually edit problematic translations
  - Try a different translation service if available
  - Break complex sentences into simpler ones

- **Technical terminology issues**
  - Add custom dictionaries in Settings > Translation > Custom Terms
  - Pre-translate technical terms manually

### Translation Timeout

- **Process takes too long**
  - Check your internet connection
  - Reduce the size of your project
  - Try translating in smaller batches
  - Verify API service status

## Voice Synthesis Issues

### Poor Voice Quality

- **Robotic or unnatural speech**
  - Try different voice models
  - Adjust speech parameters (pitch, speed, emphasis)
  - Break longer sentences into multiple segments
  - Check for punctuation issues in source text

- **Pronunciation errors**
  - Add pronunciation guides in Settings > Voice > Custom Pronunciation
  - Spell out problematic words phonetically
  - Use alternative wording when possible

### Processing Failures

- **Generation errors**
  - Check API quota limits
  - Verify voice service status
  - Reduce concurrent processing jobs
  - Update to the latest app version

## Export Problems

### Export Fails

- **Process interruption**
  - Check available disk space
  - Close other demanding applications
  - Try exporting at a lower quality
  - Export in smaller segments

- **Codec errors**
  - Install additional codecs if prompted
  - Try a different export format
  - Update the application to the latest version

### Audio Sync Issues

- **Dubbed audio out of sync**
  - Use "Fine-tune Sync" tools to adjust timing
  - Check if original video has variable frame rate
  - Export using constant frame rate option
  - Adjust global delay offset in export settings

## Performance Issues

### Application Running Slowly

- **High CPU/memory usage**
  - Close other applications
  - Reduce project complexity
  - Lower preview quality in settings
  - Check for system overheating

- **Processing takes too long**
  - Enable hardware acceleration if available
  - Upgrade hardware (SSD, more RAM)
  - Process shorter segments at a time
  - Use proxy files for editing

## Still Need Help?

If you're still experiencing issues:

1. **Check for updates**: Ensure you're using the latest version of AutoDub Pro
2. **Consult documentation**: Visit our [comprehensive documentation](https://autodubpro.com/docs)
3. **Community support**: Post your question on our [forum](https://community.autodubpro.com)
4. **Contact support**: Email us at support@autodubpro.com with:
   - Your system specifications
   - Detailed description of the issue
   - Screenshots/videos of the problem
   - Application logs (Help > Export Logs)
5. **Live chat**: Available for premium users through the application (Help > Live Support) 