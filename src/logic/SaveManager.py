import os
import subprocess

from pathlib import Path

from shared.logger import logger


class SaveFileManager:
    def __init__(self, save_editor_jar_path: str, saves_location: str, profile_nb: str):
        if not profile_nb.isdigit() or int(profile_nb) not in range(0, 9):
            raise ValueError("Invalid profile number")
        else:
            self.SaveEditorPath = save_editor_jar_path
            self.ProfileNb = profile_nb
            self.SaveProfilePath = Path(saves_location, f"profile_{profile_nb}")

    def swap_profile(self, profile_nb: str) -> None:
        if not profile_nb.isdigit() or int(profile_nb) not in range(0, 9):
            raise ValueError("Invalid profile number")
        else:
            self.ProfileNb = profile_nb
            self.SaveProfilePath = Path(self.SaveProfilePath.parent, f"profile_{profile_nb}")

    def decrypt_save_info(self, outputPath: str, fileName: str) -> None:
        if not os.path.exists(Path(f'{self.SaveProfilePath}/{fileName}')):
            logger.error(f"{fileName} doesn't exist encrypted")
            raise FileNotFoundError
        else:
            subprocess.call(['java', '-jar', Path(f'{self.SaveEditorPath}'), 'decode',
                             '-o', outputPath, Path(f'{self.SaveProfilePath}/{fileName}')])
            logger.debug(f'Decrypted {fileName}!')

    def encrypt_save_info(self, inputPath: str, fileName: str) -> None:
        if not os.path.exists(inputPath):
            logger.error(f"{inputPath} doesn't exist decrypted")
            raise FileNotFoundError
        else:
            subprocess.call(['java', '-jar', Path(f'{self.SaveEditorPath}'), 'encode',
                             '-o', Path(f'{self.SaveProfilePath}/{fileName}'), inputPath])
            logger.debug(f'Encrypted {inputPath}!')
