from backend.util import process

include_folders, ignore_folders, collections_dict = process.readFoldersAndCollections('data/video_folders.txt')
print('\nTXT file:')
for k, v in collections_dict.items():
    print('{:<60} : "{}"'.format(k, v))

include_folders, ignore_folders, collections_dict = process.readFoldersAndCollections_YAML('data/video_folders.yaml')
print('\nYAML file:')
for k, v in collections_dict.items():
    print('{:<60} : "{}"'.format(k, v))


print()