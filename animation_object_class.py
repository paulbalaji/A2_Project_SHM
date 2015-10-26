#COMP 4 - Technical Solution - Paul Balaji - last updated 24/04/2014
import pygame, sys, eztext, re, math

from pygame.locals import *
from math import pi, cos, sqrt, sin, exp, sqrt

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 600

#menu choices
SIM_P = "pendulum animation"
SIM_M = "mass-spring animation"

#colours
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)

TEXTCOLOUR  = BLACK
BGCOLOUR    = WHITE

FONT = "freesansbold.ttf"

ORIGIN = (0,0)

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

#constants used to display output values for both systems
OutputTextLeft    = 55    #x co-ordinate of beginning of displacement, acceleration, speed text
OutputTextRight   = WINDOWWIDTH - 325  #x co-ordinate of beginning of max acceleration, max speed
OutputTextTop     = 375  #y co-ordinate of beginning of displacement, acceleration, speed text
OutputTextSpacing = 50   #line spacing


class SimpleHarmonicObject(pygame.sprite.Sprite):
    """object to undergo simple harmonic motion"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

    #setup variables
    def variableSetup(self):
        self.timePassed  = 0 #since cycle adds 1 immediately
        self.framesPassed = 0
        self.xOUT = 0
        self.vOUT = 0
        self.aOUT = 0
        self.stopAt = "None" #tells object not to pause at any particular point

    #output values to display
    def outputText(self, x, v, a, vM, aM, amplitude, framesPassed, displaySurface, pause, dampType):
        #output standard values at beginning
        if framesPassed == 0:
            self.xOUT = round(amplitude,2)
            self.aOUT = 0
            self.vOUT = 0
            
        else:
            #to update at regular frame intervals
            if (framesPassed % (FPS*0.25) == 0 or pause == INSTANT) and framesPassed>0:
                if dampType == NODAMP:
                    #pendulum moving to left, or mass moving down at equilibrium
                    if self.stopAt == MIDDLEtoLOW: 
                        self.xOUT = 0
                        self.vOUT = -vM
                        self.aOUT = 0

                    #pendulum moving right, mass moving up at equilibrium
                    elif self.stopAt == MIDDLEtoHIGH: 
                        self.xOUT = 0
                        self.vOUT = vM
                        self.aOUT = 0

                    #pendulum/mass at highest displacement                        
                    elif self.stopAt == HIGH: 
                        self.xOUT = round(self.amplitude,2)
                        self.vOUT = 0
                        self.aOUT = -aM
                        
                    #pendulum/mass at lowest displacement                        
                    elif self.stopAt == LOW: 
                        self.xOUT = round(-self.amplitude,2)
                        self.vOUT = 0
                        self.aOUT = aM
                        
                    #any other time                        
                    else: 
                        self.xOUT = round(x, 2)
                        self.vOUT = v
                        self.aOUT = a
                else:
                    #at equilibrium
                    if self.stopAt == MIDDLEtoLOW or self.stopAt == MIDDLEtoHIGH:
                        self.xOUT = 0
                        self.aOUT = 0
                        self.vOUT = v

                    #at maximum or minimum displacement                        
                    elif self.stopAt == HIGH or self.stopAt == LOW:
                        self.xOUT = round(x,2)
                        self.aOUT = a
                        self.vOUT = 0

                    #any other time    
                    else:
                        self.xOUT = round(x, 2)
                        self.aOUT = a
                        self.vOUT = v
            
        #actually draw values onto screen        
        self.animationOutputText(vM, aM, amplitude, displaySurface)

    #recalculate values
    def recomputeValues(self):
        return None

    #draw to display
    def draw(self):
        return None

    #manage update cycle
    def update(self):
        return None

    #to calculate max speed of oscillating object
    def getMaximumValues(self, timePeriod, amplitude):
        frequency = 1 / timePeriod
        vmax = 2 * pi * frequency * amplitude
        amax = (2 * pi * frequency) * (2 * pi * frequency) * amplitude
        vmax = round(vmax, 5) #round to a reasonable number of decimal places
        amax = round(amax, 5)
        return vmax, amax

    #get current value for displacement
    def getDisplacement(self, amplitude, timePeriod, timePassed):
        frequency = 1 / timePeriod
        displacement = amplitude * cos(2 * pi * frequency * timePassed)
        #round whenever necessary later on
        return displacement

    #calculate current acceleration of any system
    def getAcceleration(self, timePeriod, displacement):
        frequency = 1 / timePeriod
        a = -1 * (2 * pi * frequency) * (2 * pi * frequency) * displacement
        #round whenever necessary later on
        return a

    #calculate current speed of any system
    def getSpeed(self, timePeriod, amplitude, timePassed):
        frequency = 1 / timePeriod
        v = -2 * pi * amplitude * frequency * sin(2*pi*frequency*timePassed)
        #round whenever necessary later on
        return v

    #get current values for displacement, acceleration and speed
    def getDisAccSpeeValues(self, A, T, t, dampType, k, w):
        #no damping
        if dampType == NODAMP:
            x = self.getDisplacement(A, T, t)
            a = self.getAcceleration(T, x)
            v = self.getSpeed(T, A, t)

        #with damping
        else:
            w = self.w
            #critical damping
            if dampType == CRITICAL:
                x, v, a = self.criticalValues(A, t, w)
                
            #overdamping    
            elif dampType == OVERDAMP:
                x, v, a = self.overdampValues(A, t, w, k)

            #underdamping    
            elif dampType == UNDERDAMP:
                x, v, a = self.underdampValues(A, t, w, k)

        #round to a reasonable number of decimal places
        x = round(x,5)
        a = round(a,5)
        v = round(v,5)
            
        return x, a, v

    #calculate displacement
    def critX(self,A,B,t,w):
        x = (A + (B*t))*exp(-1*w*t)
        return x

    #calculate velocity
    def critV(self,A,B,t,w):
        v = -1*exp(-1*w*t)*(w*(A+(B*t))-B)
        return v

    #calculate acceleration
    def critA(self,A, B, t, w):
        a = w*exp(-1*w*t)*(w*(A+(B*t))-(2*B))
        return a

    #return displacement, acceleration and velocity
    def criticalValues(self, A, t, w):
        #constants avoid unnecessary recalculations
        constant1 = A
        constant2 = w*A
        
        x = self.critX(constant1, constant2, t, w)
        v = self.critV(constant1, constant2, t, w)
        a = self.critA(constant1, constant2, t, w)
        
        return x, v, a

    #calculate displacement
    def overX(self, A, B, L1, L2, t):
        x = A*exp(L1*t) + B*exp(L2*t)
        return x

    #calculate velocity
    def overV(self, A, B, L1, L2, t):
        v = L1*A*exp(L1*t) + L2*B*exp(L2*t)
        return v

    #calculate acceleration
    def overA(self, A, B, L1, L2, t):
        a = L1*L1*A*exp(L1*t) + L2*L2*B*exp(L2*t)
        return a

    #return displacement, acceleration and velocity
    def overdampValues(self, A, t, w, k):
        #constants avoid unnecessary recalculations
        root1 = (-k/2) + sqrt((k*k/4)-(w*w))
        root2 = (-k/2) - sqrt((k*k/4)-(w*w))
        
        constant1 = A - ( (root1 * A) / sqrt((k*k)-(4*w*w)) )
        constant2 = A - constant1 #c1 + c2 = A
        
        x = self.overX(constant1, constant2, root1, root2, t)
        v = self.overV(constant1, constant2, root1, root2, t)
        a = self.overA(constant1, constant2, root1, root2, t)
        
        return x, v, a

    #calculate displacement
    def underX(self, coefficient, cosVal):
        x = coefficient * cosVal
        return x

    #calculate velocity
    def underV(self, coefficient, cosVal, sinVal, k, p):
        v = -0.5 * coefficient * ((k*cosVal)+(2*p*sinVal))
        return v

    #calculate acceleration
    def underA(self, coefficient, cosVal, sinVal, k, p):
        a = coefficient * ( ((k*k/4)-(p*p))*cosVal + (k*p*sinVal) )
        return a

    #return displacement, acceleration and velocity
    def underdampValues(self, A, t, w, k):
        #constants avoid unnecessary recalculations
        p = 0.5 * sqrt((4*w*w)-(k*k))
        constant1 = A*exp(-1*k*t/2)
        valCos = cos(p*t)
        valSin = sin(p*t)

        x = self.underX(constant1, valCos)
        v = self.underV(constant1, valCos, valSin, k, p)
        a = self.underA(constant1, valCos, valSin, k, p)
        
        return x, v, a

    def pauseOptions(self, pause, x, amplitude, T, v):                  
        #pause once animation reaches maximum or minimum
        if pause == MAX or pause == MIN:
            vNEXT = self.getSpeed(T, amplitude, self.timePassed + (1/FPS))

            #maximum displacement
            if pause == MAX and v > 0 and vNEXT < 0:
                pause = INSTANT
                self.stopAt = HIGH

            #minimum displacement
            elif pause == MIN and vNEXT > 0 and v < 0:
                pause = INSTANT
                self.stopAt = LOW

            #don't stop yet, keep animating
            else:
                self.stopAt = "None"
                self.simulationClockCounter()
               
        #pause once animation reaches equilibrium point
        elif pause == EQ:
            xNEXT = self.getDisplacement(self.amplitude, T, self.timePassed + (1/FPS)) #next displacement

            #object moving to the right, or upwards
            if xNEXT > 0 and x < 0:
                pause  = INSTANT                
                self.stopAt = MIDDLEtoHIGH

            #object moving to the left, or downwards    
            elif x > 0 and xNEXT < 0:
                pause  = INSTANT                
                self.stopAt = MIDDLEtoLOW

            #don't stop yet, keep animating    
            else:
                self.stopAt = "None"
                self.simulationClockCounter() #continue like normal until reach EQ point
              
        else:
            #keep the counters going when not paused
            if pause != INSTANT:
                self.stopAt = "None"
                self.simulationClockCounter()
            #if paused, do nothing
        
        return pause

    #part of update cycle	
    def simulationClockCounter(self):
        self.framesPassed += 1
        #frames passed, useful for determining what/when text to output
        self.timePassed = (self.framesPassed / FPS)
        #frames done / frames per second = time completed so far

    #clear the display
    def clearScreen(self, surface):
        surface.fill(WHITE)

    #actually blit text onto display
    def animationOutputText(self, vM, aM, AM, DISPLAYSURF):
        #make output strings       
        dispOutputText = "Displacement: " + str(self.xOUT) + " m"
        speeOutputText = "Velocity           : " + str(self.vOUT) + " ms-1"
        accnOutputText = "Acceleration  : " + str(self.aOUT) + " ms-2"

        amplitudeOutput= "Amplitude: " + str(round(AM,2)) + " m"
        maxSpeedOutput = "Max Speed: " + str(vM) + " ms-1"
        maxAccnOutput  = "Max Acceleration: " + str(aM) + " ms-2"

        #get text & rectangle objects
        xOutTextObj, xOutRectObj = makeText(dispOutputText, 15, TEXTCOLOUR, ORIGIN, False) #displacement
        vOutTextObj, vOutRectObj = makeText(speeOutputText, 15, TEXTCOLOUR, ORIGIN, False) #speed
        aOutTextObj, aOutRectObj = makeText(accnOutputText, 15, TEXTCOLOUR, ORIGIN, False) #acceleration
        
        AMOutTextObj, AMOutRectObj = makeText(amplitudeOutput, 15, TEXTCOLOUR, ORIGIN, False) #amplitude (max displacement)   
        vMOutTextObj, vMOutRectObj = makeText(maxSpeedOutput, 15, TEXTCOLOUR, ORIGIN, False) #speed
        aMOutTextObj, aMOutRectObj = makeText(maxAccnOutput, 15, TEXTCOLOUR, ORIGIN, False) #acceleration

        #move text to correct place            
        #left side
        xOutRectObj.move_ip(OutputTextLeft, OutputTextTop)
        vOutRectObj.move_ip(OutputTextLeft, OutputTextTop + OutputTextSpacing)
        aOutRectObj.move_ip(OutputTextLeft, OutputTextTop + (2*OutputTextSpacing))

        #right side
        AMOutRectObj.move_ip(OutputTextRight, OutputTextTop)
        vMOutRectObj.move_ip(OutputTextRight, OutputTextTop + OutputTextSpacing)
        aMOutRectObj.move_ip(OutputTextRight, OutputTextTop + (2*OutputTextSpacing))
        
        #copy text to screen
        DISPLAYSURF.blit(xOutTextObj, xOutRectObj)
        DISPLAYSURF.blit(vOutTextObj, vOutRectObj)
        DISPLAYSURF.blit(aOutTextObj, aOutRectObj)
        
        DISPLAYSURF.blit(AMOutTextObj, AMOutRectObj)
        DISPLAYSURF.blit(vMOutTextObj, vMOutRectObj)
        DISPLAYSURF.blit(aMOutTextObj, aMOutRectObj)



#returns surface and rectangle objects
#returned objects can be blitted later to show text on display
#if moveMiddle = False, set middle as ORIGIN
def makeText(text, size, color, middle, moveMiddle):
    fontObj = pygame.font.Font(FONT, size)
    textSurf = fontObj.render(text, True, color, BGCOLOUR)
    textRect = textSurf.get_rect()
    if moveMiddle == True:
        textRect.center = middle
    return textSurf, textRect
