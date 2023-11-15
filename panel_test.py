#!/usr/bin/python3

from pydactyl import PterodactylClient

# Create a client to connect to the panel and authenticate with your API key.
client = PterodactylClient('https://panel.x.x', 'xyz')

# Get a list of all servers the user has access to
my_servers = client.client.list_servers()
# Get the unique identifier for the first server.
#srv_id = my_servers[0]['identifier']

# Check the utilization of the server
srv_utilization = client.client.get_server_utilization('abcabcabc')
print(srv_utilization)
