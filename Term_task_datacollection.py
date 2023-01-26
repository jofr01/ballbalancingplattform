''' @file                   Term_task_datacollection.py
    @brief                  with that file data is written to or read from files
    @details                Responsible for collecting data and storing it in the appropriate format to
                            either transmit over USB serial to a host PC or to save the data as a file on the Nucleo
			    This is the State diagram we used:
			    \image html Term_datacollection_SD.png "State Diagram" width=80%
    @author                 Sebastian Bößl, Johannes Frisch
    @date                   November 3, 2021
'''

import utime


#Define State Variables
##@brief defines the initialization state
#
S0_Init = 0
##@brief defines the update state to wait for user input
#
S1_Update = 1
##@brief defines the state to collect data
#
S2_CollectData = 2


class Task_DataCollection:
    ''' @brief A Data Collection Task class
    @details Objects of this class can be used to collect data
    '''

    def __init__(self, period, start_collect_data, z_pos, x_pos, y_pos, x_vel, y_vel, theta_x, theta_y, theta_x_vel, theta_y_vel):
        ''' @brief creates a object of Task_Motor
            @param period defines the time until task_datacollection will run again
            @param start_collect_data instruction from task user to start data collection
            @param z_pos gets z value from the touchpanel whether there is a contact or not
            @param x_pos gets x position from the touchpanel
            @param y_pos gets y position from the touchpanel
            @param x_vel gets x velocity from the touchpanel
            @param y_vel gets y velocity from the touchpanel
            @param theta_x gets theta x position from the platfrom from the IMU
            @param theta_y gets theta y position from the platfrom from the IMU
            @param theta_x_velo gets theta x velocity from the platfrom from the IMU
            @param theta_y_velo gets theta y velocity from the platfrom from the IMU
        '''
        
        #class variables
        self.state = S0_Init
        self.runs = 0
        self.period = period
        #defines when the task will run again 
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period)
        
        
        #shared variables
        self.start_collect_data = start_collect_data
        self.z_pos = z_pos
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.theta_x = theta_x
        self.theta_y = theta_y
        self.theta_x_vel = theta_x_vel
        self.theta_y_vel = theta_y_vel

        
        
    def run(self):
        ''' @brief          runs one interation of the task
        '''
        #checks if it is time to run the task
        if (utime.ticks_us() >= self.next_time):
            
            #initialization state
            if (self.state == S0_Init):
                #run state 0
                
                
                #transition to state 1
                self.state = S1_Update
                
            #update state
            if (self.state == S1_Update):
                #run state 1
                
                                
                #check shared variables for commands                 
                #start data collection
                if (self.start_collect_data.num_in() > 0):
                    self.start_collect_data.get()
                    self.stop_time = utime.ticks_add(utime.ticks_ms(), 10000)
                    #file initialisieren
                    with open("Data.txt", 'w') as f:
                                                               
                        #overwrite the old file if existent 
                        f.write("")
        
                    #array initialisieren
                    self.array = ["Time[ms], Contact, X_Pos, Y_Pos, X_Vel, Y_Vel, Theta_X, Theta_Y, Theta_X_Vel, Theta_Y_Vel\n"]
                    self.state = S2_CollectData
                    
            
            if (self.state == S2_CollectData):
                if ((utime.ticks_diff(self.stop_time, utime.ticks_ms())) > 0):
                    #write data
                    self.array.append(str((10000-(utime.ticks_diff(self.stop_time, utime.ticks_ms())))) + ", " + str(self.z_pos.read()) + ", " + str(self.x_pos.read()) + ", " + str(self.y_pos.read()) + ", " + str(self.x_vel.read()) + ", " + str(self.y_vel.read()) + ", " + str(self.theta_x.read()) + ", " + str(self.theta_y.read()) + ", " + str(self.theta_x_vel.read()) + ", " + str(self.theta_y_vel.read()) + "\n")
               
                else:
                    with open("Data.txt", 'a') as f:
                        for i in self.array:
                            f.write(i)
                    self.state = S1_Update
              
                    

                
            #defines the next time the run should run
            self.next_time = utime.ticks_add(self.next_time, self.period)