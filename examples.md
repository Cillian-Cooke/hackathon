# 💡 Example Use Cases & Ideas

Here are some fun ways to use your Claude CLI at the hackathon!

## 🎯 Quick Examples to Try

### 1. Get Help with Your Code
```bash
python cli.py ask "What's wrong with this code: def hello() print('hi')"
```

### 2. Learn New Concepts
```bash
python cli.py ask "Explain APIs like I'm 5 years old"
```

### 3. Generate Ideas
```bash
python cli.py ask "Give me 5 unique hackathon project ideas using AI"
```

### 4. Debug Errors
```bash
python cli.py ask "I'm getting 'TypeError: 'str' object is not callable'. What does this mean?"
```

### 5. Get Code Snippets
```bash
python cli.py ask "Show me Python code to read a CSV file"
```

---

## 🚀 Hackathon Project Ideas

### 1. Code Review Bot
Help beginners learn by reviewing their code!

**How to build:**
- Read code file with `analyze_file()`
- Ask Claude to review it
- Show suggestions for improvement

**Example command:**
```bash
python cli.py analyze mycode.py
```

### 2. Study Buddy
Quiz yourself on any topic!

**How to build:**
- Add a `quiz` command
- Ask Claude to generate questions
- Check answers and give feedback

**Example:**
```bash
python cli.py quiz "Python basics"
```

### 3. Story Generator
Create stories from prompts!

**How to build:**
- Add a `story` command
- Send creative writing prompts to Claude
- Save output to file

**Example:**
```bash
python cli.py story "A robot who learns to paint"
```

### 4. Translation Tool
Translate text or code comments!

**How to build:**
- Add a `translate` command
- Specify source and target language
- Use Claude for natural translation

**Example:**
```bash
python cli.py translate "Hello world" --to spanish
```

### 5. Recipe Helper
Get recipes from ingredients!

**How to build:**
- Add a `recipe` command
- List available ingredients
- Claude suggests recipes

**Example:**
```bash
python cli.py recipe "chicken, rice, tomatoes"
```

### 6. Commit Message Writer
Generate good git commit messages!

**How to build:**
- Read `git diff` output
- Ask Claude to write a commit message
- Copy to clipboard

**Example:**
```bash
python cli.py commit
```

---

## 🎨 Customization Examples

### Example 1: Make Claude a Teacher

```python
def teach(self, topic):
    """Teach a topic step by step"""
    system_prompt = """You are a patient teacher who explains things clearly.
    Use simple language and lots of examples. Break complex topics into small steps."""

    question = f"Teach me about {topic}. Start with the basics."
    return self.ask(question, system_prompt)
```

### Example 2: Code Explainer

```python
def explain_code(self, code):
    """Explain what code does line by line"""
    question = f"""Explain this code line by line in simple terms:

{code}

Format:
Line 1: [explanation]
Line 2: [explanation]
etc.
"""
    return self.ask(question)
```

### Example 3: Interview Prep

```python
def interview_practice(self, topic):
    """Practice interview questions"""
    system_prompt = """You are a friendly interviewer. Ask one question at a time.
    After each answer, give constructive feedback."""

    question = f"Ask me an interview question about {topic}"
    return self.ask(question, system_prompt)
```

### Example 4: Text Summarizer

```python
def summarize_url(self, url):
    """Summarize content from a URL"""
    # You'd need to fetch the content first (using requests library)
    # This is just the Claude part:

    system_prompt = "Summarize in 3 bullet points. Be concise."
    question = f"Summarize this:\n\n{content}"
    return self.ask(question, system_prompt)
```

---

## 🔥 Advanced Ideas (For When You're Ready!)

### 1. Voice Assistant
- Use `speech_recognition` library
- Speak questions to Claude
- Use text-to-speech for responses

### 2. Slack Bot
- Integrate with Slack API
- Answer team questions automatically
- Schedule reminders

### 3. GitHub PR Reviewer
- Fetch PR diffs from GitHub
- Ask Claude to review changes
- Post comments automatically

### 4. Discord Bot
- Respond to Discord messages
- Answer questions in your server
- Moderate conversations

### 5. Web API
- Use Flask to create REST API
- Accept questions via HTTP
- Return Claude's responses as JSON

---

## 🎬 Sample Conversations

### Learning Python
```
You: python cli.py chat

You: I'm new to Python. What's a variable?
Claude: A variable is like a labeled box where you can store information...

You: Can you show me an example?
Claude: Sure! Here's a simple example:
name = "Alice"
age = 25
...

You: What about lists?
Claude: Lists are collections of items...
```

### Debugging Help
```
You: python cli.py ask "Why does 'name = input()' wait forever?"

Claude: The input() function waits for you to type something and press Enter.
It's not frozen - it's waiting for your input! Try typing something and pressing Enter.
```

### Project Planning
```
You: python cli.py chat

You: I want to build a todo app. Where do I start?
Claude: Great choice! Here's a simple roadmap:
1. Start with basic file storage (save todos to a text file)
2. Add commands: add, list, complete, delete
3. Later: add dates, priorities, etc.

You: How do I save to a file?
Claude: Use Python's built-in file operations...
```

---

## 📊 System Prompt Examples

Try these in your code to give Claude different personalities:

### The Expert
```python
system_prompt = "You are an expert programmer with 20 years of experience. Give detailed, professional advice."
```

### The Friendly Helper
```python
system_prompt = "You are a friendly, encouraging mentor. Use simple language and lots of positive reinforcement."
```

### The Critic
```python
system_prompt = "You are a code reviewer who points out problems and suggests improvements. Be thorough but constructive."
```

### The Creative Writer
```python
system_prompt = "You are a creative writer. Make responses engaging, vivid, and imaginative."
```

### The ELI5 Expert
```python
system_prompt = "Explain everything like I'm 5 years old. Use simple words and fun analogies."
```

---

## 🎯 Tips for Great Prompts

### ✅ Good Prompts
- "Explain Python decorators with a simple example"
- "Review this function and suggest improvements: [code]"
- "Generate 5 test cases for a login function"
- "What's the difference between a list and a tuple in Python?"

### ❌ Vague Prompts
- "Help me"
- "Code"
- "Explain programming"
- "What should I do?"

### 💡 Pro Tips
1. **Be specific**: The more details, the better the response
2. **Provide context**: Mention your skill level or what you've tried
3. **Ask for examples**: "Show me an example" gets you working code
4. **Iterate**: Ask follow-up questions to dig deeper
5. **Set the format**: "Explain in 3 steps" or "Give me bullet points"

---

## 🎪 Fun Challenges

Try building these during your hackathon:

1. **Fortune Teller**: Ask Claude to predict your coding future
2. **Haiku Generator**: Generate haikus about programming
3. **Code Golf**: Ask for the shortest possible solution
4. **Rubber Duck**: Explain your code problems out loud to Claude
5. **Time Traveler**: Ask "What was programming like in 1990?"

---

## 🏆 Making Your Project Stand Out

1. **Cool UI**: Add colored terminal output (use `colorama` library)
2. **Progress Bars**: Show thinking status (use `tqdm`)
3. **Save History**: Keep a log of all conversations
4. **Export Results**: Save responses to markdown files
5. **Add Emojis**: Make it fun and visual!

Example with colors:
```python
from colorama import Fore, Style

print(f"{Fore.GREEN}✓ Success!{Style.RESET_ALL}")
print(f"{Fore.RED}✗ Error!{Style.RESET_ALL}")
```

---

Remember: **The best hackathon project is one that solves a problem YOU have!**

What frustrates you? What would make your life easier? Build that! 🚀
