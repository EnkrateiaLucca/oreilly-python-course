import os

root_folder = "./"

folders = [] # variable that holds a list that will contain all the folders's paths
python_files = []
markdown_files = []
other_files = []

items = os.listdir(root_folder)

for item in items:
    # join essentially joins together the 2 paths
    full_path = os.path.join(root_folder, item)

    # this checks if the path is a real folder
    if os.path.isdir(full_path):
        folders.append(item) # what does append do?

    # extra condition to check if something is true
    elif item.endswith(".py"):
        python_files.append(item)

    elif item.endswith(".md"):
        markdown_files.append(item)

    else:
        other_files.append(item)


print("# Folder Inventory")

print("\n- Folders")
for folder in folders:
    print("  -", folder)

print("\n- Python files")
for file in python_files:
    print("  -", file)

print("\n- Markdown files")
for file in markdown_files:
    print("  -", file)

print("\n- Other files")
for file in other_files:
    print("  -", file)