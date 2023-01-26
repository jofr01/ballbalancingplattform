''' @file                   Term_task_imu.py
    @brief                  This task communicates with the IMU driver.
    @details                It is reponsible for setting up the IMU object, calibrating it on startup and updating the angles and velocities of
                            the platform. The calibration are either read from a file if existent or calibrated
                            manualy and then write to a file, to speed up future startups.
			    This is the State diagram we used:
			    \image html Term_imu_SD.png "State Diagram" width=80%
    @author                 Sebastian Bößl, Johannes Frisch
    @date                   December 03, 2021
'''

import BNO055
import utime
import pyb
import os


#Define State Variables
##@brief defines the initialization state
#
S0_Init = 0
##@brief defines the update state that calls the IMU driver functions to update the data
#
S1_Update = 1
##@brief defines the calibration of the IMU unit
#
S2_Calibration = 2


class Task_IMU:
    ''' @brief A IMU Task class
        @details Objects of this class can be used to read and calibrate the IMU.
    '''

    def __init__(self, period, get_imu_status, imu_status, theta_y, theta_x, theta_y_vel, theta_x_vel):
        ''' @brief creates a object of Task_IMU
            @param period defines the time until task_imu will run again
            @param get_imu_status queue written by user taks that requests IMU calibration data from this object
            @param imu_status contains the IMU claibration status
            @param theta_y angle of the platform tilting around the y achsis
            @param theta_x angle of the platform tilting around the x achsis
            @param theta_y_vel angular velocity of theta_y
            @param theta_x_vel angular velocity of theta_x
        '''
        
        #class variables
        self.state = S0_Init
        self.runs = 0
        self.period = period
        
        #defines when the task will run again 
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period)
        
        
        #shared variables
        self.get_imu_status = get_imu_status
        self.imu_status = imu_status
        self.theta_y = theta_y
        self.theta_x = theta_x
        self.theta_y_vel = theta_y_vel
        self.theta_x_vel = theta_x_vel
        
    
        
    def run(self):
        ''' @brief Runs the state machine implemented for this task. More information can be found in the finite state machine
        '''
        #checks if it is time to run the task
        if (utime.ticks_us() >= self.next_time):
            
            #initialization state
            if (self.state == S0_Init):
                #run state 0
                self.I2C = pyb.I2C(1, pyb.I2C.MASTER)
                self.IMU = BNO055.BNO055(self.I2C)
                
                #change IMU to fusion mode
                self.IMU.change_operating_mode(12)
                self.imu_status.write(self.IMU.calibration_status())
                
                #trying to read calibration data on startup
                filename = "IMU_cal_coeffs.txt"
                if filename in os.listdir():
                    with open("IMU_cal_coeffs.txt", 'r') as f:
                        try:
                            #Read the first line of the file
                            cal_data_string = f.readline()
                            #Split the line into multiple strings and then convert each one to a int
                            cal_values = [int(cal_value) for cal_value in cal_data_string.strip().split(',')]
                            #write data to IMU
                            self.IMU.wrt_calibration_coefficient(cal_values)
                            
                            
                            #transition to state 1
                            self.state = S1_Update

                            
                        #go to state 2 to overwrite calibration data if they are not readable
                        except:
                            self.state = S2_Calibration
                        
                #go to state 2 if file doesnt exist     
                else:
                    self.state = S2_Calibration
            
                #write calibration status to shared variable
                self.imu_status.write(self.IMU.calibration_status())
                
            #update state
            if (self.state == S1_Update):
                #run state 1
                
                                
                #check shared variables for commands                 
                #gets IMU status
                if (self.get_imu_status.num_in() > 0):
                    self.get_imu_status.get()
                    self.imu_status.write(self.IMU.calibration_status())
                    
        
                #Reading angles
                angles= self.IMU.read_euler_angles()
                self.theta_x.write(angles[1])
                self.theta_y.write(angles[2])
                #Reading velocities
                velocities= self.IMU.read_angular_velocity()
                self.theta_x_vel.write(velocities[1])
                self.theta_y_vel.write(velocities[0])
                
                
                    
            if (self.state == S2_Calibration):
                #check shared variables for commands                 
                #gets IMU status
                status =  self.IMU.calibration_status()
                if (self.get_imu_status.num_in() > 0):
                    self.get_imu_status.get()
                    self.imu_status.write(status)
                
                #checks if accelorometer and gyroscope are calibrated
                if(status[0] == True and status[1] == True and status[2] == True and status[3] == True):
                    #if IMU is fully calibrated, write the calibration coefficients to file
                    with open("IMU_cal_coeffs.txt", 'w') as f:
                        buffer = bytearray(22)
                        buffer = self.IMU.ret_calibration_coefficient()
                        cal_data_string = ""
                        for b in buffer:
                            cal_data_string += hex(b) +","
                            
                        cal_data_string = cal_data_string[:-1]
                        
                        #write the calibration coefficients to the file as a string. 
                        f.write(cal_data_string)

                        
                        #change state
                        self.state = S1_Update

                
            #defines the next time the run should run
            self.next_time = utime.ticks_add(self.next_time, self.period)