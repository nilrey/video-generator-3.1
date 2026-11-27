import ast, os, pathlib, sys, fnmatch

# Папки, которые пропускаем (имя папки или шаблон)
EXCLUDE_DIRS = {
    ".venv", "venv", "env", ".git", "__pycache__", "node_modules",
    ".idea", ".vscode", "build", "dist", ".mypy_cache", ".pytest_cache",
    "*.egg-info",
}
# Отдельные файлы, которые пропускаем (по имени или шаблону)
EXCLUDE_FILES = {"setup.py", "conftest.py"}  # при необходимости измените

def is_excluded(name, patterns):
    return any(fnmatch.fnmatch(name, p) for p in patterns)

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
out = []

for dirpath, dirnames, filenames in os.walk(root):
    # Изменяем список на месте: os.walk не зайдёт в убранные папки
    dirnames[:] = sorted(d for d in dirnames if not is_excluded(d, EXCLUDE_DIRS))
    for fn in sorted(filenames):
        if not fn.endswith(".py") or is_excluded(fn, EXCLUDE_FILES):
            continue
        p = pathlib.Path(dirpath) / fn
        rel = p.relative_to(root)
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except Exception as e:
            out.append(f"## {rel}\n(не разобран: {e})\n")
            continue
        doc = (ast.get_docstring(tree) or "").split("\n")[0]
        out.append(f"## {rel} — {doc}")
        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                d = (ast.get_docstring(n) or "").split("\n")[0]
                out.append(f"- def {n.name}({ast.unparse(n.args)}) {d}")
            elif isinstance(n, ast.ClassDef):
                ms = [m.name for m in n.body
                      if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                out.append(f"- class {n.name}: {', '.join(ms)}")
        out.append("")

pathlib.Path("PROJECT_MAP.md").write_text("\n".join(out), encoding="utf-8")
print(f"Готово: {len(out)} строк")