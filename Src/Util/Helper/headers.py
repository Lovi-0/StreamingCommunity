# 3.12.23 -> 10.12.23

# Import
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

def get_headers():
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=10)
    
    return user_agent_rotator.get_random_user_agent()