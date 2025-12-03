# ⚡ Quick Start (3 Minutes!)

**For complete beginners at the hackathon** - follow these steps exactly!

## 🎯 Goal
Get Claude AI working in your terminal in 3 minutes!

---

## Step-by-Step Setup

### 1️⃣ Get Your API Key (1 minute)

1. Open your browser and go to: **https://console.anthropic.com/**
2. Click **"Sign Up"** (you can use Google/GitHub)
3. Once logged in, click **"Get API Keys"** or **"API Keys"** in the menu
4. Click **"Create Key"**
5. Copy the key (it starts with `sk-ant-`)

**💰 Cost**: Free trial includes $5 credit - plenty for the hackathon!

---

### 2️⃣ Setup the Project (1 minute)

Open your terminal and run these commands:

```bash
# Go to the project folder
cd CLI-template

# Install the required libraries
pip install -r requirements.txt
```

**Note**: If `pip` doesn't work, try `pip3` instead:
```bash
pip3 install -r requirements.txt
```

---

### 3️⃣ Add Your API Key (30 seconds)

```bash
# Create your .env file
cp .env.example .env
```

Now edit the `.env` file:
- **Windows**: Open with Notepad
- **Mac**: `open .env` or use TextEdit
- **Linux**: `nano .env` or any text editor

Replace `your_api_key_here` with your actual API key:

**Before:**
```
ANTHROPIC_API_KEY=your_api_key_here
```

**After:**
```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

Save the file!

---

### 4️⃣ Test It! (30 seconds)

```bash
python cli.py ask "Say hello!"
```

**You should see:**
```
🤔 Asking Claude: Say hello!

🤖 Claude says:
Hello! How can I help you today?
```

---

## ✅ Success! Now What?

### Try These Commands:

**Ask a question:**
```bash
python cli.py ask "What's Python?"
```

**Start a chat:**
```bash
python cli.py chat
```

**Analyze a file:**
```bash
python cli.py analyze sample.txt
```

---

## 🆘 Something Went Wrong?

### Error: "ANTHROPIC_API_KEY not found"
- Make sure you created the `.env` file (not `.env.example`)
- Check that your API key is pasted correctly
- No spaces around the `=` sign!

### Error: "No module named 'anthropic'"
- Run `pip install -r requirements.txt` again
- Make sure you're in the CLI-template folder

### Error: "python: command not found"
- Try `python3` instead of `python`
- You might need to install Python: https://python.org

### Error: "API key invalid"
- Go back to console.anthropic.com
- Generate a new API key
- Replace it in your `.env` file

---

## 🎨 Now Customize It!

Open `cli.py` in your favorite editor and start building!

**Ideas:**
- Change line 32 to use a different AI model
- Add your own commands (see `examples.md`)
- Make Claude a pirate, teacher, or comedian
- Build something unique for the hackathon!

---

## 📚 Next Steps

1. Read `README.md` for detailed documentation
2. Check `examples.md` for project ideas
3. Start building your hackathon project!
4. Ask Claude for help: `python cli.py ask "How do I..."`

---

## 🚀 You're Ready!

You now have a working AI CLI! Go build something awesome!

**Questions?** Read the main README.md or ask Claude itself for help!

**Good luck at the hackathon!** 🎉
