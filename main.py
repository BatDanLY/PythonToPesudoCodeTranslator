import customtkinter
import tkinter as tk
import keyword
import re

# ==========================================
# Syntax definitions
# ==========================================

PYTHON_KEYWORDS = set(keyword.kwlist)

# OCR A-Level pseudocode keywords (H046/H446 spec)
PSEUDO_KEYWORDS = {
    # Structure
    "procedure", "endprocedure", "function", "endfunction",
    "class", "endclass", "inherits", "super", "new",
    "public", "private",
    # Selection
    "if", "then", "elseif", "else", "endif",
    "switch", "case", "default", "endswitch",
    # Iteration
    "for", "to", "step", "next", "while", "endwhile",
    "do", "until",
    # I/O
    "print", "input", "openRead", "openWrite",
    "readLine", "writeLine", "close", "endOfFile",
    # Misc
    "return", "global", "array",
    # Operators
    "AND", "OR", "NOT", "MOD", "DIV",
    # Literals
    "TRUE", "FALSE", "NULL",
    # in (for-in loops)
    "in",
}

PSEUDO_BUILTINS = {
    "int", "str", "float",  # casting (OCR uses same names)
}

# ==========================================
# Syntax highlighting config
# ==========================================
# Each rule: (pattern, tag, group, flags)
# flags: re.MULTILINE only for line-safe patterns; never re.DOTALL for line patterns.
# Order matters — rules applied first are painted first; later rules OVERWRITE.
# So: keywords/numbers/operators first, then strings, then comments last (highest priority).

_M = re.MULTILINE   # shorthand

PYTHON_HIGHLIGHT = [
    # --- base tokens (applied first, may be overwritten by strings/comments) ---
    (r"\b\d+(?:\.\d+)?\b",
                                      "number",   0, _M),
    (r"[+\-*/%=<>!&|^~]+",
                                      "operator", 0, _M),
    (r"\b(" + "|".join(sorted(PYTHON_KEYWORDS, key=len, reverse=True)) + r")\b",
                                      "keyword",  0, _M),
    (r"\bself\b",                     "self_kw",  0, _M),
    (r"\bdef\s+([a-zA-Z_]\w*)",      "function", 1, _M),
    (r"\bclass\s+([a-zA-Z_]\w*)",    "class_",   1, _M),
    # --- strings (overwrite keywords that appear inside strings) ---
    # triple-quoted first so they take priority over single-quoted
    (r'""".*?"""',                    "string",   0, _M | re.DOTALL),
    (r"'''.*?'''",                    "string",   0, _M | re.DOTALL),
    (r'"[^"\\\n]*(\\.[^"\\\n]*)*"',  "string",   0, _M),
    (r"'[^'\\\n]*(\\.[^'\\\n]*)*'",  "string",   0, _M),
    # --- comments LAST — highest priority, overwrite everything on the line ---
    (r"#[^\n]*",                      "comment",  0, _M),
]

PSEUDO_HIGHLIGHT = [
    # --- base tokens ---
    (r"\b\d+(?:\.\d+)?\b",
                                      "number",   0, _M),
    (r"\b(procedure|endprocedure|function|endfunction|class|endclass|"
     r"if|then|elseif|else|endif|switch|case|default|endswitch|"
     r"for|to|step|next|while|endwhile|do|until|return|global|"
     r"array|new|inherits|super|public|private|in)\b",
                                      "keyword",  0, _M),
    (r"\b(AND|OR|NOT|MOD|DIV|TRUE|FALSE|NULL)\b",
                                      "operator", 0, _M),
    (r"\b(print|input|openRead|openWrite|readLine|writeLine|close|endOfFile|"
     r"int|str|float)\b",
                                      "builtin",  0, _M),
    (r"\.length\b",                   "builtin",  0, _M),
    (r"\.subString\b",                "builtin",  0, _M),
    (r"\bprocedure\s+(\w+)",         "function", 1, _M),
    (r"\bfunction\s+(\w+)",          "function", 1, _M),
    (r"\bclass\s+(\w+)",             "class_",   1, _M),
    # --- strings ---
    (r'"[^"\\\n]*(\\.[^"\\\n]*)*"',  "string",   0, _M),
    (r"'[^'\\\n]*(\\.[^'\\\n]*)*'",  "string",   0, _M),
    # --- comments LAST ---
    (r"//[^\n]*",                     "comment",  0, _M),
]

# Tag colour schemes
PYTHON_TAGS = {
    "keyword":  "#569CD6",
    "string":   "#CE9178",
    "comment":  "#6A9955",
    "number":   "#B5CEA8",
    "function": "#DCDCAA",
    "class_":   "#4EC9B0",
    "self_kw":  "#9CDCFE",
    "operator": "#D4D4D4",
}

PSEUDO_TAGS = {
    "keyword":  "#C586C0",   # purple — structure keywords
    "operator": "#569CD6",   # blue  — AND/OR/NOT/MOD/DIV/TRUE/FALSE/NULL
    "string":   "#CE9178",
    "comment":  "#6A9955",
    "number":   "#B5CEA8",
    "function": "#DCDCAA",
    "class_":   "#4EC9B0",
    "builtin":  "#9CDCFE",   # light blue — built-in calls
}


# ==========================================
# Custom Code Editor
# ==========================================
class CodeEditor(customtkinter.CTkFrame):
    def __init__(self, master, title="Editor", mode="python", state="normal"):
        super().__init__(master, fg_color="#1e1e1e", corner_radius=14)

        self.default_state = state
        self.mode = mode  # "python" or "pseudo"
        self._highlight_job = None  # debounce handle

        # Choose tag/highlight config based on mode
        self.highlight_rules = PYTHON_HIGHLIGHT if mode == "python" else PSEUDO_HIGHLIGHT
        self.tag_colors = PYTHON_TAGS if mode == "python" else PSEUDO_TAGS

        # ==================================
        # Outer Border
        # ==================================
        border = customtkinter.CTkFrame(self, fg_color="#2d2d30", corner_radius=14)
        border.pack(fill="both", expand=True, padx=2, pady=2)

        # ==================================
        # Top Bar
        # ==================================
        top_bar = customtkinter.CTkFrame(border, fg_color="#252526", height=50, corner_radius=12)
        top_bar.pack(fill="x", padx=2, pady=2)
        top_bar.pack_propagate(False)

        # Mode badge
        badge_color = "#1f4f78" if mode == "python" else "#4a1f78"
        badge_text  = "Python"   if mode == "python" else "OCR Pseudocode"
        badge = customtkinter.CTkLabel(
            top_bar, text=badge_text,
            font=("Consolas", 11),
            text_color="#aaaaaa",
            fg_color=badge_color,
            corner_radius=6,
            width=120, height=24
        )
        badge.pack(side="left", padx=(10, 0), pady=13)

        title_label = customtkinter.CTkLabel(
            top_bar, text=title,
            font=("Segoe UI", 16, "bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="left", padx=10)

        # Button Frame
        button_frame = customtkinter.CTkFrame(top_bar, fg_color="transparent")
        button_frame.pack(side="right", padx=10)

        copy_button = customtkinter.CTkButton(
            button_frame, text="⎘  Copy",
            width=90, height=32, corner_radius=8,
            fg_color="#3a3a3a", hover_color="#505050",
            command=self.copy_text
        )
        copy_button.pack(side="left", padx=5)

        if state == "normal":
            clear_button = customtkinter.CTkButton(
                button_frame, text="✕  Clear",
                width=90, height=32, corner_radius=8,
                fg_color="#c42b1c", hover_color="#a12418",
                command=self.clear_text
            )
            clear_button.pack(side="left", padx=5)

        # ==================================
        # Editor Area
        # ==================================
        editor_frame = tk.Frame(border, bg="#1e1e1e")
        editor_frame.pack(fill="both", expand=True, padx=2, pady=(0, 2))

        self.editor_font = ("Consolas", 13)

        # Line Numbers
        self.line_numbers = tk.Text(
            editor_frame,
            width=4, padx=8, pady=10,
            takefocus=0, border=0,
            background="#252526",
            foreground="#555555",
            state="disabled",
            font=self.editor_font,
            wrap="none",
            cursor="arrow"
        )
        self.line_numbers.pack(side="left", fill="y")

        # Vertical scrollbar (right)
        self.v_scroll = customtkinter.CTkScrollbar(editor_frame, orientation="vertical")
        self.v_scroll.pack(side="right", fill="y")

        # Horizontal scrollbar (bottom)
        h_scroll_frame = tk.Frame(border, bg="#1e1e1e")
        h_scroll_frame.pack(fill="x", padx=2, pady=(0, 2))

        self.h_scroll = customtkinter.CTkScrollbar(
            h_scroll_frame, orientation="horizontal"
        )
        self.h_scroll.pack(fill="x", padx=(44, 12))

        # Main text widget
        self.text = tk.Text(
            editor_frame,
            bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white",
            undo=True, wrap="none",
            font=self.editor_font,
            padx=12, pady=10,
            border=0,
            selectbackground="#264f78",
            tabs="32",
            state=state,
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self._on_text_yscroll,
        )
        self.text.pack(side="left", fill="both", expand=True)

        self.v_scroll.configure(command=self._on_vscroll)
        self.h_scroll.configure(command=self.text.xview)

        # Configure all syntax tags
        for tag, color in self.tag_colors.items():
            self.text.tag_configure(tag, foreground=color)

        # Events
        self.text.bind("<MouseWheel>",  self._on_mousewheel)
        self.text.bind("<Button-4>",    self._on_mousewheel)
        self.text.bind("<Button-5>",    self._on_mousewheel)
        self.text.bind("<KeyRelease>",  self._on_key_release)
        self.text.bind("<Tab>",         self._insert_tab)

        if state == "normal":
            self.text.bind("<Return>",  self._auto_indent)

        self.update_line_numbers()

    # ==================================
    # Scrolling
    # ==================================
    def _on_vscroll(self, *args):
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def _on_text_yscroll(self, first, last):
        self.v_scroll.set(first, last)
        self.line_numbers.yview_moveto(first)

    def _on_mousewheel(self, event):
        # Cross-platform scroll
        if event.num == 4:
            delta = -3
        elif event.num == 5:
            delta = 3
        else:
            delta = int(-event.delta / 40)
        self.text.yview_scroll(delta, "units")
        self.line_numbers.yview_scroll(delta, "units")
        return "break"

    # ==================================
    # Buttons
    # ==================================
    def clear_text(self):
        self.set_text("")

    def copy_text(self):
        content = self.get_text()
        self.clipboard_clear()
        self.clipboard_append(content)

    # ==================================
    # Public API
    # ==================================
    def get_text(self):
        return self.text.get("1.0", "end-1c")

    def set_text(self, content):
        current_state = self.text.cget("state")
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        if current_state == "disabled":
            self.text.config(state="disabled")
        self._schedule_highlight()
        self.update_line_numbers()

    # ==================================
    # Editor behaviour
    # ==================================
    def _insert_tab(self, event):
        self.text.insert("insert", "    ")
        return "break"

    def _auto_indent(self, event):
        current_line = self.text.get("insert linestart", "insert")
        indent = re.match(r"\s*", current_line).group()
        stripped = current_line.strip()

        self.text.insert("insert", f"\n{indent}")

        # Python: indent after colon
        if self.mode == "python" and stripped.endswith(":"):
            self.text.insert("insert", "    ")

        # Pseudocode: indent after 'then', 'else', 'do', procedure/function/class lines
        if self.mode == "pseudo":
            pseudo_openers = re.compile(
                r"\b(then|else|do|procedure\s+\w+|function\s+\w+|class\s+\w+)\s*$",
                re.IGNORECASE
            )
            if pseudo_openers.search(stripped):
                self.text.insert("insert", "    ")

        return "break"

    def _on_key_release(self, event=None):
        self.update_line_numbers()
        self._schedule_highlight()

    # ==================================
    # Debounced syntax highlighting
    # ==================================
    def _schedule_highlight(self):
        """Delay highlight so rapid typing stays smooth."""
        if self._highlight_job:
            self.after_cancel(self._highlight_job)
        self._highlight_job = self.after(120, self._highlight_syntax)

    def _highlight_syntax(self):
        self._highlight_job = None
        text_content = self.text.get("1.0", "end-1c")

        # Remove all existing tags
        for tag in self.tag_colors:
            self.text.tag_remove(tag, "1.0", "end")

        # Rules are ordered so that strings then comments are applied LAST,
        # meaning they overwrite any keyword/operator colouring inside them.
        # Each rule carries its own flags — critically, line-based patterns
        # (comments, single-line strings) must NOT use re.DOTALL.
        for pattern, tag, group, flags in self.highlight_rules:
            self._apply_pattern(pattern, tag, group, flags, text_content)

    def _apply_pattern(self, pattern, tag, group, flags, text_content):
        for match in re.finditer(pattern, text_content, flags):
            try:
                start = self.text.index(f"1.0 + {match.start(group)} chars")
                end   = self.text.index(f"1.0 + {match.end(group)} chars")
                self.text.tag_add(tag, start, end)
            except tk.TclError:
                pass

    # ==================================
    # Line numbers
    # ==================================
    def update_line_numbers(self):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        count = int(self.text.index("end-1c").split(".")[0])
        self.line_numbers.insert("1.0", "\n".join(str(i) for i in range(1, count + 1)))
        self.line_numbers.config(state="disabled")


# ==========================================
# Expression & code converter
# ==========================================

def convert_expression(expr):
    expr = expr.strip()
    expr = re.sub(r'\bTrue\b',  'TRUE',  expr)
    expr = re.sub(r'\bFalse\b', 'FALSE', expr)
    expr = re.sub(r'\bNone\b',  'NULL',  expr)
    expr = re.sub(r'\band\b',   'AND',   expr)
    expr = re.sub(r'\bor\b',    'OR',    expr)
    expr = re.sub(r'\bnot\b',   'NOT',   expr)
    expr = re.sub(r'\*\*',      '^',     expr)
    expr = re.sub(r'//',        'DIV',   expr)
    expr = re.sub(r'%',         'MOD',   expr)
    expr = re.sub(r'\blen\((\w+)\)', r'\1.length', expr)

    def convert_substring(m):
        var, start, end = m.group(1), m.group(2), m.group(3)
        if start and end:
            try:
                return f"{var}.subString({start}, {int(end) - int(start)})"
            except ValueError:
                return f"{var}.subString({start}, {end}-{start})"
        return m.group(0)

    expr = re.sub(r'(\w+)\[(\d+):(\d+)\]', convert_substring, expr)
    expr = re.sub(r'\bself\.', '', expr)
    expr = re.sub(r'super\(\)\.__init__\((.*?)\)', r'super.new(\1)', expr)
    expr = re.sub(r'super\(\)\.', 'super.', expr)
    return expr


def python_to_pseudocode(code):
    lines = code.split("\n")
    pseudo = []
    stack = [(0, "root")]

    END_KEYWORD = {
        "function":  "endfunction",
        "procedure": "endprocedure",
        "class":     "endclass",
        "if":        "endif",
        "elif":      "endif",
        "else":      "endif",
        "while":     "endwhile",
        "switch":    "endswitch",
        "with":      "",
    }

    # Pre-pass: detect functions that contain 'return'
    def_has_return = {}
    current_def = None
    def_indent   = -1
    for ln in lines:
        s = ln.strip()
        m = re.match(r'def\s+(\w+)\(', s)
        if m:
            current_def      = m.group(1)
            def_indent       = len(ln) - len(ln.lstrip())
            def_has_return[current_def] = False
            continue
        if current_def:
            this_indent = len(ln) - len(ln.lstrip()) if s else def_indent + 4
            if s and this_indent <= def_indent:
                current_def = None
            elif re.match(r'return\b', s):
                def_has_return[current_def] = True

    def close_blocks_to(target_indent, suppress_one=False):
        first = True
        while len(stack) > 1 and stack[-1][0] > target_indent:
            blk_indent, btype = stack.pop()
            kw_indent = " " * (blk_indent - 4)
            if suppress_one and first:
                first = False
                continue
            first = False
            if btype.startswith("for_range:"):
                pseudo.append(kw_indent + f"next {btype.split(':',1)[1]}")
            elif btype.startswith("for_in:"):
                pass
            elif btype in END_KEYWORD and END_KEYWORD[btype]:
                pseudo.append(kw_indent + END_KEYWORD[btype])

    for line in lines:
        stripped = line.strip()

        if not stripped:
            pseudo.append("")
            continue

        indent = len(line) - len(line.lstrip())
        prefix = " " * indent

        is_continuation = bool(re.match(r'elif\s', stripped) or stripped == "else:")
        close_blocks_to(indent, suppress_one=is_continuation)

        # Comments
        if stripped.startswith("#"):
            pseudo.append(prefix + "//" + stripped[1:])
            continue

        if stripped == "pass":
            continue

        # global
        m = re.match(r'global\s+(.*)', stripped)
        if m:
            pseudo.append(prefix + f"global {m.group(1)}")
            continue

        # class
        m = re.match(r'class\s+(\w+)\s*(?:\((\w*)\))?\s*:', stripped)
        if m:
            name, parent = m.group(1), m.group(2) or ""
            if parent and parent not in ("", "object"):
                pseudo.append(prefix + f"class {name} inherits {parent}")
            else:
                pseudo.append(prefix + f"class {name}")
            stack.append((indent + 4, "class"))
            continue

        # def
        m = re.match(r'def\s+(\w+)\((.*?)\)\s*(?:->.*)?\s*:', stripped)
        if m:
            fname, params = m.group(1), m.group(2)
            clean = []
            for p in params.split(","):
                p = re.sub(r'\s*:.*$', '', p.strip())
                p = re.sub(r'\s*=.*$', '', p.strip())
                if p and p != "self":
                    clean.append(p)
            params_str = ", ".join(clean)
            if fname == "__init__":
                pseudo.append(prefix + f"public procedure new({params_str})")
                stack.append((indent + 4, "procedure"))
            elif def_has_return.get(fname, False):
                pseudo.append(prefix + f"function {fname}({params_str})")
                stack.append((indent + 4, "function"))
            else:
                pseudo.append(prefix + f"procedure {fname}({params_str})")
                stack.append((indent + 4, "procedure"))
            continue

        # return
        m = re.match(r'return\s*(.*)', stripped)
        if m:
            pseudo.append(prefix + f"return {convert_expression(m.group(1))}")
            continue

        # print
        m = re.match(r'print\((.*)\)\s*$', stripped)
        if m:
            pseudo.append(prefix + f"print({convert_expression(m.group(1))})")
            continue

        # input
        m = re.match(r'(\w+)\s*=\s*input\((.*?)\)\s*$', stripped)
        if m:
            pseudo.append(prefix + f"{m.group(1)}=input({m.group(2)})")
            continue

        # for range
        m = re.match(r'for\s+(\w+)\s+in\s+range\((.*?)\)\s*:', stripped)
        if m:
            var  = m.group(1)
            args = [a.strip() for a in m.group(2).split(",")]
            start, stop, step = "0", args[0], None
            if len(args) == 2:
                start, stop = args
            elif len(args) == 3:
                start, stop, step = args
            try:
                end_val = str(int(stop) - 1)
            except ValueError:
                end_val = f"{stop}-1"
            out = f"for {var}={start} to {end_val}"
            if step:
                out += f" step {step}"
            pseudo.append(prefix + out)
            stack.append((indent + 4, f"for_range:{var}"))
            continue

        # for-in (non-range)
        m = re.match(r'for\s+(\w+)\s+in\s+(.*?)\s*:', stripped)
        if m:
            pseudo.append(prefix + f"for {m.group(1)} in {convert_expression(m.group(2))}")
            stack.append((indent + 4, f"for_in:{m.group(1)}"))
            continue

        # while
        m = re.match(r'while\s+(.*?)\s*:', stripped)
        if m:
            pseudo.append(prefix + f"while {convert_expression(m.group(1))}")
            stack.append((indent + 4, "while"))
            continue

        # match/case
        m = re.match(r'match\s+(.*?)\s*:', stripped)
        if m:
            pseudo.append(prefix + f"switch {convert_expression(m.group(1))}:")
            stack.append((indent + 4, "switch"))
            continue

        m = re.match(r'case\s+(.*?)\s*:', stripped)
        if m:
            val = m.group(1).strip()
            pseudo.append(prefix + ("default:" if val == "_" else f"case {convert_expression(val)}:"))
            continue

        # if
        m = re.match(r'if\s+(.*?)\s*:', stripped)
        if m:
            pseudo.append(prefix + f"if {convert_expression(m.group(1))} then")
            stack.append((indent + 4, "if"))
            continue

        # elif
        m = re.match(r'elif\s+(.*?)\s*:', stripped)
        if m:
            pseudo.append(prefix + f"elseif {convert_expression(m.group(1))} then")
            stack.append((indent + 4, "elif"))
            continue

        # else
        if stripped == "else:":
            pseudo.append(prefix + "else")
            stack.append((indent + 4, "else"))
            continue

        # file open
        m = re.match(r'(\w+)\s*=\s*open\((.*?),\s*["\']([rwa])["\']\)\s*$', stripped)
        if m:
            var, fname, mode = m.group(1), m.group(2), m.group(3)
            pseudo.append(prefix + f"{var} = {'openRead' if mode=='r' else 'openWrite'}({fname})")
            continue

        m = re.match(r'with\s+open\((.*?),\s*["\']([rwa])["\']\)\s+as\s+(\w+)\s*:', stripped)
        if m:
            fname, mode, var = m.group(1), m.group(2), m.group(3)
            pseudo.append(prefix + f"{var} = {'openRead' if mode=='r' else 'openWrite'}({fname})")
            stack.append((indent + 4, "with"))
            continue

        # Normalise file methods before fallback
        stripped = re.sub(r'\.readline\(\)',  '.readLine()',  stripped)
        stripped = re.sub(r'\.readlines\(\)', '.readLine()',  stripped)
        stripped = re.sub(r'\.write\(',       '.writeLine(',  stripped)

        # list/array literal
        m = re.match(r'(\w+)\s*=\s*\[([^\[\]]*)\]\s*$', stripped)
        if m:
            var, contents = m.group(1), m.group(2).strip()
            if not contents:
                pseudo.append(prefix + f"array {var}[]")
            else:
                elements = [e.strip() for e in contents.split(",") if e.strip()]
                pseudo.append(prefix + f"array {var}[{len(elements)}]")
                for i, el in enumerate(elements):
                    pseudo.append(prefix + f"{var}[{i}]={convert_expression(el)}")
            continue

        # Fallback
        line_out = re.sub(r'\bself\.', '', stripped)
        pseudo.append(prefix + convert_expression(line_out))

    close_blocks_to(-1)
    return "\n".join(pseudo)


# ==========================================
# Main App
# ==========================================
class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")

        self.title("Python → OCR A-Level Pseudocode Converter")
        self.geometry("1700x950")
        self.minsize(1100, 600)
        self.configure(fg_color="#161616")

        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # ==================================
        # Header bar
        # ==================================
        header = customtkinter.CTkFrame(self, fg_color="#1a1a1a", height=56, corner_radius=0)
        header.grid(row=0, column=0, columnspan=3, sticky="ew")
        header.grid_propagate(False)

        app_title = customtkinter.CTkLabel(
            header,
            text="Python  →  OCR A-Level Pseudocode",
            font=("Segoe UI", 18, "bold"),
            text_color="#ffffff"
        )
        app_title.pack(side="left", padx=20)

        shortcut_hint = customtkinter.CTkLabel(
            header,
            text="Ctrl+Enter to convert",
            font=("Segoe UI", 12),
            text_color="#666666"
        )
        shortcut_hint.pack(side="right", padx=20)

        # ==================================
        # Python editor (left)
        # ==================================
        self.python_editor = CodeEditor(self, title="Python Code", mode="python")
        self.python_editor.grid(row=1, column=0, sticky="nsew", padx=(15, 8), pady=(10, 0))

        # ==================================
        # Middle controls
        # ==================================
        middle_frame = customtkinter.CTkFrame(self, fg_color="transparent", width=110)
        middle_frame.grid(row=1, column=1, sticky="ns", padx=0, pady=10)
        middle_frame.grid_propagate(False)

        # Vertical spacer to vertically centre button
        middle_frame.grid_rowconfigure(0, weight=1)
        middle_frame.grid_rowconfigure(2, weight=1)
        middle_frame.grid_columnconfigure(0, weight=1)

        btn_container = customtkinter.CTkFrame(middle_frame, fg_color="transparent")
        btn_container.grid(row=1, column=0)

        lbl = customtkinter.CTkLabel(
            btn_container,
            text="Convert",
            font=("Segoe UI", 13, "bold"),
            text_color="#888888"
        )
        lbl.pack(pady=(0, 8))

        self.convert_btn = customtkinter.CTkButton(
            btn_container,
            text="→",
            width=80, height=80,
            font=("Segoe UI", 36, "bold"),
            corner_radius=40,
            fg_color="#1f6aa5",
            hover_color="#1a5a8f",
            command=self.convert_code
        )
        self.convert_btn.pack()

        shortcut_lbl = customtkinter.CTkLabel(
            btn_container,
            text="Ctrl+Enter",
            font=("Segoe UI", 10),
            text_color="#555555"
        )
        shortcut_lbl.pack(pady=(8, 0))

        # ==================================
        # Pseudocode editor (right)
        # ==================================
        self.pseudo_editor = CodeEditor(
            self, title="OCR A-Level Pseudocode",
            mode="pseudo", state="disabled"
        )
        self.pseudo_editor.grid(row=1, column=2, sticky="nsew", padx=(8, 15), pady=(10, 0))

        # ==================================
        # Status bar
        # ==================================
        self.status_bar = customtkinter.CTkFrame(
            self, fg_color="#1a1a1a", height=32, corner_radius=0
        )
        self.status_bar.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.status_bar.grid_propagate(False)

        self.status_label = customtkinter.CTkLabel(
            self.status_bar,
            text="Ready — paste Python code on the left and press Convert.",
            font=("Segoe UI", 11),
            text_color="#666666"
        )
        self.status_label.pack(side="left", padx=16)

        self.line_count_label = customtkinter.CTkLabel(
            self.status_bar,
            text="",
            font=("Segoe UI", 11),
            text_color="#555555"
        )
        self.line_count_label.pack(side="right", padx=16)

        # Keyboard shortcut
        self.bind("<Control-Return>", lambda e: self.convert_code())
        self.python_editor.text.bind("<Control-Return>", lambda e: self.convert_code())

    # ==================================
    # Status helpers
    # ==================================
    def set_status(self, msg, color="#666666"):
        self.status_label.configure(text=msg, text_color=color)
        self.after(4000, lambda: self.status_label.configure(
            text="Ready", text_color="#555555"
        ))

    # ==================================
    # Convert
    # ==================================
    def convert_code(self):
        python_code = self.python_editor.get_text().strip()

        if not python_code:
            self.set_status("⚠  Nothing to convert — paste some Python first.", "#e8a838")
            return

        try:
            pseudocode = python_to_pseudocode(python_code)
            self.pseudo_editor.set_text(pseudocode)

            in_lines  = python_code.count("\n") + 1
            out_lines = pseudocode.count("\n") + 1
            self.line_count_label.configure(
                text=f"Python: {in_lines} lines  →  Pseudocode: {out_lines} lines"
            )
            self.set_status("✓  Conversion complete.", "#4ec94e")

        except Exception as exc:
            self.set_status(f"✗  Error during conversion: {exc}", "#e84e4e")


# ==========================================
# Run
# ==========================================
if __name__ == "__main__":
    app = App()
    app.mainloop()