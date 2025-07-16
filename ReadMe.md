

# ♟️ Chess Assistant Bot

A smart Python-based assistant that connects to [Chess.com](https://chess.com), tracks moves in real-time, and uses the **Stockfish** engine to recommend the best move. Designed for serious learners and casual players who want AI-supported analysis during live games.

---

## 📚 Table of Contents

* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)
* [Configuration](#configuration)
* [Dependencies](#dependencies)
* [Example Output](#example-output)
* [Troubleshooting](#troubleshooting)
* [Contributing](#contributing)
* [License](#license)

---

## ✨ Features

* Launches or connects to Chrome to play on Chess.com
* Uses [Stockfish](https://stockfishchess.org) to suggest the best move in real time
* Tracks move history from the Chess.com interface
* Intelligent position evaluation (score or checkmate prediction)
* Arabic-localized console interface
* Persistent user data (via `~/.chess_assistant`)
* Automated cleanup of browser sessions

---

## 🛠️ Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/nncc0/chess_Ai.git
   cd chess_Ai
   ```

2. **Install Python dependencies**

   ```bash
   pip install selenium python-chess
   ```

3. **Install ChromeDriver**

   * Make sure `chromedriver` matches your installed version of Chrome and is available in your `PATH`.

4. **Add Stockfish engine**

   * Place the Stockfish binary at the expected location:

     ```bash
     /home/dev/intelligent_agent/stockfish
     ```
   * Or modify the path in `chess_bot.py` (`self.stockfish_path`)

---

## ▶️ Usage

Run the assistant using:

```bash
python3 chess_bot.py
```

You’ll be presented with an Arabic-language menu:

1. Open browser and start a new game
2. Attach the assistant to an existing browser session
3. Cleanup old sessions
4. Exit

Once the assistant is running, it will display the following in the terminal:

* Move history
* Recommended best move
* Move evaluation (in centipawns or mate)
* Indication if it's your turn

---

## ⚙️ Configuration

To customize:

* **Stockfish path**: edit the path in `chess_bot.py`
* **Headless browser mode**: can be toggled in `setup_browser()`
* **Thread count and skill level** for Stockfish can be configured via `.engine.configure(...)`

---

## 📦 Dependencies

* Python 3.7+
* [Selenium](https://pypi.org/project/selenium/)
* [python-chess](https://pypi.org/project/python-chess/)
* Chrome & ChromeDriver
* Stockfish UCI-compatible engine

---

## 🧪 Example Output

```text
=== مساعد الشطرنج ===

📝 الحركات السابقة: e4 e5 Nf3 Nc6
💡 أفضل حركة: Bb5
📍 المربعات: b1 ➜ b5
📊 التقييم: موقف جيد (تقييم: +0.8)

🎯 دورك للعب! يُنصح بـ: Bb5 (b1 ➜ b5)
```

---

## 🛠 Troubleshooting

* **Chrome not launching**: Make sure ChromeDriver is installed and compatible
* **No Stockfish found**: Ensure the binary path exists or update `self.stockfish_path`
* **Permission errors**: Try `chmod +x` on the Stockfish binary


