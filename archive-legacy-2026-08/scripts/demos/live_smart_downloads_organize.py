import os
import shutil

# Is this folder actually there?
# If it is, I will create a smart_directory inside of it

# replace these before continuing
DOWNLOADS_PATH = "PLACE YOUR DOWNLOADS FOLDER PATH HERE"
SMART_DIR_PATH = "NAME THE SMART DIRECTORY"

smart_dir_path = os.path.join(DOWNLOADS_PATH, SMART_DIR_PATH)
if os.path.isdir(DOWNLOADS_PATH) and not os.path.isdir(smart_dir_path):
    os.mkdir(smart_dir_path)
    print("Hey! You created a sort of smart folder!!!!!")
else:
    print("Folder already exists!")

# which will hold the organized files
# Images -> to a folder called './smart_directory/images', 
images_folder_path = os.path.join(smart_dir_path, "images")
if not os.path.isdir(images_folder_path):
    os.mkdir(images_folder_path)
    print("Created images folder!")
    
docs_folder_path = os.path.join(smart_dir_path, "docs")
if not os.path.isdir(docs_folder_path):
    os.mkdir(docs_folder_path)
    print("Created docs folder!")
# docs like .txt, .md, .pdf files, will be sent to './smart_directory/docs/'

# For that we need to loop over all the files in Downloads folder
for file in os.listdir(DOWNLOADS_PATH):
    full_file_path = os.path.join(DOWNLOADS_PATH, file)
    print(f"Moving this file: {full_file_path[19:]}")
    # checking what kind of file this is
    if full_file_path.endswith(".pdf") or full_file_path.endswith(".md") or full_file_path.endswith(".txt"):
        shutil.move(full_file_path, docs_folder_path)
    elif full_file_path.endswith(".jpg") or full_file_path.endswith(".png"):
        shutil.move(full_file_path, images_folder_path)
    else:
        print(f"Not moving this file: {full_file_path[19:]}")
