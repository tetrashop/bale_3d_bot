from pathlib import Path
import sys
def fix_indent_simple(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    level = 0
    INDENT = 4
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
                    path.write_text("\n".join(out) + "\n", encoding="utf-8")
                    print(f"fixed indent: {path}")
                    if __name__ == "__main__":
                        for arg in sys.argv[1:]:
                            p = Path(arg)
                            if p.is_file() and p.suffix == ".py":
                                fix_indent_simple(p)
