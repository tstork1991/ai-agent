# tests.py  (project root)
from functions.run_python import run_python_file

def show(title, wd, path, extra=None):
    extra = extra or []
    print(f"\n{title}\n" + "-" * len(title))
    print(run_python_file(wd, path, extra))

if __name__ == "__main__":
    show("calculator/main.py (usage)", "calculator", "main.py")
    show("calculator/main.py 3+5", "calculator", "main.py", ["3 + 5"])
    show("calculator/tests.py", "calculator", "tests.py")
    show("outside working dir", "calculator", "../main.py")
    show("non-existent file", "calculator", "nonexistent.py")
