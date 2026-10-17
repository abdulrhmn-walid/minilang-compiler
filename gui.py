"""Tkinter window: type or open a MiniLang program, press Compile, read the results in tabs.

Contains no compiler logic at all: it only calls compile_source() and shows the text
produced by report.py. Run with:  python gui.py
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkfont
from tkinter.scrolledtext import ScrolledText

import report
from pipeline import compile_source

SAMPLE = """# MiniLang example: press F5 or the Compile button
int x = 10;
float y = 3.5;
char c = 'a';
if (x > 1) {
    y = y - 1;
} else {
    x = x + 1;
}
while (y > 1) {
    y = y - 1;
}
"""

TABS = ("Messages", "Tokens", "Symbol Table", "FIRST/FOLLOW", "LL(1) Table", "Parse Tree")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MiniLang Compiler")
        self.geometry("1180x720")
        self.minsize(820, 480)

        self.mono = tkfont.nametofont("TkFixedFont").copy()
        self.mono.configure(size=11)
        self.outputs = {}

        self._build_toolbar()
        self._build_statusbar()     # packed before the body so it can never be pushed out of view
        self._build_body()

        self.editor.insert("1.0", SAMPLE)
        self._show("FIRST/FOLLOW", report.first_follow_text())     # these two never change
        self._show("LL(1) Table", report.ll1_text())
        self.compile()

    # ------------------------------------------------------------------ layout
    def _build_toolbar(self):
        bar = ttk.Frame(self, padding=(8, 6))
        bar.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(bar, text="Open file...", command=self.open_file).pack(side=tk.LEFT)
        ttk.Button(bar, text="Compile  (F5)", command=self.compile).pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text="Clear", command=lambda: self.editor.delete("1.0", tk.END)).pack(side=tk.LEFT)
        self.bind("<F5>", lambda e: self.compile())
        self.bind("<Control-Return>", lambda e: self.compile())

    def _build_body(self):
        panes = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        left = ttk.Frame(panes)
        ttk.Label(left, text="Source code").pack(anchor="w")
        self.editor = ScrolledText(left, wrap=tk.NONE, font=self.mono, undo=True, width=48)
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.bind("<KeyRelease>", self._update_cursor)
        self.editor.bind("<ButtonRelease-1>", self._update_cursor)
        panes.add(left, weight=1)

        notebook = ttk.Notebook(panes)
        for name in TABS:
            widget = ScrolledText(notebook, wrap=tk.NONE, font=self.mono, state=tk.DISABLED)
            notebook.add(widget, text=name)
            self.outputs[name] = widget
        messages = self.outputs["Messages"]
        messages.tag_configure("error", foreground="#b91c1c")
        messages.tag_configure("warning", foreground="#b45309")
        messages.tag_configure("ok", foreground="#15803d")
        panes.add(notebook, weight=2)

    def _build_statusbar(self):
        self.status = tk.StringVar(value="Ready")
        self.cursor = tk.StringVar(value="Line 1, Col 1")
        bar = ttk.Frame(self, padding=(8, 2))
        bar.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(bar, textvariable=self.status).pack(side=tk.LEFT)
        ttk.Label(bar, textvariable=self.cursor).pack(side=tk.RIGHT)

    # ------------------------------------------------------------------ helpers
    def _show(self, tab, text):
        widget = self.outputs[tab]
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.config(state=tk.DISABLED)

    def _update_cursor(self, _event=None):
        line, col = self.editor.index(tk.INSERT).split(".")
        self.cursor.set(f"Line {line}, Col {int(col) + 1}")

    # ------------------------------------------------------------------ actions
    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open a MiniLang program",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, encoding="utf-8-sig") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError) as e:
            messagebox.showerror("Cannot open file", str(e))
            return
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", text)
        self.compile()

    def compile(self):
        source = self.editor.get("1.0", "end-1c")
        try:
            result = compile_source(source)
        except Exception as e:                      # a bug in the compiler must not freeze the window
            messagebox.showerror("Internal error", f"{type(e).__name__}: {e}")
            return

        messages = self.outputs["Messages"]
        messages.config(state=tk.NORMAL)
        messages.delete("1.0", tk.END)
        if not result.diagnostics.items:
            messages.insert(tk.END, "No errors or warnings.\n", "ok")
        for d in result.diagnostics.sorted():
            messages.insert(tk.END, str(d) + "\n", "error" if d.is_error else "warning")
        messages.insert(tk.END, "\n" + report.summary(result) + "\n",
                        "ok" if result.succeeded else "error")
        messages.config(state=tk.DISABLED)

        self._show("Tokens", report.tokens_text(result.tokens))
        self._show("Symbol Table", report.symbols_section(result))
        self._show("Parse Tree", report.tree_section(result))
        self.status.set(report.summary(result))


if __name__ == "__main__":
    App().mainloop()
