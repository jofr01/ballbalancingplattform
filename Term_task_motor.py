''' @file                   Term_task_motor.py
    @brief                  with that file you can access the motor driver functions
    @details                Responsible for interfacing with the motors and motor
                            drivers to deliver the correct PWM signal associated with the actuation values computed in
                            the controller task using an object of your motor driver class.
			    This is the state diagram we used:
			    \image html Term_motor_SD.png "State Diagram" width=80%
			
    @author                 Sebastian Bößl, Johannes Frisch
    @date                   November 3, 2021
'''

import motordriver
import utime
import pyb

#Define State Variables
##@brief defines the initialization state
#
S0_Init = 0
##@brief defines the update state to interact with the motor driver functions
#
S1_Update = 1




class Task_Motor:
    ''' @brief A motor task class
        @details Objects of this class can be used to control the motor.
        It determines how often it will interact with the motor and sets the duty cycle 
        It communicates with the task_contoller object and gets the instructions from there
    '''

    def __init__(self, period, motor_x_set, motor_y_set):
        ''' @brief creates a object of Task_Motor
            @param period defines the time until task_motor will run again
            @param motor_x_set gets the motor torque for the first motor
            @param motor_y_set gets the motor torque for the second motor
        '''
        
        #class variables
        self.convert_factor = (100*2.21)/(4*13.8*12)
        self.state = S0_Init
        self.runs = 0
        self.period = period
        #defines when the task will run again 
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period)
    
        #shared variables
        self.motor_x_set = motor_x_set
        self.motor_y_set = motor_y_set
        
    def run(self):
        ''' @brief          runs one interation of the task
        '''
        #checks if it is time to run the task
        if (utime.ticks_us() >= self.next_time):
            
            #initialization state
            if (self.state == S0_Init):
                #run state 0
                #creates a motor timer
                self.timer = pyb.Timer(3, freq=20000)
                #creates motordriver object
                self.motor_drv = motordriver.DRV8847()
                #creates motor object 1
                self.motor_1 = self.motor_drv.motor(pyb.Pin.cpu.B4, pyb.Pin.cpu.B5, 1, 2, 3)
                #creatse motor object 2
                self.motor_2 = self.motor_drv.motor(pyb.Pin.cpu.B0, pyb.Pin.cpu.B1, 3, 4, 3)
                
                #transition to state 1
                self.state = S1_Update
                
            #update state
            if (self.state == S1_Update):
                #run state 1
                
                #convert motor torques from controller into duty cycles
                duty_x = self.convert_factor * self.motor_x_set.read()
                duty_y = self.convert_factor * self.motor_y_set.read()
                
                #set motor speeds
                self.motor_2.set_duty(-duty_y)
                self.motor_1.set_duty(duty_x)
                
            #defines the next time the run should run
            self.next_time = utime.ticks_add(self.next_time, self.period)