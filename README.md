# RoverNet AI Interface

RoverNet is a versatile AI interface that supports multiple AI modes:
- Local AI: Uses local models via llama.cpp
- OpenAI: Direct integration with OpenAI's GPT models
- Penphin: A bicameral AI system combining logical and creative thinking

## Features

- Multiple AI modes with different capabilities
- Local text-to-speech and speech recognition
- Configurable system messages and parameters
- Resource monitoring and management
- Beautiful terminal interface with progress indicators

## Prerequisites

- Python 3.8+
- llama.cpp (for local models)
- espeak-ng (for TTS)
- aplay (for audio playback)
- OpenAI API key (for OpenAI and Penphin modes)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/CodeMusic/rovernet.git
cd rovernet
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY='your-api-key'
```

4. Configure RoverNet:
Edit `config/rovernet.yaml` to set your preferences for:
- Model paths
- Audio settings
- Resource limits
- System messages

## Usage

Run RoverNet:
```bash
./bin/rovernet
```

Choose from the available modes:
1. Local AI Mode
2. OpenAI Mode
3. Penphin Mode (Bicameral)
4. Exit

## Penphin Mode

The Penphin mode uses a bicameral AI system:
- Dolphin: Logical agent using TinyLlama
- Penguin: Creative agent using MythoMax
- Synthesis: Combines both perspectives using GPT-4

## Configuration

The `config/rovernet.yaml` file contains all configurable settings:
- Environment variables
- Audio settings
- Resource management
- AI mode configurations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
