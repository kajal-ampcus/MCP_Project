from inspect import signature
from nylas import Client

client = Client(api_key="test")

print(signature(client.notetakers.create))