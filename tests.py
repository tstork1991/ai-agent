# tests.py  (project root)
from functions.write_file import write_file

def run_case(title, wd, path, data):
    print(f"\n{title}\n" + "-" * len(title))
    print(write_file(wd, path, data))

if __name__ == "__main__":
    run_case(
        'overwrite existing lorem.txt',
        "calculator",
        "lorem.txt",
        "wait, this isn't lorem ipsum",
    )
    run_case(
        "create new pkg/morelorem.txt",
        "calculator",
        "pkg/morelorem.txt",
        "lorem ipsum dolor sit amet",
    )
    run_case(
        "outside working dir (/tmp/temp.txt)",
        "calculator",
        "/tmp/temp.txt",
        "this should not be allowed",
    )
