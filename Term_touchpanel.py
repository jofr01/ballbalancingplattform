''' @file                   Term_touchpanel.py
    @brief                  A driver for reading positions from the touchpanel
    @details                Creates a class which can be used to create a touchpanel object to get the position of the ball on the touchpanel
                            Responsible for interfacing with the resistive touch panel using an object of
                            the touch panel driver class. The task also performs filtering and calibration of the touchpanel.

    @author                 Sebastian Bößl, Johannes Frisch
    @date                   November 18, 2021
    @page touchpanel_doc    Touchpanel Driver Documentation
                            On this page you can find a detailed documentation of the touchpanel driver, including a general
            			    description of the setup, testing procedure and results and a benchmark which shows how long the driver
            			    takes to read position values from the panel.
    
    @section sec_setup      Hardware Setup
                            For this assignment we used the fully assembled ball-balancing plattform, which has a touchpanel on top
                            and is connected to the Nucleo STM32 microcontroller. In this setup we have a resistive touchpanel, 
                            which means that you can determine the position by the changing resistance, depending on where you press 
             			    on the panel. Changing resistance leads to changing voltages at the pins connected to the panel, which can
             			    be read via an ADC.
                            
                            Here is picture of the hardware setup:
                            \image html HardwareSetup.png "Hardware Setup"
                              
    
    @section sec_testing    Testing Procedure and Results
                            We tested the function of the touchpanel by performing X- and Y-Scans and comparing the read coordinates with
                            the known position we touched. In the center of the panel you should read (0, 0). In the pictures below you can
                            see that the positive x-direction is to the front and the postive y-direction is to the right (from the viewpoint
                            of the picture). The z-scan determines wheter there is something in contact with the panel at the moment or not.
                            
                            \image html TouchCenter.png "Touch in the center of the panel (x: 0mm, y: 0mm)"
                            
                            \image html TouchFrontRight.png "Touch in the front right of the panel (x: 74mm, y: 36mm)"
                            
    
    @section sec_benchmark  Benchmark
                            We took a few measures to optimize the speed of our xyz-scan function. First thing we did is to define every
                            constant value as a micropython.const(). We did this for example with the center coordinates that have to be computed
                            in the calculation of the actual coordinate. We also precomputed the scale factor in x- and y-direction and defined
                            it as a constant to reduce the calculation time. 
                            With these measures we were able to achieve an average reading time of 1239us for all coodrinates (xyz) together
                            over a total of 100 scans. With this speed we can be sure, that the touchpanel reading is fast enough to not conflict 
                            with other parts of final project, like the controller driver.
                            
                            
    
    @author                 Sebastian Bößl, Johannes Frisch
    @date                   November 18, 2021
'''

import pyb
from micropython import const
from ulab import numpy as np

class Touchpanel:
    ''' @brief          Interfaces with touchpanel
    '''
    
    def __init__(self, x_m, y_m, x_p, y_p, width , length, x_center, y_center, period):
        ''' @brief Constructs an touchpanel object
            @param x_m negativ x-Pin 
            @param y_m negativ y-Pin
            @param x_p positiv x-Pin
            @param y_p positive y-Pin
            @param length  length of the touchpanel
            @param width widths of the touchpanel
            @param x_center coordinate of the center of the touchpanel
            @param y_center coordinate of the center of the touchpanel
            @period period of task_touchpanel
        '''
        #class variables
        self.x_m = pyb.Pin(x_m)   
        self.y_m = pyb.Pin(y_m) 
        self.x_p = pyb.Pin(x_p)  
        self.y_p = pyb.Pin(y_p) 
        self.width = width
        self.length = length
        self.x_center = const(x_center)
        self.y_center = const(y_center)
        self.scale_x = const(self.width/4095)
        self.scale_y = const(self.length/4095)
        self.alpha = 0.85  #gain position
        self.beta = 0.005  #gain velocity
        self.x_fil = 0
        self.y_fil = 0
        self.y_vel = 0
        self.x_vel = 0
        self.period = period
        #desired calibration points
        self.pos1 = (-70,30)
        self.pos2 = (-70,0)
        self.pos3 = (-70,-30)
        self.pos4 = (0,30)
        self.pos5 = (0,0)
        self.pos6 = (0,-30)
        self.pos7 = (70,30)
        self.pos8 = (70,0)
        self.pos9 = (70,-30)
        
    def x_scan(self):
        ''' @brief     returns ball x-position with respect to center
            @return x-position with respect to the center
        '''
        #x-scan
        self.x_m.init(mode = pyb.Pin.OUT_PP) #sets x_m to pushpull output
        self.x_m.value(0) #set output to low
        self.y_m.init(mode = pyb.Pin.IN) #sets y_m to an input to read the voltage
        self.y_p.init(mode = pyb.Pin.IN) #sets y_p to an input to float it 
        self.x_p.init(mode = pyb.Pin.OUT_PP) #sets x_p to pushpull output
        self.x_p.value(1) #set output to high
        
        ADC = pyb.ADC(self.y_m) #give y_m Pin to read the voltage    
         
        return((ADC.read()*self.scale_x-self.x_center)) #formula to calculate x-position with respect to the center
    
    def y_scan(self):
        ''' @brief     returns ball y-position with respect to center
            @return y-position with respect to the center
        '''
        #x-scan
        self.x_m.init(mode = pyb.Pin.IN) #sets x_m to pushpull output
        self.y_m.init(mode = pyb.Pin.OUT_PP) #sets y_m to an input to read the voltage
        self.y_m.value(0) #set output to low
        self.y_p.init(mode = pyb.Pin.OUT_PP) #sets y_p to an input to float it 
        self.x_p.init(mode = pyb.Pin.IN) #sets x_p to pushpull output
        self.y_p.value(1) #set output to high

        ADC = pyb.ADC(self.x_m) #give y_m Pin to read the voltage
        
        return(ADC.read()*self.scale_y-self.y_center) #formula to calculate x-position with respect to the center
    
    def z_scan(self):
        ''' @brief     returns true or false value whether there is a contact with the touchpanel or not
            @return returns true or false value wether there is a contact with the touchpanel or not
        '''
        self.x_m.init(mode = pyb.Pin.OUT_PP) #sets x_m to pushpull output
        self.y_m.init(mode = pyb.Pin.IN) #sets y_m to an input to read the voltage
        self.x_m.value(0) #set output to low
        self.y_p.init(mode = pyb.Pin.OUT_PP) #sets y_p to an input to float it 
        self.x_p.init(mode = pyb.Pin.IN) #sets x_p to pushpull output
        self.y_p.value(1) #set output to high

        ADC = pyb.ADC(self.y_m) #give y_m Pin to read the voltage
        ADC_value = ADC.read()
        
        if(ADC_value > 4080):
            return(False)
        else:
            return(True)
        
    def all_scan(self):
        ''' @brief  returns x,y position of the touchpanel and if there is a contact or not
            @return returns x,y position of the touchpanel and if there is a contact or not
        '''
        return(self.x_scan(),self.y_scan(), self.z_scan())
    
    def filterting(self, x, y):
        """ @brief this function will allow to filter the input and get the velocity of the ball
            @param x x position of the ball
            @param y y position of the ball
            @return returns the filtered positions and the velocities
        """
        
        #calculate x-filter
        self.x_fil = self.x_fil+self.alpha*(x-self.x_fil)+self.period*self.x_vel
        #calculate x-velocity
        self.x_vel = self.x_vel +self.beta/self.period*(x-self.x_fil)
        #calulate y-filter
        self.y_fil = self.y_fil+self.alpha*(y-self.y_fil)+self.period*self.y_vel
        #calculate y-vel
        self.y_vel = self.y_vel +self.beta/self.period*(y-self.y_fil)
        
        #returns all calculated values
        return(self.x_fil,self.y_fil,self.x_vel,self.y_vel)
    
    def calibration(self, reading_data_x, reading_data_y):
        """ @brief calculates the paramters which can be used to calibrates the touchpanel
            @param reading_data_x contains all the x-values of the touchpanel which were read to calibrate the touchpanel
            @param reading_data_y contains all the y-values of the touchpanel which were read to calibrate the touchpanel
            @return returns all the values which are used to calibrate the positions of the touchpanel
        """
        #create variables
        Kxx, Kyx, Kxy, Kyy, Xc, Yc = 0,0,0,0,0,0
        #create marix for the supposed position values
        supposed_positions = np.array([(self.pos1[0], self.pos1[1]),(self.pos2[0],self.pos2[1]),(self.pos3[0],self.pos3[1]),(self.pos4[0],self.pos4[1]),(self.pos5[0],self.pos5[1]),(self.pos6[0],self.pos6[1]),(self.pos7[0],self.pos7[1]),(self.pos8[0],self.pos8[1]),(self.pos9[0],self.pos9[1])])
        
        #create matrix for the read position values
        real_positions = np.array([[reading_data_x[0], reading_data_y[0], 1],
                                   [reading_data_x[1], reading_data_y[1], 1],
                                   [reading_data_x[2], reading_data_y[2], 1],
                                   [reading_data_x[3], reading_data_y[3], 1 ],
                                   [reading_data_x[4], reading_data_y[4], 1],
                                   [reading_data_x[5], reading_data_y[5], 1],
                                   [reading_data_x[6], reading_data_y[6], 1],
                                   [reading_data_x[7], reading_data_y[7], 1],
                                   [reading_data_x[8], reading_data_y[8], 1]])
        
        #calcualtes the calibration parameters which can be used to calibrate the positions of the ball on the touchpanel
        beta = np.dot(np.dot(np.linalg.inv(np.dot(real_positions.transpose(),real_positions)), real_positions.transpose()), supposed_positions)
            
        #get values from matrix
        Kxx = beta[0][0]
        Kxy = beta[0][1]
        Kyx = beta[1][0]
        Kyy = beta[1][1]
        Xc = beta[2][0]
        Yc = beta[2][1]
        
        #return values
        return(Kxx,Kxy,Kyx,Kyy, Xc, Yc)





    

