import ntplib
from time import ctime

def synchronize_time(ntp_server='pool.ntp.org'):
    try:
        # Create an NTP client
        client = ntplib.NTPClient()
        
        # Get the current time from the NTP server
        response = client.request(ntp_server, version=3)
        
        # Display the current time
        print("Current time from NTP server:", ctime(response.tx_time))
        
        # You can also set the system time here if needed, but it usually requires admin privileges
        # Example (on Unix systems):
        # import os
        # os.system(f'date -s @{response.tx_time}')
        
    except Exception as e:
        print("Error synchronizing time:", e)

# Example usage
if __name__ == "__main__":
    synchronize_time()