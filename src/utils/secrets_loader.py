"""
Utility module to load secrets from TOML file and set them as environment variables.
"""

import os
import toml
from pathlib import Path
from typing import Dict, Any


def load_secrets_from_toml(toml_path: str = None) -> Dict[str, Any]:
    """
    Load secrets from a TOML file and set them as environment variables.
    
    Args:
        toml_path (str, optional): Path to the TOML file. 
                                 Defaults to src/.streamlit/secrets.toml
    
    Returns:
        Dict[str, Any]: Dictionary of loaded secrets
    
    Raises:
        FileNotFoundError: If the TOML file doesn't exist
        toml.TomlDecodeError: If the TOML file is malformed
    """
    if toml_path is None:
        # Default to the secrets.toml file in the project
        current_dir = Path(__file__).parent.parent
        toml_path = current_dir / ".streamlit" / "secrets.toml"
    
    toml_path = Path(toml_path)
    
    if not toml_path.exists():
        raise FileNotFoundError(f"Secrets file not found at: {toml_path}")
    
    # Read the TOML file
    try:
        secrets = toml.load(toml_path)
    except toml.TomlDecodeError as e:
        raise toml.TomlDecodeError(f"Error parsing TOML file {toml_path}: {e}")
    
    # Set environment variables
    for key, value in secrets.items():
        if isinstance(value, str):
            os.environ[key] = value
        else:
            # Convert non-string values to string
            os.environ[key] = str(value)
    
    print(f"Loaded {len(secrets)} secrets from {toml_path}")
    return secrets


def load_secrets_simple(toml_path: str = None) -> Dict[str, str]:
    """
    Simplified version that treats the TOML file as key-value pairs.
    Useful for simple TOML files without nested structures.
    
    Args:
        toml_path (str, optional): Path to the TOML file.
    
    Returns:
        Dict[str, str]: Dictionary of loaded secrets
    """
    if toml_path is None:
        current_dir = Path(__file__).parent.parent
        toml_path = current_dir / ".streamlit" / "secrets.toml"
    
    toml_path = Path(toml_path)
    
    if not toml_path.exists():
        raise FileNotFoundError(f"Secrets file not found at: {toml_path}")
    
    secrets = {}
    
    # Read the file line by line for simple key=value format
    with open(toml_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                secrets[key] = value
                os.environ[key] = value
    
    print(f"Loaded {len(secrets)} secrets from {toml_path}")
    return secrets


def get_secret(key: str, default: str = None) -> str:
    """
    Get a secret value from environment variables.
    
    Args:
        key (str): The secret key
        default (str, optional): Default value if key not found
    
    Returns:
        str: The secret value or default
    """
    return os.environ.get(key, default)


def load_secrets_and_validate(required_keys: list = None) -> Dict[str, str]:
    """
    Load secrets and validate that required keys are present.
    
    Args:
        required_keys (list, optional): List of required secret keys
    
    Returns:
        Dict[str, str]: Dictionary of loaded secrets
    
    Raises:
        ValueError: If required keys are missing
    """
    secrets = load_secrets_simple()
    
    if required_keys:
        missing_keys = [key for key in required_keys if key not in secrets]
        if missing_keys:
            raise ValueError(f"Missing required secrets: {missing_keys}")
    
    return secrets


if __name__ == "__main__":
    # Example usage
    try:
        # Load all secrets
        secrets = load_secrets_simple()
        print("Loaded secrets:", list(secrets.keys()))
        
        # Get a specific secret
        google_api_key = get_secret("GOOGLE_API_KEY")
        if google_api_key:
            print(f"Google API Key loaded: {google_api_key[:10]}...")
        
        # Validate required secrets
        required = ["GOOGLE_API_KEY", "CORE_API_KEY", "TAVILY_API_KEY"]
        load_secrets_and_validate(required)
        print("All required secrets are present!")
        
    except Exception as e:
        print(f"Error loading secrets: {e}")
