import os

def create_folder_in_working_directory(folder_name):
    """
    Create a folder in the current working directory if it doesn't already exist.

    Args:
        folder_name (str): Name of the folder to be created.

    Returns:
        str: Absolute path of the created folder.

    """
    # Get the current working directory
    current_directory = os.getcwd()
    
    # Create the full path to the new folder
    folder_path = os.path.join(current_directory, folder_name)
    
    # Check if the folder already exists; if not, create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Return the absolute path of the created folder
    return folder_path