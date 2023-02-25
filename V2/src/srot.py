import os

SIZE = 52

def rename_files(folderPath):
    # 遍历所有文件
    for i, file in enumerate(os.listdir(folderPath)):
        filePath = os.path.join(folderPath, file)

        _, fileExt = os.path.splitext(filePath)

        newName = str(i) + fileExt

        os.rename(filePath, os.path.join(folderPath, newName))
    
        print("Rename: " + file + (" " * (SIZE - len(file))) + " -> " + newName)

rename_files('./Download/')
