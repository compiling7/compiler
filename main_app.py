"""CompilerLab — PyWebView desktop application entry point.

Architecture:
  Flask backend (web_app.py) running on localhost:PORT
  PyWebView native window loads the Flask URL
  PyInstaller bundles everything into a single .exe
"""

import os
import sys
import threading
import webbrowser

# Ensure project root is on sys.path for bundled executables
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

# ── Configuration ──────────────────────────────
HOST = "127.0.0.1"
PORT = 19876  # Uncommon port to avoid conflicts
DEBUG = False

# Flag to signal server shutdown
_shutdown_event = threading.Event()


def start_server():
    """Start Flask server in a background thread."""
    from web_app import create_app
    app = create_app()
    # Suppress Flask output
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR if not DEBUG else logging.DEBUG)

    # Run Flask without reloader
    app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=False)


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class SaveApi:
    """Native API exposed to JavaScript via PyWebView JS bridge.

    Methods here can be called from JS as window.pywebview.api.<method>(...).
    """

    def save_file(self, content, filename="compiler_output.txt"):
        """Show native save dialog and write content to the selected file."""
        import webview

        # Show native OS save dialog
        file_path = webview.windows[0].create_file_dialog(
            webview.FileDialog.SAVE,
            save_filename=filename,
            file_types=('Text files (*.txt)', 'All files (*.*)'),
        )
        if not file_path:
            return False  # User cancelled

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception:
            return False


def main():
    """Main entry point."""
    # Start Flask server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Import pywebview (lazy import for faster startup)
    import webview

    # Create the native window
    window_title = "CompilerLab · Rust 编译器可视化"
    url = f"http://{HOST}:{PORT}/"

    # Native API bridge for file operations
    save_api = SaveApi()

    # Window config: large enough for the IDE layout
    window = webview.create_window(
        title=window_title,
        url=url,
        js_api=save_api,
        width=1440,
        height=900,
        min_size=(1024, 680),
        resizable=True,
        fullscreen=False,
        text_select=True,
        easy_drag=False,
    )

    # Run the window (blocks until closed)
    webview.start(
        debug=DEBUG,
        http_server=False,  # We handle HTTP ourselves via Flask
        private_mode=False,
    )


if __name__ == "__main__":
    main()
