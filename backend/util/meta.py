""" Functions for meta things, such as: favourites, likes, interactions, adding tags """

# TODO:
# - remove dependency on JsonHandler for metadata

def add_favourite(video_hash: str, metadataHandler):
    favourites = metadataHandler.getValue('favourites')
    if favourites == None:
        favourites = []
    if not hash in favourites:
        favourites.append(hash)
    metadataHandler.setValue('favourites', favourites)

def remove_favourite(video_hash: str, metadataHandler):
    favourites = metadataHandler.getValue('favourites')
    if favourites == None:
        favourites = []
        return
    if hash in favourites:
        favourites.remove(hash)
    metadataHandler.setValue('favourites', favourites)

def is_favourite(video_hash: str, metadataHandler):
    favourites = metadataHandler.getValue('favourites')
    if favourites == None:
        return False
    return hash in favourites

