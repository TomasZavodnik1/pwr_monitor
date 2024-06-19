import os
class HWVersions:
    CM1_0 = 15
    CM1_0_SLEEVE = 16
    CM2_0 = 20
    CCB3_0 = 30

class HWDetector:

    def __init__( self ):
       return 1
    
    @staticmethod
    def getCurrentDeviceID():
       current_id = subprocess.check_output([ 'cat', '/etc/machine-id' ])
       current_id = current_id.decode('utf-8')
       return current_id
       
    @staticmethod
    def getCurrentPCBVersion():
       pcb_version = subprocess.check_output([ 'cat', '/etc/comms_pcb_version' ])
       pcb_version = current_id.decode('utf-8')
       return pcb_version
       
    
    @staticmethod   
    def checkIfFileExists( file ):
        return os.is_file( file )
        
    @staticmethod 
    def detectVersion():
       device_0_46_exists = HWDetector.checkIfFileExists(  HWDetector.createPathFromAddressAndInstance( 2, 0x46 ) )
       device_0_45_exists = HWDetector.checkIfFileExists(  HWDetector.createPathFromAddressAndInstance( 2, 0x45 )  )
       device_0_44_exists = HWDetector.checkIfFileExists(  HWDetector.createPathFromAddressAndInstance( 4, 0x44 )  )       
       device_0_41_exists = HWDetector.checkIfFileExists(  HWDetector.createPathFromAddressAndInstance( 2, 0x41 )  )      
       if ( device_0_46_exists == true ):
           return HWVersions.CM2_0
           
       if ( device_0_45_exists == true ):
           return HWVersions.CM1_0_SLEEVE       
           
       if ( device_0_44_exists == true ):
           return HWVersions.CM1_0                
           
       if ( device_0_41_exists == true ):           
           return HWVersions.CM3_0
           
       return 0
    @staticmethod 
    def createPathFromAddressAndInstance( i2c_instance, i2c_address ):
        hex_address = "{:02X}".format( i2c_address )
        hex_address = hex_address.replace( "0x", "00" )
        if hex_address == "45":
            hw_mon_index =  4
        elif hex_address == "41":
            hw_mon_index =  5
        elif hex_address == "46":
            hw_mon_index =  7
        elif hex_address == "44":
            hw_mon_index =  6
        elif hex_address == "40":
            hw_mon_index =  3

        return "/sys/devices/platform/soc@0/30800000.bus/30a40000.i2c/i2c-{0}/{0}-{1}/hwmon/hwmon{2}/curr1_input".format( i2c_instance, hex_address, hw_mon_index )
    
    
    @staticmethod 
    def createCSVHeader( hw_version ):
       files = []
       csv_header = ""
       if ( hw_version == HWVersions.CM1_0_SLEEVE ):
           files.append( HWDetector.createPathFromAddressAndInstance( 2, 0x40 ) )
           files.append( HWDetector.createPathFromAddressAndInstance( 2, 0x45 ) )
           files.append( HWDetector.createPathFromAddressAndInstance( 4, 0x41 ) )
           files.append( HWDetector.createPathFromAddressAndInstance( 4, 0x44 ) )
           csv_header = "time(UNIX TIMESTAMP),2-0x40(nrf),2-0x45(mPcie_total),4-0x41(dc_jack),4-0x44(???),calculated(main_power_without_mpcie_nrf)"
           
       if ( hw_version == HWVersions.CM1_0 ):
           files.append( HWDetector.createPathFromAddressAndInstance( 4, 0x41 ) )
           files.append( HWDetector.createPathFromAddressAndInstance( 4, 0x44 ) )
           csv_header = "time(UNIX TIMESTAMP),4-0x41(dc_jack),4-0x44(???)"
           
       if ( hw_version == HWVersions.CM2_0 ):
           files.append( HWDetector.createPathFromAddressAndInstance( 2, 0x41 ) )
           files.append( HWDetector.createPathFromAddressAndInstance( 2, 0x46 ) )
           files.append( HWDetector.createPathFromAddressAndInstance( 2, 0x45 ) )
           files.append( HWDetector.createPathFromAddressAndInstance( 2, 0x40 ) )
           files.append( HWDetector.createPathFromAddressAndInstance( 2, 0x44 ) )
           csv_header = "time(UNIX TIMESTAMP),2-0x41(main_power),2-0x46(mPcie3),2-0x45(mPcie5),2-0x40(mPcie7),2-0x44(nRF),calculated(mPcie_total),calculated(main_power_without_mpcie_nrf)"     
           
       if ( hw_version == HWVersions.CM3_0 ):
           files.append( HWDetector.createPathFromAddressAndInstance( 2, 0x41 ) )
           csv_header = "time(UNIX TIMESTAMP),2-0x41(main_power)"     
           
       return files, csv_header
