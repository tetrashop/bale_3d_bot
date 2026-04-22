import os
from subprocess import call
def fix_indents_in_files(root_dir):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(subdir, file)
                print(f'Fixing indentation in {filepath}')
                call(['python', 'fix_indent_safe.py', filepath])
                fix_indents_in_files('.')
