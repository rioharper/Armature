"""
layout.py — the code-line budget every module in this model is held to.

The rules live in the plugin's `references/model-layout.md`; this file is how
a copied project enforces them without access to the plugin. Stdlib only, so
it runs where SymPy and SciPy do not:

    python analysis/model/layout.py     # the size table; exit 1 on a violation

`run_all.py` discovers the checks below like any other, so the full run and
`pytest` fail on a module over budget. Running one milestone
(`run_all.py kinematics`) leaves them out: a file still being written is not
red-barred mid-work.
"""

import ast
import io
import sys
import tokenize
from pathlib import Path

MILESTONE = (99, "Layout: code-line budget")

BUDGET = 250
EXEMPT = "LAYOUT_EXEMPT"
HERE = Path(__file__).resolve().parent
# Reported beside the modules for information only; notes carry no budget.
NOTES = HERE.parent / "derivation"

_NOT_CODE = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
             tokenize.DEDENT, tokenize.ENCODING, tokenize.ENDMARKER}
_HAS_DOCSTRING = (ast.Module, ast.ClassDef, ast.FunctionDef,
                  ast.AsyncFunctionDef)


def code_lines(source):
    """
    Lines of `source` that carry code: not blank, not comment-only, and not
    part of a docstring. A string that is data rather than a docstring counts
    on every line it spans.
    """
    tree = ast.parse(source)
    lines = source.splitlines()

    def chars(row, byte_col):   # ast columns are UTF-8 bytes; tokenize's are chars
        return len(lines[row - 1].encode()[:byte_col].decode(errors="ignore"))

    spans = []
    for node in ast.walk(tree):
        if not isinstance(node, _HAS_DOCSTRING) or not node.body:
            continue
        doc = node.body[0]
        if (isinstance(doc, ast.Expr) and isinstance(doc.value, ast.Constant)
                and isinstance(doc.value.value, str)):
            spans.append(((doc.lineno, chars(doc.lineno, doc.col_offset)),
                          (doc.end_lineno,
                           chars(doc.end_lineno, doc.end_col_offset))))

    rows = set()
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type in _NOT_CODE:
            continue
        if tok.type == tokenize.STRING and any(
                start <= tok.start and tok.end <= end for start, end in spans):
            continue
        rows.update(range(tok.start[0], tok.end[0] + 1))
    return len(rows)


def exemption(source, where):
    """
    The module's stated reason for standing over budget, or None.

    An exemption is a module-level `LAYOUT_EXEMPT = "<why this cannot split>"`.
    Anything else assigned to that name — True, an empty string, a number —
    raises, so an exemption cannot be claimed without being argued.
    """
    for node in ast.parse(source).body:
        targets = (node.targets if isinstance(node, ast.Assign)
                   else [node.target] if isinstance(node, ast.AnnAssign)
                   else [])
        if not any(isinstance(t, ast.Name) and t.id == EXEMPT for t in targets):
            continue
        value = node.value
        if (isinstance(value, ast.Constant) and isinstance(value.value, str)
                and value.value.strip()):
            return " ".join(value.value.split())
        raise ValueError(f"{where}: {EXEMPT} must be a non-empty string giving "
                         f"the reason this module stays over {BUDGET} code lines")
    return None


def model_files(root=HERE):
    """Every .py in `root` and one level into its packages — discovery's reach."""
    files = sorted(root.glob("*.py"))
    for package in sorted(p for p in root.iterdir() if (p / "__init__.py").is_file()):
        files += sorted(package.glob("*.py"))
    return files


def size_table(root=HERE):
    """One `(relative path, code lines, exemption reason or None)` per file."""
    rows = []
    for path in model_files(root):
        source = tokenize.open(path).read()
        where = path.relative_to(root).as_posix()
        rows.append((where, code_lines(source), exemption(source, where)))
    return rows


def test_modules_within_budget():
    over = [f"{where} ({count} code lines)"
            for where, count, reason in size_table()
            if count > BUDGET and reason is None]
    assert not over, (
        f"over the {BUDGET}-code-line budget: {', '.join(over)}; split along "
        f"the note's sections, or declare {EXEMPT} with the reason it cannot")
    print(f"  [PASS] every module within {BUDGET} code lines or exempt with a reason")


def test_checks_modules_are_paired():
    """A checks module whose module was renamed away never runs; say so."""
    orphans = [path.relative_to(HERE).as_posix() for path in model_files()
               if path.stem.endswith("_checks")
               and not path.with_name(path.stem[:-len("_checks")] + ".py").is_file()]
    assert not orphans, f"checks modules with no module beside them: {orphans}"
    print("  [PASS] every checks module pairs with a module")


if __name__ == "__main__":
    print(f"{'module':<34}{'code lines':>11}")
    for where, count, reason in size_table():
        flag = ("  exempt: " + reason if reason
                else "  OVER BUDGET" if count > BUDGET else "")
        print(f"{where:<34}{count:>11}{flag}")
    if NOTES.is_dir():
        print(f"\n{'note (information only)':<34}{'lines':>11}")
        for note in sorted(NOTES.glob("*.md")):
            lines = len(note.read_text(encoding="utf-8").splitlines())
            print(f"{note.name:<34}{lines:>11}")
    print("")
    try:
        test_modules_within_budget()
        test_checks_modules_are_paired()
    except AssertionError as failure:
        sys.exit(f"FAIL: {failure}")
