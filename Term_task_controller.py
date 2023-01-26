''' @file                   Term_task_controller.py
    @brief                  with that file you can access the controller functions
    @details                Responsible for implementing the closed-loop full-state-feedback controller. It calculates the torque for the motors from the gains and position, angles and velocities input.
			    This is the State diagram we used:
			    \image html Term_contoller_SD.png "State Diagram" width=80%   
    @author                 Sebastian Boessl, Johannes Frisch
    @date                   November 3, 2021
'''

import closedloop
import utime
from ulab import numpy as np

#Define State Variables
##@brief defines the initialization state
#
S0_Init = 0
##@brief defines the state to stop balance the ball
#
S1_StopBalancing = 1
##@brief defines the state to balance the ball
#
S2_Balancing = 2


class Task_Controller:
    ''' @brief A Controller Task class
        @details Objects of this class can be used to implement a closed loop controller
    '''

    def __init__(self, period, begin_balancing, stop_balancing, z_pos, x_pos, y_pos, x_vel, y_vel, theta_x, theta_y, theta_x_vel, theta_y_vel, motor_x_set, motor_y_set):
        ''' @brief creates a object of Task_Motor
            @param period defines the time until task_controller will run again
            @param begin_balancing gets instruction from task_user to begin balancing the ball
            @param stop_balancing gets instruction from task_user to stop balancing the ball
            @param z_pos gets z value from the touchpanel whether there is a contact or not
            @param x_pos gets x position from the touchpanel
            @param y_pos gets y position from the touchpanel
            @param x_vel gets x velocity from the touchpanel
            @param y_vel gets y velocity from the touchpanel
            @param theta_x gets theta x position from the platfrom from the IMU
            @param theta_y gets theta y position from the platfrom from the IMU
            @param theta_x_velo gets theta x velocity from the platfrom from the IMU
            @param theta_y_velo gets theta y velocity from the platfrom from the IMU
            @param motor_x_set calculates the torque for the motor
            @param motor_y_set calculates the torque for the motor
        '''
        
        #class variables
        self.state = S0_Init
        self.runs = 0
        self.period = period
        #defines when the task will run again 
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period)
        self.balancing = 0

        #shared variables
        self.begin_balancing = begin_balancing
        self.stop_balancing = stop_balancing
        self.z_pos = z_pos
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.theta_x = theta_x
        self.theta_y = theta_y
        self.theta_x_vel = theta_x_vel
        self.theta_y_vel = theta_y_vel
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
                
                #creates k_matrix with the gains
                K_matrix = np.array([0, -5, 0, -0.2])
                #initalize the k-matrix in the closedloop driver
                self.ctr_x = closedloop.ClosedLoop(K_matrix)
                self.ctr_y = closedloop.ClosedLoop(K_matrix)
                
                #set motor values to 0 to disable them
                self.motor_x_set.write(0)
                self.motor_y_set.write(0)
                
                #transition to state 1
                self.state = S1_StopBalancing
                
            #update state
            if (self.state == S1_StopBalancing):
                #run state 
                
                #check if it should start balancing
                if (self.begin_balancing.num_in() > 0):
                    self.begin_balancing.get()
                    self.state = S2_Balancing
                
            #check the current state
            if(self.state == S2_Balancing):
                #run state
                
                #check if it should stop balancing
                if (self.stop_balancing.num_in() > 0):
                    self.stop_balancing.get()
                    #disable motor 
                    self.motor_x_set.write(0)
                    self.motor_y_set.write(0)
                    #transition into next state+
                    self.state = S1_StopBalancing
                    
                #update state vectors
                self.stateVector_Mx = np.array([[self.x_pos.read()],
                                                 [self.theta_y.read()],
                                                 [self.x_vel.read()],
                                                 [-self.theta_y_vel.read()]])
                
                self.stateVector_My = np.array([[self.y_pos.read()],
                                                 [self.theta_x.read()],
                                                 [self.y_vel.read()],
                                                 [-self.theta_x_vel.read()]])
                          
                #call closedloop controller to calculate torques
                #only calculate torque if there is contact with the ball otherwise set it to 0
                if (self.z_pos.read() == True):
                    #calculate and set torque for the motors
                    self.motor_x_set.write(self.ctr_x.run(self.stateVector_Mx))
                    self.motor_y_set.write(self.ctr_y.run(self.stateVector_My))
                else:
                    self.motor_x_set.write(0)
                    self.motor_y_set.write(0)
                
            #defines the next time the run should run
            self.next_time = utime.ticks_add(self.next_time, self.period)