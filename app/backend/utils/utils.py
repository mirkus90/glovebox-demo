import base64
import urllib.parse

def decode_url_string(encoded_string: str) -> str:
    """Decode URL encoded string"""
    if not encoded_string:
        return encoded_string
    
    try:
        decoded_string = urllib.parse.unquote(encoded_string)
        return decoded_string
    except Exception:
        # If URL decoding fails, return the original value
        return encoded_string


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False