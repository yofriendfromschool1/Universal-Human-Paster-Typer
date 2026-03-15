#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║              H U M A N   T Y P E R                   ║
║    Clipboard → Human-like Typing Simulation          ║
╚══════════════════════════════════════════════════════╝

Cross-platform typing simulator — works on Linux (X11/Wayland),
macOS, Windows, and BSD.

Types your clipboard content like a real human — with
configurable speed, realistic typos, and self-corrections.
"""

import subprocess
import time
import random
import sys
import os
import signal
import shutil
import platform as platform_mod

# ─── ANSI Colors ───────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BG_DARK = "\033[48;5;236m"


def init_colors():
    """Enable ANSI escape codes on Windows 10+; disable if unsupported."""
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        for attr in ['RESET','BOLD','DIM','RED','GREEN','YELLOW',
                     'BLUE','MAGENTA','CYAN','WHITE','BG_DARK']:
            setattr(C, attr, '')


# ─── QWERTY Neighbor Map for Realistic Typos ──────────────
NEARBY_KEYS = {
    'a': 'sqwz',   'b': 'vghn',  'c': 'xdfv',  'd': 'sfecx',
    'e': 'wrsdf',  'f': 'dgrtcv','g': 'fhtyb', 'h': 'gjybn',
    'i': 'uojk',   'j': 'hkunm', 'k': 'jloi',  'l': 'kop',
    'm': 'njk',    'n': 'bhjm',  'o': 'iplk',  'p': 'ol',
    'q': 'wa',     'r': 'edft',  's': 'awedxz','t': 'rfgy',
    'u': 'yihj',   'v': 'cfgb',  'w': 'qase',  'x': 'zsdc',
    'y': 'tghu',   'z': 'asx',
    '1': '2q',     '2': '13qw',  '3': '24we',  '4': '35er',
    '5': '46rt',   '6': '57ty',  '7': '68yu',  '8': '79ui',
    '9': '80io',   '0': '9op',
}

# ─── Globals ───────────────────────────────────────────────
stop_typing = False
PLATFORM = {}  # Set once in main() via detect_platform()


def signal_handler(sig, frame):
    global stop_typing
    stop_typing = True


def clear_screen():
    os.system('cls' if sys.platform == 'win32' else 'clear')


# ═══════════════════════════════════════════════════════════
#  PLATFORM DETECTION
# ═══════════════════════════════════════════════════════════

def _wtype_works():
    """Probe whether wtype can actually type on this compositor.
    Many compositors (GNOME Mutter, KDE KWin) do not support
    the virtual-keyboard Wayland protocol that wtype requires."""
    if not shutil.which('wtype'):
        return False
    try:
        # Use a harmless non-printing key to probe protocol support
        r = subprocess.run(['wtype', '-k', 'Pause'],
                           capture_output=True, text=True, timeout=3)
        # If wtype reports the compositor doesn't support the protocol, it won't work
        if 'does not support' in (r.stderr or '').lower():
            return False
        # Exit code 0 means the protocol is supported and the key was sent
        return True
    except Exception:
        return False

def detect_platform():
    """Detect OS, display server, Linux distro, and package manager."""
    info = {'os': None, 'display': None, 'distro': None, 'pkg_manager': None}
    system = platform_mod.system().lower()

    if system == 'linux':
        info['os'] = 'linux'
        session = os.environ.get('XDG_SESSION_TYPE', '').lower()
        if session == 'wayland' or os.environ.get('WAYLAND_DISPLAY'):
            info['display'] = 'wayland'
        elif session == 'x11' or os.environ.get('DISPLAY'):
            info['display'] = 'x11'
        else:
            info['display'] = 'tty'
        info['distro'] = _detect_linux_distro()
        info['pkg_manager'] = _detect_pkg_manager()
        # Resolve typing backend: on Wayland, prefer ydotool (kernel uinput,
        # works on all compositors incl. GNOME/Mutter/KDE), then wtype only
        # if the compositor actually supports the virtual-keyboard protocol.
        # xdotool cannot inject input into native Wayland windows.
        if info['display'] == 'wayland':
            if shutil.which('ydotool'):
                info['typing_backend'] = 'ydotool'
            elif _wtype_works():
                info['typing_backend'] = 'wtype'
            else:
                info['typing_backend'] = 'ydotool'  # will prompt install
        elif info['display'] == 'x11':
            info['typing_backend'] = 'xdotool'
        # Resolve clipboard backend: Wayland can fallback to xclip too
        if info['display'] == 'wayland':
            if shutil.which('wl-paste'):
                info['clipboard_backend'] = 'wl-paste'
            elif shutil.which('xclip'):
                info['clipboard_backend'] = 'xclip'
            else:
                info['clipboard_backend'] = 'wl-paste'  # will prompt install
        elif info['display'] == 'x11':
            info['clipboard_backend'] = 'xclip'

    elif system == 'darwin':
        info['os'] = 'darwin'
        info['display'] = 'quartz'
        info['typing_backend'] = 'osascript'
        info['clipboard_backend'] = 'pbpaste'
        if shutil.which('brew'):
            info['pkg_manager'] = 'brew'

    elif system == 'windows':
        info['os'] = 'windows'
        info['display'] = 'win32'
        info['typing_backend'] = 'win32'
        info['clipboard_backend'] = 'powershell'

    elif system == 'freebsd':
        info['os'] = 'freebsd'
        if os.environ.get('WAYLAND_DISPLAY'):
            info['display'] = 'wayland'
            if shutil.which('ydotool'):
                info['typing_backend'] = 'ydotool'
            elif _wtype_works():
                info['typing_backend'] = 'wtype'
            else:
                info['typing_backend'] = 'ydotool'
            info['clipboard_backend'] = 'wl-paste' if shutil.which('wl-paste') else 'xclip'
        elif os.environ.get('DISPLAY'):
            info['display'] = 'x11'
            info['typing_backend'] = 'xdotool'
            info['clipboard_backend'] = 'xclip'
        else:
            info['display'] = 'tty'
        info['pkg_manager'] = 'pkg' if shutil.which('pkg') else None

    elif system == 'openbsd':
        info['os'] = 'openbsd'
        if os.environ.get('DISPLAY'):
            info['display'] = 'x11'
            info['typing_backend'] = 'xdotool'
            info['clipboard_backend'] = 'xclip'
        else:
            info['display'] = 'tty'
        info['pkg_manager'] = 'pkg_add' if shutil.which('pkg_add') else None

    else:
        info['os'] = system
        if os.environ.get('DISPLAY'):
            info['display'] = 'x11'
        elif os.environ.get('WAYLAND_DISPLAY'):
            info['display'] = 'wayland'
        else:
            info['display'] = 'tty'
        info['pkg_manager'] = _detect_pkg_manager()

    return info


def _detect_linux_distro():
    """Detect Linux distribution family from /etc/os-release."""
    try:
        with open('/etc/os-release') as f:
            content = f.read().lower()
    except (FileNotFoundError, PermissionError):
        return 'unknown'

    distro_id = distro_like = ''
    for line in content.split('\n'):
        if line.startswith('id='):
            distro_id = line.split('=', 1)[1].strip().strip('"')
        elif line.startswith('id_like='):
            distro_like = line.split('=', 1)[1].strip().strip('"')

    ids = distro_id + ' ' + distro_like
    if any(d in ids for d in ('ubuntu', 'debian', 'pop', 'mint', 'elementary', 'kali', 'zorin')):
        return 'debian'
    elif any(d in ids for d in ('arch', 'manjaro', 'endeavouros', 'garuda')):
        return 'arch'
    elif any(d in ids for d in ('fedora', 'rhel', 'centos', 'rocky', 'alma', 'nobara')):
        return 'fedora'
    elif any(d in ids for d in ('opensuse', 'suse')):
        return 'suse'
    elif 'void' in ids:
        return 'void'
    elif 'alpine' in ids:
        return 'alpine'
    elif 'gentoo' in ids:
        return 'gentoo'
    elif any(d in ids for d in ('nixos', 'nix')):
        return 'nix'
    return distro_id or 'unknown'


def _detect_pkg_manager():
    """Detect the system package manager."""
    for cmd, name in [
        ('apt', 'apt'), ('pacman', 'pacman'), ('dnf', 'dnf'),
        ('zypper', 'zypper'), ('xbps-install', 'xbps'), ('apk', 'apk'),
        ('emerge', 'emerge'), ('nix-env', 'nix'), ('pkg', 'pkg'),
    ]:
        if shutil.which(cmd):
            return name
    return None


# ═══════════════════════════════════════════════════════════
#  CLIPBOARD BACKENDS
# ═══════════════════════════════════════════════════════════

def get_clipboard():
    """Read clipboard content using the platform-appropriate method."""
    cb = PLATFORM.get('clipboard_backend')

    try:
        if cb == 'wl-paste':
            return _cmd_output(['wl-paste', '--no-newline'])
        elif cb == 'xclip':
            return _cmd_output(['xclip', '-selection', 'clipboard', '-o'])
        elif cb == 'pbpaste':
            return _cmd_output(['pbpaste'])
        elif cb == 'powershell':
            text = _cmd_output(['powershell.exe', '-NoProfile', '-Command', 'Get-Clipboard'])
            return text.rstrip('\r\n') if text else None
    except Exception:
        pass
    return None


def _cmd_output(cmd):
    """Run a command and return stdout, or None on failure."""
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    return r.stdout if r.returncode == 0 else None


# ═══════════════════════════════════════════════════════════
#  TYPING BACKENDS
# ═══════════════════════════════════════════════════════════

def type_char(char):
    """Type a single character using the platform-appropriate method."""
    if stop_typing:
        return False
    backend = PLATFORM.get('typing_backend')
    try:
        if backend == 'xdotool':
            return _x11_type_char(char)
        elif backend == 'ydotool':
            return _ydotool_type_char(char)
        elif backend == 'wtype':
            return _wayland_type_char(char)
        elif backend == 'osascript':
            return _macos_type_char(char)
        elif backend == 'win32':
            return _win32_type_char(char)
    except Exception:
        pass
    return False


def type_backspace(count=1):
    """Press backspace N times using the platform-appropriate method."""
    backend = PLATFORM.get('typing_backend')
    for _ in range(count):
        if stop_typing:
            return False
        try:
            if backend == 'xdotool':
                subprocess.run(['xdotool', 'key', '--clearmodifiers', 'BackSpace'],
                               timeout=2, capture_output=True)
            elif backend == 'ydotool':
                subprocess.run(['ydotool', 'key', '14:1', '14:0'],
                               timeout=2, capture_output=True)
            elif backend == 'wtype':
                subprocess.run(['wtype', '-k', 'BackSpace'],
                               timeout=2, capture_output=True)
            elif backend == 'osascript':
                subprocess.run(['osascript', '-e',
                               'tell application "System Events" to key code 51'],
                               timeout=2, capture_output=True)
            elif backend == 'win32':
                _win32_press_vk(0x08)  # VK_BACK
            time.sleep(random.uniform(0.03, 0.08))
        except Exception:
            return False
    return True


# ── X11 (xdotool) ─────────────────────────────────────────

_X11_KEY_MAP = {
    '\n': 'Return', '\t': 'Tab', ' ': 'space',
    '!': 'exclam', '@': 'at', '#': 'numbersign',
    '$': 'dollar', '%': 'percent', '^': 'asciicircum',
    '&': 'ampersand', '*': 'asterisk',
    '(': 'parenleft', ')': 'parenright',
    '-': 'minus', '_': 'underscore', '=': 'equal', '+': 'plus',
    '[': 'bracketleft', ']': 'bracketright',
    '{': 'braceleft', '}': 'braceright',
    '\\': 'backslash', '|': 'bar',
    ';': 'semicolon', ':': 'colon',
    "'": 'apostrophe', '"': 'quotedbl',
    ',': 'comma', '.': 'period',
    '<': 'less', '>': 'greater',
    '/': 'slash', '?': 'question',
    '`': 'grave', '~': 'asciitilde',
}

def _x11_type_char(char):
    if char in _X11_KEY_MAP:
        subprocess.run(['xdotool', 'key', '--clearmodifiers', _X11_KEY_MAP[char]],
                       timeout=2, capture_output=True)
    else:
        subprocess.run(['xdotool', 'type', '--clearmodifiers', '--delay', '0', char],
                       timeout=2, capture_output=True)
    return True


# ── Wayland (ydotool — kernel uinput) ─────────────────────
#
# ydotool type handles character→keycode translation internally.
# We only use ydotool key for non-printable keys (Enter, Tab, etc.)
# using Linux evdev keycodes.

_YDOTOOL_SPECIAL_KEYS = {
    '\n': 28,   # KEY_ENTER
    '\t': 15,   # KEY_TAB
}

def _ydotool_type_char(char):
    """Type a single character using ydotool (kernel uinput)."""
    # Special non-printable keys use evdev keycodes
    if char in _YDOTOOL_SPECIAL_KEYS:
        kc = _YDOTOOL_SPECIAL_KEYS[char]
        subprocess.run(['ydotool', 'key', f'{kc}:1', f'{kc}:0'],
                       timeout=2, capture_output=True)
        return True

    # All printable characters: use ydotool type which handles
    # character→keycode translation internally (including shift)
    subprocess.run(['ydotool', 'type', '--key-delay', '0',
                    '--key-hold', '20', '--', char],
                   timeout=2, capture_output=True)
    return True


# ── Wayland (wtype — wlroots compositors only) ────────────

def _wayland_type_char(char):
    if char == '\n':
        subprocess.run(['wtype', '-k', 'Return'], timeout=2, capture_output=True)
    elif char == '\t':
        subprocess.run(['wtype', '-k', 'Tab'], timeout=2, capture_output=True)
    else:
        # '--' prevents wtype from interpreting chars as flags
        subprocess.run(['wtype', '--', char], timeout=2, capture_output=True)
    return True


# ── macOS (osascript) ─────────────────────────────────────

_MACOS_KEYCODES = {'\n': 36, '\t': 48}  # Return, Tab

def _macos_type_char(char):
    if char in _MACOS_KEYCODES:
        code = _MACOS_KEYCODES[char]
        subprocess.run(['osascript', '-e',
                       f'tell application "System Events" to key code {code}'],
                       timeout=2, capture_output=True)
    else:
        escaped = char.replace('\\', '\\\\').replace('"', '\\"')
        subprocess.run(['osascript', '-e',
                       f'tell application "System Events" to keystroke "{escaped}"'],
                       timeout=2, capture_output=True)
    return True


# ── Windows (ctypes SendInput) ────────────────────────────

_W32_READY = False
_W32_INPUT = None
_W32_KEYBDINPUT = None

def _win32_init():
    """Lazily initialize Win32 input structures."""
    global _W32_READY, _W32_INPUT, _W32_KEYBDINPUT
    if _W32_READY:
        return
    import ctypes
    import ctypes.wintypes as wt

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD),
                     ("dwFlags", wt.DWORD), ("time", wt.DWORD),
                     ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", wt.LONG), ("dy", wt.LONG),
                     ("mouseData", wt.DWORD), ("dwFlags", wt.DWORD),
                     ("time", wt.DWORD),
                     ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [("uMsg", wt.DWORD), ("wParamL", wt.WORD),
                     ("wParamH", wt.WORD)]

    class _IU(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT),
                     ("hi", HARDWAREINPUT)]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", wt.DWORD), ("u", _IU)]

    _W32_INPUT = INPUT
    _W32_KEYBDINPUT = KEYBDINPUT
    _W32_READY = True


def _win32_type_char(char):
    """Type a character on Windows via SendInput (Unicode)."""
    import ctypes
    _win32_init()

    vk_map = {'\n': 0x0D, '\t': 0x09}  # VK_RETURN, VK_TAB
    if char in vk_map:
        _win32_press_vk(vk_map[char])
        return True

    # Unicode input
    code = ord(char)
    KEYEVENTF_UNICODE = 0x0004
    KEYEVENTF_KEYUP = 0x0002
    extra = ctypes.pointer(ctypes.c_ulong(0))

    down = _W32_INPUT()
    down.type = 1  # INPUT_KEYBOARD
    down.u.ki.wVk = 0
    down.u.ki.wScan = code
    down.u.ki.dwFlags = KEYEVENTF_UNICODE
    down.u.ki.dwExtraInfo = extra

    up = _W32_INPUT()
    up.type = 1
    up.u.ki.wVk = 0
    up.u.ki.wScan = code
    up.u.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
    up.u.ki.dwExtraInfo = extra

    arr = (_W32_INPUT * 2)(down, up)
    ctypes.windll.user32.SendInput(2, arr, ctypes.sizeof(_W32_INPUT))
    return True


def _win32_press_vk(vk):
    """Press and release a virtual key on Windows."""
    import ctypes
    _win32_init()
    extra = ctypes.pointer(ctypes.c_ulong(0))

    down = _W32_INPUT()
    down.type = 1
    down.u.ki.wVk = vk
    down.u.ki.dwFlags = 0
    down.u.ki.dwExtraInfo = extra

    up = _W32_INPUT()
    up.type = 1
    up.u.ki.wVk = vk
    up.u.ki.dwFlags = 0x0002  # KEYEVENTF_KEYUP
    up.u.ki.dwExtraInfo = extra

    arr = (_W32_INPUT * 2)(down, up)
    ctypes.windll.user32.SendInput(2, arr, ctypes.sizeof(_W32_INPUT))


# ═══════════════════════════════════════════════════════════
#  DEPENDENCY MANAGEMENT
# ═══════════════════════════════════════════════════════════

# Install commands per package manager
_INSTALL_CMD = {
    'apt':     ['sudo', 'apt', 'install', '-y'],
    'pacman':  ['sudo', 'pacman', '-S', '--noconfirm'],
    'dnf':     ['sudo', 'dnf', 'install', '-y'],
    'zypper':  ['sudo', 'zypper', 'install', '-y'],
    'xbps':    ['sudo', 'xbps-install', '-Sy'],
    'apk':     ['sudo', 'apk', 'add'],
    'emerge':  ['sudo', 'emerge'],
    'nix':     ['nix-env', '-iA'],
    'pkg':     ['sudo', 'pkg', 'install', '-y'],
    'pkg_add': ['doas', 'pkg_add'],
    'brew':    ['brew', 'install'],
}

# Package name overrides (most are same name across all managers)
_PKG_OVERRIDES = {
    'emerge': {
        'xdotool': 'x11-misc/xdotool', 'xclip': 'x11-misc/xclip',
        'wtype': 'gui-apps/wtype', 'wl-clipboard': 'gui-apps/wl-clipboard',
    },
    'nix': {
        'xdotool': 'nixpkgs.xdotool', 'xclip': 'nixpkgs.xclip',
        'wtype': 'nixpkgs.wtype', 'wl-clipboard': 'nixpkgs.wl-clipboard',
    },
}


def _pkg_name(tool, pkg_mgr):
    """Resolve the correct package name for a given tool and package manager."""
    return _PKG_OVERRIDES.get(pkg_mgr, {}).get(tool, tool)


def _get_required_tools():
    """Return list of (tool_binary, package_name) needed for this platform."""
    os_name = PLATFORM.get('os')
    backend = PLATFORM.get('typing_backend')
    cb = PLATFORM.get('clipboard_backend')

    if os_name in ('darwin', 'windows'):
        return []  # No external dependencies needed

    tools = []
    # Typing tool
    if backend == 'xdotool':
        tools.append(('xdotool', 'xdotool'))
    elif backend == 'ydotool':
        tools.append(('ydotool', 'ydotool'))
    elif backend == 'wtype':
        tools.append(('wtype', 'wtype'))
    # Clipboard tool
    if cb == 'xclip':
        tools.append(('xclip', 'xclip'))
    elif cb == 'wl-paste':
        tools.append(('wl-paste', 'wl-clipboard'))
    return tools


def _check_ydotoold():
    """Check if the ydotoold daemon is running; offer to start it if not."""
    # Check if ydotoold process is already running
    try:
        result = subprocess.run(['pgrep', '-x', 'ydotoold'],
                                capture_output=True, timeout=3)
        if result.returncode == 0:
            print(f"  {C.GREEN}✓ ydotoold daemon is running{C.RESET}")
            return True
    except Exception:
        pass

    print(f"\n  {C.YELLOW}{C.BOLD}⚠  ydotoold daemon is not running{C.RESET}")
    print(f"  {C.DIM}ydotool requires the ydotoold daemon to inject input.{C.RESET}\n")

    # Try systemd user service first
    has_systemd_service = False
    try:
        r = subprocess.run(['systemctl', '--user', 'status', 'ydotool'],
                           capture_output=True, text=True, timeout=3)
        # service unit exists if exit code is 0 (active) or 3 (inactive) but not 4 (not found)
        has_systemd_service = r.returncode in (0, 3)
    except Exception:
        pass

    if has_systemd_service:
        print(f"  {C.CYAN}Start via systemd?{C.RESET}")
        print(f"  {C.DIM}Command: systemctl --user start ydotool{C.RESET}\n")
        answer = input(f"  {C.GREEN}{C.BOLD}▶ Start ydotoold now? [Y/n]: {C.RESET}").strip().lower()
        if answer in ('', 'y', 'yes'):
            result = subprocess.run(['systemctl', '--user', 'start', 'ydotool'],
                                    capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                time.sleep(0.5)  # Give daemon a moment to start
                print(f"\n  {C.GREEN}{C.BOLD}✓ ydotoold started!{C.RESET}")
                return True
            else:
                print(f"\n  {C.RED}✗ Failed to start: {result.stderr.strip()}{C.RESET}")
    else:
        print(f"  {C.CYAN}Start ydotoold directly?{C.RESET}")
        print(f"  {C.DIM}Command: sudo ydotoold &{C.RESET}\n")
        answer = input(f"  {C.GREEN}{C.BOLD}▶ Start ydotoold now? [Y/n]: {C.RESET}").strip().lower()
        if answer in ('', 'y', 'yes'):
            try:
                subprocess.Popen(['sudo', 'ydotoold'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)  # Give daemon a moment to start
                # Verify it started
                r = subprocess.run(['pgrep', '-x', 'ydotoold'],
                                   capture_output=True, timeout=3)
                if r.returncode == 0:
                    print(f"\n  {C.GREEN}{C.BOLD}✓ ydotoold started!{C.RESET}")
                    return True
                else:
                    print(f"\n  {C.RED}✗ ydotoold does not appear to be running{C.RESET}")
            except Exception as e:
                print(f"\n  {C.RED}✗ Failed to start: {e}{C.RESET}")

    print(f"\n  {C.DIM}Start it manually before running HumanTyper:{C.RESET}")
    print(f"    {C.CYAN}sudo ydotoold &{C.RESET}")
    print(f"  {C.DIM}Or enable the systemd service:{C.RESET}")
    print(f"    {C.CYAN}systemctl --user enable --now ydotool{C.RESET}\n")
    return False


def check_dependencies():
    """Check for required tools and offer to install missing ones."""
    display = PLATFORM.get('display')
    os_name = PLATFORM.get('os')

    # Show detected environment
    os_label = {
        'linux': 'Linux', 'darwin': 'macOS', 'windows': 'Windows',
        'freebsd': 'FreeBSD', 'openbsd': 'OpenBSD',
    }.get(os_name, os_name or 'Unknown')

    display_label = {
        'x11': 'X11', 'wayland': 'Wayland', 'quartz': 'Quartz',
        'win32': 'Win32', 'tty': 'TTY (no display)',
    }.get(display, display or 'Unknown')

    distro = PLATFORM.get('distro')
    pkg_mgr = PLATFORM.get('pkg_manager')

    print(f"  {C.DIM}OS:              {os_label}{C.RESET}")
    print(f"  {C.DIM}Display server:  {display_label}{C.RESET}")
    if distro:
        print(f"  {C.DIM}Distribution:    {distro}{C.RESET}")
    if pkg_mgr:
        print(f"  {C.DIM}Package manager: {pkg_mgr}{C.RESET}")

    # Check for TTY (no display server)
    if display == 'tty':
        print(f"\n  {C.RED}{C.BOLD}✗ No display server detected!{C.RESET}")
        print(f"  {C.DIM}HumanTyper needs a graphical environment to simulate typing.{C.RESET}")
        print(f"  {C.DIM}Please run from within a desktop session (X11 or Wayland).{C.RESET}\n")
        return False

    # No deps needed for macOS/Windows
    if os_name in ('darwin', 'windows'):
        print(f"\n  {C.GREEN}✓ No external dependencies needed{C.RESET}")
        return True

    # Check required tools
    required = _get_required_tools()
    missing = [(tool, pkg) for tool, pkg in required if not shutil.which(tool)]

    if not missing:
        tools = ', '.join(t for t, _ in required)
        print(f"\n  {C.GREEN}✓ All dependencies found ({tools}){C.RESET}")
        # Check if ydotoold daemon is running when using ydotool
        if PLATFORM.get('typing_backend') == 'ydotool':
            if not _check_ydotoold():
                return False
        return True

    # Report missing
    print(f"\n  {C.RED}{C.BOLD}✗ Missing dependencies:{C.RESET}")
    for tool, _ in missing:
        print(f"    {C.YELLOW}•{C.RESET} {tool}")

    # Offer to install
    if pkg_mgr and pkg_mgr in _INSTALL_CMD:
        pkg_names = [_pkg_name(pkg, pkg_mgr) for _, pkg in missing]
        cmd = _INSTALL_CMD[pkg_mgr] + pkg_names
        cmd_str = ' '.join(cmd)

        print(f"\n  {C.CYAN}Install automatically?{C.RESET}")
        print(f"  {C.DIM}Command: {cmd_str}{C.RESET}\n")

        answer = input(f"  {C.GREEN}{C.BOLD}▶ Install now? [Y/n]: {C.RESET}").strip().lower()
        if answer in ('', 'y', 'yes'):
            print(f"\n  {C.DIM}Running: {cmd_str}{C.RESET}")
            result = subprocess.run(cmd)
            if result.returncode == 0:
                print(f"\n  {C.GREEN}{C.BOLD}✓ Installed successfully!{C.RESET}")
                return True
            else:
                print(f"\n  {C.RED}✗ Installation failed (exit code {result.returncode}){C.RESET}")
                return False
        else:
            print(f"\n  {C.DIM}Skipped. Install manually:{C.RESET}")
            print(f"    {C.CYAN}{cmd_str}{C.RESET}\n")
            return False
    else:
        # No known package manager — show generic instructions
        print(f"\n  {C.DIM}Install these tools using your system package manager:{C.RESET}")
        for tool, pkg in missing:
            print(f"    {C.CYAN}•{C.RESET} {pkg}")
        print()
        return False


# ═══════════════════════════════════════════════════════════
#  TYPO SIMULATION
# ═══════════════════════════════════════════════════════════

def get_typo_char(original):
    """Generate a realistic typo character based on QWERTY layout."""
    lower = original.lower()
    if lower in NEARBY_KEYS:
        typo = random.choice(NEARBY_KEYS[lower])
        return typo.upper() if original.isupper() else typo
    return original


def make_error(char, error_type):
    """Simulate a typing error. Returns (kind, char) or None."""
    if error_type == 1:
        wrong = get_typo_char(char)
        return ('wrong_key', wrong) if wrong != char else None
    elif error_type == 2:
        return ('double', char)
    return None


# ═══════════════════════════════════════════════════════════
#  WPM TIMING (clock-based scheduling)
# ═══════════════════════════════════════════════════════════

def compute_target_times(text, wpm):
    """
    Compute absolute target timestamps for each character so that
    the overall typing speed matches the target WPM exactly.

    Characters after punctuation get proportionally longer pauses
    (weighted distribution), with ±30% jitter rescaled to preserve total.
    """
    if not text:
        return []

    total_chars = len(text)
    total_time = (total_chars / 5.0) * (60.0 / wpm)

    weights = []
    for i, char in enumerate(text):
        prev = text[i - 1] if i > 0 else ''
        if prev in '.!?':
            w = random.uniform(4.0, 8.0)
        elif prev == ',':
            w = random.uniform(2.0, 4.0)
        elif prev == '\n':
            w = random.uniform(3.0, 5.0)
        elif prev == ' ':
            w = random.uniform(1.0, 1.3)
        else:
            w = 1.0
        weights.append(w)

    total_weight = sum(weights)
    raw_gaps = [(w / total_weight) * total_time for w in weights]

    # Jitter ±30%, then rescale to preserve total
    jittered = [g * random.uniform(0.7, 1.3) for g in raw_gaps]
    j_sum = sum(jittered)
    gaps = [g * (total_time / j_sum) for g in jittered] if j_sum > 0 else raw_gaps

    # Cumulative timestamps
    targets = []
    cumulative = 0.0
    for g in gaps:
        cumulative += g
        targets.append(cumulative)
    return targets


# ═══════════════════════════════════════════════════════════
#  TYPING SIMULATION
# ═══════════════════════════════════════════════════════════

def simulate_typing(text, wpm, error_rate, delay_seconds):
    """Main typing simulation loop with clock-based WPM scheduling."""
    global stop_typing
    stop_typing = False
    signal.signal(signal.SIGINT, signal_handler)

    targets = compute_target_times(text, wpm)

    # ── Countdown ──────────────────────────────────────
    print(f"\n  {C.YELLOW}{C.BOLD}⏱  Starting in {delay_seconds} seconds...{C.RESET}")
    print(f"  {C.DIM}Switch to your target window now!{C.RESET}")
    print(f"  {C.DIM}Press Ctrl+C to cancel{C.RESET}\n")

    try:
        for remaining in range(delay_seconds, 0, -1):
            sys.stdout.write(f"\r  {C.CYAN}{C.BOLD}  ▸ {remaining}...{C.RESET}  ")
            sys.stdout.flush()
            time.sleep(1)
            if stop_typing:
                print(f"\n\n  {C.RED}✗ Cancelled.{C.RESET}\n")
                return
        sys.stdout.write(f"\r  {C.GREEN}{C.BOLD}  ▸ Typing!{C.RESET}     \n")
        sys.stdout.flush()
    except KeyboardInterrupt:
        print(f"\n\n  {C.RED}✗ Cancelled.{C.RESET}\n")
        return

    # ── Typing Loop ────────────────────────────────────
    total_chars = len(text)
    errors_made = 0
    chars_typed = 0
    start_time = time.perf_counter()

    for i, char in enumerate(text):
        if stop_typing:
            break

        # Clock-based scheduling: sleep only until target timestamp
        wait = targets[i] - (time.perf_counter() - start_time)
        if wait > 0:
            time.sleep(wait)

        # Error simulation
        should_error = (
            random.random() < error_rate
            and char.isalpha() and i > 0 and i < total_chars - 1
        )

        if should_error:
            error_type = random.choices([1, 2], weights=[70, 30], k=1)[0]
            error = make_error(char, error_type)

            if error:
                errors_made += 1
                err_kind, err_char = error

                if err_kind == 'wrong_key':
                    type_char(err_char)
                    time.sleep(random.uniform(0.15, 0.5))
                    if random.random() < 0.3 and i + 1 < total_chars:
                        type_char(text[i + 1])
                        time.sleep(random.uniform(0.2, 0.6))
                        type_backspace(2)
                    else:
                        type_backspace(1)
                    time.sleep(random.uniform(0.05, 0.15))
                    type_char(char)

                elif err_kind == 'double':
                    type_char(char)
                    type_char(char)
                    time.sleep(random.uniform(0.15, 0.45))
                    type_backspace(1)
            else:
                type_char(char)
        else:
            type_char(char)

        chars_typed += 1

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if stop_typing:
        print(f"\n  {C.YELLOW}⚠  Typing interrupted at character {chars_typed}/{total_chars}{C.RESET}")
    else:
        print(f"\n  {C.GREEN}{C.BOLD}✓ Done!{C.RESET}")
    print(f"  {C.DIM}Characters typed: {chars_typed} | Errors simulated: {errors_made}{C.RESET}\n")


# ═══════════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════════

def print_banner():
    clear_screen()
    print(f"""
  {C.CYAN}{C.BOLD}╔══════════════════════════════════════════════╗
  ║{C.MAGENTA}       ⌨  H U M A N   T Y P E R  ⌨            {C.CYAN}║
  ║{C.DIM}{C.WHITE}   Clipboard → Human-like Typing Simulation   {C.RESET}{C.CYAN}{C.BOLD}║
  ╚══════════════════════════════════════════════╝{C.RESET}
""")


def get_int_input(prompt, default, min_val, max_val):
    while True:
        raw = input(f"  {prompt} {C.DIM}[{default}]{C.RESET}: ").strip()
        if raw == '':
            return default
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            print(f"  {C.RED}Please enter a value between {min_val} and {max_val}{C.RESET}")
        except ValueError:
            print(f"  {C.RED}Please enter a valid number{C.RESET}")


def get_float_input(prompt, default, min_val, max_val):
    while True:
        raw = input(f"  {prompt} {C.DIM}[{default}]{C.RESET}: ").strip()
        if raw == '':
            return default
        try:
            val = float(raw)
            if min_val <= val <= max_val:
                return val
            print(f"  {C.RED}Please enter a value between {min_val} and {max_val}{C.RESET}")
        except ValueError:
            print(f"  {C.RED}Please enter a valid number{C.RESET}")


def preview_text(text, max_lines=6, max_width=60):
    lines = text.split('\n')
    preview_lines = lines[:max_lines]
    truncated = len(lines) > max_lines

    print(f"  {C.WHITE}{C.BOLD}📋 Clipboard Content:{C.RESET}")
    print(f"  {C.DIM}{'─' * 50}{C.RESET}")
    for line in preview_lines:
        display = line[:max_width]
        if len(line) > max_width:
            display += '…'
        print(f"  {C.WHITE}  {display}{C.RESET}")
    if truncated:
        print(f"  {C.DIM}  ... +{len(lines) - max_lines} more lines{C.RESET}")
    print(f"  {C.DIM}{'─' * 50}{C.RESET}")
    print(f"  {C.DIM}Total: {len(text)} characters, {len(lines)} lines{C.RESET}\n")


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

def main():
    global PLATFORM

    init_colors()
    print_banner()

    # Detect platform
    PLATFORM = detect_platform()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Read clipboard
    clipboard = get_clipboard()
    if not clipboard or clipboard.strip() == '':
        print(f"\n  {C.RED}{C.BOLD}✗ Clipboard is empty!{C.RESET}")
        print(f"  {C.DIM}Copy some text to your clipboard first, then run again.{C.RESET}\n")
        sys.exit(1)

    print()
    preview_text(clipboard)

    # ── Configuration ──────────────────────────────────
    print(f"  {C.CYAN}{C.BOLD}⚙  Configuration{C.RESET}")
    print(f"  {C.DIM}Press Enter to accept defaults{C.RESET}\n")

    delay = get_int_input(
        f"{C.YELLOW}⏱  Delay before typing (seconds){C.RESET}",
        default=5, min_val=1, max_val=120)

    wpm = get_int_input(
        f"{C.YELLOW}⚡ Typing speed (WPM){C.RESET}",
        default=65, min_val=10, max_val=500)

    error_pct = get_float_input(
        f"{C.YELLOW}💥 Error rate (0-15%){C.RESET}",
        default=3.0, min_val=0.0, max_val=15.0)
    error_rate = error_pct / 100.0

    # ── Summary ────────────────────────────────────────
    print(f"\n  {C.DIM}{'─' * 50}{C.RESET}")
    print(f"  {C.WHITE}{C.BOLD}📝 Ready to type:{C.RESET}")
    print(f"    {C.CYAN}•{C.RESET} Delay:      {C.WHITE}{delay}s{C.RESET}")
    print(f"    {C.CYAN}•{C.RESET} Speed:      {C.WHITE}{wpm} WPM{C.RESET}")
    print(f"    {C.CYAN}•{C.RESET} Error rate: {C.WHITE}{error_pct}%{C.RESET}")
    print(f"    {C.CYAN}•{C.RESET} Characters: {C.WHITE}{len(clipboard)}{C.RESET}")

    est_minutes = len(clipboard) / (wpm * 5)
    if est_minutes < 1:
        est_str = f"{int(est_minutes * 60)}s"
    else:
        est_str = f"{est_minutes:.1f}min"
    print(f"    {C.CYAN}•{C.RESET} Est. time:  {C.WHITE}~{est_str}{C.RESET}")
    print(f"  {C.DIM}{'─' * 50}{C.RESET}")

    # ── Confirm ────────────────────────────────────────
    print()
    confirm = input(f"  {C.GREEN}{C.BOLD}▶  Press Enter to start (or 'q' to quit): {C.RESET}").strip().lower()
    if confirm == 'q':
        print(f"\n  {C.DIM}Bye!{C.RESET}\n")
        sys.exit(0)

    simulate_typing(clipboard, wpm, error_rate, delay)


if __name__ == '__main__':
    main()
