''' @file                   Term_BNO055.py
    @brief                  A driver for reading IMU data
    @details                Creates a class which can be used to create a IMU object to access the functions of the physical IMU.
                            You can change the operating mode, write and read calibration coefficients and read the calibration status
                            of the instruments. The most important functions are the one to read the euler angles and the angular velocities.
    @author                 Sebastian Bößl, Johannes Frisch
    @date                   December 03, 2021
'''

import pyb
import struct


buffer = bytearray([4])

class BNO055:
    ''' @brief Class to interface with IMU
    '''
    
    def __init__(self, pyb_I2C_object):
        ''' @brief Constructs an BNO055 object
            @param pyb_I2C_object preconfigured object in master mode
        '''
        #class variables
        self.I2C = pyb_I2C_object
        
        
    def change_operating_mode(self, mode):
        ''' @brief Changes the operating mode of the IMU
            @param mode operating mode of the desired IMU mode in binary data
        '''
        #writes to IMU to change operating mode
        self.I2C.mem_write(mode, 0x28, 0x3D) 
    
    def calibration_status(self,):
        ''' @brief Retrieves the calibration status from the IMU
            @return the status values of the callibration status
        '''
        #reads the calibration status
        buffer_bytes = self.I2C.mem_read(buffer, 0x28, 0x35)
        #creates 4 tuples of the separated Bits of the sensors
        cal_status = (buffer_bytes[0] & 0b11, (buffer_bytes[0] & 0b11 << 2) >> 2, (buffer_bytes[0] & 0b11 << 4) >> 4 , (buffer_bytes[0] & 0b11 << 6) >> 6)

        #checks the calibration status      
        if (cal_status[0] == 3): #checks if magnetometer sensor is calibrated
            magneto = True
        else:
            magneto = False
            
        if(cal_status[1] == 3): #checks if accelerometer sensor is calibrated
            acc = True
        else:
            acc = False
            
        if(cal_status[2] == 3): #checks if gyroscope sensor is calibrated
            gyr = True
        else:
            gyr = False
            
        if(cal_status[3] == 3): #checks if system is calibrated
            sys = True
        else:
            sys = False
        
        return(magneto,acc,gyr,sys)      
        
    def ret_calibration_coefficient(self,):
        ''' @brief Retrieves the calibration coefficients from the IMU as binary data
            @return bytearray of the buffer with the callibration data
        '''
        #declares buffer
        buffer = bytearray(22)
        #reads the calibration status
        self.I2C.mem_read(buffer, 0x28, 0x55)
        #return buffer array
        return(buffer)       
        
    def wrt_calibration_coefficient(self, calibration_data):
        ''' @brief Write the calibration coefficients to the IMU from pre-recorded binary data
        '''
        #writes calibration_data to the IMU
        self.I2C.mem_write(bytearray(calibration_data), 0x28, 0x55)
        
    def read_euler_angles(self,):
        ''' @brief Read euler angles from the IMU to use as state measurements
            @return signed euler values in a tuple
        '''
        #creates bytearray
        buffer = bytearray(6)
        #reads the euler angles from IMU
        self.I2C.mem_read(buffer, 0x28, 0x1A)
        #tranform the bytearray in signed values
        eul_signed_ints = struct.unpack('<hhh', buffer)
        #create a tuple with the singed int euler values
        eul_values = tuple(eul_int/16 for eul_int in eul_signed_ints)
        #returns euler angles
        return(eul_values)
      
    def read_angular_velocity(self,):
        ''' @brief Read angular velocity from the IMU to use as state measurements
            @return signed angular velocities in a tuple
        '''
        #creates bytearray
        buffer = bytearray(6)
        #reads the euler angles from IMU
        self.I2C.mem_read(buffer, 0x28, 0x14)
        #tranform the bytearray in signed values
        angular_signed_ints = struct.unpack('<hhh', buffer)
        #create a tuple with the singed int angular velocity values
        angular_velocity_values = tuple(ang_int/16 for ang_int in angular_signed_ints)
        #returns angular velocity values
        return(angular_velocity_values)       
    
