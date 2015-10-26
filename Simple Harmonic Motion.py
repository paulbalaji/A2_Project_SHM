#COMP 4 - Technical Solution - Paul Balaji - last updated 24/04/2014
import pygame, sys, eztext, re, math

from mass_spring_class import *
from pendulum_bob_class import *
from pygame.locals import *

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 600

PEND_PIC    = "pendulum.jpg"
MASS_PIC    = "mass_spring.jpg"
PAUSE_PIC   = "pause_button.png"
PLAY_PIC    = "play_button.png"
REFRESH_PIC = "refresh_button.png"

#necessary colours
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
BLUE     = (  0,   0, 255)

#important colours
TEXTCOLOUR  = BLACK
BGCOLOUR    = WHITE
ALERTCOLOUR = RED

FONT = "freesansbold.ttf"

#menu choices
MAIN  = "main"
OPT_P = "pendulum options"
OPT_M = "mass-spring options"
SIM_P = "pendulum animation"
SIM_M = "mass-spring animation"

#status choices
OPTIONS = "in a menu or animation"
VAL_P   = "getting pendulum values"
VAL_M   = "getting mass-spring values"

#pause options
INSTANT = "animation paused at moment button was clicked"
EQ      = "animation paused at equilibrium"
MAX 	= "animation paused on highest displacement"
MIN  	= "animation paused on lowest displacement"
PLAY 	= "animation plays normally"
RESET   = "reset animation to beginning"

#damping types
CRITICAL  = "critical damping"
OVERDAMP  = "overdamped motion"
UNDERDAMP = "underdamped motion"
NODAMP    = "no damping"

#constant used in various calculations
gravConstant = 9.81

def main():
    global FPSCLOCK, DISPLAYSURF, events
    pygame.init() #setup pygame
    FPSCLOCK = pygame.time.Clock() #setup pygame clock
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT)) #setup main surface
    pygame.display.set_caption("Simple Harmonic Motion") #window title

    #store co-ordinates of mouse events
    mousex = 0
    mousey = 0

    #setup objects used in main menu
    setupMainObjects()
    #setup objects used during runtime
    setupRuntimeObjects()

    #variables used in main menu
    menu, status, pendInput, massInput, pendFirstAsk, massFirstAsk = setupMainMenuObject()

    #variables used to get user input
    pendLengthInput, pendAmpInput, pendDampInput = setupPendInputObjects()
    massMassInput, massSpringConstantInput, massAmpInput, massDampInput = setupMassInputObjects()

    #animation will be paused once it is ready to be played
    pause = INSTANT
    
    drawMainMenu()

    clickedButton = None
            
    while True:
        #get list of events since last frame update
        events = pygame.event.get()
        
        for event in events:
            #quit system
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #if something was clicked
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos #get position of click
                #track what object this happend over
                clickedButton, pause = getButton(clickedButton, mousex, mousey, menu, pause)

        #user has option to choose what to do & button was clicked
        if status == OPTIONS and clickedButton != None:
                #exits to main menu straight away if clicked
                if clickedButton == "mainMenuRectObj":
                    pause = INSTANT
                    drawMainMenu()
                    menu = MAIN
                    status = OPTIONS
                        
                else:
                    #if inside the main menu
                    if menu == MAIN:
                        #goes to pendulum input sequence
                        if clickedButton == "pendTextRectObj":
                            status = VAL_P #getting values for pendulum
                            pendLengthInput, pendAmpInput, pendDampInput = setupPendInputObjects()
                            pendInput, pendFirstAsk, status, menu = getPendInputs(menu,
                                                                                  status,
                                                                                  pendInput,
                                                                                  pendLengthInput,
                                                                                  pendAmpInput,
                                                                                  pendDampInput,
                                                                                  pendFirstAsk)

                        #goes to mass-spring input sequence
                        elif clickedButton == "massTextRectObj":
                            status = VAL_M #getting values for mass-spring
                            massMassInput, massSpringConstantInput, massAmpInput, massDampInput = setupMassInputObjects()
                            massInput, massFirstAsk, status, menu = getMassInputs(menu,
                                                                                  status,
                                                                                  massInput,
                                                                                  massMassInput,
                                                                                  massSpringConstantInput,
                                                                                  massAmpInput,
                                                                                  massDampInput,
                                                                                  massFirstAsk)

                    #just after inputs have been taken
                    elif menu == OPT_P:
                        menu = SIM_P #simulation screen
                        
                        #setup objects/variables for simulation
                        dampType, w = getDampType(pendDamping, menu)
                        pendulumObject = PendulumBob(pendLength, pendAmplitude, DISPLAYSURF, pendDamping, dampType, w)

                    #just after inputs have been taken
                    elif menu == OPT_M:   
                        menu = SIM_M #simulation screen

                        #setup object for simulation
                        dampType, w = getDampType(massDamping, menu)
                        massObject = MassOnSpring(massMass, massSpringConstant, massAmplitude, DISPLAYSURF, massDamping, dampType, w)


                    elif menu == SIM_P:
                        #prevents unnecessary use of CPU/GPU if user chooses to go back
                        #goes back to beginning of pendulum system input
                        if clickedButton == "pendBackRectObj":
                            menu = MAIN
                            pause = INSTANT
                            status = OPTIONS
                            clickedButton = "pendTextRectObj"                            
                            
                        else:
                            #update object
                            pause = pendulumObject.update(pause)
                            drawAnimationWindow(pause)


                    elif menu == SIM_M:
                        #prevents unnecessary use of CPU/GPU if user chooses to go back
                        #goes back to beginning of mass-spring system input
                        if clickedButton == "massBackRectObj":
                            menu = MAIN
                            pause = INSTANT
                            status = OPTIONS
                            clickedButton = "massTextRectObj"

                        else:
                            #update object
                            pause = massObject.update(pause)
                            drawAnimationWindow(pause)
                            
        #getting pendulum inputs after first time                    
        elif status == VAL_P:
            pendInput, pendFirstAsk, status, menu = getPendInputs(menu,
                                                                  status,
                                                                  pendInput,
                                                                  pendLengthInput,
                                                                  pendAmpInput,
                                                                  pendDampInput,
                                                                  pendFirstAsk)

        #getting mass-spring inputs after first time
        elif status == VAL_M:
            massInput, massFirstAsk, status, menu = getMassInputs(menu,
                                                                  status,
                                                                  massInput,
                                                                  massMassInput,
                                                                  massSpringConstantInput,
                                                                  massAmpInput,
                                                                  massDampInput,
                                                                  massFirstAsk)
       
        pygame.display.update() #refresh screen
        FPSCLOCK.tick(FPS) #keep a constant frame rate


#returns surface and rectangle objects
#returned objects can be blitted later to show text on display
#if moveMiddle = False, set middle as ORIGIN
def makeText(text, size, colour, middle, moveMiddle):
    fontObj = pygame.font.Font(FONT, size)
    textSurf = fontObj.render(text, True, colour, BGCOLOUR)
    textRect = textSurf.get_rect()
    if moveMiddle == True:
        textRect.center = middle
    return textSurf, textRect

#get the type of damping that will occur, if any
def getDampType(k, menu):
    if k == 0:
        #no damping
        dampType = NODAMP
        w = 0
        
    else:
        #get w if mass-spring chosen
        if menu == SIM_M:
            w = math.sqrt(massMass / massSpringConstant) *100 #to exaggerate the damping effect because it's not visible normally
        #else if pendulum chosen
        elif menu == SIM_P:
            w = math.sqrt(gravConstant / pendLength)
        discriminant = round((k*k/4)-(w*w))
        if discriminant > 0:
            dampType = OVERDAMP
        elif discriminant < 0:
            dampType = UNDERDAMP
        else:
            dampType = CRITICAL
            
    return dampType, w

#get which button was clicked/hovered over
def getButton(current, x, y, menu, pause):
    #decide which menu button clicked in
    #return to main menu button
    if mainMenuRectObj.collidepoint((x,y)):
            return "mainMenuRectObj", pause

    #main menu    
    elif menu == MAIN:
        if pendTextRectObj.collidepoint((x,y)):
            return "pendTextRectObj", pause
        elif massTextRectObj.collidepoint((x,y)):
            return "massTextRectObj", pause

    #buttons in either animation window    
    elif menu == SIM_P or menu == SIM_M:
        #button to change options
        if backRectObj.collidepoint((x,y)):
            if menu == SIM_P:
                return "pendBackRectObj", pause

            elif menu == SIM_M:
                return "massBackRectObj", pause

        #reset animation to initial conditions
        if refreshButtonRect.collidepoint((x,y)):
            pause = RESET
            return "refreshButtonRect", pause
		
	#instant pause button
        elif pauseButtonRect.collidepoint((x,y)):
            pause = INSTANT
            return "pauseSimRectObj", pause
		
	#pause at EQ
        elif equiPauseSimRectObj.collidepoint((x,y)):
            pause = EQ
            return "equiPauseSimRectObj", pause
        
        #pause at max high displacement
        elif maxAmpPauseSimRectObj.collidepoint((x,y)):
            pause = MAX
            return "maxAmpPauseSimRectObj", pause
        
        #pause at max low displacement
        elif minAmpPauseSimRectObj.collidepoint((x,y)):
            pause = MIN
            return "minAmpPauseSimRectObj", pause
		
	#continue animation
        elif playButtonRect.collidepoint((x,y)):
            pause = PLAY
            return "continueRectObj", pause
            
        
    #no button clicked
    return current, pause

#draw main menu
def drawMainMenu():
    clearScreen()
    
    DISPLAYSURF.blit(pendTextSurfObj, pendTextRectObj)
    DISPLAYSURF.blit(massTextSurfObj, massTextRectObj)
    DISPLAYSURF.blit(titleTextSurfObj, titleTextRectObj)

#draw animation window
def drawAnimationWindow(pause):
    DISPLAYSURF.blit(backSurfObj, backRectObj) #change options
    
    drawPauseAnimationButtons(pause)

    drawMainMenuButton() #go to main menu

def drawPauseAnimationButtons(pause):
    if pause == PLAY:
        DISPLAYSURF.blit(pauseButtonPic, pauseButtonRect) #pause button
        DISPLAYSURF.blit(equiPauseSimSurfObj, equiPauseSimRectObj) #EQ pause button
        DISPLAYSURF.blit(maxAmpPauseSimSurfObj, maxAmpPauseSimRectObj) #Max X pause button
        DISPLAYSURF.blit(minAmpPauseSimSurfObj, minAmpPauseSimRectObj) #Min X pause button
    elif pause == INSTANT:
        DISPLAYSURF.blit(playButtonPic, playButtonRect) #play/resume button
    DISPLAYSURF.blit(refreshButtonPic, refreshButtonRect) #reset button

#draw main menu button
def drawMainMenuButton():
    DISPLAYSURF.blit(mainMenuSurfObj, mainMenuRectObj)

#clear screen / fill all white
def clearScreen():
    DISPLAYSURF.fill(WHITE)

#main menu object setup
def setupMainObjects():
    #globalise so it reduces confusion when passing parameters
    global pendTextSurfObj, pendTextRectObj, massTextSurfObj, massTextRectObj, titleTextSurfObj, titleTextRectObj
    
    pendTextSurfObj, pendTextRectObj   = makeText("Pendulum", 30, TEXTCOLOUR, (400,250), True) #pendulum input button
    massTextSurfObj, massTextRectObj   = makeText("Mass-Spring", 30, TEXTCOLOUR, (400,350), True) #mass-spring input button
    titleTextSurfObj, titleTextRectObj = makeText("Choose a system", 50, TEXTCOLOUR, (400,100), True) #text

#animation window object setup
def setupRuntimeObjects():
    global backSurfObj, backRectObj, equiPauseSimSurfObj, equiPauseSimRectObj
    global maxAmpPauseSimSurfObj, maxAmpPauseSimRectObj, minAmpPauseSimSurfObj, minAmpPauseSimRectObj
    global pauseButtonPic, playButtonPic, pauseButtonRect, playButtonRect, refreshButtonPic, refreshButtonRect
    
    backSurfObj, backRectObj   = makeText("Change Options", 20, TEXTCOLOUR, (90,585), True) #change options button

    minAmpPauseSimSurfObj, minAmpPauseSimRectObj     = makeText("Min X", 25, TEXTCOLOUR, (175,540), True) #Min X pause button
    equiPauseSimSurfObj, equiPauseSimRectObj         = makeText("Equilibrium", 25, TEXTCOLOUR, (375,540), True) #EQ pause button
    maxAmpPauseSimSurfObj, maxAmpPauseSimRectObj     = makeText("Max X", 25, TEXTCOLOUR, (575,540), True) #Max X pause button
    
    pauseButtonPic   = pygame.image.load(PAUSE_PIC)
    playButtonPic    = pygame.image.load(PLAY_PIC)
    refreshButtonPic = pygame.image.load(REFRESH_PIC)
    
    pauseButtonRect   = pauseButtonPic.get_rect()
    playButtonRect    = playButtonPic.get_rect()
    refreshButtonRect = refreshButtonPic.get_rect()

    #position of pause, play & reset button
    pauseButtonRect.center   = (325,430)
    playButtonRect.center    = (425,430)
    refreshButtonRect.center = (770,50)

#return to main menu button setup
def setupMainMenuObject():
    global mainMenuSurfObj, mainMenuRectObj

    menu = MAIN
    status = OPTIONS #gives user options to choose
    
    #which question is being asked
    #the first question asked once an option is chosen
    pendInput = "first" 
    massInput = "first"
    
    #is this first time of asking?
    #first time asking a particular question
    pendFirstAsk = True
    massFirstAsk = True

    mainMenuSurfObj, mainMenuRectObj   = makeText("Go to Main Menu", 20, TEXTCOLOUR, (710,585), True) #main menu button

    return menu, status, pendInput, massInput, pendFirstAsk, massFirstAsk

#setup objects needed to input text for pendulum system
def setupPendInputObjects():
    pendLengthInput         = eztext.Input(maxlength=45, color=TEXTCOLOUR, prompt='Enter string length in cm (upto 150): ')
    pendAmpInput            = eztext.Input(maxlength=45, color=TEXTCOLOUR, prompt='Enter an amplitude in cm (less than string length): ')
    pendDampInput           = eztext.Input(maxlength=45, color=TEXTCOLOUR, prompt='Enter a damping constant (0 if undamped, upto 15): ')

    return pendLengthInput, pendAmpInput, pendDampInput

#setup objects needed to input text for mass-spring system
def setupMassInputObjects():
    massMassInput           = eztext.Input(maxlength=45, color=TEXTCOLOUR, prompt='Enter mass in grams (upto 10000): ')
    massSpringConstantInput = eztext.Input(maxlength=45, color=TEXTCOLOUR, prompt='Enter spring constant in N/m (upto 500): ')
    massAmpInput            = eztext.Input(maxlength=45, color=TEXTCOLOUR, prompt='Enter amplitude in cm (upto 100): ')
    massDampInput           = eztext.Input(maxlength=45, color=TEXTCOLOUR, prompt='Enter a damping constant (0 if undamped, upto 25): ')
    
    return massMassInput, massSpringConstantInput, massAmpInput, massDampInput

#get pendulum system inputs for simulation
def getPendInputs(menu, status, pendInput, pendLengthInput, pendAmpInput, pendDampInput, pendFirstAsk):
    #keep it global to prevent confusion when passing parameters
    #because different values returned each time function is called
    global pendLength, pendAmplitude, pendDamping
    
    #first question - string length
    if pendInput == "first":
        if pendFirstAsk: #first time asking this question
            clearScreen() #remove unwanted items from screen
            pendFirstAsk = False
        val = pendLengthInput.update(events, DISPLAYSURF) #get input
        pendLength = checkInput(status, val, 150, False) #check input
        if pendLength != None: #if returned value is not None, then it is valid
            pendInput = "second" #continue to next input
            pendFirstAsk = True #first time asking question 2, so reset this
            pendLength = pendLength/100 #convert to meters
        pendLengthInput.draw(DISPLAYSURF) #draw this object on-screen
        
###################the above pattern is repeated for all conditions when the mass-spring or pendulum system is asking for an input###################

    #second question - amplitude    
    elif pendInput == "second":
        if pendFirstAsk:
            clearScreen()
            pendFirstAsk = False
        val = pendAmpInput.update(events, DISPLAYSURF)
        pendAmplitude = checkInput(status, val, pendLength*100, False) #length*100 because need to convert back to cm
        if pendAmplitude != None:
            pendInput = "third"
            pendFirstAsk = True
            pendAmplitude = pendAmplitude/100 #convert to meters
        pendAmpInput.draw(DISPLAYSURF)

    #third question - damping    
    elif pendInput == "third":
        if pendFirstAsk:
            clearScreen()
            pendFirstAsk = False
        val = pendDampInput.update(events, DISPLAYSURF)
        pendDamping = checkInput(status, val, 15, True)
        if pendDamping != None:
            pendInput = "finished"
            pendFirstAsk = True
        pendDampInput.draw(DISPLAYSURF)

    #all done    
    elif pendInput == "finished": #all inputs have been entered and validated       
        menu = OPT_P #go to pendulum options to initialise objects for animation
        status = OPTIONS #not entering values, don't keep VAL_P
        pendInput = "first" #if user wants to re-enter values, they'll start from the beginning

    return pendInput, pendFirstAsk, status, menu

#get mass-spring system inputs for simulation
def getMassInputs(menu, status, massInput, massMassInput, massSpringConstantInput, massAmpInput, massDampInput, massFirstAsk):
    #keep it global to prevent confusion when passing parameters
    #because different values returned each time function is called
    global massMass, massSpringConstant, massAmplitude, massDamping
    
    #first question - mass
    if massInput == "first":
        if massFirstAsk:
            clearScreen()
            massFirstAsk = False
        val = massMassInput.update(events, DISPLAYSURF)
        massMass = checkInput(status, val, 10000, False)
        if massMass != None:
            massInput = "second"
            massFirstAsk = True
            massMass = massMass/1000 #convert to Kg
        massMassInput.draw(DISPLAYSURF)

    #second question - spring constant    
    elif massInput == "second":
        if massFirstAsk:
            clearScreen()
            massFirstAsk = False
        val = massSpringConstantInput.update(events, DISPLAYSURF)
        massSpringConstant = checkInput(status, val, 500, False)
        if massSpringConstant != None:
            massInput = "third"
            massFirstAsk = True
        massSpringConstantInput.draw(DISPLAYSURF)

    #third question - amplitude    
    elif massInput == "third":
        if massFirstAsk:
            clearScreen()
            massFirstAsk = False
        val = massAmpInput.update(events, DISPLAYSURF)
        massAmplitude = checkInput(status, val, 100, False)
        if massAmplitude != None:
            massInput = "fourth"
            massFirstAsk = True
            massAmplitude = massAmplitude/100 #convert to meters & round
        massAmpInput.draw(DISPLAYSURF)

    #fourth question - damping
    elif massInput == "fourth":
        if massFirstAsk:
            clearScreen()
            massFirstAsk = False
        val = massDampInput.update(events, DISPLAYSURF)
        massDamping = checkInput(status, val, 25, True)
        if massDamping != None:
            massInput = "finished"
            massFirstAsk = True
        massDampInput.draw(DISPLAYSURF)

    #all done    
    elif massInput == "finished": #all inputs entered & validated
        menu = OPT_M #go to mass options to initialise animation objects
        status = OPTIONS #not asking for input, leave VAL_M
        massInput = "first" #if user wants to re-enter values, they'll start from the beginning
        
    return massInput, massFirstAsk, status, menu

#add splash images/text here
def splashScreen(status):
    #if asking for pendulum inputs
    if status == VAL_P:
        picture   = pygame.image.load(PEND_PIC) #image of pendulum
        placement = (0,150) #position
    #if asking for mass-spring inputs
    elif status == VAL_M:
        picture   = pygame.image.load(MASS_PIC) #image of mass on a spring
        placement = (363,170) #position
    DISPLAYSURF.blit(picture, placement) #draw image onto screen at desired position

    #####option to add text later
    #if status == VAL_P:
    #    string = "Pendulum System"
    #elif status == VAL_M:
    #    string = "Mass-Spring System"
    #else:
    #    string = ""
    #splashTextObj, splashRectObj = makeText(string, 50, BLUE, (400,300), True)
    #DISPLAYSURF.blit(splashTextObj, splashRectObj)

#output alert if entered value isn't inside correct range
def outputAlert(string):
    alertTextObj, alertRectObj = makeText(string, 30, RED, ORIGIN, False) #make text
    alertRectObj.move_ip(0,120) #move text to desired position
    DISPLAYSURF.blit(alertTextObj, alertRectObj) #draw text

#check values that have been entered
def checkInput(status, val, maxi, damp):
    #setup alert string
    string = "must be greater than 0 and maximum of {0}".format(maxi) 
    if re.match("^[+-]?\d+(\.\d+)?$",str(val)): #RegEx
        val = float(val) #ensures value is of correct type
        #not checking damping constant
        if damp == False:
            if val>maxi or val<=0:
                outputAlert(string) #alert
                splashScreen(status) #draw image
                return None
            else:
                splashScreen(status) #draw image
                return val

        #this means the value being checked is damping constant
        #damping constant can be 0
        elif damp == True: 
            if val>maxi or val<0:
                outputAlert(string) #alert
                splashScreen(status) #draw image
                return None
            else:
                splashScreen(status) #draw image
                return val
    else:
        if str(val) != "None":
            outputAlert(string) #alert if type is not correct
        splashScreen(status) #draw image
        return None

if __name__ == "__main__":
    main() #automatically starts main procedure when file is run
