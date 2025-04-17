import os
import subprocess

# Ensure the current working directory is the same as the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Create or overwrite the markdown file
markdown_file = "project_context.md"
with open(markdown_file, "w") as md:
    # Add level 1 title
    md.write("# Project Context\n\n")

    # Add level 2 subtitle for activity
    md.write("## Activity\n\n")
    readme_file = os.path.join(script_dir, "README.md")
    if os.path.exists(readme_file):
        with open(readme_file, "r") as f:
            md.write(f.read())
        md.write("\n")

    # Add level 2 subtitle for project file structure
    md.write("## Project File Structure\n\n")
    md.write("```shell\n")
    # Run the tree command excluding the tp2_venv directory
    tree_output = subprocess.getoutput("tree -I 'tp2_venv'")
    md.write(tree_output + "\n")
    md.write("```\n\n")

    # Add level 2 subtitle for source code
    md.write("## Source Code\n\n")
    src_path = os.path.join(script_dir, "src")
    if os.path.exists(src_path):
        for root, _, files in os.walk(src_path):
            for file in files:
                if file.endswith((".py", ".asm", ".c")):
                    file_path = os.path.join(root, file)
                    md.write(f"### {file}\n\n")
                    md.write("```" + file.split('.')[-1] + "\n")
                    with open(file_path, "r") as f:
                        md.write(f.read())
                    md.write("\n```\n\n")

    # Add level 2 subtitle for batch shell scripts
    md.write("## Batch Shell Scripts\n\n")
    for file in os.listdir(script_dir):
        if file.endswith(".sh"):
            md.write(f"### {file}\n\n")
            md.write("```bash\n")
            with open(file, "r") as f:
                md.write(f.read())
            md.write("\n```\n\n")

    # Add level 2 subtitle for Python requirements
    requirements_file = os.path.join(script_dir, "requirements.txt")
    if os.path.exists(requirements_file):
        md.write("## Python Requirements\n\n")
        md.write("```text\n")
        with open(requirements_file, "r") as f:
            md.write(f.read())
        md.write("\n```\n")
