import yaml

def load_config(config_file="config.yml"):
    """
    Load configuration settings from a YAML file.
    
    Args:
        config_file (str): Path to the YAML configuration file.
    
    Returns:
        dict: Dictionary containing configuration settings.
    
    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    try:
        with open(config_file, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        raise
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        raise
