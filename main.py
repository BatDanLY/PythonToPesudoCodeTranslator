import customtkinter
import tkinter as tk
import keyword
import re


# ==========================================
# Custom Code Editor
# ==========================================
class CodeEditor(customtkinter.CTkFrame):
    def __init__(self, master, title="Editor", state="normal"):
        super().__init__(master, fg_color="#1e1e1e", corner_radius=14)

        self.default_state = state

        # ==================================
        # Outer Border
        # ==================================
        border = customtkinter.CTkFrame(
            self,
            fg_color="#2d2d30",
            corner_radius=14
        )
        border.pack(fill="both", expand=True, padx=2, pady=2)

        # ==================================
        # Top Bar
        # ==================================
        top_bar = customtkinter.CTkFrame(
            border,
            fg_color="#252526",
            height=50,
            corner_radius=12
        )
        top_bar.pack(fill="x", padx=2, pady=2)

        top_bar.pack_propagate(False)

        # Title
        title_label = customtkinter.CTkLabel(
            top_bar,
            text=title,
            font=("Segoe UI", 16, "bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="left", padx=15)

        # Button Frame
        button_frame = customtkinter.CTkFrame(
            top_bar,
            fg_color="transparent"
        )
        button_frame.pack(side="right", padx=10)

        # Copy Button
        copy_button = customtkinter.CTkButton(
            button_frame,
            text="Copy",
            width=80,
            height=32,
            corner_radius=8,
            command=self.copy_text
        )
        copy_button.pack(side="left", padx=5)

        # Clear Button
        clear_button = customtkinter.CTkButton(
            button_frame,
            text="Clear",
            width=80,
            height=32,
            corner_radius=8,
            fg_color="#c42b1c",
            hover_color="#a12418",
            command=self.clear_text
        )
        clear_button.pack(side="left", padx=5)

        # ==================================
        # Editor Area
        # ==================================
        editor_frame = tk.Frame(
            border,
            bg="#1e1e1e"
        )
        editor_frame.pack(fill="both", expand=True, padx=2, pady=(0, 2))

        # Shared font
        self.editor_font = ("Consolas", 13)

        # Line Numbers
        self.line_numbers = tk.Text(
            editor_frame,
            width=5,
            padx=10,
            pady=10,
            takefocus=0,
            border=0,
            background="#252526",
            foreground="#858585",
            state="disabled",
            font=self.editor_font,
            wrap="none"
        )

        self.line_numbers.pack(side="left", fill="y")

        # Main Text Editor
        self.text = tk.Text(
            editor_frame,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            undo=True,
            wrap="none",
            font=self.editor_font,
            padx=12,
            pady=10,
            border=0,
            selectbackground="#264f78",
            tabs=("32"),
            state=state
        )

        self.text.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = customtkinter.CTkScrollbar(
            editor_frame,
            command=self.on_scroll
        )

        scrollbar.pack(side="right", fill="y")

        self.text.configure(yscrollcommand=scrollbar.set)

        # Keep line numbers synced
        self.text.bind("<MouseWheel>", self.sync_scroll)
        self.text.bind("<Button-4>", self.sync_scroll)
        self.text.bind("<Button-5>", self.sync_scroll)
        self.text.bind("<KeyRelease>", self.on_key_release)

        # Python keywords
        self.python_keywords = keyword.kwlist

        # Syntax highlighting
        self.text.tag_configure("keyword", foreground="#569CD6")
        self.text.tag_configure("string", foreground="#CE9178")
        self.text.tag_configure("comment", foreground="#6A9955")
        self.text.tag_configure("number", foreground="#B5CEA8")
        self.text.tag_configure("function", foreground="#DCDCAA")
        self.text.tag_configure("class", foreground="#4EC9B0")

        # Events
        self.text.bind("<Tab>", self.insert_spaces)
        self.text.bind("<Return>", self.auto_indent)

        self.update_line_numbers()

    # ==================================
    # Scroll Sync
    # ==================================
    def on_scroll(self, *args):
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def sync_scroll(self, event=None):
        self.line_numbers.yview_moveto(self.text.yview()[0])

    # ==================================
    # Buttons
    # ==================================
    def clear_text(self):
        self.set_text("")

    def copy_text(self):
        self.clipboard_clear()
        self.clipboard_append(self.get_text())

    # ==================================
    # Helpers
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

        self.highlight_syntax()
        self.update_line_numbers()

    # ==================================
    # Editor Features
    # ==================================
    def insert_spaces(self, event):
        self.text.insert("insert", "    ")
        return "break"

    def auto_indent(self, event):
        current_line = self.text.get("insert linestart", "insert")

        indent = re.match(r"\s*", current_line).group()

        self.text.insert("insert", f"\n{indent}")

        if current_line.strip().endswith(":"):
            self.text.insert("insert", "    ")

        return "break"

    def on_key_release(self, event=None):
        self.highlight_syntax()
        self.update_line_numbers()
        self.sync_scroll()

    # ==================================
    # Line Numbers
    # ==================================
    def update_line_numbers(self):
        self.line_numbers.config(state="normal")

        self.line_numbers.delete("1.0", "end")

        line_count = int(self.text.index("end-1c").split(".")[0])

        line_numbers_string = "\n".join(
            str(i) for i in range(1, line_count + 1)
        )

        self.line_numbers.insert("1.0", line_numbers_string)

        self.line_numbers.config(state="disabled")

        self.sync_scroll()

    # ==================================
    # Syntax Highlighting
    # ==================================
    def highlight_syntax(self):

        for tag in [
            "keyword",
            "string",
            "comment",
            "number",
            "function",
            "class"
        ]:
            self.text.tag_remove(tag, "1.0", "end")

        # Keywords
        for kw in self.python_keywords:
            self.highlight_pattern(
                rf"\b{kw}\b",
                "keyword"
            )

        # Strings
        self.highlight_pattern(r'"[^"]*"', "string")
        self.highlight_pattern(r"'[^']*'", "string")

        # Comments
        self.highlight_pattern(r"#.*", "comment")

        # Numbers
        self.highlight_pattern(r"\b\d+\b", "number")

        # Functions
        self.highlight_pattern(
            r"\bdef\s+([a-zA-Z_]\w*)",
            "function",
            group=1
        )

        # Classes
        self.highlight_pattern(
            r"\bclass\s+([a-zA-Z_]\w*)",
            "class",
            group=1
        )

    def highlight_pattern(self, pattern, tag, group=0):

        text = self.text.get("1.0", "end-1c")

        for match in re.finditer(pattern, text, re.MULTILINE):

            start = self.text.index(
                f"1.0 + {match.start(group)} chars"
            )

            end = self.text.index(
                f"1.0 + {match.end(group)} chars"
            )

            self.text.tag_add(tag, start, end)


def convert_expression(expr):
    """Convert a Python expression to OCR pseudocode style."""
    expr = expr.strip()

    # Boolean / None literals
    expr = re.sub(r'\bTrue\b', 'TRUE', expr)
    expr = re.sub(r'\bFalse\b', 'FALSE', expr)
    expr = re.sub(r'\bNone\b', 'NULL', expr)

    # Logical operators (whole words only)
    expr = re.sub(r'\band\b', 'AND', expr)
    expr = re.sub(r'\bor\b', 'OR', expr)
    expr = re.sub(r'\bnot\b', 'NOT', expr)

    # Arithmetic operators
    expr = re.sub(r'\*\*', '^', expr)  # ** -> ^
    expr = re.sub(r'//', 'DIV', expr)  # // -> DIV
    expr = re.sub(r'%', 'MOD', expr)  # %  -> MOD

    # len(x) -> x.length
    expr = re.sub(r'\blen\((\w+)\)', r'\1.length', expr)

    # String slicing: s[a:b] -> s.subString(a, b-a)
    def convert_substring(m):
        var, start, end = m.group(1), m.group(2), m.group(3)
        if start and end:
            try:
                length = int(end) - int(start)
                return f"{var}.subString({start}, {length})"
            except ValueError:
                return f"{var}.subString({start}, {end}-{start})"
        return m.group(0)

    expr = re.sub(r'(\w+)\[(\d+):(\d+)\]', convert_substring, expr)

    # Remove self. references
    expr = re.sub(r'\bself\.', '', expr)

    # super().__init__ -> super.new
    expr = re.sub(r'super\(\)\.__init__\((.*?)\)', r'super.new(\1)', expr)
    expr = re.sub(r'super\(\)\.', 'super.', expr)

    return expr


def python_to_pseudocode(code):
    """
    Convert Python source code to OCR AS/A Level pseudocode (H046/H446).

    Spec coverage:
      Variables & assignment      global keyword
      Casting: int() str() float() Output: print()
      Input: input()              Comments: # -> //
      Count-controlled loops: for/range -> for i=x to y / next i
      Condition-controlled loops: while -> while/endwhile
      Selection: if/elseif/else/endif
      Switch: match/case -> switch/case/endswitch
      Functions (with return)     Procedures (no return)
      Classes, constructors (new), Inheritance (inherits / super)
      Arrays: list -> array[n] + indexed assignments
      File I/O: openRead/openWrite, readLine/writeLine/close
      Operators: AND OR NOT ^ DIV MOD  len()->length  slice->subString
    """

    lines = code.split("\n")
    pseudo = []

    # Stack entries: (python_indent_level, block_type)
    # block_type: root | if | elif | else | for_range:<var> | for_in:<var>
    #             while | function | procedure | class | switch | with
    stack = [(0, "root")]

    # Keys that produce closing keywords when the block ends
    END_KEYWORD = {
        "function": "endfunction",
        "procedure": "endprocedure",
        "class": "endclass",
        "if": "endif",
        "elif": "endif",
        "else": "endif",
        "while": "endwhile",
        "switch": "endswitch",
        "with": "",  # no OCR keyword; file closed explicitly
    }

    # Pre-pass: detect which `def` names contain a `return` statement
    def_has_return = {}
    current_def = None
    def_indent = -1
    for ln in lines:
        s = ln.strip()
        m = re.match(r'def\s+(\w+)\(', s)
        if m:
            current_def = m.group(1)
            def_indent = len(ln) - len(ln.lstrip())
            def_has_return[current_def] = False
            continue
        if current_def:
            this_indent = len(ln) - len(ln.lstrip()) if s else def_indent + 4
            if s and this_indent <= def_indent:
                current_def = None
            elif re.match(r'return\b', s):
                def_has_return[current_def] = True

    def close_blocks_to(target_indent, suppress_one=False):
        """
        Pop and emit closing keywords for all blocks whose indent > target_indent.
        suppress_one: if True, suppress the closing keyword for the innermost block
                      (used for elif/else which continue the same if structure).
        """
        first = True
        while len(stack) > 1 and stack[-1][0] > target_indent:
            blk_indent, btype = stack.pop()
            kw_indent = " " * (blk_indent - 4)
            if suppress_one and first:
                first = False
                continue  # don't emit closing keyword for this one
            first = False
            if btype.startswith("for_range:"):
                var = btype.split(":", 1)[1]
                pseudo.append(kw_indent + f"next {var}")
            elif btype.startswith("for_in:"):
                pass  # no closing keyword
            elif btype in END_KEYWORD and END_KEYWORD[btype]:
                pseudo.append(kw_indent + END_KEYWORD[btype])

    for line in lines:
        stripped = line.strip()

        # ── Blank lines ────────────────────────────────────────────────────────
        if not stripped:
            pseudo.append("")
            continue

        indent = len(line) - len(line.lstrip())
        prefix = " " * indent

        # ── Peek: is this an elif/else? If so, suppress the closing endif ──────
        is_continuation = bool(
            re.match(r'elif\s', stripped) or stripped == "else:"
        )

        # ── Close blocks we've dedented out of ────────────────────────────────
        close_blocks_to(indent, suppress_one=is_continuation)

        # ── Comments ──────────────────────────────────────────────────────────
        if stripped.startswith("#"):
            pseudo.append(prefix + "//" + stripped[1:])
            continue

        # ── pass ──────────────────────────────────────────────────────────────
        if stripped == "pass":
            continue

        # ── global ────────────────────────────────────────────────────────────
        m = re.match(r'global\s+(.*)', stripped)
        if m:
            pseudo.append(prefix + f"global {m.group(1)}")
            continue

        # ── CLASS ─────────────────────────────────────────────────────────────
        m = re.match(r'class\s+(\w+)\s*(?:\((\w*)\))?\s*:', stripped)
        if m:
            name, parent = m.group(1), m.group(2) or ""
            if parent and parent not in ("", "object"):
                pseudo.append(prefix + f"class {name} inherits {parent}")
            else:
                pseudo.append(prefix + f"class {name}")
            stack.append((indent + 4, "class"))
            continue

        # ── DEF ───────────────────────────────────────────────────────────────
        m = re.match(r'def\s+(\w+)\((.*?)\)\s*(?:->.*)?\s*:', stripped)
        if m:
            fname = m.group(1)
            params = m.group(2)

            # Clean params: strip type hints, defaults, 'self'
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

        # ── RETURN ────────────────────────────────────────────────────────────
        m = re.match(r'return\s*(.*)', stripped)
        if m:
            pseudo.append(prefix + f"return {convert_expression(m.group(1))}")
            continue

        # ── PRINT ─────────────────────────────────────────────────────────────
        m = re.match(r'print\((.*)\)\s*$', stripped)
        if m:
            pseudo.append(prefix + f"print({convert_expression(m.group(1))})")
            continue

        # ── INPUT assignment ──────────────────────────────────────────────────
        m = re.match(r'(\w+)\s*=\s*input\((.*?)\)\s*$', stripped)
        if m:
            pseudo.append(prefix + f"{m.group(1)}=input({m.group(2)})")
            continue

        # ── FOR range ─────────────────────────────────────────────────────────
        m = re.match(r'for\s+(\w+)\s+in\s+range\((.*?)\)\s*:', stripped)
        if m:
            var = m.group(1)
            args = [a.strip() for a in m.group(2).split(",")]
            start = "0"
            step = None
            if len(args) == 1:
                stop = args[0]
            elif len(args) == 2:
                start, stop = args
            else:
                start, stop, step = args
            # OCR for is inclusive; range() stop is exclusive -> subtract 1
            try:
                end_val = str(int(stop) - 1)
            except ValueError:
                end_val = f"{stop}-1"
            line_out = f"for {var}={start} to {end_val}"
            if step:
                line_out += f" step {step}"
            pseudo.append(prefix + line_out)
            stack.append((indent + 4, f"for_range:{var}"))
            continue

        # ── FOR in (non-range) ────────────────────────────────────────────────
        m = re.match(r'for\s+(\w+)\s+in\s+(.*?)\s*:', stripped)
        if m:
            var = m.group(1)
            collection = convert_expression(m.group(2))
            pseudo.append(prefix + f"for {var} in {collection}")
            stack.append((indent + 4, f"for_in:{var}"))
            continue

        # ── WHILE ─────────────────────────────────────────────────────────────
        m = re.match(r'while\s+(.*?)\s*:', stripped)
        if m:
            pseudo.append(prefix + f"while {convert_expression(m.group(1))}")
            stack.append((indent + 4, "while"))
            continue

        # ── match/case -> switch/case/endswitch ───────────────────────────────
        m = re.match(r'match\s+(.*?)\s*:', stripped)
        if m:
            pseudo.append(prefix + f"switch {convert_expression(m.group(1))}:")
            stack.append((indent + 4, "switch"))
            continue

        m = re.match(r'case\s+(.*?)\s*:', stripped)
        if m:
            val = m.group(1).strip()
            if val == "_":
                pseudo.append(prefix + "default:")
            else:
                pseudo.append(prefix + f"case {convert_expression(val)}:")
            continue

        # ── IF ────────────────────────────────────────────────────────────────
        m = re.match(r'if\s+(.*?)\s*:', stripped)
        if m:
            pseudo.append(prefix + f"if {convert_expression(m.group(1))} then")
            stack.append((indent + 4, "if"))
            continue

        # ── ELIF  (block already popped by close_blocks_to with suppress) ─────
        m = re.match(r'elif\s+(.*?)\s*:', stripped)
        if m:
            pseudo.append(prefix + f"elseif {convert_expression(m.group(1))} then")
            stack.append((indent + 4, "elif"))
            continue

        # ── ELSE  (block already popped by close_blocks_to with suppress) ─────
        if stripped == "else:":
            pseudo.append(prefix + "else")
            stack.append((indent + 4, "else"))
            continue

        # ── FILE I/O ──────────────────────────────────────────────────────────
        m = re.match(r'(\w+)\s*=\s*open\((.*?),\s*["\']([rwa])["\']\)\s*$', stripped)
        if m:
            var, fname, mode = m.group(1), m.group(2), m.group(3)
            fn = "openRead" if mode == "r" else "openWrite"
            pseudo.append(prefix + f"{var} = {fn}({fname})")
            continue

        m = re.match(r'with\s+open\((.*?),\s*["\']([rwa])["\']\)\s+as\s+(\w+)\s*:', stripped)
        if m:
            fname, mode, var = m.group(1), m.group(2), m.group(3)
            fn = "openRead" if mode == "r" else "openWrite"
            pseudo.append(prefix + f"{var} = {fn}({fname})")
            stack.append((indent + 4, "with"))
            continue

        # Normalise file methods
        stripped = re.sub(r'\.readline\(\)', '.readLine()', stripped)
        stripped = re.sub(r'\.readlines\(\)', '.readLine()', stripped)
        stripped = re.sub(r'\.write\(', '.writeLine(', stripped)

        # ── LIST / ARRAY literal  x = [...] ───────────────────────────────────
        m = re.match(r'(\w+)\s*=\s*\[([^\[\]]*)\]\s*$', stripped)
        if m:
            var = m.group(1)
            contents = m.group(2).strip()
            if not contents:
                pseudo.append(prefix + f"array {var}[]")
            else:
                elements = [e.strip() for e in contents.split(",") if e.strip()]
                pseudo.append(prefix + f"array {var}[{len(elements)}]")
                for i, el in enumerate(elements):
                    pseudo.append(prefix + f"{var}[{i}]={convert_expression(el)}")
            continue

        # ── Fallback: general expression / assignment ─────────────────────────
        line_out = re.sub(r'\bself\.', '', stripped)
        line_out = convert_expression(line_out)
        pseudo.append(prefix + line_out)

    # ── Flush any remaining open blocks ──────────────────────────────────────
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

        self.configure(fg_color="#161616")

        # Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        self.grid_rowconfigure(0, weight=1)

        # ==================================
        # Left Editor
        # ==================================
        self.python_editor = CodeEditor(
            self,
            title="Python Code"
        )

        self.python_editor.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(15, 8),
            pady=15
        )

        # ==================================
        # Middle Controls
        # ==================================
        middle_frame = customtkinter.CTkFrame(
            self,
            fg_color="transparent"
        )

        middle_frame.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        title = customtkinter.CTkLabel(
            middle_frame,
            text="Convert",
            font=("Segoe UI", 18, "bold")
        )

        title.pack(pady=(200, 10))

        convert_button = customtkinter.CTkButton(
            middle_frame,
            text="→",
            width=90,
            height=90,
            font=("Segoe UI", 40, "bold"),
            corner_radius=45,
            command=self.convert_code
        )

        convert_button.pack()

        # ==================================
        # Right Editor
        # ==================================
        self.pseudo_editor = CodeEditor(
            self,
            title="OCR A-Level Pseudocode",
            state="disabled"
        )

        self.pseudo_editor.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=(8, 15),
            pady=15
        )

    # ==================================
    # Convert
    # ==================================
    def convert_code(self):

        python_code = self.python_editor.get_text()

        pseudocode = python_to_pseudocode(python_code)

        self.pseudo_editor.set_text(pseudocode)


# ==========================================
# Run
# ==========================================
if __name__ == "__main__":

    app = App()

    app.mainloop()