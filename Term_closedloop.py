''' @file                   Term_closedloop.py
    @brief                  A controller driver for closed loop control
    @details                Creates a class which can be used to set up a closed loop control system. It takes in the state vector
                            which contains the values of the touchpanel and the IMU and uses the gain values to calculate a motor torque.
    @author                 Sebastian Bößl, Johannes Frisch
    @date                   October 28, 2021
'''

from ulab import numpy as np

class ClosedLoop:
    ''' @brief A closedloop class
        @details Objects of this class can be used to implement a closed loop controller. 
    '''
    
    def __init__(self, K_matrix):
        ''' @brief          Constructs an closed loop controller object
            @param K_matrix Contains the gain values for the closedloop controler. First the gain for the x, then theta, x_dot and theta_dot.
        '''    
        #class variables
        self.K_matrix = K_matrix
       
    def run(self, state_vector):
        """ @brief Takes in the state_vector containing all the touchpanel and IMU values and calculates the motor torque.
            @param state_vector contains the touchpanel values and the IMU values as well as the velocities.  
            @param motor_torque returns the motor_torque 
        """
        
        #calculate the motor torque
        motor_torque = np.dot(-self.K_matrix, state_vector)
        #return motor_torque
        return motor_torque[0]
    
    def get_K(self):
        """ @brief returns the K_Matrix with the gains.
            @return returns the K_matrix with the gains.
        """
        return self.K_matrix                   
     
         
    def set_K(self, K_matrix):
        """ @brief sets the K_Matrix with the gains.
        """
        
        self.K_matrix = K_matrix
        
    

