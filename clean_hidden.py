#!/usr/bin/env python3
from pathlib import Path
bad = {'\u200c', '\u200b', '\u200d', '\ufeff'}
for p in Path('.').glob('*.py'):
    s = p.read_text(encoding='utf-8', errors='ignore')
    t = ''.join(ch for ch in s if ch not in bad)
    p.write_text(t, encoding='utf-8')
    print('cleaned', p)
