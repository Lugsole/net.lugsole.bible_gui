from .config import pkgdatadir, application_id, user_data_dir, translationdir
import os


def find_file_on_path(find_file):
    path = [user_data_dir, translationdir]
    for i in path:
        if os.path.isfile(os.path.join(i, find_file)):
            return i


def walk_files_on_path():
    path = [user_data_dir, translationdir]
    all_files_hash = {}
    for i in path:

        for root, dirs, files in os.walk(i):
            for filename in files:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, i)
                if not os.path.relpath(rel_path, i) in all_files_hash:
                    all_files_hash[rel_path] = i

    return all_files_hash
