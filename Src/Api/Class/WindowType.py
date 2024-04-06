# 03.03.24

from typing import Dict, Any


class WindowVideo:
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a WindowVideo object.

        Args:
            data (dict): A dictionary containing data for the video.
        """
        self.data = data
        self.id: int = data.get('id', '')
        self.name: str = data.get('name', '')
        self.filename: str = data.get('filename', '')
        self.size: str = data.get('size', '')
        self.quality: str = data.get('quality', '')
        self.duration: str = data.get('duration', '')
        self.views: int = data.get('views', '')
        self.is_viewable: bool = data.get('is_viewable', '')
        self.status: str = data.get('status', '')
        self.fps: float = data.get('fps', '')
        self.legacy: bool = data.get('legacy', '')
        self.folder_id: int = data.get('folder_id', '')
        self.created_at_diff: str = data.get('created_at_diff', '')


class WindowParameter:
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a WindowParameter object.

        Args:
            data (dict): A dictionary containing parameters for the window.
        """
        self.data = data
        self.token: str = data.get('token', '')
        self.token360p: str = data.get('token360p', '')
        self.token480p: str = data.get('token480p', '')
        self.token720p: str = data.get('token720p', '')
        self.token1080p: str = data.get('token1080p', '')
        self.expires: str = data.get('expires', '')
