from session_handler import DropBoxUpload
from os import path
from tqdm import tqdm

def upload(dropbox_file_path: str, local_file_path: str) -> None:
    file_size = path.getsize(local_file_path) // (10 ** 6)

    with DropBoxUpload(dropbox_file_path, local_file_path) as dropbox:
        if file_size < 150: # arquivos pequenos
            data = open(local_file_path, 'rb').read()
            dropbox.append(data)
        else: # arquivos grandes
            BATCH_SIZE = 10_000_000

            data = open(local_file_path, 'rb').read()
            data_len = len(data)
            total_steps = data_len // BATCH_SIZE
            steps = data_len // total_steps

            for i in tqdm(range(0, data_len, steps)):
                dropbox.append(data[i:i+steps])
            else:
                if i < data_len:
                    dropbox.append(data[i:])
