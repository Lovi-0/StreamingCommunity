# 04.4.24

import base64
import json
import logging
import ssl
import time
import re
import urllib.parse
import urllib.request
import urllib.error
from typing import Dict, Optional, Union, Unpack


# Constants
HTTP_TIMEOUT = 4
HTTP_RETRIES = 2
HTTP_DELAY = 1


class RequestError(Exception):
    """Custom exception class for request errors."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None) -> None:
        """
        Initialize a RequestError instance.

        Args:
            message (str): The error message.
            original_exception (Optional[Exception], optional): The original exception that occurred. Defaults to None.
        """
        super().__init__(message)
        self.original_exception = original_exception

    def __str__(self) -> str:
        """Return a string representation of the exception."""
        if self.original_exception:
            return f"{super().__str__()} Original Exception: {type(self.original_exception).__name__}: {str(self.original_exception)}"
        else:
            return super().__str__()


class Response:
    """Class representing an HTTP response."""
    def __init__(
        self,
        status: int,
        text: str,
        is_json: bool = False,
        content: bytes = b"",
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        redirect_url: Optional[str] = None,
        response_time: Optional[float] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initialize a Response object.

        Args:
            status (int): The HTTP status code of the response.
            text (str): The response content as text.
            is_json (bool, optional): Indicates if the response content is JSON. Defaults to False.
            content (bytes, optional): The response content as bytes. Defaults to b"".
            headers (Optional[Dict[str, str]], optional): The response headers. Defaults to None.
            cookies (Optional[Dict[str, str]], optional): The cookies set in the response. Defaults to None.
            redirect_url (Optional[str], optional): The URL if a redirection occurred. Defaults to None.
            response_time (Optional[float], optional): The time taken to receive the response. Defaults to None.
            timeout (Optional[float], optional): The request timeout. Defaults to None.
        """
        self.status_code = status
        self.text = text
        self.is_json = is_json
        self.content = content
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.redirect_url = redirect_url
        self.response_time = response_time
        self.timeout = timeout
        self.ok = 200 <= status < 300

    def raise_for_status(self):
        """Raise an error if the response status code is not in the 2xx range."""
        if not self.ok:
            raise RequestError(f"Request failed with status code {self.status_code}")

    def json(self):
        """Return the response content as JSON if it is JSON."""
        if self.is_json:
            return json.loads(self.text)
        else:
            return None


class ManageRequests:
    """Class for managing HTTP requests."""
    def __init__(
        self, 
        url: str, 
        method: str = 'GET', 
        headers: Optional[Dict[str, str]] = None,
        timeout: float = HTTP_TIMEOUT, 
        retries: int = HTTP_RETRIES,
        params: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True,
        auth: Optional[tuple] = None,
        proxy: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        redirection_handling: bool = True,
    ):
        """
        Initialize a ManageRequests object.

        Args:
            url (str): The URL to which the request will be sent.
            method (str, optional): The HTTP method to be used for the request. Defaults to 'GET'.
            headers (Optional[Dict[str, str]], optional): The request headers. Defaults to None.
            timeout (float, optional): The request timeout. Defaults to HTTP_TIMEOUT.
            retries (int, optional): The number of retries in case of request failure. Defaults to HTTP_RETRIES.
            params (Optional[Dict[str, str]], optional): The query parameters for the request. Defaults to None.
            verify_ssl (bool, optional): Indicates whether SSL certificate verification should be performed. Defaults to True.
            auth (Optional[tuple], optional): Tuple containing the username and password for basic authentication. Defaults to None.
            proxy (Optional[str], optional): The proxy URL. Defaults to None.
            cookies (Optional[Dict[str, str]], optional): The cookies to be included in the request. Defaults to None.
            redirection_handling (bool, optional): Indicates whether redirections should be followed. Defaults to True.
        """
        self.url = url
        self.method = method
        self.headers = headers or {'User-Agent': 'Mozilla/5.0'}
        self.timeout = timeout
        self.retries = retries
        self.params = params
        self.verify_ssl = verify_ssl
        self.auth = auth
        self.proxy = proxy
        self.cookies = cookies
        self.redirection_handling = redirection_handling

    def add_header(self, key: str, value: str) -> None:
        """Add a header to the request."""
        self.headers[key] = value

    def send(self) -> Response:
        """Send the HTTP request."""
        start_time = time.time()
        self.attempt = 0
        redirect_url = None

        while self.attempt < self.retries:
            try:
                req = self._build_request()
                response = self._perform_request(req)
                return self._process_response(response, start_time, redirect_url)
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                self._handle_error(e)
                attempt += 1

    def _build_request(self) -> urllib.request.Request:
        """Build the urllib Request object."""
        headers = self.headers.copy()
        if self.params:
            url = self.url + '?' + urllib.parse.urlencode(self.params)
        else:
            url = self.url
        req = urllib.request.Request(url, headers=headers, method=self.method)
        if self.auth:
            req.add_header('Authorization', 'Basic ' + base64.b64encode(f"{self.auth[0]}:{self.auth[1]}".encode()).decode())
        if self.cookies:
            cookie_str = '; '.join([f"{name}={value}" for name, value in self.cookies.items()])
            req.add_header('Cookie', cookie_str)
        return req

    def _perform_request(self, req: urllib.request.Request) -> urllib.response.addinfourl:
        """Perform the HTTP request."""
        if self.proxy:
            proxy_handler = urllib.request.ProxyHandler({'http': self.proxy, 'https': self.proxy})
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
        if not self.verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            response = urllib.request.urlopen(req, timeout=self.timeout, context=ssl_context)
        else:
            response = urllib.request.urlopen(req, timeout=self.timeout)
        return response

    def _process_response(self, response: urllib.response.addinfourl, start_time: float, redirect_url: Optional[str]) -> Response:
        """Process the HTTP response."""
        response_data = response.read()
        content_type = response.headers.get('Content-Type', '').lower()
        is_response_api = "json" in content_type
        if self.redirection_handling and response.status in (301, 302, 303, 307, 308):
            location = response.headers.get('Location')
            logging.info(f"Redirecting to: {location}")
            redirect_url = location
            self.url = location
            return self.send()
        return self._build_response(response, response_data, start_time, redirect_url, content_type)

    def _build_response(self, response: urllib.response.addinfourl, response_data: bytes, start_time: float, redirect_url: Optional[str], content_type: str) -> Response:
        """Build the Response object."""
        response_time = time.time() - start_time
        response_headers = dict(response.headers)
        response_cookies = {}

        for cookie in response.headers.get_all('Set-Cookie', []):
            cookie_parts = cookie.split(';')
            cookie_name, cookie_value = cookie_parts[0].split('=')
            response_cookies[cookie_name.strip()] = cookie_value.strip()

        return Response(
            status=response.status,
            text=response_data.decode('latin-1'),
            is_json=("json" in content_type),
            content=response_data,
            headers=response_headers,
            cookies=response_cookies,
            redirect_url=redirect_url,
            response_time=response_time,
            timeout=self.timeout,
        )

    def _handle_error(self, e: Union[urllib.error.URLError, urllib.error.HTTPError]) -> None:
        """Handle request error."""
        logging.error(f"Request failed for URL '{self.url}': {str(e)}")
        if self.attempt < self.retries:
            logging.info(f"Retrying request for URL '{self.url}' (attempt {self.attempt}/{self.retries})")
            time.sleep(HTTP_DELAY)
        else:
            logging.error(f"Maximum retries reached for URL '{self.url}'")
            raise RequestError(str(e))


class ValidateRequest:
    """Class for validating request inputs."""
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        url_regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(url_regex, url) is not None

    @staticmethod
    def validate_headers(headers: Dict[str, str]) -> bool:
        """Validate header values."""
        for key, value in headers.items():
            if not isinstance(key, str) or not isinstance(value, str):
                return False
        return True


class ValidateResponse:
    """Class for validating response data."""
    @staticmethod
    def is_valid_json(data: str) -> bool:
        """Check if response data is a valid JSON."""
        try:
            json.loads(data)
            return True
        except ValueError:
            return False


class SSLHandler:
    """Class for handling SSL certificates."""
    @staticmethod
    def load_certificate(custom_cert_path: str) -> None:
        """Load custom SSL certificate."""
        ssl_context = ssl.create_default_context(cafile=custom_cert_path)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE


class KwargsRequest():
    """Class representing keyword arguments for a request."""
    url: str
    headers: Optional[Dict[str, str]] = None
    timeout: float = HTTP_TIMEOUT
    retries: int = HTTP_RETRIES
    params: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None


class Request:
    """Class for making HTTP requests."""
    def __init__(self) -> None:
        pass

    def get(self, url: str, **kwargs: Unpack[KwargsRequest]):
        """
        Send a GET request.

        Args:
            url (str): The URL to which the request will be sent.
            **kwargs: Additional keyword arguments for the request.

        Returns:
            Response: The response object.
        """
        return self._send_request(url, 'GET', **kwargs)

    def post(self, url: str, **kwargs: Unpack[KwargsRequest]):
        """
        Send a POST request.

        Args:
            url (str): The URL to which the request will be sent.
            **kwargs: Additional keyword arguments for the request.

        Returns:
            Response: The response object.
        """
        return self._send_request(url, 'POST', **kwargs)

    def put(self, url: str, **kwargs: Unpack[KwargsRequest]):
        """
        Send a PUT request.

        Args:
            url (str): The URL to which the request will be sent.
            **kwargs: Additional keyword arguments for the request.

        Returns:
            Response: The response object.
        """
        return self._send_request(url, 'PUT', **kwargs)

    def delete(self, url: str, **kwargs: Unpack[KwargsRequest]):
        """
        Send a DELETE request.

        Args:
            url (str): The URL to which the request will be sent.
            **kwargs: Additional keyword arguments for the request.

        Returns:
            Response: The response object.
        """
        return self._send_request(url, 'DELETE', **kwargs)

    def _send_request(self, url: str, method: str, **kwargs: Unpack[KwargsRequest]):
        """Send an HTTP request."""
        # Add validation checks for URL and headers
        if not ValidateRequest.validate_url(url):
            raise ValueError("Invalid URL format")

        if 'headers' in kwargs and not ValidateRequest.validate_headers(kwargs['headers']):
            raise ValueError("Invalid header values")

        return ManageRequests(url, method, **kwargs).send()


# Out
request = Request()