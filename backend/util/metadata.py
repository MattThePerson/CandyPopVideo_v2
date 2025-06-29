# NTFS Alternate Data Streams 

def set_NTFS_ADS_tag(filepath: str, name: str, value: str):
    """  """
    # print('\nwriting tag to:', filepath)
    try:
        with open(f'{filepath}:{name}', 'w') as f:
            f.write(value)
    except FileNotFoundError:
        ...


def get_NTFS_ADS_tag(filepath: str, name: str) -> str|None:
    """  """
    # print('\ngetting tag from:', filepath)
    try:
        with open(f'{filepath}:{name}', 'r') as f:
            value = f.read()
            # print('value:', value)
            return value
    except FileNotFoundError:
        return None

