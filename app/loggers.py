import logging

""" 
logger.debug('This is a debug message')  # Detailed information, typically of interest only when diagnosing problems.
logger.info('This is an info message')  # Confirmation that things are working as expected.
logger.warning('This is a warning message')  # An indication that something unexpected happened, but the software is still working.
logger.error('This is an error message')  # Due to a more serious problem, the software has not been able to perform some function.
logger.critical('This is a critical message')  # A serious error, indicating that the program itself may be unable to continue running.
"""

_logger_dir = '.logs'

# Configure the root logger (optional, for general logging)
logging.basicConfig(
    level=logging.WARNING,  # Root logger level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=f'{_logger_dir}/root.log',
    filemode='w'
)

# Configure hashing logger
LOGGER_HASHING = logging.getLogger('hashing')
LOGGER_HASHING.setLevel(logging.DEBUG)
handler = logging.FileHandler(f'{_logger_dir}/hashing.log', mode='a')
handler.setFormatter( logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') )
LOGGER_HASHING.addHandler(handler)

# Configure hashing collisions logger
LOGGER_COLLISIONS = logging.getLogger('hash-collision')
LOGGER_COLLISIONS.setLevel(logging.INFO)
handler = logging.FileHandler(f'{_logger_dir}/hashing_collisions.log', mode='a')
handler.setFormatter( logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') )
LOGGER_COLLISIONS.addHandler(handler)

# Configure hashing failed logger
LOGGER_HASHING_FAILED = logging.getLogger('hashing-failed')
LOGGER_HASHING_FAILED.setLevel(logging.ERROR)
handler = logging.FileHandler(f'{_logger_dir}/hashing_failed.log', mode='a')
handler.setFormatter( logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') )
LOGGER_HASHING_FAILED.addHandler(handler)

# Configure hashing failed logger
MEDIA_GEN = logging.getLogger('media-gen')
MEDIA_GEN.setLevel(logging.INFO)
handler = logging.FileHandler(f'{_logger_dir}/media_gen.log', mode='w')
handler.setFormatter( logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') )
MEDIA_GEN.addHandler(handler)

# Configure hashing failed logger
MEDIA_GEN_FAILED = logging.getLogger('media-gen-failed')
MEDIA_GEN_FAILED.setLevel(logging.ERROR)
handler = logging.FileHandler(f'{_logger_dir}/media_gen_failed.log', mode='a')
handler.setFormatter( logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') )
MEDIA_GEN_FAILED.addHandler(handler)

# Configure hashing failed logger
LOADING_FAILED = logging.getLogger('loading-failed')
LOADING_FAILED.setLevel(logging.ERROR)
handler = logging.FileHandler(f'{_logger_dir}/video_loading_failed.log', mode='a')
handler.setFormatter( logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') )
LOADING_FAILED.addHandler(handler)

