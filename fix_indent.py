from pathlib import Path
import re
import sys
BAD_CHARS = {
"\u200c", # ZWNJ
"\u200b", # ZWSP
"\u200d", # ZWJ
"\ufeff", # BOM
}
DEDENT_BEFORE = (
"elif ", "else:", "except ", "finally:"
)
INDENT_WIDTH = 4
def remove_bad_chars(text: str) -> str:
    return "".join(ch for ch in text if ch not in BAD_CHARS)
    def normalize_line(line: str) -> str:
        # تبدیل tab به 4 فاصله و حذف فاصلههای انتهایی
        return line.expandtabs(INDENT_WIDTH).rstrip()
        def should_dedent_before(line: str) -> bool:
            stripped = line.lstrip()
            return stripped.startswith(DEDENT_BEFORE)
            def should_indent_after(line: str) -> bool:
                stripped = line.rstrip()
                if not stripped:
                    return False
                    # اگر خط با ":" تمام شود، معمولاً باید بلوک بعدی یک سطح برود داخل
                    if stripped.endswith(":"):
                        return True
                        return False
                        def fix_indentation(text: str) -> str:
                            lines = text.splitlines()
                            out = []
                            indent = 0
                            for raw in lines:
                                line = normalize_line(raw)
                                stripped = line.lstrip()
                                if not stripped:
                                    out.append("")
                                    continue
                                    # اگر خط از نوع elif/else/except/finally باشد، یک سطح کم کن
                                    if should_dedent_before(line):
                                        indent = max(0, indent - 1)
                                        # خطوطی که باید در سطح فعلی نوشته شوند
                                        if stripped.startswith((")", "]", "}",)):
                                            indent = max(0, indent - 1)
                                            out.append((" " * (indent * INDENT_WIDTH)) + stripped)
                                            # اگر خط با : تمام میشود، سطح بعدی را زیاد کن
                                            if should_indent_after(line):
                                                indent += 1
                                                return "\n".join(out) + "\n"
                                                def process_file(path: Path) -> None:
                                                    original = path.read_text(encoding="utf-8", errors="ignore")
                                                    cleaned = remove_bad_chars(original)
                                                    fixed = fix_indentation(cleaned)
                                                    path.write_text(fixed, encoding="utf-8")
                                                    print(f"fixed: {path}")
                                                    def main():
                                                        if len(sys.argv) < 2:
                                                            print("Usage: python3 fix_indent.py <file.py> [more files...]")
                                                            sys.exit(1)
                                                            for arg in sys.argv[1:]:
                                                                p = Path(arg)
                                                                if p.is_file() and p.suffix == ".py":
                                                                    process_file(p)
                                                                else:
                                                                    print(f"skip: {p}")
                                                                    if __name__ == "__main__":
                                                                        main()
