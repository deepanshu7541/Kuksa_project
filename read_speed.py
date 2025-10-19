from time import sleep
from kuksa_client.grpc import VSSClient

c = VSSClient('127.0.0.1', 55556)
c.connect()

v1 = c.get_current_values(['Vehicle.Speed'])['Vehicle.Speed'].value
sleep(1.0)
v2 = c.get_current_values(['Vehicle.Speed'])['Vehicle.Speed'].value

print("Vehicle.Speed v1:", v1)
print("Vehicle.Speed v2:", v2, " (should be different)")
