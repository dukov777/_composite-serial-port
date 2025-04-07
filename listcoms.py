import serial.tools.list_ports

# Get all available ports with detailed information
ports = list(serial.tools.list_ports.comports())

for port in ports:
    if "STM32" in port.description:
        print (port)
        
        # Print all available attributes
        for attr in dir(port):
            if not attr.startswith('_') and not callable(getattr(port, attr)):
                print(f"  {attr}: {getattr(port, attr)}")
        print()