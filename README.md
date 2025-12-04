# 🐉 AI Dungeon Master

A web-based D&D adventure game powered by Google's Gemini AI. Experience dynamic, AI-generated storytelling with persistent campaigns, randomized characters, and immersive settings.

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)
![Gemini](https://img.shields.io/badge/Gemini-AI-4285F4?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## 🏆 Hackathon Winner

This project was built at the [**Claude Builder Club @ TCD Hackathon**](https://cbc-at-trinity-hackathon.devpost.com/) (December 2025) and won:

- 🥇 **Best Team Collaboration**
- 🎨 **Most Creative Use of Claude**

---

## ✨ Features

- **AI-Powered Dungeon Master** — Dynamic storytelling that adapts to your choices
- **Randomized Adventures** — Each reset generates new characters, settings, and themes
- **Persistent Campaigns** — Your progress is automatically saved
- **Multiple Themes** — Medieval Fantasy, Steampunk, Sci-Fi, Post-Apocalyptic, and more
- **Character Variety** — Random races (Human, Elf, Dwarf, Orc) and classes (Warrior, Mage, Rogue, Engineer, Cleric)
- **Dark/Light Mode** — Toggle between themes for comfortable play
- **CLI & Web Modes** — Play in your terminal or browser

## 📋 Prerequisites

- Python 3.12 or higher
- Node.js 18+ and npm
- Google Gemini API key

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Cillian-Cooke/hackathon.git
cd hackathon
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add your Gemini API key to the `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> **📝 Getting a Gemini API Key:**
> 1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
> 2. Sign in with your Google account
> 3. Click "Create API Key"
> 4. Copy the key and paste it in your `.env` file

### 3. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd my-react-app
npm install
```

## 🎮 Running the Game

### Web Mode (Recommended)

Start both the backend server and frontend in separate terminals:

**Terminal 1 — Backend:**
```bash
source venv/bin/activate  # If not already activated
uvicorn server:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd my-react-app
npm run dev
```

Open your browser to `http://localhost:5173`

### CLI Mode

For a terminal-based experience:

```bash
source venv/bin/activate
python cli.py
```

## 🎯 How to Play

1. **Start** — The AI Dungeon Master sets the scene
2. **Type Actions** — Enter what your character does (e.g., "I search the room", "Attack the goblin")
3. **Special Commands:**
   - `📖 Summary of Story` — Get a recap of your adventure
   - `👤 Player Status` — View your character's stats and abilities
   - `🔥 Reset Campaign` — Start a completely new adventure

## 🏗️ Project Structure

```
hackathon/
├── my-react-app/       # Node Modules and React Deps
│   └── src/ 
│       └── main.jsx    # React application entry
├── cli.py              # CLI game engine & DM logic
├── server.py           # FastAPI backend server
├── style.css           # Application styles
├── index.html          # HTML entry point
├── .env                # Environment variables (create this)
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
├── package.json        # Node dependencies
└── README.md           # This file
```

## 📦 Dependencies

### Python
- `fastapi` — Web framework for the API
- `uvicorn` — ASGI server
- `google-genai` — Gemini AI SDK
- `python-dotenv` — Environment variable management
- `pydantic` — Data validation

### Frontend
- `react` — UI framework
- `react-icons` — Icon components
- `vite` — Build tool and dev server

## 🔧 Configuration

The game can be customized by modifying constants in `cli.py`:

| Setting | Description | Default |
|---------|-------------|---------|
| `GEMINI_MODEL` | AI model to use | `gemini-2.5-flash` |
| `TOTAL_STAT_POINTS` | Points for character stats | `30` |
| `max_output_tokens` | Response length limit | `2048` |

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Claude Builder Club @ TCD](https://www.instagram.com/cbcattrinity/) for hosting the hackathon
- [Google Gemini](https://deepmind.google/technologies/gemini/) for the AI capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent Python web framework
- [Vite](https://vitejs.dev/) for the blazing fast frontend tooling

---

<p align="center">
  Made with ❤️ at the Claude Builder Club @ TCD Hackathon
</p>
