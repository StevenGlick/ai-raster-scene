"""Build the distributable skill zip.

    python package_skill.py            -> dist/<name>.zip
    python package_skill.py --list     -> just print what would go in

The skill is everything Claude needs at runtime: SKILL.md, the scripts, the scene
format reference, the example scenes and requirements.txt. The repo also carries a
README gallery, tests and CI config, which are several megabytes of PNG and are no
use inside a skill - those are deliberately left out.

The skill name is read from the SKILL.md front matter, so renaming the skill only
means editing SKILL.md.
"""
import argparse
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))

# Files and directories that make up the skill, relative to the repo root.
INCLUDE_FILES = ['SKILL.md', 'requirements.txt', 'LICENSE']
INCLUDE_DIRS = ['scripts', 'references', 'examples']
# Never ship these, wherever they turn up.
EXCLUDE_DIRS = {'__pycache__', '.git', '.pytest_cache'}
EXCLUDE_EXTS = {'.pyc', '.pyo'}


def skill_name(path=None):
    """Read `name:` out of the SKILL.md YAML front matter."""
    path = path or os.path.join(ROOT, 'SKILL.md')
    with open(path, encoding='utf-8') as f:
        if f.readline().strip() != '---':
            raise SystemExit('SKILL.md does not start with YAML front matter')
        for line in f:
            if line.strip() == '---':
                break
            if line.startswith('name:'):
                return line.split(':', 1)[1].strip()
    raise SystemExit('no `name:` found in the SKILL.md front matter')


def members():
    """Every (absolute path, path inside the zip) pair that belongs in the skill."""
    out = []
    for rel in INCLUDE_FILES:
        src = os.path.join(ROOT, rel)
        if os.path.exists(src):
            out.append((src, rel))
    for d in INCLUDE_DIRS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, d)):
            dirnames[:] = [n for n in dirnames if n not in EXCLUDE_DIRS]
            for fn in sorted(filenames):
                if os.path.splitext(fn)[1] in EXCLUDE_EXTS:
                    continue
                src = os.path.join(dirpath, fn)
                out.append((src, os.path.relpath(src, ROOT).replace(os.sep, '/')))
    return sorted(out, key=lambda p: p[1])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--list', action='store_true', help='print the file list and exit')
    ap.add_argument('-o', '--out', help='output zip path (default dist/<name>.zip)')
    args = ap.parse_args()

    name = skill_name()
    files = members()
    total = sum(os.path.getsize(s) for s, _ in files)

    if args.list:
        for _, arc in files:
            print(arc)
        print(f'\n{len(files)} files, {total / 1024:.0f} KB uncompressed', file=sys.stderr)
        return

    out = args.out or os.path.join(ROOT, 'dist', name + '.zip')
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    # Everything sits under a single <name>/ folder, which is what the skill loaders expect.
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for src, arc in files:
            z.write(src, f'{name}/{arc}')
    print(f'{out}  ({len(files)} files, {total / 1024:.0f} KB -> '
          f'{os.path.getsize(out) / 1024:.0f} KB zipped)')


if __name__ == '__main__':
    main()
