# Find all instances of the specific USB device with VID_0483 and PID_52A4
$deviceInstances = Get-PnpDevice -PresentOnly | Where-Object { $_.DeviceID -like "USB\VID_0483&PID_52A4*" }

# Create an array to store device information
$deviceInfoArray = @()

# For each instance, collect both the friendly name and bus-reported description
foreach ($device in $deviceInstances) {
    # Create an object for this device
    $deviceInfo = [PSCustomObject]@{
        DeviceID = $device.DeviceID
        Status = $device.Status
        FriendlyName = $null
        BusReportedDescription = $null
    }
    
    # Get friendly name
    $friendlyNameProp = Get-PnpDeviceProperty -InstanceId $device.DeviceID | 
                        Where-Object { $_.KeyName -like "*DEVPKEY_Device_FriendlyName" }
    if ($friendlyNameProp) {
        $deviceInfo.FriendlyName = $friendlyNameProp.Data
    }
    
    # Get bus-reported device description
    $busDescProp = Get-PnpDeviceProperty -InstanceId $device.DeviceID | 
                  Where-Object { $_.KeyName -like "*DEVPKEY_Device_BusReportedDeviceDesc" }
    if ($busDescProp) {
        $deviceInfo.BusReportedDescription = $busDescProp.Data
    }
    
    # Add to the array
    $deviceInfoArray += $deviceInfo
}

# Convert to JSON and save to file
$jsonOutput = $deviceInfoArray | ConvertTo-Json -Depth 4
$jsonOutput | Out-File -FilePath "USB_Device_Info.json" -Encoding UTF8

# Display confirmation
Write-Host "Device information saved to USB_Device_Info.json"
Write-Host "Found $($deviceInfoArray.Count) device instances"

# Optionally display the JSON content in console
Write-Host "JSON content:"
$jsonOutput