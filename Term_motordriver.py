''' @file                   Term_motordriver.py
    @brief                  contains 2 classes to create a motor object and driver
    @details                contains a class called DRV8847 to create a motor driver and configure the DRV8847 which can be used to perform motor control. Also contains a class called motor which can be used to apply PWM to a motor
    @author                 Sebastian Bößl, Johannes Frisch
    @date                   October 25, 2021
'''
import pyb

class DRV8847:
    ''' @brief A motor driver class for the DRV8847 from TI.
        @details Objects of this class can be used to configure the DRV8847
        motor driver and to create one or moreobjects of the
        Motor class which can be used to perform motor
        control.
    
        Refer to the DRV8847 datasheet here:
        https://www.ti.com/lit/ds/symlink/drv8847.pdf
    '''
    
    def __init__ (self):
        ''' @brief Initializes and returns a DRV8847 object.
        '''
    
    def disable (self):
        ''' @brief Puts the DRV8847 in sleep mode.
        '''
        #disables the motor
        self.set_duty(0)
   
    def motor (self, pinIn1, pinIn2, chNum1, chNum2, Timer):
        ''' @brief Initializes and returns a motor object associated with the DRV8847.
            @param pinIn1 value of Pin1 of motor
            @param pinIn2 value of Pin2 of motor
            @param chNum1 value of Timer Channel 1
            @param chNum2 value of Timer Channel 2
            @param Timer for the motor
            @return An object of class Motor
            '''
        #creates motor object
        return Motor(pinIn1, pinIn2, chNum1, chNum2, Timer)

class Motor:
    ''' @brief A motor class for one channel of the DRV8847.
        @details Objects of this class can be used to apply PWM to a given
        DC motor.
    '''
    
    def __init__ (self, pinIn1, pinIn2, chNum1, chNum2, Timer):
        ''' @brief Initializes and returns a motor object associated with the DRV8847.
            @details Objects of this class should not be instantiated
            directly. Instead create a DRV8847 object and use
            that to create Motor objects using the method
            DRV8847.motor().
            @param pinIn1 value of Pin1 of motor
            @param pinIn2 value of Pin2 of motor
            @param chNum1 value of Timer Channel 1
            @param chNum2 value of Timer Channel 2
            @param Timer for the motor
            '''
        ##@brief initialize the timer
        #
        self.timer = Timer
        ##@brief initialize timer channel 1
        #
        self.tch1 = self.timer.channel(chNum1, pyb.Timer.PWM, pin=pinIn1)
        ##@brief initialize timer channel 2
        #
        self.tch2 = self.timer.channel(chNum2, pyb.Timer.PWM, pin=pinIn2)
        
    
    def set_duty (self, duty):
    
        ''' @brief Set the PWM duty cycle for the motor channel.
            @details This method sets the duty cycle to be sent
            to the motor to the given level. Positive values
            cause effort in one direction, negative values
            in the opposite direction.
            @param duty A signed number holding the duty
            cycle of the PWM signal sent to the motor
        '''
        #checks if the duty cycle is negativ or positive
        if (duty > 0): #forward
            self.tch1.pulse_width_percent(100)
            self.tch2.pulse_width_percent(100-duty)       
        elif (duty < 0): #backward
            self.tch1.pulse_width_percent(100+duty)
            self.tch2.pulse_width_percent(100)           
        else: #zero
            self.tch1.pulse_width_percent(0)
            self.tch2.pulse_width_percent(0)
        
