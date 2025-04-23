# Reference: https://stackoverflow.com/questions/440040/how-can-i-parse-the-ioreg-output-in-python
# 
# This script is used to parse the output of the ioreg command and extract information about USB interfaces.
# It can be used to list all USB interfaces, or to find the TTY device for a specific interface.

import plistlib
import subprocess
import json
import os
import sys
import argparse

def get_usb_interfaces():
    # Option 1: Get data from ioreg command
    try:
        output = subprocess.check_output(["ioreg", "-arlw0", "-c", "IOUSBHostInterface"])
        pl = plistlib.loads(output, fmt=plistlib.FMT_XML)
        return pl
    except Exception as e:
        print(f"Error getting data from ioreg: {e}")
        return []

def load_from_file(file_path):
    # Option 2: Load from XML file
    try:
        with open(file_path, 'rb') as f:
            pl = plistlib.load(f)
            return pl
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return []

def traverse_plist(pl, level=0):
    """Recursively traverse a plist structure"""
    indent = "  " * level
    
    if isinstance(pl, dict):
        for key, value in pl.items():
            if isinstance(value, (dict, list)):
                print(f"{indent}{key}:")
                traverse_plist(value, level + 1)
            else:
                print(f"{indent}{key}: {value}")
    elif isinstance(pl, list):
        print(f"{indent}List with {len(pl)} items:")
        for i, item in enumerate(pl):
            print(f"{indent}Item {i+1}:")
            traverse_plist(item, level + 1)
    else:
        print(f"{indent}{pl}")

def find_tty_by_interface_name(pl, interface_name):
    """Find TTY device for a specific interface name"""
    if not isinstance(pl, list):
        print("Error: Expected a list at the top level")
        return None
    
    for interface in pl:
        if not isinstance(interface, dict):
            continue
            
        name = interface.get('IORegistryEntryName', '')
        if name != interface_name:
            continue
            
        # Look for data interfaces (class 10) with TTY devices
        if interface.get('bInterfaceClass') == 10:
            children = interface.get('IORegistryEntryChildren', [])
            for child in children:
                if not isinstance(child, dict):
                    continue
                    
                grandchildren = child.get('IORegistryEntryChildren', [])
                for gc in grandchildren:
                    if not isinstance(gc, dict):
                        continue
                        
                    tty_device = gc.get('IOTTYDevice', None)
                    if tty_device:
                        return tty_device
    return None

def extract_usb_info(pl, interface_name=None):
    """Extract useful information from the plist structure"""
    if not isinstance(pl, list):
        print("Error: Expected a list at the top level")
        return
    
    # If interface_name is provided, only show TTY for that interface
    if interface_name:
        tty_device = find_tty_by_interface_name(pl, interface_name)
        if tty_device:
            print(f"TTY device for {interface_name}: {tty_device}")
        else:
            print(f"No TTY device found for interface: {interface_name}")
        return
    
    # Otherwise show all interfaces
    print(f"Found {len(pl)} USB interfaces")
    
    for i, interface in enumerate(pl):
        if not isinstance(interface, dict):
            print(f"\nInterface #{i+1} is not a dictionary, it's a {type(interface)}")
            continue
            
        print(f"\n--- USB Interface #{i+1} ---")
        
        # Basic info
        name = interface.get('IORegistryEntryName', 'Unknown')
        print(f"Name: {name}")
        
        # Interface details
        print(f"Class: {interface.get('bInterfaceClass', 'Unknown')}")
        print(f"SubClass: {interface.get('bInterfaceSubClass', 'Unknown')}")
        print(f"Protocol: {interface.get('bInterfaceProtocol', 'Unknown')}")
        
        # Product info
        if 'USB Product Name' in interface:
            print(f"Product: {interface['USB Product Name']}")
        if 'USB Vendor Name' in interface:
            print(f"Vendor: {interface['USB Vendor Name']}")
        if 'USB Serial Number' in interface:
            print(f"Serial: {interface['USB Serial Number']}")
        
        # IDs
        print(f"Vendor ID: {interface.get('idVendor', 'Unknown')}")
        print(f"Product ID: {interface.get('idProduct', 'Unknown')}")
        print(f"Location ID: {interface.get('locationID', 'Unknown')}")
        
        # Children
        children = interface.get('IORegistryEntryChildren', [])
        if children:
            print(f"\n  Children ({len(children)}):")
            for j, child in enumerate(children):
                if not isinstance(child, dict):
                    print(f"  Child #{j+1} is not a dictionary")
                    continue
                    
                child_name = child.get('IORegistryEntryName', 'Unknown')
                child_class = child.get('IOClass', 'Unknown')
                print(f"  - Child #{j+1}: {child_name} (Class: {child_class})")
                
                # Look for TTY devices in grandchildren
                grandchildren = child.get('IORegistryEntryChildren', [])
                if grandchildren:
                    print(f"    Grandchildren ({len(grandchildren)}):")
                    for k, gc in enumerate(grandchildren):
                        if not isinstance(gc, dict):
                            continue
                            
                        gc_name = gc.get('IORegistryEntryName', 'Unknown')
                        tty_device = gc.get('IOTTYDevice', None)
                        if tty_device:
                            print(f"    - #{k+1}: {gc_name} (TTY: {tty_device})")
                        else:
                            print(f"    - #{k+1}: {gc_name}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='USB Interface Information Tool',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog='''\
Example usage:

  usb-list.py -l                               # List all USB interfaces
  usb-list.py -l --debug file.xml              # List all interfaces from file.xml
  usb-list.py "STM32 CDC ACM0"                 # Find TTY device for STM32 CDC ACM0
  usb-list.py "STM32 CDC ACM0" --debug usbio.xml  # Find TTY device from XML file
''')
    parser.add_argument('interface_name', nargs='?', 
                      help='Name of the interface to find TTY device for (e.g., "STM32 CDC ACM0")')
    parser.add_argument('--list', '-l', action='store_true', 
                      help='List all interfaces with their details')
    parser.add_argument('--debug', metavar='XML_FILE',
                      help='Load data from the given XML file instead of running ioreg command')
    args = parser.parse_args()
    
    if args.debug:
        print(f"Loading from file: {args.debug}")
        pl = load_from_file(args.debug)
    else:
        print("Getting data from ioreg command")
        pl = get_usb_interfaces()
    if not pl:
        print("No data to process")
        return
    
    # Process the data
    if args.list or not args.interface_name:
        extract_usb_info(pl)
    else:
        extract_usb_info(pl, args.interface_name)

if __name__ == "__main__":
    main()
