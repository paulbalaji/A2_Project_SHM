#COMP 4 - Technical Solution - Paul Balaji - last updated 24/04/2014
import pygame, sys, math

from animation_object_class import *
from pygame.locals import *
from math import sqrt, pi

WINDOWWIDTH = 800
WINDOWHEIGHT = 600

#point from which mass-spring system hangs
PIVOT = (int(WINDOWWIDTH/2)-25, int(WINDOWHEIGHT/25))

#necessary colours
BLACK    = (  0,   0,   0)
RED      = (255,   0,   0)
BLUE     = (  0,   0, 255)

#mass-spring colours
SPRINGCOLOUR = RED
MASSCOLOUR   = BLUE

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

#constants used in animation
MassDisplayX = PIVOT[0]
MassDisplayY = 250
MassWidth = 16
MassHeight = 16
MassTopLeftX = MassDisplayX - (MassWidth/2)

#damping types
CRITICAL  = "critical damping"
OVERDAMP  = "overdamped motion"
UNDERDAMP = "underdamped motion"
NODAMP    = "no damping"

class MassOnSpring(SimpleHarmonicObject):
    """mass-spring system object"""

    #initialise class
    def __init__(self, mass, springConstant, amplitude, displaySurface, damp, dampType, w):
        super(MassOnSpring,self).__init__()

        self.variableSetup()

        self.displaySurface = displaySurface

        self.WINDOWWIDTH = WINDOWWIDTH

        self.mass = mass
        self.springConstant = springConstant
        self.amplitude = amplitude
        self.damp = damp
        self.dampType = dampType
        self.w = w #angular velocity
        
    #recalculate values for animation
    def recomputeValues(self):
        T       = self.getMassTimePeriod(self.mass, self.springConstant)

        x, a, v = self.getDisAccSpeeValues(self.amplitude, T, self.timePassed, self.dampType, self.damp, self.w)
        
        vM, aM  = self.getMaximumValues(T, self.amplitude)

        change = self.massScaleToScreen(x, self.amplitude)
        
        #negative changes in Y cause upwards movement, reverse sign to compensate [ - change]
        #massOutputY is the final y co-ordinate of middle of rectangle
        massOutputY  = MassDisplayY - change
        MassTopLeftY = massOutputY - (MassHeight/2)

        return T, x, v, a, vM, aM, MassTopLeftY


    #calculate time period of mass-spring system
    def getMassTimePeriod(self, mass, springConstant):
        T = 2 * pi * sqrt(mass/springConstant)
        return round(T,5)
    

    #to convert raw displacement into a pixel y co-ordinate
    def massScaleToScreen(self, x, A):
        massMaxPixelHeight = 200 * A #scale up amplitude
        ratio = x / A
        change = round(ratio * massMaxPixelHeight)
        return change
    

    #draw shapes to represent different things
    def draw(self, MassTopLeftY):
        if self.dampType == NODAMP:
            #check for any "pause" exceptions
            #highest displacement
            if self.stopAt == HIGH:
                addA = round(self.amplitude * 200)
                MassTopLeftY = MassDisplayY - addA

            #lowest displacement    
            elif self.stopAt == LOW:
                addA = round(self.amplitude * 200)
                MassTopLeftY = MassDisplayY + addA

            #at equilibrium    
            elif self.stopAt == MIDDLEtoLOW or self.stopAt == MIDDLEtoHIGH:
                MassTopLeftY = MassDisplayY - (MassHeight/2)

        #damped at equilibrium
        else:
            if self.stopAt == MIDDLEtoLOW or self.stopAt == MIDDLEtoHIGH:
                MassTopLeftY = MassDisplayY - (MassHeight/2)

        #draw rectangle to represent the mass
        pygame.draw.rect(self.displaySurface,
                         MASSCOLOUR,
                         (MassTopLeftX, MassTopLeftY, MassWidth, MassHeight))

        #draw a line to represent the spring
        #link from NEAR top of screen, until top of rectangle (representing mass)
        pygame.draw.aaline(self.displaySurface,
                           SPRINGCOLOUR,
                           PIVOT,
                           (MassDisplayX, MassTopLeftY),2)

        #visual consistency with other model
        pygame.draw.line(self.displaySurface, BLACK, (0, PIVOT[1]), (WINDOWWIDTH, PIVOT[1]))

        #pivot point
        pygame.draw.circle(self.displaySurface, BLACK, PIVOT, 5, 0)

        #parallel to equilbrium 
        pygame.draw.line(self.displaySurface, BLACK, (325, MassDisplayY), (425, MassDisplayY))
            
    #manage update cycle
    def update(self, pause):
        #to refresh the screen, stopping previous shapes staying on-screen
        self.clearScreen(self.displaySurface)
        #values go back to what they were at the start
        if pause == RESET:
            self.timePassed = 0
            self.framesPassed = 0
            pause = INSTANT
        T, x, v, a, vM, aM, MassTopLeftY = self.recomputeValues()
        pause = self.pauseOptions(pause, x, self.amplitude, T, v)
        self.draw(MassTopLeftY)
        self.outputText(x, v, a, vM, aM, self.amplitude, self.framesPassed, self.displaySurface, pause, self.dampType)
        
        return pause
