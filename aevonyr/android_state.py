"""Non-destructive check of initialized Waydroid image files."""
from pathlib import Path
import configparser


def ready(directory='/var/lib/waydroid'):
    directory=Path(directory)
    config=configparser.ConfigParser(interpolation=None)
    try:
        with (directory/'waydroid.cfg').open() as stream:config.read_file(stream)
        images=Path(config.get('waydroid','images_path',fallback=str(directory/'images')))
        return all((images/name).is_file() and (images/name).stat().st_size>0 for name in ('system.img','vendor.img'))
    except (OSError,configparser.Error):return False

if __name__=='__main__':
    raise SystemExit(0 if ready() else 1)
