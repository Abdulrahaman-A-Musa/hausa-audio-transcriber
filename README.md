# 🎤 Hausa Audio Transcriber

A powerful Streamlit web application for transcribing Hausa audio recordings with automatic English translation and speaker identification.

## 🌟 Features

- **🎯 Automatic Hausa Transcription** - Uses Google Speech Recognition API
- **🌐 English Translation** - Real-time translation of transcribed text
- **👥 Speaker Identification** - Automatically separates Interviewer questions from Respondent answers
- **⏱️ Timestamped Output** - Track when each segment was spoken
- **📦 Batch Processing** - Upload and process up to 10 audio files at once
- **📥 CSV Export** - Download results in structured CSV format
- **🎵 Multiple Formats** - Supports WAV, MP3, M4A, AMR, AAC, 3GP, and more

## 🚀 Live Demo

[Try the app here](https://your-app-url.streamlit.app) *(Update with your actual URL after deployment)*

## 📋 Use Cases

Perfect for:
- Survey interviews transcription
- Research data collection
- Healthcare surveys (mortality, reproductive health)
- Field research documentation
- Quality control and verification

## 🛠️ Technologies Used

- **Python 3.11+**
- **Streamlit** - Web framework
- **Google Speech Recognition** - Transcription engine
- **Google Translate** - Translation service
- **FFmpeg** - Audio format conversion
- **Pandas** - Data processing

## 📊 Output Formats

### 1. Timestamped Transcript
```
AUDIO MINUTE        | ROLE              | TRANSCRIBED VERSION
00:00 - 01:00 min   | ❓ INTERVIEWER    | Q36. How many household members...
01:00 - 02:00 min   | 💭 RESPONDENT     | Three people
```

### 2. English Translation
```
AUDIO MINUTE        | ROLE              | TRANSLATED VERSION
00:00 - 01:00 min   | ❓ INTERVIEWER    | Q36. How many household members...
01:00 - 02:00 min   | 💭 RESPONDENT     | Three people
```

### 3. CSV Export
All results can be downloaded as CSV files for easy import into Excel or databases.

## 🎯 Installation

### Prerequisites
- Python 3.11 or higher
- FFmpeg (for audio conversion)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/hausa-transcriber.git
cd hausa-transcriber
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run hausa_wav_only.py
```

4. Open your browser to `http://localhost:8501`

## 📦 Deployment

### Streamlit Community Cloud (Recommended)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy with one click!

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## 📖 Usage

1. **Upload Audio Files** - Select 1-10 audio files (MP3, WAV, M4A, AMR, etc.)
2. **Choose Display Options** - Select which views to show
3. **Click Transcribe** - Process all files automatically
4. **View Results** - See timestamped transcripts with speaker roles
5. **Download** - Export results as CSV

## 🎨 Features in Detail

### Speaker Detection
The app automatically identifies speakers:
- **❓ INTERVIEWER** - Detects survey questions (Q1, Q36, "how many", "menene", etc.)
- **💭 RESPONDENT** - Identifies answers and responses

### Batch Processing
- Upload up to 10 files at once
- Progress tracking for each file
- Continues processing even if one file fails

### Audio Format Support
- **Native Support**: WAV, FLAC, OGG
- **With FFmpeg**: MP3, M4A, AMR, AAC, 3GP, WMA, WebM

## 🔧 Configuration

### Display Options
- Toggle timestamped transcript (with ROLE)
- Toggle English translation (with ROLE)
- Customizable output formats

### Audio Processing
- 60-second chunks for optimal processing
- Ambient noise reduction
- Dynamic energy threshold for quiet voices

## 📊 Technical Specifications

- **Chunk Duration**: 60 seconds
- **Energy Threshold**: 300 (sensitive to quiet voices)
- **Pause Threshold**: 0.8 seconds
- **Max File Size**: 200MB per file
- **Max Files**: 10 files per batch

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Abdulrahaman Musa**
- Data Scientist | Survey Research Specialist
- Built with ❤️ for Hausa Language Speakers

## 🙏 Acknowledgments

- Google Speech Recognition API
- Streamlit Community
- FFmpeg Team
- Hausa language speakers and researchers

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Contact: [your-email@example.com]

## 🎯 Roadmap

- [ ] Add more language support
- [ ] Improve speaker diarization
- [ ] Add audio quality enhancement
- [ ] Export to more formats (JSON, Excel)
- [ ] Advanced filtering options

---

**Built for accurate transcription of survey interviews in Hausa language with English translation and speaker identification.**

© 2026 Abdulrahaman Musa | Mortality Survey Transcription Tool
