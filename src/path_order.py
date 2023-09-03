from .config import pkgdatadir, application_id, user_data_dir, translationdir
import os

def find_file_on_path(find_file):
    path = [user_data_dir, translationdir]
    #print(find_file)
    for i in path:
        #print(i)
        if os.path.isfile(os.path.join(i, find_file)):
            return i

def walk_files_on_path():
    path = [user_data_dir, translationdir]
    all_files_hash = {}
    for i in path:

        for root, dirs, files in os.walk(i):
            for filename in files:
                full_path = os.path.join(root, filename)
                #print("relpath",os.path.relpath(full_path, i))
                rel_path = os.path.relpath(full_path, i)
                #print("rel_path", rel_path)
                if not os.path.relpath(rel_path, i)  in  all_files_hash:
                    #print(rel_path, i)
                    all_files_hash[rel_path] = i

    return all_files_hash
