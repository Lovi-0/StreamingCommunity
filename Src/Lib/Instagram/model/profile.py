# 24.03.24

from typing import List


class BioLink:
    def __init__(self, title: str, lynx_url: str, url: str, link_type: str):
        """
        Initialize a BioLink object.

        Args:
            title (str): The title of the link.
            lynx_url (str): The Lynx URL of the link.
            url (str): The URL of the link.
            link_type (str): The type of the link.
        """
        self.title = title
        self.lynx_url = lynx_url
        self.url = url
        self.link_type = link_type

    def __str__(self) -> str:
        """
        Return a string representation of the BioLink object.

        Returns:
            str: String representation of the BioLink object.
        """
        return f"Title: {self.title}, Lynx URL: {self.lynx_url}, URL: {self.url}, Link Type: {self.link_type}"


class InstaProfile:
    def __init__(self, data: dict):
        """
        Initialize an InstaProfile object.

        Args:
            data (dict): Data representing the Instagram profile.
        """
        self.data = data

    def get_username(self) -> str:
        """
        Get the username of the Instagram profile.

        Returns:
            str: Username of the Instagram profile.
        """
        try:
            return self.data['data']['user']['username']
        except KeyError:
            raise KeyError("Username not found in profile data.")

    def get_full_name(self) -> str:
        """
        Get the full name of the Instagram profile.

        Returns:
            str: Full name of the Instagram profile.
        """
        try:
            return self.data['data']['user']['full_name']
        except KeyError:
            raise KeyError("Full name not found in profile data.")

    def get_biography(self) -> str:
        """
        Get the biography of the Instagram profile.

        Returns:
            str: Biography of the Instagram profile.
        """
        try:
            return self.data['data']['user']['biography']
        except KeyError:
            raise KeyError("Biography not found in profile data.")

    def get_bio_links(self) -> List[BioLink]:
        """
        Get the bio links associated with the Instagram profile.

        Returns:
            List[BioLink]: List of BioLink objects representing bio links.
        """
        try:
            bio_links_data = self.data['data']['user']['bio_links']
            return [BioLink(link['title'], link['lynx_url'], link['url'], link['link_type']) for link in bio_links_data]
        except KeyError:
            raise KeyError("Bio links not found in profile data.")

    def get_external_url(self) -> str:
        """
        Get the external URL of the Instagram profile.

        Returns:
            str: External URL of the Instagram profile.
        """
        try:
            return self.data['data']['user']['external_url']
        except KeyError:
            raise KeyError("External URL not found in profile data.")

    def get_followers_count(self) -> int:
        """
        Get the number of followers of the Instagram profile.

        Returns:
            int: Number of followers of the Instagram profile.
        """
        try:
            return self.data['data']['user']['edge_followed_by']['count']
        except KeyError:
            raise KeyError("Followers count not found in profile data.")

    def get_following_count(self) -> int:
        """
        Get the number of accounts the Instagram profile is following.

        Returns:
            int: Number of accounts the Instagram profile is following.
        """
        try:
            return self.data['data']['user']['edge_follow']['count']
        except KeyError:
            raise KeyError("Following count not found in profile data.")

    def is_private(self) -> bool:
        """
        Check if the Instagram profile is private.

        Returns:
            bool: True if the profile is private, False otherwise.
        """
        try:
            return self.data['data']['user']['is_private']
        except KeyError:
            raise KeyError("Private status not found in profile data.")

