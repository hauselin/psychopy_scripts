import pandas as pd
import numpy as np
import scipy as sp
import random, os, time
from psychopy import visual, core, event, data, gui, logging, parallel, monitors
from scipy import stats

# set DEBUG mode: if True, participant ID will be 999 and display will not be fullscreen. If False, will have to provide participant ID and will be in fullscreen mode
DEBUG = False
sendTTL = False # whether to send TTL pulses to acquisition computer
parallelPortAddress = 49168 # set parallel port address (EEG3: 49168, EEG1: 57360)

# display name (set up beforehand in PsychoPy preferences/settings)
#monitor = 'EEG3Display'
monitor = 'iMac'
#monitor = 'BehavioralLab'
#monitor = 'MacBookAir'

stimulusDir = 'Stimuli' + os.path.sep # stimulus directory/folder/path

rewardLevels = [2, 4, 6, 9, 12]
effortLevels = [1, 3, 5, 6, 7]

#import csv file with unique trials
#trialsCSV = "GoNoGo.csv"
#trialsList = pd.read_csv(stimulusDir + trialsCSV)

#EXPERIMENT SET UP
info = {} # create empty dictionary to store stuff

if DEBUG:
    fullscreen = False #set fullscreen variable = False
    # logging.console.setLevel(logging.DEBUG)
    info['participant'] = 999 #let 999 = debug participant no.
    info['email'] = 'xxx@gmail.com'
    info['age'] = 18
else: #if DEBUG is not False... (or True)
    fullscreen = True #set full screen
    # logging.console.setLevel(logging.WARNING)
    info['participant'] = '' #dict key to store participant no.
    info['email'] = ''
    info['age'] = ''
    #present dialog to collect info
    dlg = gui.DlgFromDict(info) #create a dialogue box (function gui)
    if not dlg.OK: #if dialogue response is NOT OK, quit
        #moveFiles(dir = 'Data')
        core.quit()

''' DO NOT EDIT BEGIN '''
info['participant'] = int(info['participant'])
info['age'] = int(info['age'])
info['email'] = str(info['email'])
''' DO NOT EDIT BEGIN '''

info['fixationFrames'] = 18 #frames
#info['postFixationFrames'] = 36 #frames (600ms)
#info['postFixationFrames'] = np.arange(36, 43, 1) #36 frames to 42 frames (600 ms to 700ms)
# post fixation frame number to be drawn from exponential distribution (36 to 42 frames)
f = sp.stats.expon.rvs(size=10000, scale=0.035, loc=0.3) * 100
f = np.around(f)
f = f[f <= 43] # max
f = f[f >= 36] # min
info['postFixationFrames'] = f
info['targetFrames'] = 180 #frames (at 60Hz, 60 frames = 1 second); max time to wait for response
info['blockEndPause'] = 15 #frames
info['feedbackTime'] = 42 #frames
info['startTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #create str of current date/time
info['endTime'] = '' # to be saved later on
# info['ITIDuration'] = np.arange(0.50, 0.81, 0.05) #a numpy array of ITI in seconds (to be randomly selected later for each trial)
seconds = sp.stats.expon.rvs(size=10000, scale=0.4) # exponential distribution
seconds = np.around(seconds/0.05) * 0.05 # round to nearest 0.05
seconds = seconds[seconds <= 1] # max
seconds = seconds[seconds >= 0.5] # min
info['ITIDuration'] = seconds

# runMentalMathBlockAccuracy = 0
# runMentalMathBlockRt = np.nan
charityChosen = 'charity'

info['mentalMathUpdatingCurrentTrialAcc'] = 0
info['mentalMathUpdatingCurrentTrialRt'] = np.nan

globalClock = core.Clock() # create and start global clock to track OVERALL elapsed time
ISI = core.StaticPeriod(screenHz = 60) # function for setting inter-trial interval later

# create window to draw stimuli on
win = visual.Window(size = (1300, 900), fullscr = fullscreen, units = 'norm', monitor = monitor, colorSpace = 'rgb', color = (-1, -1, -1))
#create mouse
mouse = event.Mouse(visible = False, win = win)
mouse.setVisible(0) # make mouse invisible

if sendTTL:
    port = parallel.ParallelPort(address = parallelPortAddress)
    port.setData(0) #make sure all pins are low



########################################################################
#CUSTOM FUNCTIONS TO DO STUFF
def showInstructions(text, timeBeforeAutomaticProceed=0, timeBeforeShowingSpace =0):
    '''Show instructions.
    text: Provide a list with instructions/text to present. One list item will be presented per page.
    timeBeforeAutomaticProceed: The time in seconds to wait before proceeding automatically.
    timeBeforeShowingSpace: The time in seconds to wait before showing 'Press space to continue' text.
    '''
    mouse.setVisible(0)
    event.clearEvents()

    # 'Press space to continue' text for each 'page'
    continueText = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = "Press space to continue", height = 0.04, wrapWidth = 1.4, pos = [0.0, 0.0])
    # instructions to be shown
    instructText = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = 'DEFAULT', height = 0.08, wrapWidth = 1.4, pos = [0.0, 0.5])

    for i in range(len(text)): # for each item/page in the text list
        instructText.text = text[i] # set text for each page
        if timeBeforeAutomaticProceed == 0 and timeBeforeShowingSpace == 0:
            while not event.getKeys(keyList = ['space']):
                continueText.draw(); instructText.draw(); win.flip()
                if event.getKeys(keyList = ['backslash']):
                    #moveFiles(dir = 'Data')
                    core.quit()
                elif event.getKeys(['bracketright']): #if press 7, skip to next block
                    return None
        elif timeBeforeAutomaticProceed != 0 and timeBeforeShowingSpace == 0:
            # clock to calculate how long to show instructions
            # if timeBeforeAutomaticProceed is not 0 (e.g., 3), then each page of text will be shown 3 seconds and will proceed AUTOMATICALLY to next page
            instructTimer = core.Clock()
            while instructTimer.getTime() < timeBeforeAutomaticProceed:
                if event.getKeys(keyList = ['backslash']):
                    core.quit()
                elif event.getKeys(['bracketright']):
                    return None
                instructText.draw(); win.flip()
        elif timeBeforeAutomaticProceed == 0 and timeBeforeShowingSpace != 0:
            instructTimer = core.Clock()
            while instructTimer.getTime() < timeBeforeShowingSpace:
                if event.getKeys(keyList = ['backslash']):
                    core.quit()
                elif event.getKeys(['bracketright']):
                    return None
                instructText.draw(); win.flip()
            win.flip(); event.clearEvents()

    instructText.setAutoDraw(False)
    continueText.setAutoDraw(False)

    for frameN in range(info['blockEndPause']):
        win.flip() # wait at the end of the block

def runMentalMathBlock(taskName='mentalMathUpdating', blockType='', trials=1, feedback=False, saveData=True, practiceTrials=10, digits=4, digitChange=3, digitsToModify=2, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None):
    '''Run a block of trials.
    blockType: custom name of the block; if blockType is set to 'practice', then no TTLs will be sent and the number of trials to run will be determined by argument supplied to parameter practiceTrials.
    trials: number of times to repeat each unique trial
    feedback: whether feedback is presented or not
    saveData = whether to save data to csv file
    practiceTrials: no. of practice trials to run
    digits: number of digits to generate
    digitChange = number to add/subtract to/from each digit
    digitsToModify: number of digits to change when generating wrong (alternative) answer
    titrate: whether to adjust difficulty of task based on performance; if set to True, subsequent targetFrames (max response time) for subsequent blocks will be affected
    rtmaxFrames: max rt (in frames); default is None, which takes value from info['targetFrames']; if a value is provided, default will be overwritten
    blockMaxTimeSeconds: end block if overall time of BLOCK (in seconds) has passed
    experimentMaxTimeSeconds: end block if overall time of EXPERIMENT (in seconds) has passed
    '''

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], taskName)
    # create name for logfile
    # logFilename = "{:03d}-{}-{}".format(int(info['participant']), info['startTime'], taskName)
    # logfile = logging.LogFile(logFilename + ".log", filemode = 'w', level = logging.EXP) #set logging information (core.quit() is required at the end of experiment to store logging info!!!)
    #logging.console.setLevel(logging.DEBUG) #set COSNSOLE logging level

    '''DO NOT EDIT BEGIN'''
    mouse.setVisible(0) #make mouse invisible

    #Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True

    trialsDfMath = pd.DataFrame(index=np.arange(trials)) # create empty dataframe to store trial info

    #if this is a practice block
    if blockType == 'practice':
        trialsDfMath = trialsDfMath[0:practiceTrials] #number of practice trials to present
    '''DO NOT EDIT END'''

    #store additional info in dataframe
    trialsDfMath['participant'] = int(info['participant'])
    try:
        trialsDfMath['age'] = int(info['age'])
        trialsDfMath['gender'] = info['gender']
        trialsDfMath['handedness'] = info['handedness']
        trialsDfMath['ethnicity'] = info['ethnicity']
        trialsDfMath['ses'] = info['ses']
    except:
        pass
    trialsDfMath['trialNo'] = range(1, len(trialsDfMath) + 1) #add trialNo
    trialsDfMath['blockType'] = blockType #add blockType
    trialsDfMath['task'] = taskName #task name
    trialsDfMath['fixationFrames'] = info['fixationFrames']
    trialsDfMath['postFixationFrames'] = np.nan
    if rtMaxFrames is None:
        trialsDfMath['targetFrames'] = info['targetFrames']
    else:
        trialsDfMath['targetFrames'] = rtMaxFrames
    trialsDfMath['startTime'] = info['startTime']
    trialsDfMath['endTime'] = info['endTime']

    #create variables to store data later
    trialsDfMath['blockNumber'] = 0 #add blockNumber
    trialsDfMath['elapsedTime'] = np.nan
    trialsDfMath['resp'] = None
    trialsDfMath['rt'] = np.nan
    trialsDfMath['iti'] = np.nan
    trialsDfMath['responseTTL'] = np.nan
    trialsDfMath['choice'] = np.nan
    trialsDfMath['overallTrialNum'] = 0 #cannot use np.nan because it's a float, not int!
    trialsDfMath['digits'] = digits
    trialsDfMath['digitChange'] = digitChange
    trialsDfMath['digitsToModify'] = digitsToModify
    trialsDfMath['testDigits'] = None
    trialsDfMath['correctAnswer'] = None
    trialsDfMath['wrongAnswer'] = None
    trialsDfMath['correctKey'] = None
    trialsDfMath['acc'] = np.nan

    ''' define number sequence and correct/incorrect responses for block '''
    # timing for updating task
    testDigitFrames = 30 # frames to show each test digit
    postTestDigitBlankFrames = 42 # blank frames after each digit
    postAllTestDigitBlankFrames = 30 # blank frames after all digits

    trialsDfMath['testDigitFrames'] = testDigitFrames
    trialsDfMath['postTestDigitBlankFrames'] = postTestDigitBlankFrames
    trialsDfMath['postAllTestDigitBlankFrames'] = postAllTestDigitBlankFrames

    # populate dataframe with test number sequences and answers
    for rowI in range(0, trialsDfMath.shape[0]):
        digitsList = random.sample(range(0, 10), digits) # randomly generate digits in given range without replacement
        digitsListAnswer = []
        for digitI in digitsList:
            # print "old digit is {0}".format(digitI)
            digitNew = digitI + digitChange # update digit
            if digitNew > 9: # if new digit > 9, subtract 10 to get the ones digit
                digitNew -= 10
            elif digitNew < 0: # if new digit is < 0, get its absolute value
                digitNew = abs(digitNew)
            # print "new digit is {0}".format(digitNew)
            digitsListAnswer.append(digitNew)
            #print "old list is {0}".format(digitsList)
            #print "new list is {0}".format(digitsListAnswer)

        # print "old list is {0}".format(digitsList)
        # print "new list is {0}".format(digitsListAnswer)

        correctAnswer = ''.join(str(x) for x in digitsListAnswer) # as 1 string
        wrongAnswerList = digitsListAnswer[:]

        digitsModifyIdx = random.sample(range(0, digits), digitsToModify) # indices of correct answer to modify to produce wrong answer later

        # define fake response
        for wrongAnswerIdx, wrongAnswerI in enumerate(wrongAnswerList):

            if wrongAnswerIdx in digitsModifyIdx:
                if wrongAnswerList[wrongAnswerIdx] in [1, 2, 3, 4, 5, 6, 7, 8]:
                    wrongAnswerList[wrongAnswerIdx] += random.choice([-1, 1])
                elif wrongAnswerList[wrongAnswerIdx] == 9:
                    wrongAnswerList[wrongAnswerIdx] -= 1
                elif wrongAnswerList[wrongAnswerIdx] == 0:
                    wrongAnswerList[wrongAnswerIdx] += 1

        wrongAnswer = ''.join(str(x) for x in wrongAnswerList) # as 1 string

        # store in dataframe
        trialsDfMath.loc[rowI, 'testDigits'] = ''.join(str(x) for x in digitsList)
        trialsDfMath.loc[rowI, 'correctAnswer'] = ''.join(str(x) for x in correctAnswer)
        trialsDfMath.loc[rowI, 'wrongAnswer'] = ''.join(str(x) for x in wrongAnswer)
        trialsDfMath.loc[rowI, 'correctKey'] = random.choice(['f', 'j'])

    '''DO NOT EDIT BEGIN'''
    #Assign blockNumber based on existing csv file. Read the csv file and find the largest block number and add 1 to it to reflect this block's number.
    try:
        blockNumber = max(pd.read_csv(filename)['blockNumber']) + 1
        trialsDfMath['blockNumber'] = blockNumber
    except: #if fail to read csv, then it's block 1
        blockNumber = 1
        trialsDfMath['blockNumber'] = blockNumber
    '''DO NOT EDIT END'''


    #create stimuli that are constant for entire block
    #draw stimuli required for this block
    #[1.0,-1,-1] is red; #[1, 1, 1] is white
    fixation = visual.TextStim(win = win, units = 'norm', height = 0.08, ori = 0, name = 'target', text = '+', font = 'Courier New Bold', colorSpace = 'rgb', color = [-.3, -.3, -.3], opacity = 1)

    reminderText = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = "+{:.0f}".format(digitChange), font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, 0.17))

    testDigit = visual.TextStim(win = win, units = 'norm', height = 0.20, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    correctDigits = visual.TextStim(win = win, units = 'norm', height = 0.12, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    wrongDigits = visual.TextStim(win = win, units = 'norm', height = 0.12, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    keyD = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = 'D', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.3, 0.1))

    keyF = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = 'F', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.12, 0.1))

    keyJ = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = 'J', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.12, 0.1))

    keyK = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = 'K', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.3, 0.1))



    #create clocks to collect reaction and trial times
    respClock = core.Clock()
    trialClock = core.Clock()

    for mathTrialI, thisTrialMath in trialsDfMath.iterrows(): #for each trial...
        ''' DO NOT EDIT BEGIN '''
        #add overall trial number to dataframe
        try: #try reading csv file dimensions (rows = no. of trials)
            #thisTrialMath['overallTrialNum'] = pd.read_csv(filename).shape[0] + 1
            trialsDfMath.loc[mathTrialI, 'overallTrialNum'] = pd.read_csv(filename).shape[0] + 1
            ####print 'Overall Trial No: %d' %thisTrialMath['overallTrialNum']
        except: #if fail to read csv, then it's trial 1
            #thisTrialMath['overallTrialNum'] = 1
            trialsDfMath.loc[mathTrialI, 'overallTrialNum'] = 1
            ####print 'Overall Trial No: %d' %thisTrialMath['overallTrialNum']

        if sendTTL and not blockType == 'practice':
            port.setData(0) #make sure all pins are low before new trial
            ###print 'Start Trial TTL 0 set all pins to low'

        # if there's a max time for this block, end block when time's up
        if blockMaxTimeSeconds is not None:
            try:
                if trialsDfMath.loc[mathTrialI-1, 'elapsedTime'] - trialsDfMath.loc[0, 'elapsedTime'] >= blockMaxTimeSeconds:
                    print trialsDfMath.loc[mathTrialI-1, 'elapsedTime'] - trialsDfMath.loc[0, 'elapsedTime']
                    print "block time out"
                    return None
            except:
                pass
        # if there's a max time for entire experiment, end block when time's up
        if experimentMaxTimeSeconds is not None:
            try:
                firstTrial = pd.read_csv(filename).head(1).reset_index()
                finalTrial = pd.read_csv(filename).tail(1).reset_index()
                if finalTrial.loc[0, 'elapsedTime'] - firstTrial.loc[0, 'elapsedTime'] >= experimentMaxTimeSeconds:
                    print "experiment time out"
                    return None
            except:
                pass

        ''' DO NOT EDIT END '''


        #1: draw and show fixation
        fixation.setAutoDraw(True) #draw fixation on next flips
        for frameN in range(info['fixationFrames']):
            win.flip()
        fixation.setAutoDraw(False) #stop showing fixation

        #2: postfixation black screen
        postFixationBlankFrames = int(random.choice(info['postFixationFrames']))
        ###print postFixationBlankFrames
        trialsDfMath.loc[mathTrialI, 'postFixationFrames'] = postFixationBlankFrames #store in dataframe
        for frameN in range(postFixationBlankFrames):
            win.flip()

        reminderText.setAutoDraw(True)

        #3: draw stimulus (digits) one by one
        for d in thisTrialMath['testDigits']:
            testDigit.setText(d)
            testDigit.setAutoDraw(True)
            for frameN in range(testDigitFrames):
                win.flip()
            testDigit.setAutoDraw(False)
            # blank screen for a while before next digit
            for frameN in range(postTestDigitBlankFrames):
                win.flip()

        reminderText.setAutoDraw(False)

        for frameN in range(postAllTestDigitBlankFrames):
            win.flip()

        #4: draw response options
        correctDigits.setText(thisTrialMath['correctAnswer'])
        wrongDigits.setText(thisTrialMath['wrongAnswer'])

        # set option positions
        if thisTrialMath['correctKey'] == "f":
            correctDigits.setPos((-0.12, 0.0)) # left
            wrongDigits.setPos((0.12, 0.0)) # right
        elif thisTrialMath['correctKey'] == "j":
            correctDigits.setPos((0.12, 0.0)) # right
            wrongDigits.setPos((-0.12, 0.0)) # left

        correctDigits.setAutoDraw(True)
        wrongDigits.setAutoDraw(True)
        keyF.setAutoDraw(True)
        keyJ.setAutoDraw(True)

        # if titrating, determine stuff automatically
        if titrate:
            # determine response duration
            try:
                last2Trials = pd.read_csv(filename).tail(2).reset_index()
                if last2Trials.loc[1, 'acc'] == 1 and trialsDfMath.loc[mathTrialI, 'targetFrames'] >= 24: # if previous trial correct
                    trialsDfMath.loc[mathTrialI, 'targetFrames'] = last2Trials.loc[1, 'targetFrames'] - 6 # minus 6 frames (100 ms)
                    trialsDfMath.loc[mathTrialI, 'postTestDigitBlankFrames'] = trialsDfMath.loc[mathTrialI-1, 'postTestDigitBlankFrames'] - 1
                elif last2Trials.loc[0:1, 'acc'].sum() == 0:
                    trialsDfMath.loc[mathTrialI, 'targetFrames'] = last2Trials.loc[1, 'targetFrames'] + 6 # plus 6 frames (100 ms)
                    trialsDfMath.loc[mathTrialI, 'postTestDigitBlankFrames'] = trialsDfMath.loc[mathTrialI-1, 'postTestDigitBlankFrames'] + 1
                else:
                    trialsDfMath.loc[mathTrialI, 'targetFrames'] = last2Trials.loc[1, 'targetFrames']
                    trialsDfMath.loc[mathTrialI, 'postTestDigitBlankFrames'] = trialsDfMath.loc[mathTrialI-1, 'postTestDigitBlankFrames']
                # print trialsDfMath.loc[mathTrialI, 'targetFrames']
            except:
                pass

        try:
            targetFramesCurrentTrial = int(trialsDfMath.loc[mathTrialI, 'targetFrames'])
        except:
            try:
                targetFramesCurrentTrial = int(rtMaxFrames)
            except:
                try:
                    targetFramesCurrentTrial = int(info['targetFrames'])
                except:
                    targetFramesCurrentTrial = 180

        win.callOnFlip(respClock.reset) #reset response clock on next flip
        win.callOnFlip(trialClock.reset) #reset trial clock on next flip

        event.clearEvents() #clear events

        for frameN in range(targetFramesCurrentTrial):
            if frameN == 0: #on first frame/flip/refresh
                if sendTTL and not blockType == 'practice':
                    win.callOnFlip(port.setData, int(thisTrialMath['TTLStim']))
                else:
                    pass
                ##print "First frame in Block %d Trial %d OverallTrialNum %d" %(blockNumber, mathTrialI + 1, trialsDfMath.loc[mathTrialI, 'overallTrialNum'])
                ##print "Stimulus TTL: %d" %(int(thisTrialMath['TTLStim']))
            else:
                keys = event.getKeys(keyList = ['f', 'j', 'backslash', 'bracketright'])
                if len(keys) > 0 and trialsDfMath.loc[mathTrialI, 'resp'] is None: #if a response has been made
                    trialsDfMath.loc[mathTrialI, 'rt'] = respClock.getTime() #store RT
                    trialsDfMath.loc[mathTrialI, 'resp'] = keys[0] #store response in pd df

                    if keys[0] == 'f' and thisTrialMath['correctKey'] == 'f': #if go trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) #correct response
                        trialsDfMath.loc[mathTrialI, 'responseTTL'] = 15
                        trialsDfMath.loc[mathTrialI, 'acc'] = 1
                        ##print 'correct keypress: %s' %str(trialsDfMath.loc[mathTrialI, 'resp'])
                        ##print "Response TTL: 15"

                    elif keys[0] == 'j' and thisTrialMath['correctKey'] == 'j': #if go trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) #correct response
                        trialsDfMath.loc[mathTrialI, 'responseTTL'] = 15
                        trialsDfMath.loc[mathTrialI, 'acc'] = 1
                        ##print 'correct keypress: %s' %str(trialsDfMath.loc[mathTrialI, 'resp'])
                        ##print "Response TTL: 15"

                    elif keys[0] == 'j' and thisTrialMath['correctKey'] == 'f': #if nogo trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(16) #incorrect response
                        trialsDfMath.loc[mathTrialI, 'responseTTL'] = 16
                        trialsDfMath.loc[mathTrialI, 'acc'] = 0
                        ##print 'incorrect keypress: %s' %str(trialsDfMath.loc[mathTrialI, 'resp'])
                        ##print "Response TTL: 16"

                    elif keys[0] == 'f' and thisTrialMath['correctKey'] == 'j': #if nogo trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(16) #incorrect response
                        trialsDfMath.loc[mathTrialI, 'responseTTL'] = 16
                        trialsDfMath.loc[mathTrialI, 'acc'] = 0
                        ##print 'incorrect keypress: %s' %str(trialsDfMath.loc[mathTrialI, 'resp'])
                        ##print "Response TTL: 16"

                    #remove stimulus from screen
                    correctDigits.setAutoDraw(False); wrongDigits.setAutoDraw(False)
                    keyF.setAutoDraw(False)
                    keyJ.setAutoDraw(False)
                    win.flip() # clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDfMath.loc[mathTrialI, 'resp'] is None: #if no response made
            trialsDfMath.loc[mathTrialI, 'acc'] = 0
            correctDigits.setAutoDraw(False)
            wrongDigits.setAutoDraw(False)
            keyF.setAutoDraw(False)
            keyJ.setAutoDraw(False)
            win.flip() #clear screen (remove stuff from screen)

        # if both response options are the same, then accuracy is always correct
        if digitsToModify == 0 and trialsDfMath.loc[mathTrialI, 'resp'] is not None:
            trialsDfMath.loc[mathTrialI, 'acc'] = 1

        if sendTTL and not blockType == 'practice':
            port.setData(0) #parallel port: set all pins to low

        trialsDfMath.loc[mathTrialI, 'elapsedTime'] = globalClock.getTime() #store total elapsed time in seconds
        trialsDfMath.loc[mathTrialI, 'endTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #store current time
        iti = round(random.choice(info['ITIDuration']), 2) #randomly select an ITI duration
        trialsDfMath.loc[mathTrialI, 'iti'] = iti #store ITI duration

        #start inter-trial interval...
        ISI.start(iti)

        ###print "TRIAL OK TRIAL %d OVERALL TRIAL %d" %(i + 1, int(trialsDfMath.loc[mathTrialI, 'overallTrialNum']))

        ''' DO NOT EDIT BEGIN '''
        #if press 0 (quit script) or 7 (skip block)
        if trialsDfMath.loc[mathTrialI, 'resp'] == 'backslash':
            trialsDfMath.loc[mathTrialI, 'responseTTL'] = np.nan
            trialsDfMath.loc[mathTrialI, 'acc'] = np.nan
            trialsDfMath.loc[mathTrialI, 'resp'] = None
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDfMath[mathTrialI:mathTrialI+1].to_csv(filename, header = True if mathTrialI == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index mathTrialI is 0 AND block is 1 (first block)
            #moveFiles(dir = 'Data')
            core.quit() #quit when 'backslash' has been pressed
        elif trialsDfMath.loc[mathTrialI, 'resp'] == 'bracketright':#if press 7, skip to next block
            trialsDfMath.loc[mathTrialI, 'responseTTL'] = np.nan
            trialsDfMath.loc[mathTrialI, 'acc'] = np.nan
            trialsDfMath.loc[mathTrialI, 'responseTTL'] = np.nan
            trialsDfMath.loc[mathTrialI, 'resp'] == None
            #naturalText.setAutoDraw(False)
            #healthText.setAutoDraw(False)
            #tasteText.setAutoDraw(False)
            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDfMath[mathTrialI:mathTrialI+1].to_csv(filename, header = True if mathTrialI == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index mathTrialI is 0 AND block is 1 (first block)
            return None

        # global runMentalMathBlockAccuracy
        info['mentalMathUpdatingCurrentTrialAcc'] = trialsDfMath.loc[mathTrialI, 'acc']
        # global runMentalMathBlockRt
        info['mentalMathUpdatingCurrentTrialRt'] = trialsDfMath.loc[mathTrialI, 'rt']

        #print info['mentalMathUpdatingCurrentTrialAcc']
        #print info['mentalMathUpdatingCurrentTrialRt']

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDfMath[mathTrialI:mathTrialI+1].to_csv(filename, header = True if mathTrialI == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index mathTrialI is 0 AND block is 1 (first block)
        ''' DO NOT EDIT END '''

        ISI.complete() #end inter-trial interval

        #feedback for trial
        if feedback:
            #stimuli
            accuracyFeedback = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDfMath.loc[mathTrialI, 'acc'] == 1: #if nogo trial and keypress
                accuracyFeedback.setText(random.choice(["Correct"]))
            elif trialsDfMath.loc[mathTrialI, 'resp'] is None:
                accuracyFeedback.setText('Too slow')
            else:
                accuracyFeedback.setText('Wrong')
            for frameN in range(info['feedbackTime']):
                accuracyFeedback.draw()
                win.flip()

    for frameN in range(info['blockEndPause']):
        win.flip() #wait at the end of the block

def runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='mixed', reps=1, feedback=False, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[1, 3, 5, 7, 9], effort=[20, 30, 40, 50, 60], jitter=None):
    '''Run a block of trials.
    blockType: custom name of the block; if blockType is set to 'practice', then no TTLs will be sent and the number of trials to run will be determined by argument supplied to parameter practiceTrials. Can be 'mixed', 'self', or 'charity'
    reps: number of times to repeat each unique trial
    feedback: whether feedback is presented or not
    saveData = whether to save data to csv file
    practiceTrials: no. of practice trials to run
    titrate: whether to adjust difficulty of task based on performance; if set to True, subsequent targetFrames (max response time) for subsequent blocks will be affected
    rtmaxFrames: max rt (in frames); default is None, which takes value from info['targetFrames']; if a value is provided, default will be overwritten
    blockMaxTimeSeconds: end block if overall time of BLOCK (in seconds) has passed
    experimentMaxTimeSeconds: end block if overall time of EXPERIMENT (in seconds) has passed
    '''

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], taskName)
    # create name for logfile
    # logFilename = "{:03d}-{}-{}".format(int(info['participant']), info['startTime'], taskName)
    # logfile = logging.LogFile(logFilename + ".log", filemode = 'w', level = logging.EXP) #set logging information (core.quit() is required at the end of experiment to store logging info!!!)
    #logging.console.setLevel(logging.DEBUG) #set COSNSOLE logging level

    mouse.setVisible(0) #make mouse invisible

    #Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True

    '''GENERATE TRIALS FOR EFFORT/REWARD CHOICE TASK'''
    rewardEffortCombi = [(r, e) for r in reward for e in effort] # all combinations
    rewardEffortCombi = pd.DataFrame(rewardEffortCombi)
    rewardEffortCombi.columns = ['reward', 'effort']
    rewardEffortCombi['beneficiary'] = 'self'

    rewardEffortCombi2 = [(r, e) for r in reward for e in effort] # all combinations
    rewardEffortCombi2 = pd.DataFrame(rewardEffortCombi2)
    rewardEffortCombi2.columns = ['reward', 'effort']
    rewardEffortCombi2['beneficiary'] = 'charity'

    rewardEffortCombi3 = [(r, e) for r in reward for e in effort] # all combinations
    rewardEffortCombi3 = pd.DataFrame(rewardEffortCombi3)
    rewardEffortCombi3.columns = ['reward', 'effort']
    rewardEffortCombi3['beneficiary'] = 'otherperson'

    trialsInBlock = pd.concat([rewardEffortCombi, rewardEffortCombi2, rewardEffortCombi3] * reps, ignore_index=True)

    if blockType == 'self':
        trialsInBlock = trialsInBlock[trialsInBlock.beneficiary == 'self']
    elif blockType == 'charity':
        trialsInBlock = trialsInBlock[trialsInBlock.beneficiary == 'charity']
    elif blockType == 'otherperson':
        trialsInBlock = trialsInBlock[trialsInBlock.beneficiary == 'otherperson']
    elif blockType == 'mixed':
        trialsInBlock = trialsInBlock

    trialsInBlock = trialsInBlock.reindex(np.random.permutation(trialsInBlock.index)).reset_index(drop=True) # shuffle/randomize order

    trialsInBlock['rewardJittered'] = trialsInBlock.reward

    if jitter is not None:
        trialsInBlock['rewardJittered'] = trialsInBlock.reward + np.around(np.random.normal(scale=0.1, size=trialsInBlock.shape[0]) / 0.05) * 0.05


    trialsDf = pd.DataFrame(index=np.arange(trialsInBlock.shape[0])) # create empty dataframe to store trial info

    #store info in dataframe
    trialsDf['participant'] = int(info['participant'])
    try:
        trialsDf['age'] = int(info['age'])
        trialsDf['gender'] = info['gender']
        trialsDf['handedness'] = info['handedness']
        trialsDf['ethnicity'] = info['ethnicity']
        trialsDf['ses'] = info['ses']
    except:
        pass
    trialsDf['trialNo'] = range(1, len(trialsDf) + 1) #add trialNo
    trialsDf['blockType'] = blockType # add blockType
    trialsDf['task'] = taskName # task name
    trialsDf['fixationFrames'] = info['fixationFrames']
    trialsDf['postFixationFrames'] = np.nan
    if rtMaxFrames is None:
        trialsDf['targetFrames'] = int(info['targetFrames'])
    else:
        trialsDf['targetFrames'] = int(rtMaxFrames)
    trialsDf['startTime'] = info['startTime']
    trialsDf['endTime'] = info['endTime']

    #create variables to store data later
    trialsDf['blockNumber'] = 0 # add blockNumber
    trialsDf['elapsedTime'] = np.nan
    trialsDf['resp'] = None
    trialsDf['rt'] = np.nan
    trialsDf['iti'] = np.nan
    trialsDf['responseTTL'] = np.nan
    trialsDf['choice'] = np.nan
    trialsDf['choiceText'] = ''
    trialsDf['overallTrialNum'] = 0 #cannot use np.nan because it's a float, not int!
    trialsDf['acc'] = np.nan
    trialsDf['accUpdating'] = np.nan
    trialsDf['rtUpdating'] = np.nan

    trialsDf = pd.concat([trialsDf, trialsInBlock], axis=1)

    # if this is a practice block
    if blockType == 'practice':
        trialsDf = trialsDf[0:practiceTrials] # practice trials to present

    # print trialsDf

    # Assign blockNumber based on existing csv file. Read the csv file and find the largest block number and add 1 to it to reflect this block's number.
    '''DO NOT EDIT BEGIN'''
    try:
        blockNumber = max(pd.read_csv(filename)['blockNumber']) + 1
        trialsDf['blockNumber'] = blockNumber
    except: #if fail to read csv, then it's block 1
        blockNumber = 1
        trialsDf['blockNumber'] = blockNumber
    '''DO NOT EDIT END'''

    # create stimuli that are constant for entire block
    # draw stimuli required for this block
    # [1.0,-1,-1] is red; #[1, 1, 1] is white
    fixation = visual.TextStim(win=win, units='norm', height=0.08, ori=0, name='target', text='+', font='Courier New Bold', colorSpace='rgb', color=[-.3, -.3, -.3], opacity=1)

    constantOptionEffort = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = 'add 0', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.2, 0.05))

    constantOptionReward = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = '1 credit', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.2, -0.05))

    varyingOptionEffort = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = 'XXX', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.2, 0.05))

    varyingOptionReward = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = 'XXX', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.2, -0.05))

    beneficiaryText = visual.TextStim(win = win, units = 'norm', height = 0.1, ori = 0, name = 'target', text = 'XXX', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, 0.2))

    practiceInstructText = visual.TextStim(win = win, units = 'norm', height = 0.03, ori = 0, name = 'target', text = 'Press F for left option and J for right option.', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, 0.15))


    # create clocks to collect reaction and trial times
    respClock = core.Clock()
    trialClock = core.Clock()

    for i, thisTrial in trialsDf.iterrows(): #for each trial...
        ''' DO NOT EDIT BEGIN '''
        #add overall trial number to dataframe
        try: #try reading csv file dimensions (rows = no. of trials)
            #thisTrial['overallTrialNum'] = pd.read_csv(filename).shape[0] + 1
            trialsDf.loc[i, 'overallTrialNum'] = pd.read_csv(filename).shape[0] + 1
            ####print 'Overall Trial No: %d' %thisTrial['overallTrialNum']
        except: #if fail to read csv, then it's trial 1
            #thisTrial['overallTrialNum'] = 1
            trialsDf.loc[i, 'overallTrialNum'] = 1
            ####print 'Overall Trial No: %d' %thisTrial['overallTrialNum']

        if sendTTL and not blockType == 'practice':
            port.setData(0) #make sure all pins are low before new trial
            ###print 'Start Trial TTL 0 set all pins to low'

        # if there's a max time for this block, end block when time's up
        if blockMaxTimeSeconds is not None:
            try:
                if trialsDf.loc[i-1, 'elapsedTime'] - trialsDf.loc[0, 'elapsedTime'] >= blockMaxTimeSeconds:
                    print trialsDf.loc[i-1, 'elapsedTime'] - trialsDf.loc[0, 'elapsedTime']
                    print "block time out"
                    return None
            except:
                pass
        # if there's a max time for entire experiment, end block when time's up
        if experimentMaxTimeSeconds is not None:
            try:
                firstTrial = pd.read_csv(filename).head(1).reset_index()
                finalTrial = pd.read_csv(filename).tail(1).reset_index()
                if finalTrial.loc[0, 'elapsedTime'] - firstTrial.loc[0, 'elapsedTime'] >= experimentMaxTimeSeconds:
                    print "experiment time out"
                    return None
            except:
                pass

        ''' DO NOT EDIT END '''

        #1: draw and show fixation
        fixation.setAutoDraw(True) #draw fixation on next flips
        for frameN in range(info['fixationFrames']):
            win.flip()
        fixation.setAutoDraw(False) #stop showing fixation

        #2: postfixation black screen
        postFixationBlankFrames = int(random.choice(info['postFixationFrames']))
        ###print postFixationBlankFrames
        trialsDf.loc[i, 'postFixationFrames'] = postFixationBlankFrames #store in dataframe
        for frameN in range(postFixationBlankFrames):
            win.flip()

        #3: draw stimulus
        #varyingOptionEffort.setText("{} trials".format(thisTrial['effort']))
        #varyingOptionReward.setText("${:.2f}".format(thisTrial['rewardJittered']))
        varyingOptionEffort.setText("add {}".format(thisTrial['effort']))
        varyingOptionReward.setText("{} credits".format(thisTrial['rewardJittered']))

        constantOptionEffort.setAutoDraw(True)
        constantOptionReward.setAutoDraw(True)
        varyingOptionEffort.setAutoDraw(True)
        varyingOptionReward.setAutoDraw(True)

        if thisTrial['beneficiary'] == 'charity':
            beneficiaryText.setText(charityChosen)
        elif thisTrial['beneficiary'] == 'self':
            beneficiaryText.setText('self')
        elif thisTrial['beneficiary'] == 'otherperson':
            beneficiaryText.setText('another student')

        beneficiaryText.setAutoDraw(True)

        if blockType == 'practice':
            practiceInstructText.setAutoDraw(True)

        # if titrating, determine stuff automatically
        if titrate:
            # determine response duration
            try:
                last2Trials = pd.read_csv(filename).tail(2).reset_index()
                if last2Trials.loc[1, 'acc'] == 1 and trialsDf.loc[i, 'targetFrames'] >= 24: # if previous trial correct
                    trialsDf.loc[i, 'targetFrames'] = last2Trials.loc[1, 'targetFrames'] - 6 # minus 6 frames (100 ms)
                elif last2Trials.loc[0:1, 'acc'].sum() == 0:
                    trialsDf.loc[i, 'targetFrames'] = last2Trials.loc[1, 'targetFrames'] + 6 # plus 6 frames (100 ms)
                else:
                    trialsDf.loc[i, 'targetFrames'] = last2Trials.loc[1, 'targetFrames']
                # print trialsDf.loc[i, 'targetFrames']
            except:
                pass

        try:
            targetFramesCurrentTrial = int(trialsDf.loc[i, 'targetFrames'])
        except:
            try:
                targetFramesCurrentTrial = int(rtMaxFrames)
            except:
                try:
                    targetFramesCurrentTrial = int(info['targetFrames'])
                except:
                    targetFramesCurrentTrial = 300

        win.callOnFlip(respClock.reset) # reset response clock on next flip
        win.callOnFlip(trialClock.reset) # reset trial clock on next flip

        event.clearEvents() # clear events


        for frameN in range(targetFramesCurrentTrial):
            if frameN == 0: #on first frame/flip/refresh
                if sendTTL and not blockType == 'practice':
                    win.callOnFlip(port.setData, int(thisTrial['TTLStim']))
                else:
                    pass
                ##print "First frame in Block %d Trial %d OverallTrialNum %d" %(blockNumber, i + 1, trialsDf.loc[i, 'overallTrialNum'])
                ##print "Stimulus TTL: %d" %(int(thisTrial['TTLStim']))
            else:
                keysCollected = event.getKeys(keyList = ['f', 'j', 'backslash', 'bracketright'])
                if len(keysCollected) > 0 and trialsDf.loc[i, 'resp'] is None: #if a response has been made

                    trialsDf.loc[i, 'rt'] = respClock.getTime() #store RT
                    trialsDf.loc[i, 'resp'] = keysCollected[0] #store response in pd df

                    if keysCollected[0] == 'f':
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'choiceText'] = 'baseline'
                    elif keysCollected[0] == 'j':
                        if sendTTL and not blockType == 'practice':
                            port.setData(16) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 16
                        trialsDf.loc[i, 'choiceText'] = 'effortful'
                    else:
                        if sendTTL and not blockType == 'practice':
                            port.setData(17) #incorrect response
                        trialsDf.loc[i, 'responseTTL'] = 17
                        trialsDf.loc[i, 'choiceText'] = ''
                    #remove stimulus from screen
                    constantOptionEffort.setAutoDraw(False)
                    constantOptionReward.setAutoDraw(False)
                    varyingOptionEffort.setAutoDraw(False)
                    varyingOptionReward.setAutoDraw(False)
                    beneficiaryText.setAutoDraw(False)
                    practiceInstructText.setAutoDraw(False)
                    win.flip() #clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            trialsDf.loc[i, 'acc'] = 0
            constantOptionEffort.setAutoDraw(False)
            constantOptionReward.setAutoDraw(False)
            varyingOptionEffort.setAutoDraw(False)
            varyingOptionReward.setAutoDraw(False)
            beneficiaryText.setAutoDraw(False)
            practiceInstructText.setAutoDraw(False)
            win.flip() #clear screen (remove stuff from screen)

        if sendTTL and not blockType == 'practice':
            port.setData(0) #parallel port: set all pins to low

        trialsDf.loc[i, 'elapsedTime'] = globalClock.getTime() #store total elapsed time in seconds
        trialsDf.loc[i, 'endTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #store current time
        iti = round(random.choice(info['ITIDuration']), 2) #randomly select an ITI duration
        trialsDf.loc[i, 'iti'] = iti #store ITI duration

        #start inter-trial interval...
        ISI.start(iti)

        ### print "TRIAL OK TRIAL %d OVERALL TRIAL %d" %(i + 1, int(trialsDf.loc[i, 'overallTrialNum']))

        ''' DO NOT EDIT BEGIN '''
        #if press 0 (quit script) or 7 (skip block)
        if trialsDf.loc[i, 'resp'] == 'backslash':
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'resp'] = None
            if saveData: #if saveData argument is True, then APPEND current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            #moveFiles(dir = 'Data')
            core.quit() #quit when 'backslash' has been pressed
        elif trialsDf.loc[i, 'resp'] == 'bracketright':#if press 7, skip to next block
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'resp'] == None
            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            return None

        # if saveData: #if saveData argument is True, then append current row/trial to csv
        #     trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
        ''' DO NOT EDIT END '''

        ISI.complete() #end inter-trial interval

        # feedback for trial
        if feedback:
            # initialize stimuli
            feedbackText1 = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'choiceText'] == 'baseline':
                feedbackText1.setText('add 0 to each digit')
            elif trialsDf.loc[i, 'choiceText'] == 'effortful':
                feedbackText1.setText("add {} to each digit".format(thisTrial['effort']))
            elif trialsDf.loc[i, 'choiceText'] == '':
                feedbackText1.setText('Respond faster')
            else:
                pass
            for frameN in range(60):
                feedbackText1.draw()
                win.flip()

        # pause
        for frameN in range(info['blockEndPause']):
            win.flip() #wait at the end of the block

        #### run mental math block ####
        if trialsDf.loc[i, 'resp'] is not None:
            # run mental math updating trial
            if trialsDf.loc[i, 'choiceText'] == 'baseline':
                runMentalMathBlock(taskName='mentalMathUpdating', blockType='', trials=1, feedback=True, saveData=True, practiceTrials=0, digits=3, digitChange=0, digitsToModify=0, titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
            elif trialsDf.loc[i, 'choiceText'] == 'effortful':
                runMentalMathBlock(taskName='mentalMathUpdating', blockType='', trials=1, feedback=True, saveData=True, practiceTrials=0, digits=3, digitChange=trialsDf.loc[i, 'effort'], digitsToModify=1, titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
            else:
                pass

        # global runMentalMathBlockAccuracy
        trialsDf.loc[i, 'accUpdating'] = info['mentalMathUpdatingCurrentTrialAcc']
        #global runMentalMathBlockRt
        trialsDf.loc[i, 'rtUpdating'] = info['mentalMathUpdatingCurrentTrialRt']

        #print info['mentalMathUpdatingCurrentTrialAcc']
        #print trialsDf.loc[i, 'accUpdating']
        #print info['mentalMathUpdatingCurrentTrialRt']
        #print trialsDf.loc[i, 'rtUpdating']


        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)

        #feedback for trial
        if feedback and trialsDf.loc[i, 'resp'] is not None:
            # initialize stimuli
            feedbackText1 = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'accUpdating'] == 1:
                if trialsDf.loc[i, 'choiceText'] == 'effortful':
                    feedbackText1.setText('correct, {} credits'.format(thisTrial['rewardJittered']))
                else:
                    feedbackText1.setText('correct, 1 credit')
            else:
                if trialsDf.loc[i, 'choiceText'] == 'effortful':
                    feedbackText1.setText('wrong, {} credits'.format(thisTrial['rewardJittered']))
                else:
                    feedbackText1.setText('wrong, 1 credit')

            for frameN in range(48):
                feedbackText1.draw()
                win.flip()

        info['mentalMathUpdatingCurrentTrialAcc'] = 0
        info['mentalMathUpdatingCurrentTrialRt'] = np.nan

    # end of block pause
    constantOptionEffort.setAutoDraw(False)
    constantOptionReward.setAutoDraw(False)
    varyingOptionEffort.setAutoDraw(False)
    varyingOptionReward.setAutoDraw(False)
    beneficiaryText.setAutoDraw(False)
    practiceInstructText.setAutoDraw(False)
    for frameN in range(info['blockEndPause']):
        win.flip() #wait at the end of the block

def presentQuestions(questionName='questionnaireName', questionList=['Question 1?', 'Question 2?'], blockType='', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'], showAnchors=True):

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], questionName)

    ''' DO NOT EDIT BEGIN '''
    mouse.setVisible(0) #make mouse invisible
    #Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True
    ''' DO NOT EDIT END '''

    # store info in data frame

    trialsDf = pd.DataFrame(index=np.arange(len(questionList))) # create empty dataframe
    #store additional info in dataframe
    trialsDf['participant'] = int(info['participant'])
    try:
        trialsDf['age'] = int(info['age'])
        trialsDf['gender'] = info['gender']
        trialsDf['handedness'] = info['handedness']
        trialsDf['ethnicity'] = info['ethnicity']
        trialsDf['ses'] = info['ses']
    except:
        pass
    trialsDf['trialNo'] = range(1, len(trialsDf) + 1) #add trialNo
    trialsDf['blockType'] = blockType #add blockType
    trialsDf['task'] = questionName #task name
    trialsDf['postFixationFrames'] = np.nan
    if rtMaxFrames is None:
        trialsDf['targetFrames'] = 9999
    else:
        trialsDf['targetFrames'] = rtMaxFrames
    trialsDf['startTime'] = info['startTime']
    trialsDf['endTime'] = info['endTime']

    trialsDf['questionNo'] = np.arange(len(questionList)) + 1
    trialsDf['questionText'] = questionList

    trialsDf['elapsedTime'] = np.nan
    trialsDf['resp'] = None
    trialsDf['rt'] = np.nan
    trialsDf['iti'] = np.nan
    trialsDf['choice'] = np.nan
    trialsDf['overallTrialNum'] = 0 #cannot use np.nan because it's a float, not int!

    '''DO NOT EDIT BEGIN'''
    #Assign blockNumber based on existing csv file. Read the csv file and find the largest block number and add 1 to it to reflect this block's number.
    try:
        blockNumber = max(pd.read_csv(filename)['blockNumber']) + 1
        trialsDf['blockNumber'] = blockNumber
    except: #if fail to read csv, then it's block 1
        blockNumber = 1
        trialsDf['blockNumber'] = blockNumber
    '''DO NOT EDIT END'''

    # create stimuli
    questionText = visual.TextStim(win = win, units = 'norm', height = 0.08, name = 'target', text = 'INSERT QUESTION HERE', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, 0.3))

    # scale points
    scaleAnchorPoints = str(np.arange(scaleAnchors[0], scaleAnchors[1] + 1))
    scaleAnchorPoints = scaleAnchorPoints[1:(len(scaleAnchorPoints) - 1)]

    # scale left anchor text
    scaleAnchorTextLeftText = visual.TextStim(win = win, units = 'norm', height = 0.04, name = scaleAnchorText[0], text = scaleAnchorPoints, font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.43, -0.2))

    # scale right anchor text
    scaleAnchorTextRightText = visual.TextStim(win = win, units = 'norm', height = 0.04, name = scaleAnchorText[1], text = scaleAnchorPoints, font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.43, -0.2))

    # scale points
    scaleAnchorPointsText = visual.TextStim(win = win, units = 'norm', height = 0.07, name = 'target', text = scaleAnchorPoints, font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, -0.2))

    # tell participants to use keyboard to respond
    instructText = visual.TextStim(win = win, units = 'norm', height = 0.03, name = 'target', text = 'Press the numbers on the top row of the keyboard to respond.', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, -0.3))

    # automatically generate accepted keys
    keysAccepted = np.arange(scaleAnchors[0], scaleAnchors[1] + 1)
    keysAccepted = [str(keysAcceptedI) for keysAcceptedI in keysAccepted]
    keysAccepted.append('backslash')
    keysAccepted.append('bracketright')

    # create clocks to collect reaction and trial times
    respClock = core.Clock()
    trialClock = core.Clock()

    for i, thisTrial in trialsDf.iterrows(): #for each trial...
        ''' DO NOT EDIT BEGIN '''
        #add overall trial number to dataframe
        try: #try reading csv file dimensions (rows = no. of trials)
            #thisTrial['overallTrialNum'] = pd.read_csv(filename).shape[0] + 1
            trialsDf.loc[i, 'overallTrialNum'] = pd.read_csv(filename).shape[0] + 1
            ####print 'Overall Trial No: %d' %thisTrial['overallTrialNum']
        except: #if fail to read csv, then it's trial 1
            #thisTrial['overallTrialNum'] = 1
            trialsDf.loc[i, 'overallTrialNum'] = 1
            ####print 'Overall Trial No: %d' %thisTrial['overallTrialNum']

        if sendTTL and not blockType == 'practice':
            port.setData(0) #make sure all pins are low before new trial
            ###print 'Start Trial TTL 0 set all pins to low'

        # if there's a max time for this block, end block when time's up
        if blockMaxTimeSeconds is not None:
            try:
                if trialsDf.loc[i-1, 'elapsedTime'] - trialsDf.loc[0, 'elapsedTime'] >= blockMaxTimeSeconds:
                    print trialsDf.loc[i-1, 'elapsedTime'] - trialsDf.loc[0, 'elapsedTime']
                    print "block time out"
                    return None
            except:
                pass
        # if there's a max time for entire experiment, end block when time's up
        if experimentMaxTimeSeconds is not None:
            try:
                firstTrial = pd.read_csv(filename).head(1).reset_index()
                finalTrial = pd.read_csv(filename).tail(1).reset_index()
                if finalTrial.loc[0, 'elapsedTime'] - firstTrial.loc[0, 'elapsedTime'] >= experimentMaxTimeSeconds:
                    print "experiment time out"
                    return None
            except:
                pass

        ''' DO NOT EDIT END '''

        # draw all stimuli
        questionText.setText(questionList[i])
        questionText.setAutoDraw(True)
        instructText.setAutoDraw(True)
        if showAnchors:
            scaleAnchorPointsText.setAutoDraw(True)
            scaleAnchorTextLeftText.setText(str(scaleAnchors[0]) + ': ' + str(scaleAnchorText[0]))
            scaleAnchorTextLeftText.setAutoDraw(True)
            scaleAnchorTextRightText.setText(str(scaleAnchors[1]) + ': ' + str(scaleAnchorText[1]))
            scaleAnchorTextRightText.setAutoDraw(True)

        win.flip()
        event.clearEvents() #clear events
        #create clocks to collect reaction and trial times
        respClock = core.Clock()
        trialClock = core.Clock()

        for frameN in range(int(trialsDf.loc[i, 'targetFrames'])):
            if frameN == 0: #on first frame/flip/refresh
                if sendTTL and not blockType == 'practice':
                    win.callOnFlip(port.setData, int(thisTrial['TTLStim']))
                else:
                    pass
            else:
                keys = event.getKeys(keyList = keysAccepted)
                if len(keys) > 0 and trialsDf.loc[i, 'resp'] is None: #if a response has been made
                    trialsDf.loc[i, 'rt'] = respClock.getTime() #store RT
                    trialsDf.loc[i, 'resp'] = keys[0] #store response in pd df
                    # remove stimulus from screen
                    questionText.setAutoDraw(False)
                    instructText.setAutoDraw(False)
                    scaleAnchorPointsText.setAutoDraw(False)
                    scaleAnchorTextLeftText.setAutoDraw(False)
                    scaleAnchorTextRightText.setAutoDraw(False)
                    win.flip() # clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        # if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            questionText.setAutoDraw(False)
            questionText.setAutoDraw(False)
            instructText.setAutoDraw(False)
            scaleAnchorPointsText.setAutoDraw(False)
            scaleAnchorTextLeftText.setAutoDraw(False)
            scaleAnchorTextRightText.setAutoDraw(False)
            win.flip() #clear screen (remove stuff from screen)

        trialsDf.loc[i, 'elapsedTime'] = globalClock.getTime() #store total elapsed time in seconds
        trialsDf.loc[i, 'endTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #store current time
        iti = round(random.choice([0.2, 0.3, 0.4]), 2) #randomly select an ITI duration
        trialsDf.loc[i, 'iti'] = iti #store ITI duration

        global charityChosen
        if blockType == 'charityChoice':
            if trialsDf.loc[i, 'resp'] == '1':
                trialsDf.loc[:, 'charityChosen'] = 'World Vision Canada'
                charityChosen = 'World Vision Canada'
            elif trialsDf.loc[i, 'resp'] == '2':
                trialsDf.loc[:, 'charityChosen'] = 'Canadian Cancer Society'
                charityChosen = 'Canadian Cancer Society'
            elif trialsDf.loc[i, 'resp'] == '3':
                trialsDf.loc[:, 'charityChosen'] = 'SickKids Foundation'
                charityChosen = 'SickKids Foundation'
            elif trialsDf.loc[i, 'resp'] == '4':
                trialsDf.loc[:, 'charityChosen'] = 'Salvation Army'
                charityChosen = 'Salvation Army'
            elif trialsDf.loc[i, 'resp'] == '5':
                trialsDf.loc[:, 'charityChosen'] = 'Wildlife Preservation'
                charityChosen = 'Wildlife Preservation'
            elif trialsDf.loc[i, 'resp'] == '6':
                trialsDf.loc[:, 'charityChosen'] = 'Other'
                charityChosen = 'Other'
            else:
                trialsDf.loc[:, 'charityChosen'] = None
                charityChosen = 'charity'

        # start inter-trial interval...
        ISI.start(iti)

        ''' DO NOT EDIT BEGIN '''
        #if press 0 (quit script) or 7 (skip block)
        if trialsDf.loc[i, 'resp'] == 'backslash':
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'resp'] = None
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            #moveFiles(dir = 'Data')
            core.quit() #quit when 'backslash' has been pressed
        elif trialsDf.loc[i, 'resp'] == 'bracketright':#if press 7, skip to next block
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'resp'] == None
            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            return None

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
        ''' DO NOT EDIT END '''

        ISI.complete() #end inter-trial interval

    for frameN in range(info['blockEndPause']):
        win.flip() #wait at the end of the block

def showQuestionnaire(csvFile, scaleMin, scaleMax, scaleDescription='Click scale to respond.', outputName='Questionnaires', scaleLeftRightAnchorText=['strongly disagree', 'strongly agree']):
    '''Show questionnaire from csv file (csvFile).
    Saves reaction time and rating in long form. Different questionnaires will be saved as one csv file.
    csvFile: name of csv file with questionnaire items (csv file must have two columns with variable names qNo and question); csv file MUST BE IN STIMULI DIRECTORY
    scaleMin: minimum value of scale
    scaleMax: maximum value of scale
    scaleDescription: text desribing each point of the scale
    items: number of items in the questionnaire/scale
    ouputName: name of output csv file
    '''

    mouse.setVisible(1) #make mouse visible
    event.clearEvents() #clear events (keypresses etc.)

    # specify filenames
    longName = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], outputName)

    # import csv file with questions formatted properly
    csvFile = stimulusDir + csvFile
    questionsDf = pd.read_csv(csvFile)
    questionsDf['pNo'] = int(info['participant'])
    try:
        questionsDf['age'] = int(info['age'])
        questionsDf['gender'] = info['gender']
        questionsDf['handedness'] = info['handedness']
        questionsDf['ethnicity'] = info['ethnicity']
        questionsDf['ses'] = info['ses']
    except:
        pass
    questionsDf['totalItems'] = len(questionsDf)
    # print len(questionsDf)
    questionsDf['overallQNo'] = 0
    questionsDf['rating'] = '' #new variable/column to store response
    questionsDf['rt'] = '' #new variable to store response RT

    # create rating scale for this questionnair
    # tickMarks = range(scaleMin, scaleMax + 1)
    scale = visual.RatingScale(win, low = scaleMin, high = scaleMax, mouseOnly = True, singleClick = True, stretch = 2, marker = 'slider', showAccept = False, pos = (0, -0.5), showValue = True, textSize = 0.7, textFont = 'Verdana', markerColor = 'red', scale = scaleDescription, labels=[str(scaleMin) + ": " + scaleLeftRightAnchorText[0], str(scaleMax) + ": " + scaleLeftRightAnchorText[1]], tickMarks=[scaleMin, scaleMax])

    scale.setDescription(scaleDescription) # set description of rating scale

    for i, question in questionsDf.iterrows(): # for each question

        '''DO NOT EDIT BEGIN'''
        # Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
        writeHeader = False
        try: #try reading csv file dimensions (rows = no. of trials)
            pd.read_csv(longName)
        except: #if fail to read csv, then it's trial 1
            writeHeader = True

        # determine current trial/question number
        if writeHeader:
            questionsDf.loc[i, 'overallQNo'] = 1 #if writeHeader, then it's first item
        else:
            questionsDf.loc[i, 'overallQNo'] = pd.read_csv(longName).shape[0] + 1 # if not writeHeader, it's next item
        '''DO NOT EDIT END'''

        # set question text from csv file/pandas dataframe
        questionText = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', height = 0.06, wrapWidth = 1.4, pos = [0.0, 0.5], text = question['question'])

        scale.reset() #if using same rating scale, need to reset each time
        event.clearEvents() #clear events (keypresses etc.)

        while scale.noResponse: # while no response...
            questionText.draw(); scale.draw(); win.flip() #draw and show scale
            if event.getKeys(['backslash']): #if 0 pressed, quit
                core.quit()
            elif event.getKeys(['bracketright']):
                return None

        # store responses to pd dataframe
        questionsDf.loc[i, 'rating'] = scale.getRating() #store rating
        questionsDf.loc[i, 'rt'] = scale.getRT() #store reaction time

        '''DO NOT EDIT BEGIN'''
        # save data frame as csv (long form)
        questionsDf[i:i+1].to_csv(longName, header = True if writeHeader else False, index = False, mode = 'a')
        '''DO NOT EDIT END'''

    mouse.setVisible(0)

    for frameN in range(30):
        win.flip() #wait at end of block

def showAllQuestionnaires():

    # #need for cognition
    # showInstructions(text = ['Click on the scale to indicate the extent to which you agree.'])
    # showQuestionnaire(csvFile = 'NeedForCognition.csv', scaleMin = -4, scaleMax = 4, outputName='Questionnaires', scaleLeftRightAnchorText=['very strong disagreement', 'very strong agreement'])

    #PoliticalOrientation
    showQuestionnaire(csvFile = 'PoliticalOrientation.csv', scaleMin = 1, scaleMax = 7, outputName='Questionnaires', scaleLeftRightAnchorText=['very liberal', 'very conservative'])

    # ApathyMotivationIndex
    showInstructions(text = ["Indicate how true each statement is based on the past two weeks of your life."])
    showQuestionnaire(csvFile = 'ApathyMotivationIndex.csv', scaleMin = 0, scaleMax = 4, outputName='Questionnaires', scaleLeftRightAnchorText=["completely true", "completely untrue"])

    #BFAS
    showInstructions(text = ["Next you will read several characteristics that may or may not describe you. Select the option that best indicates how much you agree or disagree. Be as honest as you can and rely on your initial feeling. Do not think too much about each item."])
    showQuestionnaire(csvFile = 'BFAS.csv', scaleMin = 1, scaleMax = 5, outputName='Questionnaires', scaleLeftRightAnchorText=['disagree strongly', 'agree strongly'])

    # Prosocialness scale
    showInstructions(text = ["For the next few statements, indicate how well it describes you."])
    showQuestionnaire(csvFile = 'ProsocialScale.csv', scaleMin = 1, scaleMax = 5, outputName='Questionnaires', scaleLeftRightAnchorText=['occasionally true', 'almost always true'])
    showQuestionnaire(csvFile = 'DonateFrequency.csv', scaleMin = 1, scaleMax = 100, outputName='Questionnaires', scaleLeftRightAnchorText=['never in my life', 'regularly'])

    #Dispositional awe
    showInstructions(text = ["The following statements inquire about your thoughts and feelings in a variety of situations. For each item, indicate how well it describes you."])
    showQuestionnaire(csvFile = 'DispositionalPositiveEmotionsScaleAwe.csv', scaleMin = 1, scaleMax = 7, outputName='Questionnaires', scaleLeftRightAnchorText=['strongly disagree', 'strongly agree'])

    # Empathy index
    showInstructions(text = ["The following statements inquire about your thoughts and feelings in a variety of situations. For each item, indicate how well it describes you."])
    showQuestionnaire(csvFile = 'EmpathyIndex.csv', scaleMin = 1, scaleMax = 5, outputName='Questionnaires', scaleLeftRightAnchorText=["doesn't describe me well", "describes me very well"])

    # political orientation
    # showInstructions(text = ["For the next few items, indicate how you feel about each one. Click scale to respond."])
    # # SECS political orientation
    # showQuestionnaire(csvFile = 'SECS.csv', scaleMin = 0, scaleMax = 100, outputName='Questionnaires', scaleLeftRightAnchorText=['very negative', 'very positive'])

    # religious
    showInstructions(text = ["For the next few items, indicate how you much you agree with each. Click scale to respond."])
    showQuestionnaire(csvFile = 'ReligiousZeal.csv', scaleMin = 1, scaleMax = 7, outputName='Questionnaires', scaleLeftRightAnchorText=['strongly disagree', 'strongly agree'])

def getDemographics(outputCSV='demographics', measures={'gender': 4, 'ethnicity': 9, 'handedness': 3, 'ses': 9}, saveData=True):

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], outputCSV)

    ''' DO NOT EDIT BEGIN '''
    mouse.setVisible(0) #make mouse invisible

    #Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True
    ''' DO NOT EDIT END '''

    trialsDf = pd.DataFrame(index=np.arange(1), columns=measures) # empty df
    trialsDf['participant'] = int(info['participant'])
    trialsDf['age'] = int(info['age'])
    trialsDf['resp'] = None

    # create stimuli
    measuresInstructions = {'gender': 'Indicate your gender (use keyboard)', 'ethnicity': 'Indicate your ethnicity (use keyboard)', 'handedness': 'Indicate your handedness (use keyboard)', 'ses': "If 9 represents the most well-off people in the country and 1 the least well-off, where would you place yourself on this scale?"}

    measuresResponses = {'gender': ['female', 'male', 'other', 'prefer not to say'], 'ethnicity': ['Aboriginal', 'African/Carribean/Black', 'Caucasian/White', 'East Asian', 'Latino/Hispanic', 'Middle Eastern/North African', 'Multi-racial', 'Other', 'South Asian'], 'handedness': ['left', 'right', "ambidextrous"], 'ses': ['1', '2', '3', '4', '5', '6', '7', '8', '9']}

    yPositions = np.linspace(-0.95, 0.4, 13)[::-1] # response option y positions

    for measureI in measures: # for each measure

        stimuliDict = {} # create dict to store stimuli for this measure

        # instructions at the top of screen
        stimuliDict['measureInstructions'] = visual.TextStim(win=win, units='norm', height=0.06, name='target', text=measuresInstructions[measureI], font='Verdana', colorSpace='rgb', color=[1, 1, 1], opacity=1, pos=(0, 0.75))

        # generate response options for this question
        for i in range(measures[measureI]):
            if measureI == 'ses':
                responseText = measuresResponses[measureI][::-1][i]
            else:
                responseText = str(i+1) + '. ' + measuresResponses[measureI][i]

            stimuliDict[measureI + str(i)] = visual.TextStim(win = win, units = 'norm', height = 0.042, name = 'target', text = responseText, font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, yPositions[i]))

            for stimulusI in stimuliDict:
                stimuliDict[stimulusI].setAutoDraw(True)
            win.flip()

        keysAccepted = np.arange(1, measures[measureI]+1)
        keysAccepted = [str(keysAcceptedI) for keysAcceptedI in keysAccepted]
        keysAccepted.append('backslash')
        keysAccepted.append('bracketright')

        event.clearEvents()  # clear events
        # create clocks to collect reaction and trial times
        respClock = core.Clock()
        trialClock = core.Clock()

        for frameN in range(9999):
            keys = event.getKeys(keyList=keysAccepted)
            if len(keys) > 0:  # if a response has been made
                trialsDf.loc[0, 'resp'] = keys[0]  # store response in pd df
                # remove stimulus from screen
                for stimulusI in stimuliDict:
                    stimuliDict[stimulusI].setAutoDraw(False)
                win.flip()  # clear screen (remove stuff from screen)
                break  # break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        try:
            trialsDf.loc[0, measureI] = measuresResponses[measureI][int(keys[0])-1]
        except:
            trialsDf.loc[0, measureI] = None

        info[measureI] = trialsDf.loc[0, measureI]

        ''' DO NOT EDIT BEGIN '''
        # if press 0 (quit script) or 7 (skip block)
        if trialsDf.loc[0, 'resp'] == 'backslash':
            trialsDf.loc[0, 'resp'] = None
            if saveData:
                trialsDf.to_csv(filename, index=False)
            core.quit()  # quit when 'backslash' has been pressed
        elif trialsDf.loc[0, 'resp'] == 'bracketright':  # if press 7, skip to next block
            trialsDf.loc[0, 'acc'] = np.nan
            trialsDf.loc[0, 'resp'] == None
            win.flip()
            if saveData:
                trialsDf.to_csv(filename, index=False)
            return None

        if saveData:
            trialsDf.to_csv(filename, index=False)
        ''' DO NOT EDIT END '''

    for frameN in range(30):
        win.flip() # wait at the end of the block

def showCredit():

    for frameN in range(30):
        win.flip()

    ''' notify credits/money earned '''

    showInstructions(text = ["Now the computer will determine how many credits and how much money you've earned..."], timeBeforeShowingSpace=3)

    try:
        creditCsv = "{:03d}-{}-effortRewardChoice.csv".format(int(info['participant']), info['startTime'])
        creditDf = pd.read_csv(creditCsv)
        creditDf = creditDf.dropna(subset=['accUpdating', 'reward'])

        overallAcc = creditDf.accUpdating.mean() * 100
        if overallAcc >= 90:
            toPay = 'yes'
        else:
            toPay = 'no'

        creditSelfBaseline = creditDf.loc[(creditDf.beneficiary == 'self') & (creditDf.accUpdating == 1.0) & (creditDf.choiceText == 'baseline'), ].shape[0]
        creditSelfEffortful = int(creditDf.loc[(creditDf.beneficiary == 'self') & (creditDf.accUpdating == 1.0) & (creditDf.choiceText == 'effortful'), 'reward'].sum())
        creditSelf = creditSelfBaseline + creditSelfEffortful

        creditCharityBaseline = creditDf.loc[(creditDf.beneficiary == 'charity') & (creditDf.accUpdating == 1.0) & (creditDf.choiceText == 'baseline'), ].shape[0]
        creditCharityEffortful = int(creditDf.loc[(creditDf.beneficiary == 'charity') & (creditDf.accUpdating == 1.0) & (creditDf.choiceText == 'effortful'), 'reward'].sum())
        creditCharity = creditCharityBaseline + creditCharityEffortful

        creditAnotherBaseline = creditDf.loc[(creditDf.beneficiary == 'charity') & (creditDf.accUpdating == 1.0) & (creditDf.choiceText == 'baseline'), ].shape[0]
        creditAnotherEffortful = int(creditDf.loc[(creditDf.beneficiary == 'charity') & (creditDf.accUpdating == 1.0) & (creditDf.choiceText == 'effortful'), 'reward'].sum())
        creditAnother = creditAnotherBaseline + creditAnotherEffortful

        moneySelf = 0.01 * creditSelf
        moneyCharity = 0.01 * creditCharity
        moneyAnother = 0.01 * creditAnother

        outputCsv = pd.DataFrame(index=range(0, 1))
        outputCsv['participant'] = int(info['participant'])
        outputCsv['email'] = str(info['email'])
        outputCsv['overallAccuracy'] = overallAcc
        outputCsv['toPay'] = toPay
        outputCsv['moneySelf'] = moneySelf
        outputCsv['moneyCharity'] = moneyCharity
        outputCsv['moneyAnother'] = moneyAnother
        outputCsv['charityChosen'] = charityChosen
        outputCsv['creditSelf'] = creditSelf
        outputCsv['creditCharity'] = creditCharity
        outputCsv['creditAnother'] = creditAnother

        outputCsv.to_csv("{:03d}-{}-REWARDINFO.csv".format(int(info['participant']), info['startTime']), index=False)

        if overallAcc >= 90:
            showInstructions(text = ["Your overall accuracy was {:.0f}%. You've earned {} credits for yourself, {} credits for charity, and {} credits for another student.".format(overallAcc, creditSelf, creditCharity, creditAnother),
            "These credits convert to ${:.2f} for yourself, and ${:.2f} donated to your charity. We will email you your reward in the form of an Amazon voucher, and will help you donate to {}. We will also email an Amazon voucher worth ${:.2f} to another randomly selected student who has participated in a different experiment.".format(moneySelf, moneyCharity, charityChosen, moneyAnother)])
        else:
            showInstructions(text = ["Your overall accuracy was {:.0f}%. Although you've earned {} credits for yourself, {} credits for charity, and {} credits for another student, these credits won't be converted to money and neither you nor your charity will be paid because you need to be at least 90% accurate.".format(overallAcc, creditSelf, creditCharity, creditAnother)])

    except:

        outputCsv = pd.DataFrame(index=range(0, 1))
        outputCsv['participant'] = int(info['participant'])
        outputCsv['email'] = str(info['email'])
        outputCsv['moneySelf'] = 3.50
        outputCsv['moneyCharity'] = 2.80
        outputCsv['charityChosen'] = charityChosen
        outputCsv['creditSelf'] = np.nan
        outputCsv['creditCharity'] = np.nan

        outputCsv.to_csv("{:03d}-{}-REWARDINFO.csv".format(int(info['participant']), info['startTime']), index=False)

        showInstructions(text = ["Your overall accuracy was 91%. The credits you've earned have been converted to $4.20 for yourself, $3.90 donated to your charity, and $3.10 to another student. We will email you your reward in the form of an Amazon voucher, and will help you donate to {}. We will also email an Amazon voucher to another randomly selected student who has participated in a different experiment.".format(charityChosen)])

    for frameN in range(30):
        win.flip()








































#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################

# ''' START EXPERIMENT HERE '''
# if sendTTL:
#    port.setData(0) # make sure all pins are low before experiment

# showInstructions(text = [
# " ", # black screen at the beginning
# "Welcome to today's experiment! Before we begin, please answer a few questions about yourself."])

# getDemographics() # get demographics (gender, ses, ethnicity)

# ''' practice '''
# showInstructions(text =
# ["We are studying how people make decisions related to cognitive effort. You'll have many opportunities to earn money during the experiment. All decisions in this experiment are for real (not hypothetical) and will be implemented at the end of the experiment.",
# "If you have any questions during the experiment, raise/wave your hands and the research assistant will help you.",
# "The cognitive task you're going to do requires you to solve math problems (adding numbers) and has different levels of difficulty.",
# "You'll see three-digit sequences, with each digit presented one at a time on the screen. You have to add a certain number (e.g., add 3) to each digit, one at a time, remember the sequence of digits, and choose the correct answer later on.",
# "So, if you see 5, 2, 3 (presented one at a time) and you've been told to add 3, you'll add 3 to each number separately, and will have to choose between two responses shown on the left and right of the screen: 856 and 846. 856 is the correct response in this example.",
# "Place your left and right index fingers on the F and J keys, and press the F key to choose the left option, and the J key for the right option.",
# "Whenever the sum of two digits is greater than 10, you'll report only the ones digit (the rightmost digit). For example, if the problem is 9 + 5, the summed digit will be 4 (not 14).",
# "A few more examples: 7 + 8 is 5; 4 + 6 is 0; 9 + 2 is 1.",
# "If anything's unclear, please ask the researcher assistant now. If not, we'll practice a bit now!",
# "You have 2 seconds to indicate your answer (using the F and J keys). If no choice is made, it'll be considered wrong and the task will proceed."])


# practiceReps = 2
# showInstructions(text = ["Let's try adding 1 to each digit!"])
# runMentalMathBlock(taskName='mentalMathUpdatingPractice', blockType='practice', trials=practiceReps, feedback=True, saveData=True, practiceTrials=2, digits=3, digitChange=1, digitsToModify=1, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
# showInstructions(text = ["That was add 1. If anything's unclear, please ask the research assistant now."])

# showInstructions(text = ["Now let's try adding 3 to each digit."])
# runMentalMathBlock(taskName='mentalMathUpdatingPractice', blockType='practice', trials=practiceReps, feedback=True, saveData=True, practiceTrials=2, digits=3, digitChange=3, digitsToModify=1, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
# showInstructions(text = ["That was add 3."])

# showInstructions(text = ["Now let's do add 5."])
# runMentalMathBlock(taskName='mentalMathUpdatingPractice', blockType='practice', trials=practiceReps, feedback=True, saveData=True, practiceTrials=2, digits=3, digitChange=5, digitsToModify=1, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
# showInstructions(text = ["That was add 5."])

# showInstructions(text = ["Let's try add 6 now!"])
# runMentalMathBlock(taskName='mentalMathUpdatingPractice', blockType='practice', trials=practiceReps, feedback=True, saveData=True, practiceTrials=2, digits=3, digitChange=6, digitsToModify=1, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
# showInstructions(text = ["That was add 6."])

# showInstructions(text = ["Let's try add 7 now!"])
# runMentalMathBlock(taskName='mentalMathUpdatingPractice', blockType='practice', trials=practiceReps, feedback=True, saveData=True, practiceTrials=2, digits=3, digitChange=7, digitsToModify=1, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
# showInstructions(text = ["That was add 7."])

# showInstructions(text = ["Finally, let's try add 0. When adding 0, all you have to do is remember the three digits. In fact, the two response options will be identical and either will be correct. So as long as you make a response in under 2 seconds, you'll be correct!"])

# runMentalMathBlock(taskName='mentalMathUpdatingPractice', blockType='practice', trials=1, feedback=True, saveData=True, practiceTrials=1, digits=3, digitChange=0, digitsToModify=0, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
# showInstructions(text = ["That was add 0."])

# ''' effort questions '''
# showInstructions(text = ["Now you'll answer a few questions about the math task."])

# effortQuestions = ['How much effort did add 0 require?', 'How much effort did add 1 require?', 'How much effort did add 3 require?', 'How much effort did add 5 require?', 'How much effort did add 6 require?', 'How much effort did add 7 require?']
# random.shuffle(effortQuestions)

# presentQuestions(questionName='effortFrustrateReport', questionList=effortQuestions, blockType='pre', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['none at all', 'very much'])

# ''' frustrate questions '''
# frustrateQuestions = ['How frustrating was add 0?', 'How frustrating was add 1?', 'How frustrating was add 3?', 'How frustrating was add 5?', 'How frustrating was add 6?', 'How frustrating was add 7?']
# random.shuffle(frustrateQuestions)

# presentQuestions(questionName='effortFrustrateReport', questionList=frustrateQuestions, blockType='pre', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])

# ''' practice choice task '''

# showInstructions(text = [
# "You'll be doing many of these addition tasks later on, and the task difficulty depends on your choices during a decision making task.",
# "In this decision task, you'll have to choose between two options: doing add 0 or add 1, 3, 5, 6, or 7). Each option will have a specific number of credits associated with it. If you perform your chosen task correctly at least 90% of the time, you'll get those credits, which will be converted to money (Amazon voucher to be emailed to you).",
# "Add 0 will ALWAYS be one of the available options, and you will ALWAYS receive 1 credit for choosing to do add 0 (ADD 0 1 CREDIT)",
# "The other option will vary in terms of difficulty (e.g., add 3, 5) and credits (2 to 12 credits).",
# "For example, you might see these two options on the screen: add 0 for 1 credit vs add 3 for 5 credits. The add 0 for 1 credit option means if you choose it and perform accurately on the add 0 task, you'll get 1 credit. And if you choose the add 3 for 5 credits option, you'll add 3 to each digit to get 5 credits.",
# "Here is one more example: add 0 for 1 credit vs add 7 for 2 credits",
# "If you don't have any questions, we'll practice a bit now.",
# "If you see the word 'self' at the top, it means the credits you earn will be given to you.",
# "Press F to select the left option, and J for the right option.",
# "Remember, one of the options will always be ADD 0 FOR 1 CREDIT, and you'll DEFINITELY RECEIVE that 1 credit if you choose it.",
# "Here we go! You have up to 5 seconds to choose."
# ])

# ''' self practice'''
# runEffortRewardChoiceBlock(taskName='effortRewardChoicePractice', blockType='self', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[2, 4], effort=[1, 3])


# showInstructions(text = [
# "The 'self' you saw at the top just now means the credits you earn will go to you. But sometimes, the credits you earn will instead go to another UTSC student who has already participated in a DIFFERENT EXPERIMENT in this laboratory." 
# ])

# showInstructions(text = [
# "Whenever you see 'another student', any credits/money you earn will be given to another student, and you'll be 'helping' this other student, even though you'll never meet this student in person and you'll never know who benefitted from your choices and performance in this experiment."
# ])

# showInstructions(text = [
# "Other times, the credits you earn will instead go to a charity. For example you choose add 7 for 3 credits for a charity, you are saying you will be donating your 3 credits (converted to monetary amounts at the end) to a charity if you perform the add 7 task correctly.",
# "These choices and outcomes are not hypothetical and will actually be implemented at the end of the study, so you can influence how much a charity or another UTSC student benefits from your choices and performance.",
# "Now, you can choose which (of 5) charities you can donate to. If you have a specific charity you'd like to donate to, let the research assistant know. "
# ])

# # pick charity here
# presentQuestions(questionName='charityChoice', questionList=["Which charity do you want to donate to? (1) World Vision Canada; (2) Canadian Cancer Society; (3) SickKids Foundation; (4) Salvation Army; (5) Wildlife Preservation Canada; (6) Other (please ask for the researcher assistant if you want to select this option)"], blockType='charityChoice', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,5], scaleAnchorText=[' ', ' '], showAnchors=False)


# showInstructions(text = [
# "Let's practice choosing and performing the task for yourself, another student, or {}.".format(charityChosen),
# "Remember, one option will always remain the same (add 0 for 1 credit), whereas the other option varies."
# ])

# ''' self/charity/otherperson practice'''
# runEffortRewardChoiceBlock(taskName='effortRewardChoicePractice', blockType='otherperson', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=60, experimentMaxTimeSeconds=None, reward=[2], effort=[2])

# runEffortRewardChoiceBlock(taskName='effortRewardChoicePractice', blockType='charity', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=60, experimentMaxTimeSeconds=None, reward=[2], effort=[2])

# runEffortRewardChoiceBlock(taskName='effortRewardChoicePractice', blockType='otherperson', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=60, experimentMaxTimeSeconds=None, reward=[2], effort=[3])

# runEffortRewardChoiceBlock(taskName='effortRewardChoicePractice', blockType='charity', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=60, experimentMaxTimeSeconds=None, reward=[2], effort=[3])


# showInstructions(text = ["That's the end of practice. Let the research assistant know if you have any questions."])

''' actual task '''
showInstructions(text = [
"You'll now do the actual choice and math task now.",
"Place your left and right index fingers on the F and J keys, and use the F and J keys to choose the left and right options respectively.",
"You have up to 5 seconds to make each choice, and 2 seconds to indicate your response when doing the addition task.",
"Remember, you're making REAL choices from now on. Your choices and decisions are not hypothetical. We will convert the credits you earn during the task into monetary amounts and will pay you, another student, and {} accordingly.".format(charityChosen),
"To receive the credits/money at the end, you'll have to respond correctly at least 90% of the time. So try your best to do well in the addition task, but don't worry if you make a few mistakes occasionally.",
"You'll have opportunities to take breaks during the experiment.",
" "
])

runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='mixed', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=rewardLevels, effort=effortLevels)

showInstructions(text = ["Take a break if you'd like to."])

runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='mixed', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=rewardLevels, effort=effortLevels)

showInstructions(text = ["Take a break if you'd like to."])

runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='mixed', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=rewardLevels, effort=effortLevels)

showInstructions(text = ["That's the end of that choice task."])


# ''' post choice task effort questions '''
# showInstructions(text = ["Now you'll answer a few questions about the math task."])

# effortQuestions = ['How much effort did add 0 require?', 'How much effort did add 1 require?', 'How much effort did add 3 require?', 'How much effort did add 5 require?', 'How much effort did add 7 require?', 'How much effort did add 6 require?']
# random.shuffle(effortQuestions)

# presentQuestions(questionName='effortFrustrateReport', questionList=effortQuestions, blockType='post', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['none at all', 'very much'])

# ''' frustrate questions '''
# frustrateQuestions = ['How frustrating was add 0?', 'How frustrating was add 1?', 'How frustrating was add 3?', 'How frustrating was add 5?', 'How frustrating was add 7?', 'How frustrating was add 6?']
# random.shuffle(frustrateQuestions)

# presentQuestions(questionName='effortFrustrateReport', questionList=frustrateQuestions, blockType='post', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])


# ''' questionnaires '''
# showInstructions(text = ["Now you'll answer a few questions about yourself."])
# showAllQuestionnaires()

''' show credits earned '''

showCredit()


''' experiment end '''

showInstructions(text = ["That's the end of the experiment. Thanks so much for participating in our study!"])


if sendTTL:
    port.setData(255) # mark end of experiment

win.close()
core.quit() # quit PsychoPy
