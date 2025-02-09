""" TEMP LIB: Will outsource to handymatt """
from pathlib import Path
import os
import json


def metadata_save(data, dirname):
    _id = data.get("id")
    fn = f'{_id}.json'
    savedir = os.path.join(dirname, '.metadata')
    os.makedirs(savedir, exist_ok=True)
    savepath = os.path.join(savedir, fn)
    print('saving metatada to: "{}"'.format(savepath))
    with open(savepath, 'w') as f:
        json.dump(data, f, indent=4)

def metadata_load(path, _id):
    obj = Path(path)
    if obj.is_file():
        obj = obj.parent
    parts = str(obj).split(os.sep)
    if ':' in parts[0]:
        parts[0] += os.sep
    fn = f'{_id}.json'
    while parts != []:
        parts1 = parts.copy() + [fn]
        parts2 = parts.copy() + ['.metadata', fn]
        paths = [os.path.join(*parts1), os.path.join(*parts2)]
        for path in paths:
            if os.path.exists(path):
                return read_json_file(path)
        parts.pop()
    return None

def read_json_file(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

