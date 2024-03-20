# 3.12.23 -> 10.12.23

# Import
import fake_useragent

# Variable
useragent = fake_useragent.UserAgent(use_external_data=True)

def get_headers():
    return useragent.firefox