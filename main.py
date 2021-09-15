from upload import upload
from os import listdir
from os.path import isfile, join, abspath, isdir

def upload_folder(folder_name: str):
    print(f'uploading folder {folder_name}')
    folder_full_path = abspath(folder_name)
    all_files = [f'{folder_full_path}/{f}' for f in listdir(folder_full_path) if isfile(join(folder_full_path, f))]
    all_folders = [f'{folder_full_path}/{f}' for f in listdir(folder_full_path) if isdir(join(folder_full_path, f))]
    dropbox_file_names = [f.replace(folder_full_path, folder_name[1:]) for f in all_files]
    dropbox_folder_names = [f.replace(folder_full_path, folder_name[1:]) for f in all_folders]

    for local_file, dropbox_file in zip(all_files, dropbox_file_names):
        print(f'uploading file {dropbox_file}')
        upload(dropbox_file, local_file)

    for dropbox_file in dropbox_folder_names:
        upload_folder(f'.{dropbox_file}')

upload_folder('./junk-files')
