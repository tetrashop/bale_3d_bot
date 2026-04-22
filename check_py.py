#!/usr/bin/env python3
from pathlib import Path
import py_compile
import sys
files = (
[Path(x) for x in sys.argv[1:]]
if len(sys.argv) > 1
else list(Path(".").glob("*.py"))
)
for f in files:
    try:
        py_compile.compile(str(f), doraise=True)
        print(f"OK {f}")
    except Exception as e:
        print(f"FAIL {f}: {e}")
