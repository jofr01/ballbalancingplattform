''' @file                   Term_main.py
    @brief                  In that file the main program is executed
    @details                In this file all the task for the whole ball balancing aplication are executed.
    @author                 Sebastian Bößl, Johannes Frisch
    @date                   November 3, 2021
'''

import task_controller
import task_user
import task_motor
import task_imu
import task_touchpanel
import task_datacollection
import shares


if __name__ == '__main__':
    
    #shared variables
    
    ## @brief sends instruction from task_user to task_motor to clear the faults of the motors
    #
    clear_fault = shares.Queue()
    ## @brief sends instruction from task_user to task_datacollection to start collecting data
    #
    start_data_collection = shares.Queue()
    ## @brief sends instruction from task_user to task_IMU to get IMU calibration status
    #
    get_imu_status = shares.Queue()
    ## @brief sends instruction from task_user to task_touchpanel to start calibration process or read calibration values from file if existent
    #
    calibrate_touchpanel = shares.Queue()
    ## @brief sends instruction from task_user to task_controller to begin balancing of the platform
    #
    begin_balancing = shares.Queue()
    ## @brief sends instruction from task_user to task_controller to stop balancing of the platform
    #
    stop_balancing = shares.Queue()
    ## @brief sends instruction from task_user to task_touchpanel to read x,y value
    #
    UserInputTouch = shares.Queue()
    ## @brief sends instruction from task_touchpanel to task_user that calibration is finished
    #  
    CalibrationFinished = shares.Queue()
    ## @brief sends instruction from task_touchpanel to task_user to print instructions
    #  
    getUserInputTouch = shares.Queue()
    ## @brief sends instruction from task_touchpanel to task_user to print that the Point for the touchpanel is calibrated.
    #
    PointFinished = shares.Queue()
    
 
    ## @brief indicates a fault on the motor
    #
    fault = shares.Share()
    ## @brief sends actuation level from task_controller to task_motor 
    #
    motor_x_set = shares.Share(0)
    ## @brief sends actuation level from task_controller to task_motor 
    #
    motor_y_set = shares.Share(0)
    ## @brief sends IMU status tupel from task_imu to task_user 
    #
    imu_status = shares.Share()
    ## @brief contains actual theta_y angle of the platform (written by task_imu) 
    #
    theta_y = shares.Share()
    ## @brief contains actual theta_x angle of the platform (written by task_imu) 
    #
    theta_x = shares.Share()
    ## @brief contains actual theta_y velocity of the platform (written by task_imu) 
    #
    theta_y_vel = shares.Share()
    ## @brief contains actual theta_x velocity of the platform (written by task_imu) 
    #
    theta_x_vel = shares.Share()
    ## @brief contains actual z position from touchpanel read (written by task_touchpanel) 
    #
    z_pos = shares.Share()
    ## @brief contains actual x position from touchpanel read (written by task_touchpanel) 
    #
    x_pos = shares.Share()
    ## @brief contains actual y position from touchpanel read (written by task_touchpanel) 
    #
    y_pos = shares.Share()
    ## @brief contains actual x velocity from touchpanel read (written by task_touchpanel) 
    #
    x_vel = shares.Share()
    ## @brief contains actual y velocity from touchpanel read (written by task_touchpanel) 
    #
    y_vel = shares.Share()

    
    
    #initiating tasks
    user = task_user.Task_User(100000, calibrate_touchpanel, get_imu_status, begin_balancing, stop_balancing, start_data_collection, imu_status, UserInputTouch, CalibrationFinished, getUserInputTouch, PointFinished)
    motor = task_motor.Task_Motor(5000, motor_x_set, motor_y_set)
    touchpanel = task_touchpanel.Task_Touchpanel(5000, calibrate_touchpanel, z_pos, x_pos, y_pos, x_vel, y_vel, UserInputTouch, CalibrationFinished, getUserInputTouch, PointFinished)
    imu = task_imu.Task_IMU(10000, get_imu_status, imu_status, theta_y, theta_x, theta_y_vel, theta_x_vel)
    controller = task_controller.Task_Controller(10000, begin_balancing, stop_balancing, z_pos, x_pos, y_pos, x_vel, y_vel, theta_x, theta_y, theta_x_vel, theta_y_vel, motor_x_set, motor_y_set)
    datacollection = task_datacollection.Task_DataCollection(50000, start_data_collection, z_pos, x_pos, y_pos, x_vel, y_vel, theta_x, theta_y, theta_x_vel, theta_y_vel)
    
    while(True):
        
        #try to run the different tasks
        try:
            user.run()
            touchpanel.run()
            imu.run()
            controller.run()
            motor.run()
            datacollection.run()
            
        #checks if there is a KeyboardInterrupt
        except KeyboardInterrupt:
            break
    #Prints the errror message
    print('Program terminating')
