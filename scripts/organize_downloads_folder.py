# check the folder to see which files and folders are there
# library to perform file operations
import os
import shutil

def organize_files(folder_path):
    # .txt and .md files -> doc-files folder
    # this gets all the files from that folder
    files = os.listdir(folder_path)
    for f in files:
        if f.endswith(".txt") or f.endswith(".md"):
            # move the file to the doc-files folder
            file_path = os.path.join(folder_path, f)
            print(file_path)
            destination_folder = os.path.join(folder_path, "doc-files")
            shutil.move(file_path, destination_folder)
        elif f.endswith(".pdf"):
            file_path = os.path.join(folder_path, f)
            print(file_path)
            destination_folder = os.path.join(folder_path, "PDFs")
            shutil.move(file_path, destination_folder)
        else:
            print("File not moved!")
    return "Files organized!"
    # # .pdf -> PDFs folder

folder_path = "/Users/greatmaster/Downloads"
organize_files(folder_path=folder_path)

