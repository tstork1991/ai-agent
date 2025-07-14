"""
Top-level functional checks for get_files_info().
Run manually via:  uv run tests.py
"""
from functions.get_files_info import get_files_info

def separator(title: str) -> None:
    print("\n" + title)
    print("-" * len(title))

if __name__ == "__main__":
    # 1. Current directory (calculator/.)
    separator("Result for current directory:")
    print(get_files_info("calculator", "."))

    # 2. calculator/pkg
    separator("Result for 'pkg' directory:")
    print(get_files_info("calculator", "pkg"))

    # 3. Absolute path outside working dir
    separator("Result for '/bin' directory:")
    print(get_files_info("calculator", "/bin"))

    # 4. Relative path that escapes upward
    separator("Result for '../' directory:")
    print(get_files_info("calculator", "../"))
