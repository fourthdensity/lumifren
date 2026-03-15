# Contributing to Lumifren

First off, thank you for considering contributing to Lumifren! 💖

## Ways to Contribute

### 🐛 Bug Reports
- Use GitHub Issues
- Include: OS, browser, steps to reproduce, expected vs actual behavior
- Screenshots/logs are super helpful

### 💡 Feature Requests
- Open an issue with `[Feature]` prefix
- Describe the use case, not just the solution
- We love hearing how you use Lumifren!

### 🔧 Code Contributions

1. **Fork** the repo
2. **Create a branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Test** your changes locally
5. **Commit** (`git commit -m 'Add amazing feature'`)
6. **Push** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### 📝 Documentation
- Fix typos, improve explanations
- Add examples, tutorials
- Translate to other languages

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/lumifren.git
cd lumifren

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run locally
python kimi_chat_app.py
```

## Code Style

- Python: Follow PEP 8
- JavaScript: Use modern ES6+
- Keep functions small and focused
- Comment the "why", not the "what"

## Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Keep first line under 50 chars
- Reference issues when relevant (`Fixes #123`)

## Questions?

- Open a GitHub Discussion
- Join our Discord (coming soon)

---

By contributing, you agree that your contributions will be licensed under the AGPL-3.0 License.
