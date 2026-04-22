#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys
BAD_CHARS = {"\u200c", "\u200b", "\u200d", "\ufeff"}
INDENT = 4
def backup_file(path: Path) -> Path:
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    return bak
    def remove_bad_chars(text: str) -> str:
        return "".join(ch for ch in text if ch not in BAD_CHARS)
        def fix_simple_indentation(text: str) -> str:
            lines = text.splitlines()
            out = []
            level = 0
            for raw in lines:
                line = raw.expandtabs(INDENT).rstrip()
                stripped = line.lstrip()
                if not stripped:
                    out.append("")
                    continue
                    if stripped.startswith(("elif ", "else:", "except ", "finally:")):
                        level = max(0, level - 1)
                        out.append((" " * (level * INDENT)) + stripped)
                        if stripped.endswith(":"):
                            level += 1
                            return "\n".join(out) + "\n"
                            def process_file(path: Path) -> None:
                                backup_file(path)
                                original = path.read_text(encoding="utf-8", errors="ignore")
                                cleaned = remove_bad_chars(original)
                                fixed = fix_simple_indentation(cleaned)
                                path.write_text(fixed, encoding="utf-8")
                                print(f"fixed: {path}  (backup: {path}.bak)")
                                def main():
                                    if len(sys.argv) < 2:
                                        print("Usage: python3 fix_indent_safe.py <file.py> [more files...]")
                                        sys.exit(1)
                                        for arg in sys.argv[1:]:
                                            p = Path(arg)
                                            if p.is_file() and p.suffix == ".py":
                                                process_file(p)
                                            else:
                                                print(f"skip: {p}")
                                                if __name__ == "__main__":
                                                    main()
