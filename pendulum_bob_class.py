#COMP 4 - Technical Solution - Paul Balaji - last updated 24/04/2014
import pygame, sys, math

from animation_object_class import *
from pygame.locals import *
from math import sin, acos, cos, radians, degrees, sqrt, trunc

WINDOWWIDTH = 800
WINDOWHEIGHT = 600

#gravitational constant
gravConstant = 9.81

#radius of pendulum bob
BOBSIZE = 15

#point from which pendulum pivots
PIVOT = (int(WINDOWWIDTH/2)-25, int(WINDOWHEIGHT/25))

#pause options
INSTANT = "animation paused at moment button was clicked"
EQ      = "animation paused at equilibrium"
MAX	= "animation paused on highest displacement"
MIN  	= "animation paused on lowest displacement"
PLAY 	= "animation plays normally"
RESET   = "reset animation to beginning"

#stopping points
HIGH         = "at highest/most positive"
LOW          = "at lowest/most negative"
MIDDLEtoLOW  = "at EQ, towards minimum"
MIDDLEtoHIGH = "at EQ, towards maximum"

#damping types
CRITICAL  = "critical damping"
OVERDAMP  = "overdamped motion"
UNDERDAMP = "underdamped motion"
NODAMP    = "no damping"

#necessary colours
BLACK    = (  0,   0,   0)
RED      = (255,   0,   0)
BLUE     = (  0,   0, 255)

#most of this comes from a file found on GitHub, I needed to adapt it to fit into my system
class PendulumBob(SimpleHarmonicObject):
    """pendulum bob object"""

    #initialise class
    def __init__(self, length, amplitude, displaySurface, damp, dampType, w):
        super(PendulumBob,self).__init__()

        self.variableSetup()

        self.displaySurface = displaySurface

        self.length = length
        self.amplitude = amplitude
        self.damp = damp
        self.dampType = dampType
        self.w = w


    #get swinglength and theta value
    def getBobCentre(self, length, displacement):
        #scale up length * displacement into values that can be represented by pixels
        swinglength = 200 * length 
        swingDisplacement = 200 * displacement

        ratio = displacement / length
        alpha = acos(ratio)
        height = swinglength * sin(alpha) #swinglength is the on-screen pixel size, length is real world
        height = trunc(height) #get an integer value
        outputDisplacement = trunc(swingDisplacement) #get an integer value

        #height and displacement to output
        outputHeight       = PIVOT[1] + height
        outputDisplacement = PIVOT[0] + outputDisplacement

        #co-ordinate of pendulum bob
        centre = (outputDisplacement, outputHeight)

        return centre
        
    #calculate values for animation
    def recomputeValues(self):        
        T       = self.getPendTimePeriod(self.length)
        x, a, v = self.getDisAccSpeeValues(self.amplitude, T, self.timePassed, self.dampType, self.damp, self.w)
        vM, aM  = self.getMaximumValues(T, self.amplitude)

        bobCentre = self.getBobCentre(self.length, x)

        return T, x, v, a, vM, aM, bobCentre

    
    #calculate time period of pendulum system
    def getPendTimePeriod(self,length):
        T = 2 * pi * sqrt(length/gravConstant)
        return round(T,5)
    
    #draw updates to screen
    def draw(self, circleMiddle):
        if self.dampType == NODAMP:
            #highest displacement
            if self.stopAt == HIGH:
                circleMiddle = self.getBobCentre(self.length, self.amplitude)

            #lowest displacement    
            elif self.stopAt == LOW:
                circleMiddle = self.getBobCentre(self.length, -(self.amplitude))

            #at equilibrium    
            elif self.stopAt == MIDDLEtoLOW or self.stopAt == MIDDLEtoHIGH:
                circleMiddle = self.getBobCentre(self.length, 0) #displacement is 0

        #damped at equilibrium
        else:
            if self.stopAt == MIDDLEtoLOW or self.stopAt == MIDDLEtoHIGH:
                circleMiddle = self.getBobCentre(self.length, 0) #displacement is 0
            
        pygame.draw.circle(self.displaySurface, BLACK, PIVOT, 5, 0) #pivot
        pygame.draw.aaline(self.displaySurface, RED, PIVOT, circleMiddle) #pivot to pendulum bob
        pygame.draw.circle(self.displaySurface, BLUE, circleMiddle, BOBSIZE, 0) #pendulum bob
        pygame.draw.aaline(self.displaySurface, BLACK, (0, PIVOT[1]), (WINDOWWIDTH, PIVOT[1])) #parallel to pivot
    	
    #manage the update cycle
    def update(self, pause):
        #to refresh the screen, stopping previous shapes staying on-screen
        self.clearScreen(self.displaySurface)
        #values go back to what they were at the start
        if pause == RESET:
            self.timePassed = 0
            self.framesPassed = 0
            pause = INSTANT
        T, x, v, a, vM, aM, bobCentre = self.recomputeValues()
        pause = self.pauseOptions(pause, x, self.amplitude, T, v)
        self.draw(bobCentre)
        self.outputText(x, v, a, vM, aM, self.amplitude, self.framesPassed, self.displaySurface, pause, self.dampType)
        
        return pause
