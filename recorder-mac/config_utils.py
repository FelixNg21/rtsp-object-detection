def get_env_list(env_str):
    """
    Convert an environment variable string to a list of strings.

    Args:
        env_str (str): The environment variable string to convert.

    Returns:
        list: The list of strings.
    """
    return env_str.split(',') if env_str else []