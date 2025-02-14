import asyncio
import bleak
import device_model
import time
# 扫描到的设备 Scanned devices
devices = []
# 蓝牙设备 BLEDevice
BLEDevice = None


# 扫描蓝牙设备并过滤名称
# Scan Bluetooth devices and filter names
async def scan(timeout=20):
    global devices
    global BLEDevice
    find = []
    print("Searching for Bluetooth devices......")
    try:
        devices = await bleak.BleakScanner.discover(timeout=timeout)
        print("Search ended")
        for d in devices:
            if d.name is not None and "WT" in d.name:
                find.append(d)
                print(d)
        if len(find) == 0:
            print("No devices found in this search!")
        else:
            user_input = input("Please enter the Mac address you want to connect to (e.g. DF:E9:1F:2C:BD:59)：")
            for d in devices:
                if d.address == user_input:
                    BLEDevice = d
                    break
    except Exception as ex:
        print("Bluetooth search failed to start")
        print(ex)


# 指定MAC地址搜索并连接设备
# Specify MAC address to search and connect devices
async def scanByMac(device_mac):
    global BLEDevice
    print("Searching for Bluetooth devices......")
    BLEDevice = await bleak.BleakScanner.find_device_by_address(device_mac, timeout=5)

num_segment = 1000
# 数据更新时会调用此方法 This method will be called when data is updated
def updateData(DeviceModel):
    # 直接打印出设备数据字典 Directly print out the device data dictionary
    # print(DeviceModel.deviceData)
    # 获得X轴加速度 Obtain X-axis acceleration
    # print(DeviceModel.get("AccX"))
    # save to file
    # saave AccX, AccY, AccZ, AsX, AsY, AsZ by plain number
    if DeviceModel.sample_count % num_segment == 0:
        if DeviceModel.sample_count != 0:
            DeviceModel.sample_count = 0
            sample_rate = num_segment / (time.time() - DeviceModel.start_time)
            print('finish one segment with sample rate of ', sample_rate)
        DeviceModel.start_time = time.time()
        DeviceModel.save_txt = "{}.txt".format(str(DeviceModel.start_time))
    with open(DeviceModel.save_txt, "a") as f:
        print(time.time())
        f.write(str(DeviceModel.get("AccX")) + " " + str(DeviceModel.get("AccY")) + " " + str(DeviceModel.get("AccZ"))
                + " " + str(DeviceModel.get("AsX")) + " " + str(DeviceModel.get("AsY")) + " " + str(DeviceModel.get("AsZ")) + "\n")
    DeviceModel.sample_count += 1
    

if __name__ == '__main__':
    # 方式一：广播搜索和连接蓝牙设备
    # Method 1:Broadcast search and connect Bluetooth devices
    asyncio.run(scan())

    # # 方式二：指定MAC地址搜索并连接设备
    # # Method 2: Specify MAC address to search and connect devices
    address1 = "CC:C4:5B:DF:A5:04"
    # address2 = "EC:41:65:FE:6D:3E"
    # asyncio.run(scanByMac(address1))

    if BLEDevice is not None:
        # 创建设备 Create device
        device = device_model.DeviceModel("MyBle5.0", BLEDevice, updateData)
        # 开始连接设备 Start connecting devices
        asyncio.run(device.openDevice())
    else:
        print("This BLEDevice was not found!!")