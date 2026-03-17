<p align="center">
  <img src="https://img.shields.io/badge/python-3.6+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.6+">
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20BSD-brightgreen?style=for-the-badge" alt="Cross-Platform">
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="MIT License">
</p>

<h1 align="center">⌨️ HumanTyper</h1>

<p align="center">
  <b>Clipboard → Human-like Typing Simulation</b><br>
  <sub>Types your clipboard content like a real student drafting an essay — with burst typing, word substitutions, fatigue, and natural pauses.</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/zero%20dependencies-on%20macOS%20%26%20Windows-success?style=flat-square" alt="Zero deps">
  <img src="https://img.shields.io/badge/accurate%20WPM-clock--based%20scheduling-informational?style=flat-square" alt="Accurate WPM">
  <img src="https://img.shields.io/badge/150%2B%20synonyms-built--in-blueviolet?style=flat-square" alt="Built-in synonyms">
</p>

---

## ✨ Features

- **Accurate WPM** — Clock-based scheduling ensures your target WPM is actually hit, regardless of system overhead
- **Burst Typing** — Types words in customizable bursts then pauses (simulating brainstorming/thinking), just like a real student writing an essay
- **Word Substitution & Draft Corrections** — Occasionally types a synonym, pauses, backspaces it, and retypes the correct word — simulating vocabulary choices during drafting
- **150+ Built-in Synonyms** — Offline dictionary covering common essay words, with complexity filtering (simple/moderate/complex)
- **Fatigue Simulation** — Typing speed gradually decreases over time (configurable 0–30% slowdown)
- **Micro-hesitations** — Random pauses before long/uncommon words (≥8 characters)
- **Paragraph Thinking Pauses** — Longer configurable pauses at paragraph boundaries (0–500s)
- **Sentence-start Slowdown** — First 1–2 words of each sentence typed ~20% slower
- **Re-reading Pauses** — Periodic pauses as if scanning what was just typed
- **Realistic Typos** — Simulates QWERTY-based mistakes (nearby key presses, double taps) with natural self-corrections
- **Decimal Precision** — All timing controls accept decimal values (e.g., `2.5s` delay, `1.3–4.7s` burst pauses)
- **Cross-Platform** — Works on Linux (X11 & Wayland), macOS, Windows, FreeBSD, and OpenBSD
- **Auto-Install Dependencies** — Detects your OS, distro, and package manager, then offers to install missing tools
- **Zero External Dependencies** on macOS & Windows — uses built-in OS APIs
- **Fully Customizable** — Every timing, rate, and behavior is adjustable (all values support 0–500s range with decimals)

## 🚀 Quick Start

```bash
# Copy some text to your clipboard, then:
python3 humantyper.py
```

That's it. The script will detect your platform, check for dependencies, show a preview of your clipboard, and guide you through configuration.

## 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/humantyper.git
cd humantyper
```

No `pip install` needed — it's a single Python file with no third-party dependencies.

### Platform Requirements

| Platform | Typing Tool | Clipboard Tool | Auto-installed? |
|----------|------------|----------------|:---:|
| **Linux (X11)** | `xdotool` | `xclip` | ✅ |
| **Linux (Wayland)** | `ydotool` or `wtype` | `wl-paste` | ✅ |
| **macOS** | CoreGraphics (built-in) | `pbpaste` (built-in) | — |
| **Windows** | Win32 `SendInput` (built-in) | PowerShell (built-in) | — |
| **FreeBSD / OpenBSD** | `xdotool` | `xclip` | ✅ |

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

  ⚙  Basic Configuration
  Press Enter to accept defaults

  ⏱  Delay before typing (0-500 seconds) [5.0]: 2.5
  ⚡ Typing speed (WPM) [65]: 80
  💥 Error rate (0-15%) [3.0]: 2

  🔧 Configure advanced settings? [y/N]: y

  ── Burst Typing ──
    Enable burst typing? [Y/n]:
    Words per burst [8]: 6
    Min thinking pause between bursts (sec) [2.0]: 1.5
    Max thinking pause between bursts (sec) [5.0]: 4.0

  ── Word Substitution (Draft Corrections) ──
    Enable word substitution? [Y/n]:
    Substitution rate (0-50%) [3.0]: 5
    Word complexity (simple/moderate/complex) [moderate]:

  ── Human-like Behavior ──
    Fatigue slowdown (0-30%) [10.0]: 15
    Min paragraph pause (sec) [2.0]:
    Max paragraph pause (sec) [8.0]:
    Hesitate before long words? [Y/n]:
    Simulate re-reading pauses? [Y/n]:
```

### Basic Settings

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| **Delay** | 5.0s | 0.0–500.0s | Countdown before typing starts (supports decimals) |
| **WPM** | 65 | 10–500 | Typing speed in words per minute |
| **Error Rate** | 3% | 0–15% | Chance of simulated QWERTY typos with corrections |

### Advanced Settings

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| **Burst Typing** | on | — | Type words in bursts then pause (brainstorming) |
| **Words per Burst** | 8 | 1–100 | How many words to type before pausing |
| **Burst Pause** | 2.0–5.0s | 0.0–500.0s | Min/max thinking pause between bursts |
| **Word Substitution** | on | — | Type synonym → pause → backspace → correct word |
| **Substitution Rate** | 3% | 0–50% | How often words get "drafted wrong" |
| **Word Complexity** | moderate | simple/moderate/complex | Prefer shorter, any, or longer synonyms |
| **Fatigue** | 10% | 0–30% | Max typing speed decrease by end of text |
| **Paragraph Pause** | 2.0–8.0s | 0.0–500.0s | Thinking pause at paragraph boundaries |
| **Long-word Hesitation** | on | — | Brief pause before words ≥ 8 characters |
| **Re-reading Pauses** | on | — | Periodic pauses every 15–40 words |

### How It Works

1. **Copy** text to your clipboard
2. **Run** `python3 humantyper.py`
3. **Configure** basic settings (speed, delay, errors)
4. **Optionally** configure advanced settings (bursts, substitutions, fatigue)
5. **Switch** to your target window during the countdown
6. **Watch** it type like a student drafting an essay ⌨️

Press **Ctrl+C** at any time to stop.

## 🧠 Technical Details

### WPM Accuracy

HumanTyper uses **clock-based scheduling** to achieve accurate WPM within each typing burst:

1. Pre-computes target timestamps for each character based on the WPM budget
2. Characters after punctuation get proportionally longer pauses (weighted distribution)
3. ±30% per-character jitter is applied, then rescaled to preserve the total time budget
4. During typing, the real wall clock is checked before each keystroke — sleep only until the target time
5. If the typing backend is slow, the sleep is skipped entirely (self-correcting)

### Burst Typing

Text is tokenized into words and grouped into bursts. Each burst is typed at the target WPM, then the typer pauses for a configurable duration — simulating a student thinking about what to write next.

### Word Substitution (Draft Corrections)

When enabled, the typer occasionally:
1. Looks up a synonym from the built-in 150+ word dictionary
2. Types the synonym at a slightly faster pace
3. Pauses briefly (simulating "noticing" the wrong word)
4. Backspaces the entire synonym
5. Retypes the correct word

This mimics a student reconsidering vocabulary choices while drafting an essay. The `complexity` setting controls whether shorter (casual), any, or longer (formal) synonyms are preferred.

### Fatigue Simulation

Typing speed gradually decreases as the text progresses. The effective WPM is calculated as:
```
effective_wpm = base_wpm × (1 - fatigue_rate × progress)
```
where `progress` goes from 0.0 to 1.0 over the text.

### Typo Simulation

Errors are generated using a QWERTY neighbor map — when a "mistake" is made, it's a key physically adjacent to the intended key. The script then:
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
- [ ] Custom synonym dictionary loading from file

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Made with ☕ and a dislike for typing things twice</sub>
</p>
