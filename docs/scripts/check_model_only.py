"""Assert a patched .pbit changed the model and NOTHING else.

After two rounds of Desktop rejecting hand-edited PBIR visuals, the
report layer is now off limits. This proves it: every package part except
DataModelSchema must be byte-identical to the original.

That is a far stronger guarantee than "the JSON still parses", and it is
the one that matters - if not a single byte of the report changed, the
report cannot be the reason Desktop refuses the file.
"""
import sys
import zipfile
from pathlib import Path

ALLOWED = {"DataModelSchema", "UnappliedChanges"}


def parts(p):
    with zipfile.ZipFile(p) as z:
        return {n: z.read(n) for n in z.namelist()}


def main():
    orig, new = Path(sys.argv[1]), Path(sys.argv[2])
    a, b = parts(orig), parts(new)
    problems = []

    if set(a) != set(b):
        for n in sorted(set(a) - set(b)):
            problems.append(f"part lost: {n}")
        for n in sorted(set(b) - set(a)):
            problems.append(f"part added: {n}")

    changed = [n for n in sorted(set(a) & set(b)) if a[n] != b[n]]
    for n in changed:
        if n not in ALLOWED:
            problems.append(f"changed outside the model: {n}")

    report = [n for n in changed if n.startswith("Report/")]
    print(f"{new.name}")
    print(f"  parts: {len(b)}   changed: {len(changed)}   "
          f"report parts changed: {len(report)}")
    if problems:
        for p in problems[:20]:
            print(f"  FAIL {p}")
        return 1
    print("  only DataModelSchema differs - the report layer is untouched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
