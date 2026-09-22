import time
import timeit
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.logger import get_logger

logger = get_logger(__name__)

class HttpClientError(Exception):
    '''
    Raised when an HTTP Request fails after retried
    '''
    pass

def build_session() -> requests.Session:
    '''
    Creates a Session preconfigured to automatically retry failed requests before giving up
    '''

    session = requests.Session()

    retry_strategy = Retry(
            total = 3,
            backoff_factor = 1,
            status_forcelist = [429, 500, 502, 503, 504]
        )
    adapter = HTTPAdapter(max_retries = retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


_session = build_session()

def get_json(url : str, params : dict | None = None, headers : dict | None = None, timeout : int = 10) -> dict:
    '''
    Makes a GET request and returns the parsed JSON response
    '''

    try:
        response = _session.get(url, params = params, headers = headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP GET failed for {url} : {e}")
        raise HttpClientError(f"Request to {url} failed : {e}") from e

def post_json(url : str, data : dict | None = None, headers : dict | None = None, timeout : int = 10) -> dict:
    '''
    Same as get_json but POST
    '''
    try:
        response = _session.post(url, data=data, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP POST failed for {url} : {e}")
        raise HttpClientError(f"Request to {url} failed : {e}") from e

def post_text(url : str, body : str, headers : dict | None = None, timeout : int = 10) -> list | dict :
    '''
    Makes POST request with a raw text body
    '''
    try:
        response = _session.post(url, data=body.encode("utf-8"), headers=headers, timeout=timeout)
        response.raise_for_status();
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP POST (text) failed for {url} : {e}")
        raise HttpClientError(f"Request to {url} failed : {e}") from e

