import os
import inspect

def get_locations(datadir="twitter_data"):
    '''
    Returns the directory of located script along with the root directory (eg: where twitter_data is located)
    
    Parameters:
    ___________
    datadir: The current root directory

    Returns:
    ________
    dir_location, root_dir_location
    '''

    path = get_name()
    dir_location = os.path.dirname(path)
    root_dir_location = dir_location.split(datadir)[0] + datadir

    return dir_location, root_dir_location

def get_name():
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    filename = module.__file__

    full_path = os.path.realpath(filename)

    return full_path