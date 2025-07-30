import os


def read_file_contents(file_path, max_chars=2500):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if len(content) > max_chars:
                return content[:max_chars] + "\n\n... [TRUNCATED]"
            return content
    except Exception as e:
        return f"Could not read {file_path}: {e}"


def main(root_dir="."):
    important_files = [
        "README.md",
        "requirements.txt",
        "app/main.py",
        "app/auth.py",
        "app/vectorstore.py",
        "app/query_models.py",
        "app/models/source_of_truth.py",
        "app/retrievers/base.py",
        "app/retrievers/chroma.py",
        "app/retrievers/faiss.py",
        "app/retrievers/mock.py",
        "app/retrievers/registry.py",
        "frontend/app/page.tsx",
        "frontend/components/AskForm.tsx",
        "frontend/components/LoginForm.tsx",
        "frontend/components/AnswerDisplay.tsx",
        "frontend/components/SourcesList.tsx",
        "frontend/utils/askBackend.ts",  # NEW: included in summary
        "frontend/utils/login.ts",  # NEW: included in summary
        "tests/test_api.py",
        ".github/workflows/ci.yml",
        "Dockerfile",
        ".env.example",  # OPTIONAL: include if you add it
    ]

    output = []
    output.append("## 🚀 Focused Project Summary\n")

    for rel_path in important_files:
        abs_path = os.path.join(root_dir, rel_path)
        if os.path.exists(abs_path):
            ext = os.path.splitext(abs_path)[-1]
            if ext == ".py":
                lang = "python"
            elif ext in [".ts", ".tsx"]:
                lang = "typescript"
            elif ext in [".yml", ".yaml"]:
                lang = "yaml"
            elif ext == ".md":
                lang = "markdown"
            elif ext == ".env":
                lang = "ini"
            else:
                lang = "text"
            output.append(
                f"\n### {rel_path}\n```{lang}\n{read_file_contents(abs_path)}\n```"
            )
        else:
            output.append(f"\n### {rel_path}\nFile not found.\n")

    with open("focused_project_summary_for_chatgpt.md", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    print("✅ Focused summary written to focused_project_summary_for_chatgpt.md")


if __name__ == "__main__":
    main()
