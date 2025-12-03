# Simple Claude CLI Template

## Getting Started: Use This Template!

**This is a GitHub template repository** - you can create your own copy with one click!

### How to Create Your Own Repository:

1. **Click the "Use this template" button** at the top of this GitHub page (green button)
2. **Choose "Create a new repository"**
3. **Name your repository** (e.g., "my-hackathon-project")
4. **Choose Public or Private** (your choice!)
5. **Click "Create repository"**

🎉 **Done!** You now have your own copy of this template that you can customize!

### Next Steps:

Now that you have your own repository:
1. **Clone it to your computer**: `git clone <your-repo-url>`
2. **Follow the setup instructions below** to get Claude AI working
3. **Start customizing** for your hackathon project!

---

## 📦 Setup (5 minutes)

**Now that you have your own repository, let's get it running!**

### Step 1: Get Your API Key

1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up (As TCD Claude Builder, you have free API credits!)
3. Click "Get API Keys"
4. Copy your API key (it looks like: `sk-ant-...`)

### Step 2: Install Python (if you don't have it)

**Check if you have Python:**
```bash
python --version
```

If you see `Python 3.7` or higher, you're good! If not:
- **Windows**: Download from [python.org](https://python.org)
- **Mac**: `brew install python3` or download from [python.org](https://python.org)
- **Linux**: You're using Linux...You don't need this

### Step 3: Clone Your Repository

If you created your own repository using the template (recommended):

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

Or if you're just trying this out:

```bash
# Download as ZIP from GitHub and unzip it
# OR
git clone <this-template-url>
cd CLI-template
```

### Step 4: Install Required Libraries

```bash
pip install -r requirements.txt
```

This installs:
- `anthropic` - Claude API library
- `python-dotenv` - For managing your API key safely

### Step 5: Add Your API Key

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` in any text editor (Notepad, VS Code, etc.)

3. Replace `your_api_key_here` with your actual API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```

4. Save the file

**⚠️ IMPORTANT**: Never share your `.env` file or commit it to GitHub!

---

## 🎮 How to Use

### 1. Ask Claude a Question

```bash
python cli.py ask "What is the meaning of life?"
```

```bash
python cli.py ask "Explain quantum computing in simple terms"
```

### 2. Chat with Claude (Interactive Mode)

```bash
python cli.py chat
```

Then just type your messages! Type `quit` or `exit` to end the conversation.

Example conversation:
```
💬 Starting chat with Claude!
Type 'quit' or 'exit' to end the conversation
--------------------------------------------------

😊 You: Hi! Can you help me with my hackathon project?

🤖 Claude: Of course! I'd love to help with your hackathon project...

😊 You: I want to build a weather app

🤖 Claude: Great idea! Here's how you could approach it...

😊 You: quit

👋 Goodbye! Thanks for chatting!
```

### 3. Analyze a File

```bash
python cli.py analyze mycode.py
```

This sends the file contents to Claude and asks for an analysis!

### 4. Get Help

```bash
python cli.py help
```

---

## 🎨 Customization Ideas for Your Hackathon

Here are some easy ways to customize this for your project:

### 1. Change Claude's Personality

In `cli.py`, modify the `ask()` method to add a system prompt:

```python
# Make Claude a pirate
system_prompt = "You are a friendly pirate. Always talk like a pirate!"
answer = cli.ask("What is Python?", system_prompt=system_prompt)
```

### 2. Create Your Own Command

Add a new method to the `ClaudeCLI` class:

```python
def summarize(self, text):
    """Summarize any text"""
    question = f"Summarize this in 3 bullet points:\n\n{text}"
    return self.ask(question)
```

Then add it to the `main()` function:

```python
elif command == 'summarize':
    text = ' '.join(sys.argv[2:])
    result = cli.summarize(text)
    print(f"\n📝 Summary:\n{result}\n")
```

### 3. Build a Specific Tool

Some ideas:
- **Code Reviewer**: Analyze code and suggest improvements
- **Story Generator**: Create stories from prompts
- **Study Buddy**: Explain concepts and quiz you
- **Recipe Helper**: Suggest recipes from ingredients
- **Language Tutor**: Practice conversations in any language

### 4. Change the Model

In the `__init__` method, change this line:

```python
self.model = "claude-3-5-sonnet-20241022"  # Fast and smart

# Other options:
# self.model = "claude-3-5-haiku-20241022"  # Faster, cheaper
# self.model = "claude-3-opus-20240229"      # Most powerful
```

---

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Make sure you created the `.env` file (copy from `.env.example`)
- Check that your API key is correct
- Make sure there are no spaces around the `=` sign

### "Module not found" error
- Run `pip install -r requirements.txt` again
- Try `pip3` instead of `pip`
- Make sure you're in the right directory

### "Permission denied"
- On Mac/Linux, try: `chmod +x cli.py`
- Or just use: `python cli.py` instead of `./cli.py`

### Rate limit errors
- You're making too many requests
- Wait a few seconds between requests
- Check your API usage at [console.anthropic.com](https://console.anthropic.com/)

---

## 📚 Learn More

- **Claude API Docs**: [https://docs.anthropic.com/](https://docs.anthropic.com/)
- **Python Tutorial**: [https://docs.python.org/3/tutorial/](https://docs.python.org/3/tutorial/)
- **API Pricing**: [https://www.anthropic.com/pricing](https://www.anthropic.com/pricing)

## 💡 Hackathon Tips

1. **Start Simple**: Get the basic CLI working first, then add features
2. **Test Often**: Try your commands frequently to catch bugs early
3. **Ask Claude**: Use Claude itself to help you code! (`python cli.py ask "How do I add colors to terminal output?"`)
4. **Add Comments**: Help your teammates understand your code
5. **Have Fun**: Build something weird and creative!

## 📝 Project Structure

```
CLI-template/
├── cli.py              # Main file - all the code is here!
├── requirements.txt    # Python libraries needed
├── .env.example        # Template for API key
├── .env               # Your actual API key (never commit this!)
├── .gitignore         # Keeps secrets safe
└── README.md          # This file!
```
