<p align="center">
  <img src="https://img.shields.io/badge/python-3.6+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.6+">
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20BSD-brightgreen?style=for-the-badge" alt="Cross-Platform">
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="MIT License">
</p>

<h1 align="center">⌨️ HumanTyper</h1>

<p align="center">
  <b>Clipboard → Human-like Typing Simulation</b><br>
  <sub>Types your clipboard content like a real human — with configurable speed, realistic typos, and self-corrections.</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/zero%20dependencies-on%20macOS%20%26%20Windows-success?style=flat-square" alt="Zero deps">
  <img src="https://img.shields.io/badge/accurate%20WPM-clock--based%20scheduling-informational?style=flat-square" alt="Accurate WPM">
</p>

---

## ✨ Features

- **Accurate WPM** — Clock-based scheduling ensures your target WPM is actually hit, regardless of system overhead
- **Realistic Typos** — Simulates QWERTY-based mistakes (nearby key presses, double taps) with natural self-corrections
- **Cross-Platform** — Works on Linux (X11 & Wayland), macOS, Windows, FreeBSD, and OpenBSD
- **Auto-Install Dependencies** — Detects your OS, distro, and package manager, then offers to install missing tools
- **Zero External Dependencies** on macOS & Windows — uses built-in OS APIs
- **Configurable** — Adjust typing speed (WPM), error rate, and start delay
- **Human-like Rhythm** — Longer pauses after punctuation, natural jitter between keystrokes

## 🚀 Quick Start

```bash
# Copy some text to your clipboard, then:
python3 humantyper.py
```

That's it. The script will detect your platform, check for dependencies, show a preview of your clipboard, and guide you through configuration.

## 📦 Installation

```bash
git clone https://github.com/yofriendfromschool1/Universal-Human-Paster-Typer.git
cd Universal-Human-Paster-Typer
```

No `pip install` needed — it's a single Python file with no third-party dependencies.

### Platform Requirements

| Platform | Typing Tool | Clipboard Tool | Auto-installed? |
|----------|------------|----------------|:---:|
| **Linux (X11)** | `xdotool or ydotool` | `xclip` | ✅ |
| **Linux (Wayland)** | `xdotool or ydotool` (XWayland) or `wtype` | `wl-paste` | ✅ |
| **macOS** | `osascript` (built-in) | `pbpaste` (built-in) | — |
| **Windows** | Win32 `SendInput` (built-in) | PowerShell (built-in) | — |
| **FreeBSD / OpenBSD** | `xdotool or ydotool` | `xclip` | ✅ |

On Linux/BSD, if dependencies are missing, HumanTyper will detect your package manager and offer to install them automatically:

> **Supported package managers:** apt, pacman, dnf, zypper, xbps, apk, emerge, nix, pkg, pkg_add, brew

## 🎮 Usage

```
╔══════════════════════════════════════════════╗
║       ⌨  H U M A N   T Y P E R  ⌨            ║
║   Clipboard → Human-like Typing Simulation   ║
╚══════════════════════════════════════════════╝

  📋 Clipboard Content:
  ──────────────────────────────────────────────────
    The quick brown fox jumps over the lazy dog...
  ──────────────────────────────────────────────────
  Total: 44 characters, 1 lines

  ⚙  Configuration
  Press Enter to accept defaults

  ⏱  Delay before typing (seconds) [5]:
  ⚡ Typing speed (WPM) [65]: 150
  💥 Error rate (0-15%) [3.0]: 2
```

### Options

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| **Delay** | 5s | 1–120s | Countdown before typing starts (switch to your target window!) |
| **WPM** | 65 | 10–500 | Typing speed in words per minute |
| **Error Rate** | 3% | 0–15% | Chance of simulated typos with automatic corrections |

### How It Works

1. **Copy** text to your clipboard
2. **Run** `python3 humantyper.py`
3. **Configure** speed, delay, and error rate
4. **Switch** to your target window during the countdown
5. **Watch** it type like a human ⌨️

Press **Ctrl+C** at any time to stop.

## 🧠 Technical Details

### WPM Accuracy

HumanTyper uses **clock-based scheduling** to achieve accurate WPM:

1. Pre-computes target timestamps for each character based on the WPM budget
2. Characters after punctuation get proportionally longer pauses (weighted distribution)
3. ±30% per-character jitter is applied, then rescaled to preserve the total time budget
4. During typing, the real wall clock is checked before each keystroke — sleep only until the target time
5. If the typing backend is slow, the sleep is skipped entirely (self-correcting)

This approach is similar to how game loops and audio engines maintain consistent timing regardless of per-frame overhead.

### Typo Simulation

Errors are generated using a QWERTY neighbor map — when a "mistake" is made, it's a key physically adjacent to the intended key, just like real typos. The script then:

1. Types the wrong character
2. Pauses briefly (simulating "noticing" the mistake)
3. Sometimes types one more character before catching the error
4. Backspaces to delete the mistake
5. Retypes the correct character

## 🤝 Contributing

Contributions are welcome! Some ideas:

- [ ] Add support for more keyboard layouts (AZERTY, DVORAK, Colemak)
- [ ] Configurable pause patterns (e.g., "thinking" pauses mid-sentence)
- [ ] Support for typing from a file instead of clipboard
- [ ] GUI frontend
- [ ] Being able to type higher than 260 WPM on linux

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Made with ☕ and a dislike for typing things twice</sub>
</p>
