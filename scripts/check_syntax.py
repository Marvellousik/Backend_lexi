import ast
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

python_services_dir = os.path.join(REPO_ROOT, "zuri-Python Services", "services")
ai_main_dir = os.path.join(REPO_ROOT, "zuri-ai-main")

files_to_check = [
    os.path.join(python_services_dir, "audio", "main.py"),
    os.path.join(python_services_dir, "evaluation", "main.py"),
    os.path.join(python_services_dir, "evaluation", "database.py"),
    os.path.join(python_services_dir, "orchestrator", "main.py"),
    os.path.join(python_services_dir, "retrieval", "main.py"),
    os.path.join(python_services_dir, "retrieval", "database.py"),
    os.path.join(python_services_dir, "ingestion", "main.py"),
    os.path.join(python_services_dir, "ingestion", "models.py"),
    os.path.join(python_services_dir, "ingestion", "embedder.py"),
    os.path.join(python_services_dir, "ingestion", "chunker.py"),
    os.path.join(python_services_dir, "ingestion", "parser.py"),
    os.path.join(ai_main_dir, "api.py"),
    os.path.join(ai_main_dir, "worker.py"),
    os.path.join(ai_main_dir, "job_queue.py"),
    os.path.join(ai_main_dir, "database.py"),
]

errors = 0
for f in files_to_check:
    rel = os.path.relpath(f, REPO_ROOT)
    try:
        with open(f, encoding="utf-8") as fh:
            ast.parse(fh.read())
        print(f"  OK   {rel}")
    except SyntaxError as e:
        print(f"  FAIL {rel}: {e}")
        errors += 1
    except FileNotFoundError:
        print(f"  MISS {rel}")
        errors += 1

print(f"\nResult: {len(files_to_check) - errors}/{len(files_to_check)} files valid")
if errors:
    sys.exit(1)
print("All Python syntax checks passed!")
