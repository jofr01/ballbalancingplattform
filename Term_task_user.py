''' @file                   Term_task_user.py
    @brief                  with that file you can access the user interface functions
    @details                Responsible for interaction between the user and the program. This interface
                            include commands that allow the user to begin balancing, stop the balancing, start the
                            data collection, calibrate the touchpanel or get the imu-status.
			    This is the State diagram we used:
			    \image html Term_user_SD.png "State Diagram" width=80%
    @author                 Sebastian Boessl, Johannes Frisch
    @date                   November 30, 2021

'''

import utime
import pyb

#Define State Variables
S0_Init = 0
S1_PrintUI = 1
S2_WaitForInput = 2
S3_BeginBalancing = 3
S4_StopBalancing = 4
S5_GetIMUStatus = 5
S6_ClearFault = 6
S7_CalibrateTouchpanel = 7
S8_StartDataCollection = 8


class Task_User:
    ''' @brief a class to create a User_Task
        @details a way to interact with the user. Prints out statements for the user and reads the user input. 
    '''
    def __init__(self, period, calibrate_touchpanel, get_imu_status, begin_balancing, stop_balancing, start_data_collection, imu_status, UserInputTouch, CalibrationFinished, getUserInputTouch, PointFinished):
        ''' @brief Constructs an Task_user object
            @param period defines the next time the task is going to run
            @param calibrate_touchpanel Sends instruction from task_user to task_touchpanel to start the calibration of the touchpanel
            @param get_imu_status Sends instruction from task_user to task_imu to get the imu calibration status
            @param begin_balancing Sends instruction from task_user to task_controller to start balancing the ball
            @param stop_balancing Sends instruction from task_user to task_controller to stop balancing the ball
            @param start_data_collection Sends instruction from task_user to task_data_collection to start collecting data
            @param imu_status share value of the imu status
            @param UserInputTouch
            @param CalibrationFinished sends instruction from task_touchpanel to task_user to print that the calibration is finished
            @param getUserInputTouch sends instruction from task_touchpanel to task_user to print instructions
            @param PointFinished sends instruction from task_touchpanel to task_user to print that one point is calibrated
        '''
        #class variables
        #defines current state
        self.state = S0_Init            
        #counts the number of iterations                                
        self.runs = 0          
        #defines the next time the task is going to run                                         
        self.period = period 
        #defines the next time the task is going to run                                          
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period) 
        
        #initalizes shared variables
        self.calibrate_touchpanel = calibrate_touchpanel
        self.get_imu_status = get_imu_status
        self.begin_balancing = begin_balancing
        self.stop_balancing = stop_balancing
        self.start_data_collection = start_data_collection
        self.imu_status = imu_status
        self.UserInputTouch = UserInputTouch
        self.CalibrationFinished = CalibrationFinished
        self.getUserInputTouch = getUserInputTouch
        self.PointFinished = PointFinished
    
    def run(self):
        ''' @brief          runs one interation of the task
        '''
        #checks if it is time to run the task
        if (utime.ticks_us() >= self.next_time):                        
            
            #checks the current state
            if (self.state == S0_Init):                                 
                #run state 0
                #creates a serport object
                self.serport = pyb.USB_VCP()                            
                #transition to state 1
                self.state = S1_PrintUI
                
            #checks the current state
            if (self.state == S1_PrintUI):                              
                #run state 1               
                #print User Interface
                print('-------------------------------------------------------------------------------------------')
                print("\n\nChoose one of the following commands:\n")
                print("'b'\tBegin balancing of the platform")
                print("'s'\tStop balancing of the platform")
                print("'d'\tCollect position and velocity data of the platform and the ball")
                print("'t'\tCalibrate touchpanel")
                print("'i'\tDisplay IMU Status")
                print('-------------------------------------------------------------------------------------------')
                
                #transition to the next state
                self.state = S2_WaitForInput
                print('----------------------------------------------------')
                print('Wait for user input...')
                print('----------------------------------------------------')
                        
            #checks if it is time to run the task
            if (self.state == S3_BeginBalancing):                         
                #run state 3
                
                #send instruction to task_controller to start the ball balancing process
                self.begin_balancing.put(1)   
                
                #transition to the next state
                self.state = S2_WaitForInput
                print('----------------------------------------------------')
                print('Wait for user input...')
                print('----------------------------------------------------')
            
            #checks if it is time to run the task
            if (self.state == S4_StopBalancing):                         
                #run state 4
                
                #send instruction to task_controller to stop the ball balancing process
                self.stop_balancing.put(1)   
                
                #transition to the next state
                self.state = S2_WaitForInput
                print('----------------------------------------------------')
                print('Wait for user input...')
                print('----------------------------------------------------')
            
            #checks if it is time to run the task
            if (self.state == S5_GetIMUStatus):                         
                #run state 5
                #prints the status of the IMU
                status = self.imu_status.read()
                print('Calibration Status is: Magnetometer: ', status[0],',', 'Acceloremeter: ', status[1], ',',  'Gyroscope: ', status[2], 'System: ', status[3])

                #transition to the next state
                self.state = S2_WaitForInput
                print('----------------------------------------------------')
                print('Wait for user input...')
                print('----------------------------------------------------')
            
            #checks if it is time to run the task
            if (self.state == S7_CalibrateTouchpanel):                         
                #run state 7     
                #checks if it should print instructions
                if(self.getUserInputTouch.num_in() > 0):
                    self.getUserInputTouch.get()
                    print('----------------------------------------------------')
                    print('Calibration of Touchpanel')
                    print('Touch first point and press g one time and wait until you get a verfication that the point is calibrated.')
                    print('Then continue doing that for 9 points total.')
                    print('----------------------------------------------------')
                    
                #checks user input
                if (self.serport.any()):                    
                    #read input            
                    self.user_in = self.serport.read(1)                 
                    #checks if the user input is equal to g
                    if (self.user_in.decode() == 'g'):   
                        #send instruction to task_touchpanel to get the first point
                        self.UserInputTouch.put(1)      
                
                #checks if point is calibrated
                if(self.PointFinished.num_in() > 0):
                    self.PointFinished.get()
                    print('----------------------------------------------------')
                    print("Point calibrated")
                    print('----------------------------------------------------')
                
                #checks if calibration is finished
                if(self.CalibrationFinished.num_in() > 0):
                    self.CalibrationFinished.get()
                    #print verification
                    print('----------------------------------------------------')
                    print("Calibration is finished.")
                    print('----------------------------------------------------')
                    #change state
                    self.state = S2_WaitForInput
                    print('----------------------------------------------------')
                    print('Wait for user input...')
                    print('----------------------------------------------------')
                            
            #checks if it is time to run the task
            if (self.state == S8_StartDataCollection):                         
                #run state 8
                            
                #send instruction to task_touchpanel to start the data collection
                self.start_data_collection.put(1)   
                
                #transition to the next state
                self.state = S2_WaitForInput
                print('----------------------------------------------------')
                print('Wait for user input...')
                print('----------------------------------------------------')
                
            #checks if it is time to run the task
            if (self.state == S2_WaitForInput):                         
                #run state 2
                #checks if the user put in something and checks what the input was
                self.check_user_input()  

            
    def check_user_input(self):
        ''' @brief      Checks if and what letter the user entered
        '''
        #checks if there is a user input
        if (self.serport.any()):                    
            #read input            
            self.user_in = self.serport.read(1)                 
            #checks if the user input is equal to b
            if (self.user_in.decode() == 'b'):                  
                #transition to state 3 - begin balancing of the platform  
                self.state = S3_BeginBalancing
                self.user_in = ' '
            #checks if the user input is equal to s     
            elif (self.user_in.decode() == 's'):                
                #transition to state 4 - stop balancing of the platform
                self.state = S4_StopBalancing
                self.user_in = ' '
            #checks if the user input is equal to i
            elif (self.user_in.decode() == 'i'):                
                #transition to state 5 - get the status of the IMU
                self.state = S5_GetIMUStatus
                self.user_in = ' '
                #send instruction to task_imu to get the IMU status
                self.get_imu_status.put(1) 
            #checks if the user input is equal to t
            elif (self.user_in.decode() == 't'):                
                #transition to state 7 - start calibration of touchpanel
                self.state = S7_CalibrateTouchpanel
                self.user_in = ' '
                #send instruction to task_touchpanel to calibrate the touchpanel
                self.calibrate_touchpanel.put(1) 
            #checks if the user input is equal to d
            elif (self.user_in.decode() == 'd'):                
            #transition to state 8 - start data collection process
                self.state = S8_StartDataCollection
                self.user_in = ' '
            
            else:
                print('----------------------------------------------------')
                print('Unknown user input: Try again')
                print('----------------------------------------------------')
                
                