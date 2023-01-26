''' @file                   Term_task_touchpanel.py
    @brief                  with that file you can access the touchpanel functions
    @details                this file reads the values from the touchpanel and calibrates and filters them. It also calculates the velocities of the ball. Furthermore you can start the calibration process for the touchpanel.
			    This is the State diagram we used:
			    \image html Term_touchpanel_SD.png "State Diagram" width=80%
    @author                 Sebastian Bößl, Johannes Frisch
    @date                   November 3, 2021
'''

import touchpanel
import utime
import pyb
import os


#Define State Variables
##@brief defines the initialization state
#
S0_Init = 0
##@brief defines the update state to interact with the touchpanel functions
#
S1_Update = 1
##@brief defines the state to calibrate the touchpanel
#
S2_Calibrate = 2
##@brief defines the state to write the touchpanel calibration to a file
#
S3_WriteFile = 3

class Task_Touchpanel:
    ''' @brief A Touchpanel Task class
        @details Objects of this class can be used to read and calibrate the touchpanel.
                There is also an alpha-/beta-filter method implemented.
    '''

    def __init__(self, period, calibrate_touchpanel, z_pos, x_pos, y_pos, x_vel, y_vel, UserInputTouch, CalibrationFinished, getUserInputTouch, PointFinished):
        ''' @brief creates a object of Task_Touchpanel
            @param period defines the time until task_touchpanel will run again
            @param calibrate_touchpanel instruction from task_user to task_touchpanel to start the calibration
            @param z_pos indicates whether the ball is on the touchpanel or not
            @param x_pos filtered x-position from the touchpanel
            @param y_pos filtered y-position from the touchpanel
            @param x_vel filtered x-velocity from the touchpanel
            @param y_vel filtered y-velocity from the touchpanel
            @param UserInputTouch sends confirmation from task_user to task_touchpanel that someone is touching the touchpanel for the calibration
            @param CalibrationFinished sends instruction from task_touchpanel to task_user to print out that the calibration is finished
            @param getUserInputTouch sends instruction from task_touchpanel to task_user to print instructions on how to calibrate the ball
            @param PointFinished sends instruction from task_touchpanel to task_user to print out that one point of the touchpanel is calibrated
        '''
        
        #class variables
        self.state = S0_Init
        self.runs = 0
        self.period = period
        self.cal_values = []
        self.Kxx = 0
        self.Kyx = 0
        self.Kyy = 0
        self.Kxy = 0
        self.Xc = 0
        self.Yc = 0
        self.count = 0
        self.pos_data_x = []
        self.pos_data_y = []
	     
        #defines when the task will run again 
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period)
        #shared variables
        self.calibrate_touchpanel = calibrate_touchpanel
        self.z_pos = z_pos
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.UserInputTouch = UserInputTouch
        self.CalibrationFinished = CalibrationFinished
        self.getUserInputTouch = getUserInputTouch
        self.PointFinished = PointFinished 
        
    def run(self):
        ''' @brief          runs one interation of the task
        '''
        #checks if it is time to run the task
        if (utime.ticks_us() >= self.next_time):

            #initialization state
            if (self.state == S0_Init):
                #run state 0
                self.touchpanel = touchpanel.Touchpanel(pyb.Pin.cpu.A1, pyb.Pin.cpu.A0, pyb.Pin.cpu.A7, pyb.Pin.cpu.A6, 176, 100, 88, 50, self.period)
                
                #transition to state 1
                self.state = S1_Update
                
            #update state
            if (self.state == S1_Update):
                #reset
                x = 0
                y = 0
                #run state 1
                
                #check shared variables for commands
                if (self.calibrate_touchpanel.num_in() > 0):
                    self.calibrate_touchpanel.get()
                    
                    #check if file exists/read from file
                    filename = "RT_cal_coeffs.txt"
                    if filename in os.listdir():
                        with open(filename, 'r') as f:
                            #Read the first line of the file
                            cal_data_string = f.readline()
                            #Split the line into multiple strings and then convert each one to a float
                            (self.Kxx, self.Kxy, self.Kyx, self.Kyy, self.Xc, self.Yc) = [float(cal_value) for cal_value in cal_data_string.strip().split(',')]
                            
                            #write to task_user that calibration is finisehd
                            self.CalibrationFinished.put(1)  
                    else:                    
                        #transition to next state
                        self.state = S2_Calibrate
                        #print instructions to user
                        self.getUserInputTouch.put(1)
                        
                #get all touchpanel values
                x,y,z = self.touchpanel.all_scan()
		            
                #get calibration values
                Kxx = self.Kxx
                Kxy = self.Kxy
                Kyx = self.Kyx
                Kyy = self.Kyy
                Xc = self.Xc
                Yc = self.Yc
                
                #calculate calibrate values
                x = Kxx*x+Kxy*y+Xc
                y = Kyx*x+Kyy*y+Yc
                
                #calculate filtered values
                x,y,x_vel,y_vel = self.touchpanel.filterting(x,y)
                
                #write data in shared variables
                self.z_pos.write(z)
                self.x_pos.write(x)
                self.y_pos.write(y)
                self.x_vel.write(x_vel)
                self.y_vel.write(y_vel) 
            
            #check state
            if(self.state == S2_Calibrate):
                #check if there is a touch on touchpanel
                if(self.touchpanel.z_scan() == True) and (self.count <= 9):
                    #checks if the user entered the confirmation that he touches the ball
                    if(self.UserInputTouch.num_in() > 0):
                        self.UserInputTouch.get()
                        #get x and y value
                        x = self.touchpanel.x_scan()
                        y = self.touchpanel.y_scan()
                        
                        #append position data to list
                        self.pos_data_x.append(x)
                        self.pos_data_y.append(y)  

                        #write to task_user that calibration is finisehd
                        self.PointFinished.put(1)                                        
                        
                        #increase counter
                        self.count +=1
                 #checks if there are all the position data       
                if(self.count  == 9):
                    #calibrates data
                    (self.Kxx, self.Kxy, self.Kyx, self.Kyy, self.Xc, self.Yc) = self.touchpanel.calibration(self.pos_data_x,self.pos_data_y)  
                    #transition to next state
                    self.state = S3_WriteFile                                          
              
            #checks the current state                     
            if(self.state == S3_WriteFile):  
                #write data in the file
                filename = "RT_cal_coeffs.txt"
                with open(filename, 'w') as f:
                    # Then write the calibration coefficients to the file as a string. 
                    f.write(f"{self.Kxx}, {self.Kxy}, {self.Kyx}, {self.Kyy}, {self.Xc}, {self.Yc}\r\n") 
                    
                #write to task_user that calibration is finisehd
                self.CalibrationFinished.put(1)  
                    
                #transition to next state
                self.state = S1_Update                                
               
            #defines the next time the run should run
            self.next_time = utime.ticks_add(self.next_time, self.period)