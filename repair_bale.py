#!/usr/bin/env python3
# -- coding: utf-8 --
from pathlib import Path
import shutil
import subprocess
import sys
import re
import traceback
TARGET = Path("bale.py")
BACKUP = Path("bale.py.bak")
CLEANED = Path("bale.cleaned.py")
HIDDEN_CHARS = {
"\u200c": "ZERO WIDTH NON-JOINER (U+200C)",
"\u200f": "RIGHT-TO-LEFT MARK (U+200F)",
"\ufeff": "BOM (U+FEFF)",
"\u200b": "ZERO WIDTH SPACE (U+200B)",
"\u202a": "LEFT-TO-RIGHT EMBEDDING (U+202A)",
"\u202b": "RIGHT-TO-LEFT EMBEDDING (U+202B)",
"\u202c": "POP DIRECTIONAL FORMATTING (U+202C)",
"\u202d": "LEFT-TO-RIGHT OVERRIDE (U+202D)",
"\u202e": "RIGHT-TO-LEFT OVERRIDE (U+202E)",
"\u2066": "LEFT-TO-RIGHT ISOLATE (U+2066)",
"\u2067": "RIGHT-TO-LEFT ISOLATE (U+2067)",
"\u2068": "FIRST STRONG ISOLATE (U+2068)",
"\u2069": "POP DIRECTIONAL ISOLATE (U+2069)",
}
def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")
    def write_text(path: Path, text: str):
        path.write_text(text, encoding="utf-8")
        def show_hidden(text: str):
            found = False
            for i, line in enumerate(text.splitlines(), 1):
                hits = [name for ch, name in HIDDEN_CHARS.items() if ch in line]
                if hits:
                    found = True
                    print(f"خط {i}: {', '.join(hits)}")
                    print(repr(line))
                    if not found:
                        print("کاراکتر مخفی پیدا نشد.")
                        def remove_hidden(text: str) -> str:
                            for ch in HIDDEN_CHARS:
                                text = text.replace(ch, "")
                                return text
                                def normalize_newlines(text: str) -> str:
                                    return text.replace("\r\n", "\n").replace("\r", "\n")
                                    def run_compile(path: Path):
                                        p = subprocess.run(
                                        [sys.executable, "-m", "py_compile", str(path)],
                                        capture_output=True,
                                        text=True
                                        )
                                        return p.returncode == 0, p.stdout, p.stderr
                                        def main():
                                            print("=== شروع تعمیر فایل ===")
                                            if not TARGET.exists():
                                                print("فایل bale.py پیدا نشد.")
                                                sys.exit(1)
                                                original = read_text(TARGET)
                                                print(f"فایل: {TARGET}")
                                                print("وضعیت کاراکترهای مخفی:")
                                                show_hidden(original)
                                                print("\n=== ساخت بکاپ ===")
                                                shutil.copy2(TARGET, BACKUP)
                                                print(f"بکاپ ساخته شد: {BACKUP}")
                                                print("\n=== پاکسازی ===")
                                                cleaned = normalize_newlines(original)
                                                cleaned = remove_hidden(cleaned)
                                                write_text(CLEANED, cleaned)
                                                print(f"نسخه پاکسازیشده ذخیره شد: {CLEANED}")
                                                print("\n=== تست کامپایل نسخه پاکسازیشده ===")
                                                ok, out, err = run_compile(CLEANED)
                                                if ok:
                                                    print("کامپایل موفق بود ✅")
                                                    shutil.copy2(CLEANED, TARGET)
                                                    print(f"نسخه سالم جایگزین شد: {TARGET}")
                                                else:
                                                    print("کامپایل ناموفق بود ❌")
                                                    if out.strip():
                                                        print("--- STDOUT ---")
                                                        print(out)
                                                        if err.strip():
                                                            print("--- STDERR ---")
                                                            print(err)
                                                            print("\nفایل اصلی دستنخورده مانده و بکاپ موجود است:")
                                                            print(BACKUP)
                                                            sys.exit(2)
                                                            print("\n=== تست نهایی روی فایل اصلی ===")
                                                            ok2, out2, err2 = run_compile(TARGET)
                                                            if ok2:
                                                                print("فایل اصلی هم سالم است ✅")
                                                            else:
                                                                print("فایل اصلی هنوز خطا دارد ❌")
                                                                if err2.strip():
                                                                    print(err2)
                                                                    print("\n=== پایان ===")
                                                                    print("فایلها:")
                                                                    print(f"- اصلی: {TARGET}")
                                                                    print(f"- بکاپ: {BACKUP}")
                                                                    print(f"- پاکسازیشده: {CLEANED}")
                                                                    if name == "main":
                                                                        try:
                                                                            main()
                                                                        except KeyboardInterrupt:
                                                                            print("\nمتوقف شد.")
                                                                            sys.exit(130)
                                                                        except Exception:
                                                                            print("\nخطای غیرمنتظره:")
                                                                            traceback.print_exc()
                                                                            sys.exit(99)
