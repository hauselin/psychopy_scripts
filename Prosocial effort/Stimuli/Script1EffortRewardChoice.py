import pandas as pd
import numpy as np
import scipy as sp
import random, os, time
from psychopy import visual, core, event, data, gui, logging, parallel, monitors

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

#import csv file with unique trials
#trialsCSV = "GoNoGo.csv"
#trialsList = pd.read_csv(stimulusDir + trialsCSV)

#EXPERIMENT SET UP
info = {} # create empty dictionary to store stuff

if DEBUG:
    fullscreen = False #set fullscreen variable = False
    logging.console.setLevel(logging.DEBUG)
    info['participant'] = 999 #let 999 = debug participant no.
    info['email'] = 'xxx@gmail.com'
    info['age'] = 18
else: #if DEBUG is not False... (or True)
    fullscreen = True #set full screen
    logging.console.setLevel(logging.WARNING)
    info['participant'] = '7' #dict key to store participant no.
    info['email'] = 'xxx@gmail.com'
    info['age'] = 18
    #present dialog to collect info
    dlg = gui.DlgFromDict(info) #create a dialogue box (function gui)
    if not dlg.OK: #if dialogue response is NOT OK, quit
        #moveFiles(dir = 'Data')
        core.quit()

''' DO NOT EDIT BEGIN '''
info['participant'] = int(info['participant'])
info['age'] = int(info['age'])
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
info['feedbackTime'] = 48 #frames
info['startTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #create str of current date/time
info['endTime'] = '' # to be saved later on
# info['ITIDuration'] = np.arange(0.50, 0.81, 0.05) #a numpy array of ITI in seconds (to be randomly selected later for each trial)
# iti duration to be drawn from from exponential distribution (0.5 to 1.5)
seconds = sp.stats.expon.rvs(size=10000, scale=0.4) # exponential distribution
seconds = np.around(seconds/0.05) * 0.05
seconds = seconds[seconds <= 1.50] # max
seconds = seconds[seconds >= 0.50] # min
info['ITIDuration'] = seconds
runMentalMathBlockAccuracy = 0
runMentalMathBlockRt = np.nan
charityChosen = 'charity'

globalClock = core.Clock() # create and start global clock to track OVERALL elapsed time
ISI = core.StaticPeriod(screenHz = 60) # function for setting inter-trial interval later

# create window to draw stimuli on
win = visual.Window(size = (800, 600), fullscr = fullscreen, units = 'norm', monitor = monitor, colorSpace = 'rgb', color = (-1, -1, -1))
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
                elif event.getKeys(['bracketright']):  block
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
    logFilename = "{:03d}-{}-{}".format(int(info['participant']), info['startTime'], taskName)
    logfile = logging.LogFile(logFilename + ".log", filemode = 'w', level = logging.EXP) #set logging information (core.quit() is required at the end of experiment to store logging info!!!)
    #logging.console.setLevel(logging.DEBUG) #set COSNSOLE logging level

    '''DO NOT EDIT BEGIN'''
    mouse.setVisible(0) #make mouse invisible

    #Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True

    trialsDf = pd.DataFrame(index=np.arange(trials)) # create empty dataframe to store trial info

    #if this is a practice block
    if blockType == 'practice':
        trialsDf = trialsDf[0:practiceTrials] #number of practice trials to present
    '''DO NOT EDIT END'''

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
    trialsDf['task'] = taskName #task name
    trialsDf['fixationFrames'] = info['fixationFrames']
    trialsDf['postFixationFrames'] = np.nan
    if rtMaxFrames is None:
        trialsDf['targetFrames'] = info['targetFrames']
    else:
        trialsDf['targetFrames'] = rtMaxFrames
    trialsDf['startTime'] = info['startTime']
    trialsDf['endTime'] = info['endTime']

    #create variables to store data later
    trialsDf['blockNumber'] = 0 #add blockNumber
    trialsDf['elapsedTime'] = np.nan
    trialsDf['resp'] = None
    trialsDf['rt'] = np.nan
    trialsDf['iti'] = np.nan
    trialsDf['responseTTL'] = np.nan
    trialsDf['choice'] = np.nan
    trialsDf['overallTrialNum'] = 0 #cannot use np.nan because it's a float, not int!
    trialsDf['digits'] = digits
    trialsDf['digitChange'] = digitChange
    trialsDf['digitsToModify'] = digitsToModify
    trialsDf['testDigits'] = None
    trialsDf['correctAnswer'] = None
    trialsDf['wrongAnswer'] = None
    trialsDf['correctKey'] = None
    trialsDf['acc'] = np.nan

    ''' define number sequence and correct/incorrect responses for block '''
    # timing for updating task
    testDigitFrames = 30 # frames to show each test digit
    postTestDigitBlankFrames = 60 # blank frames after each digit
    postAllTestDigitBlankFrames = 30 # blank frames after all digits

    trialsDf['testDigitFrames'] = testDigitFrames
    trialsDf['postTestDigitBlankFrames'] = postTestDigitBlankFrames
    trialsDf['postAllTestDigitBlankFrames'] = postAllTestDigitBlankFrames

    # populate dataframe with test number sequences and answers
    for rowI in range(0, trialsDf.shape[0]):
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
        #print "new list is {0}".format(digitsListAnswer)

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
        trialsDf.loc[rowI, 'testDigits'] = ''.join(str(x) for x in digitsList)
        trialsDf.loc[rowI, 'correctAnswer'] = ''.join(str(x) for x in correctAnswer)
        trialsDf.loc[rowI, 'wrongAnswer'] = ''.join(str(x) for x in wrongAnswer)
        trialsDf.loc[rowI, 'correctKey'] = random.choice(['f', 'j'])

    '''DO NOT EDIT BEGIN'''
    #Assign blockNumber based on existing csv file. Read the csv file and find the largest block number and add 1 to it to reflect this block's number.
    try:
        blockNumber = max(pd.read_csv(filename)['blockNumber']) + 1
        trialsDf['blockNumber'] = blockNumber
    except: #if fail to read csv, then it's block 1
        blockNumber = 1
        trialsDf['blockNumber'] = blockNumber
    '''DO NOT EDIT END'''


    #create stimuli that are constant for entire block
    #draw stimuli required for this block
    #[1.0,-1,-1] is red; #[1, 1, 1] is white
    fixation = visual.TextStim(win = win, units = 'norm', height = 0.08, ori = 0, name = 'target', text = '+', font = 'Courier New Bold', colorSpace = 'rgb', color = [1, -1, -1], opacity = 1)

    testDigit = visual.TextStim(win = win, units = 'norm', height = 0.20, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    correctDigits = visual.TextStim(win = win, units = 'norm', height = 0.12, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    wrongDigits = visual.TextStim(win = win, units = 'norm', height = 0.12, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)



    #create clocks to collect reaction and trial times
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

        #3: draw stimulus (digits) one by one
        for d in thisTrial['testDigits']:
            testDigit.setText(d)
            testDigit.setAutoDraw(True)
            for frameN in range(testDigitFrames):
                win.flip()
            testDigit.setAutoDraw(False)
            # blank screen for a while before next digit
            for frameN in range(postTestDigitBlankFrames):
                win.flip()

        for frameN in range(postAllTestDigitBlankFrames):
            win.flip()

        #4: draw response options
        correctDigits.setText(thisTrial['correctAnswer'])
        wrongDigits.setText(thisTrial['wrongAnswer'])

        # set option positions
        if thisTrial['correctKey'] == "f":
            correctDigits.setPos((-0.12, 0.0)) # left
            wrongDigits.setPos((0.12, 0.0)) # right
        elif thisTrial['correctKey'] == "j":
            correctDigits.setPos((0.12, 0.0)) # right
            wrongDigits.setPos((-0.12, 0.0)) # left

        correctDigits.setAutoDraw(True)
        wrongDigits.setAutoDraw(True)

        # if titrating, determine stuff automatically
        if titrate:
            # determine response duration
            try:
                last2Trials = pd.read_csv(filename).tail(2).reset_index()
                if last2Trials.loc[1, 'acc'] == 1 and trialsDf.loc[i, 'targetFrames'] >= 24: # if previous trial correct
                    trialsDf.loc[i, 'targetFrames'] = last2Trials.loc[1, 'targetFrames'] - 6 # minus 6 frames (100 ms)
                    trialsDf.loc[i, 'postTestDigitBlankFrames'] = trialsDf.loc[i-1, 'postTestDigitBlankFrames'] - 1
                elif last2Trials.loc[0:1, 'acc'].sum() == 0:
                    trialsDf.loc[i, 'targetFrames'] = last2Trials.loc[1, 'targetFrames'] + 6 # plus 6 frames (100 ms)
                    trialsDf.loc[i, 'postTestDigitBlankFrames'] = trialsDf.loc[i-1, 'postTestDigitBlankFrames'] + 1
                else:
                    trialsDf.loc[i, 'targetFrames'] = last2Trials.loc[1, 'targetFrames']
                    trialsDf.loc[i, 'postTestDigitBlankFrames'] = trialsDf.loc[i-1, 'postTestDigitBlankFrames']
                # print trialsDf.loc[i, 'targetFrames']
            except:
                pass

        win.callOnFlip(respClock.reset) #reset response clock on next flip
        win.callOnFlip(trialClock.reset) #reset trial clock on next flip

        event.clearEvents() #clear events

        for frameN in range(int(trialsDf.loc[i, 'targetFrames'])):
            if frameN == 0: #on first frame/flip/refresh
                if sendTTL and not blockType == 'practice':
                    win.callOnFlip(port.setData, int(thisTrial['TTLStim']))
                else:
                    pass
                ##print "First frame in Block %d Trial %d OverallTrialNum %d" %(blockNumber, i + 1, trialsDf.loc[i, 'overallTrialNum'])
                ##print "Stimulus TTL: %d" %(int(thisTrial['TTLStim']))
            else:
                keys = event.getKeys(keyList = ['f', 'j', 'backslash', 'bracketright'])
                if len(keys) > 0 and trialsDf.loc[i, 'resp'] is None: #if a response has been made
                    trialsDf.loc[i, 'rt'] = respClock.getTime() #store RT
                    trialsDf.loc[i, 'resp'] = keys[0] #store response in pd df

                    if keys[0] == 'f' and thisTrial['correctKey'] == 'f': #if go trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) #correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1
                        ##print 'correct keypress: %s' %str(trialsDf.loc[i, 'resp'])
                        ##print "Response TTL: 15"

                    elif keys[0] == 'j' and thisTrial['correctKey'] == 'j': #if go trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) #correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1
                        ##print 'correct keypress: %s' %str(trialsDf.loc[i, 'resp'])
                        ##print "Response TTL: 15"

                    elif keys[0] == 'j' and thisTrial['correctKey'] == 'f': #if nogo trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(16) #incorrect response
                        trialsDf.loc[i, 'responseTTL'] = 16
                        trialsDf.loc[i, 'acc'] = 0
                        ##print 'incorrect keypress: %s' %str(trialsDf.loc[i, 'resp'])
                        ##print "Response TTL: 16"

                    elif keys[0] == 'f' and thisTrial['correctKey'] == 'j': #if nogo trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(16) #incorrect response
                        trialsDf.loc[i, 'responseTTL'] = 16
                        trialsDf.loc[i, 'acc'] = 0
                        ##print 'incorrect keypress: %s' %str(trialsDf.loc[i, 'resp'])
                        ##print "Response TTL: 16"

                    #remove stimulus from screen
                    correctDigits.setAutoDraw(False); wrongDigits.setAutoDraw(False)
                    win.flip() # clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            trialsDf.loc[i, 'acc'] = 0
            correctDigits.setAutoDraw(False); wrongDigits.setAutoDraw(False)
            win.flip() #clear screen (remove stuff from screen)

        # if both response options are the same, then accuracy is always correct
        if digitsToModify == 0 and trialsDf.loc[i, 'resp'] is not None:
            trialsDf.loc[i, 'acc'] = 1


        if sendTTL and not blockType == 'practice':
            port.setData(0) #parallel port: set all pins to low

        trialsDf.loc[i, 'elapsedTime'] = globalClock.getTime() #store total elapsed time in seconds
        trialsDf.loc[i, 'endTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #store current time
        iti = round(random.choice(info['ITIDuration']), 2) #randomly select an ITI duration
        trialsDf.loc[i, 'iti'] = iti #store ITI duration

        #start inter-trial interval...
        ISI.start(iti)

        ###print "TRIAL OK TRIAL %d OVERALL TRIAL %d" %(i + 1, int(trialsDf.loc[i, 'overallTrialNum']))

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
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'resp'] == None
            #naturalText.setAutoDraw(False)
            #healthText.setAutoDraw(False)
            #tasteText.setAutoDraw(False)
            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            return None

        global runMentalMathBlockAccuracy
        runMentalMathBlockAccuracy = trialsDf.loc[i, 'acc']
        global runMentalMathBlockRt
        runMentalMathBlockRt = trialsDf.loc[i, 'rt']

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
        ''' DO NOT EDIT END '''

        ISI.complete() #end inter-trial interval

        #feedback for trial
        if feedback:
            #stimuli
            accuracyFeedback = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'acc'] == 1: #if nogo trial and keypress
                accuracyFeedback.setText(random.choice(["Correct"]))
            elif trialsDf.loc[i, 'resp'] is None:
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
    logFilename = "{:03d}-{}-{}".format(int(info['participant']), info['startTime'], taskName)
    logfile = logging.LogFile(logFilename + ".log", filemode = 'w', level = logging.EXP) #set logging information (core.quit() is required at the end of experiment to store logging info!!!)
    #logging.console.setLevel(logging.DEBUG) #set COSNSOLE logging level

    mouse.setVisible(0) #make mouse invisible

    #Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True

    trialsDf = pd.DataFrame(index=np.arange(reps * len([(r, e) for r in reward for e in effort]))) # create empty dataframe to store trial info

    #if this is a practice block
    if blockType == 'practice':
        trialsDf = trialsDf[0:practiceTrials] # practice trials to present

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

    '''GENERATE TRIALS FOR EFFORT/REWARD CHOICE TASK'''
    if blockType == 'self':
        rewardEffortCombi = [(r, e) for r in reward for e in effort] # all combinations
        rewardEffortCombi = pd.DataFrame(rewardEffortCombi)
        rewardEffortCombi.columns = ['reward', 'effort']
        rewardEffortCombi['beneficiary'] = 'self'
        trialsInBlock = pd.concat([rewardEffortCombi], ignore_index=True)
    elif blockType == 'charity':
        rewardEffortCombi2 = pd.DataFrame(rewardEffortCombi2)
        rewardEffortCombi2.columns = ['reward', 'effort']
        rewardEffortCombi2['beneficiary'] = 'charity'
        trialsInBlock = pd.concat([rewardEffortCombi2], ignore_index=True)
    else:
        rewardEffortCombi = [(r, e) for r in reward for e in effort] # all combinations
        rewardEffortCombi = pd.DataFrame(rewardEffortCombi)
        rewardEffortCombi.columns = ['reward', 'effort']
        rewardEffortCombi['beneficiary'] = 'self'

        rewardEffortCombi2 = [(r, e) for r in reward for e in effort] # all combinations
        rewardEffortCombi2 = pd.DataFrame(rewardEffortCombi2)
        rewardEffortCombi2.columns = ['reward', 'effort']
        rewardEffortCombi2['beneficiary'] = 'charity'

        trialsInBlock = pd.concat([rewardEffortCombi, rewardEffortCombi2], ignore_index=True)

    trialsInBlock = trialsInBlock.reindex(np.random.permutation(trialsInBlock.index)).reset_index(drop=True) # shuffle
    trialsInBlock['rewardJittered'] = trialsInBlock.reward
    if jitter is not None:
        trialsInBlock['rewardJittered'] = trialsInBlock.reward + np.around(np.random.normal(scale=0.1, size=trialsInBlock.shape[0]) / 0.05) * 0.05

    trialsDf = pd.concat([trialsDf, trialsInBlock], axis=1)
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
    fixation = visual.TextStim(win=win, units='norm', height=0.08, ori=0, name='target', text='+', font='Courier New Bold', colorSpace='rgb', color=[1, -1, -1], opacity=1)

    constantOptionEffort = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = 'add 0', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.12, 0.05))

    constantOptionReward = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = '1 credit', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.12, -0.05))

    varyingOptionEffort = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = 'XXX', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.12, 0.05))

    varyingOptionReward = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = 'XXX', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.12, -0.05))

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
        else:
            beneficiaryText.setText('self')

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

        win.callOnFlip(respClock.reset) # reset response clock on next flip
        win.callOnFlip(trialClock.reset) # reset trial clock on next flip

        event.clearEvents() # clear events

        for frameN in range(int(trialsDf.loc[i, 'targetFrames'])):
            if frameN == 0: #on first frame/flip/refresh
                if sendTTL and not blockType == 'practice':
                    win.callOnFlip(port.setData, int(thisTrial['TTLStim']))
                else:
                    pass
                ##print "First frame in Block %d Trial %d OverallTrialNum %d" %(blockNumber, i + 1, trialsDf.loc[i, 'overallTrialNum'])
                ##print "Stimulus TTL: %d" %(int(thisTrial['TTLStim']))
            else:
                keys = event.getKeys(keyList = ['f', 'j', 'backslash', 'bracketright'])
                if len(keys) > 0 and trialsDf.loc[i, 'resp'] is None: #if a response has been made
                    trialsDf.loc[i, 'rt'] = respClock.getTime() #store RT
                    trialsDf.loc[i, 'resp'] = keys[0] #store response in pd df

                    if keys[0] == 'f':
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'choiceText'] = 'baseline'
                    elif keys[0] == 'j':
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

        ###print "TRIAL OK TRIAL %d OVERALL TRIAL %d" %(i + 1, int(trialsDf.loc[i, 'overallTrialNum']))

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

        #feedback for trial
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
            for frameN in range(info['feedbackTime']):
                feedbackText1.draw()
                win.flip()

        # pause
        for frameN in range(info['blockEndPause']):
            win.flip() #wait at the end of the block

        #### run mental math block ####
        if trialsDf.loc[i, 'resp'] is not None:
            # run mental math updating trial
            if trialsDf.loc[i, 'choiceText'] == 'baseline':
                runMentalMathBlock(taskName='mentalMathUpdating', blockType='', trials=1, feedback=True, saveData=True, practiceTrials=0, digits=3, digitChange=0, digitsToModify=0, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
            elif trialsDf.loc[i, 'choiceText'] == 'effortful':
                runMentalMathBlock(taskName='mentalMathUpdating', blockType='', trials=1, feedback=True, saveData=True, practiceTrials=0, digits=3, digitChange=trialsDf.loc[i, 'effort'], digitsToModify=2, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
            else:
                pass

        global runMentalMathBlockAccuracy
        trialsDf.loc[i, 'accUpdating'] = runMentalMathBlockAccuracy
        global runMentalMathBlockRt
        trialsDf.loc[i, 'rtUpdating'] = runMentalMathBlockRt

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)

        #feedback for trial
        if feedback:
            # initialize stimuli
            feedbackText1 = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'accUpdating'] == 1:
                if trialsDf.loc[i, 'choiceText'] == 'effortful':
                    feedbackText1.setText('{} credits'.format(thisTrial['rewardJittered']))
                else:
                    feedbackText1.setText('1 credit')
            else:
                feedbackText1.setText('no credits earned')

            for frameN in range(48):
                feedbackText1.draw()
                win.flip()

        # pause
        for frameN in range(info['blockEndPause'] * 2):
            win.flip() #wait at the end of the block

    # end of block pause
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

def showQuestionnaire(csvFile, scaleMin, scaleMax, scaleDescription, outputName='Questionnaires'):
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
    scale = visual.RatingScale(win, low = scaleMin, high = scaleMax, tickMarks = range(scaleMin, scaleMax + 1), mouseOnly = True, singleClick = True, stretch = 2, marker = 'slider', showAccept = False, pos = (0, -0.5), showValue = True, textSize = 0.7, textFont = 'Verdana', markerColor = 'red', scale = scaleDescription)

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

    #BFAS
    showInstructions(text = ["Next you will read several characteristics that may or may not describe you. Select the option that best indicates how much you agree or disagree. Be as honest as you can and rely on your initial feeling. Do not think too much about each item."])
    showQuestionnaire(csvFile = 'BFAS.csv', scaleMin = 1, scaleMax = 5, scaleDescription = '1: disagree strongly, 5: agree strongly')

    #ApathyMotivationIndex
    showInstructions(text = ["Indicate how true each statement is based on the past two weeks of your life."])
    showQuestionnaire(csvFile = 'ApathyMotivationIndex.csv', scaleMin = 0, scaleMax = 4, scaleDescription = "0: completely true, 4: completely untrue")

    #Dispositional awe
    showInstructions(text = ["The following statements inquire about your thoughts and feelings in a variety of situations. For each item, indicate how well it describes you."])
    showQuestionnaire(csvFile = 'DispositionalPositiveEmotionsScaleAwe.csv', scaleMin = 1, scaleMax = 7, scaleDescription = '1: strongly disagree, 7: strongly agree')

    #Empathy index
    showInstructions(text = ["The following statements inquire about your thoughts and feelings in a variety of situations. For each item, indicate how well it describes you."])
    showQuestionnaire(csvFile = 'EmpathyIndex.csv', scaleMin = 1, scaleMax = 5, scaleDescription = "1: doesn't describe me well , 5: describes me very well")

    #PoliticalOrientation
    showInstructions(text = ["Click scale to respond."])
    showQuestionnaire(csvFile = 'PoliticalOrientation.csv', scaleMin = 1, scaleMax = 7, scaleDescription = "1: very liberal, 3: moderate/middle-of-the-road, 7: very conservative")

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

















#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################
''' START EXPERIMENT HERE '''

if sendTTL:
   port.setData(0) # make sure all pins are low before experiment

showInstructions(text = [
" ", # black screen at the beginning
"Welcome to today's experiment! Before we begin, please answer a few questions about yourself."])

getDemographics() # get demographics (gender, ses, ethnicity, handedness)

runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='mixed', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[2, 4, 6, 9, 12], effort=[1, 2, 3, 5, 7])

''' practice '''
showInstructions(text =
["We are studying how people make decisions related to cognitive effort. You will also have many opportunities to earn money during the experiment.",
"If you have any questions during the experiment, raise/wave your hands and the research assistant will help you.",
"The cognitive task you're going to do requires you to solve math problems (adding numbers) and has different levels of difficulty.",
"You'll see three-digit sequences, with each digit presented one at a time on the screen. You have to add a certain number (e.g., add 3) to each digit, one at a time, remember the sequence of digits, and choose the correct answer later on.",
"So, if you see 5, 2, 3 (presented on at a time) and you've been told to add 3, you'll add 3 to each number separately, and will have to choose between two responses shown on the left and right of the screen: 856 and 846. 856 is the correct response in this example.",
"Place your left and right index fingers on the F and J keys, and press the F key to choose the left option, and the J key for the right option.",
"Whenever the sum of two digits is greater than 10, you'll report only the ones digit (the rightmost digit). For example, if the problem is 9 + 5, the summed digit will be 4 (not 14).",
"A few more examples: 7 + 8 is 5; 4 + 6 is 0; 9 + 2 is 1.",
"If anything's unclear, please ask the researcher assistant now. If not, we'll practice a bit now!",
"You have 2 seconds to indicate your answer (using the F and J keys). If no choice is made, it'll be considered wrong and the task will proceed."])

showInstructions(text = ["Let's try adding 1 to each digit!"])
runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=3, feedback=True, saveData=True, practiceTrials=3, digits=3, digitChange=1, digitsToModify=2, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
showInstructions(text = ["That was add 1. If anything's unclear, please ask the research assistant now!"])

showInstructions(text = ["Now let's try adding 2 to each digit."])
runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=3, feedback=True, saveData=True, practiceTrials=3, digits=3, digitChange=2, digitsToModify=2, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
showInstructions(text = ["That was add 2."])

showInstructions(text = ["Now let's do add 3."])
runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=3, feedback=True, saveData=True, practiceTrials=3, digits=3, digitChange=3, digitsToModify=2, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
showInstructions(text = ["That was add 3."])

showInstructions(text = ["Let's try add 5 now!"])
runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=3, feedback=True, saveData=True, practiceTrials=3, digits=3, digitChange=5, digitsToModify=2, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
showInstructions(text = ["That was add 5."])

showInstructions(text = ["Let's try add 7 now!"])
runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=3, feedback=True, saveData=True, practiceTrials=3, digits=3, digitChange=7, digitsToModify=2, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
showInstructions(text = ["That was add 7."])

showInstructions(text = ["Finally, let's try add 0. When adding 0, all you have to do is remember the three digits. In fact, the two response options will be identical and either will be correct. So as long as you make a response in under 2 seconds, you'll be correct!"])
runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=3, feedback=True, saveData=True, practiceTrials=2, digits=3, digitChange=0, digitsToModify=0, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None)
showInstructions(text = ["That was add 0."])

''' effort questions '''
showInstructions(text = ["Now you'll answer a few questions about the math task."])

effortQuestions = ['How much effort did add 0 require?', 'How much effort did add 1 require?', 'How much effort did add 2 require?', 'How much effort did add 3 require?', 'How much effort did add 5 require?', 'How much effort did add 7 require?']
random.shuffle(effortQuestions)

presentQuestions(questionName='effortFrustrateReport', questionList=effortQuestions, blockType='pre', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['none at all', 'very much'])

''' frustrate questions '''
frustrateQuestions = ['How frustrating was add 0?', 'How frustrating was add 1?', 'How frustrating was add 2?', 'How frustrating was add 3?', 'How frustrating was add 5?', 'How frustrating was add 7?']
random.shuffle(frustrateQuestions)

presentQuestions(questionName='effortFrustrateReport', questionList=frustrateQuestions, blockType='pre', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])


''' practice choice task '''

showInstructions(text = [
"You'll be doing many of these addition tasks later on, and the task difficulty (add 0, 1, 2, 3, 5, or 7) depends on your choices during a decision making task.",
"In this decision task, you'll have to choose between two options: doing add 0 or add 1, 2, 3, 5, or 7). Each option will have a specific number of credits associated with it. If you perform your chosen task correctly, you'll get those credits, which will be converted to money (Amazon voucher to be emailed to you).",
"Add 0 will ALWAYS be one of the available options, and you will ALWAYS receive 1 credit for choosing to do add 0. The other option will vary in terms of difficulty (add 1, 2, 3, 5, or 7) and credits (2 to 12 credits).",
"For example, you might see these two options on the screen: add 0 for 1 credit vs add 3 for 5 credits. The add 0 for 1 credit option means if you choose it and perform accurately on the add 0 task, you'll get 1 credit. And if you choose the add 3 option for 5 credits option, you'll get 5 credits if you perform the add 3 task accurately.",
"Here is one more example: add 0 for 1 credit vs add 7 for 2 credits",
"If you don't have any questions, we'll practice a bit now.",
"If you see the word 'self' at the top, it means the credits you earn will be given to you.",
"Here we go! You have up to 5 seconds to choose."
])

''' self practice'''
runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='self', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[2], effort=[1, 3])

showInstructions(text = [
"The 'self' you saw at the top just now means the credits you earn will go to you. But sometimes, the credits you earn will instead go to a charity. In this case, for example you choose add 7 for 3 credits for a charity, you are saying you will be donating your 3 credits (converted to monetary amounts at the end) to a charity if you got perform the add 7 task correctly.",
"So, in this choice task, you can earn credits/money for yourself or for a charity, so decide carefully and try to do the addition task well!",
"Now, you can choose which (of 5) charity you want to donate to. If you have a specific charity you'd like to donate to, let the research assistant know. "
])

# pick charity here
presentQuestions(questionName='charityChoice', questionList=["Which charity do you want to donate to? (1) World Vision Canada; (2) Canadian Cancer Society; (3) SickKids Foundation; (4) Salvation Army; (5) Wildlife Preservation Canada; (6) Other (please ask for the researcher assistance if you want to select this option)"], blockType='charityChoice', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,5], scaleAnchorText=[' ', ' '], showAnchors=False)

showInstructions(text = [
"Let's practice choosing and performing the task for both yourself and {}.".format(charityChosen),
"Remember, one option always remain the same (add 0 for 1 credit), whereas the other option varies."
])

''' self/charity practice'''
runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='charity', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=60, experimentMaxTimeSeconds=None, reward=[2], effort=[3])

runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='self', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=60, experimentMaxTimeSeconds=None, reward=[10], effort=[4])

showInstructions(text = ["That's the end of practice. Let the research assistant know if you have any questions."])

''' actual task '''
showInstructions(text = [
"You'll now do the actual choice and math task now.",
"Place your left and right index fingers on the F and J keys, and use the F and J keys to choose the left and right options respectively.",
"You have up to 5 seconds to make each choice, and 2 seconds to indicate your response when doing the addition task.",
"Remember, you're making REAL choices from now on. Your choices and decisions are not hypothetical. We will convert the credits you earn during the task into monetary amounts and will pay you and {} accordingly.".format(charityChosen),
"You'll have opportunities to take breaks during the experiment."
])

runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='mixed', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[2, 4, 6, 9, 12], effort=[1, 2, 3, 5, 7])

showInstructions(text = ["Take a break. Press space when ready to continue."])

runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='mixed', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[2, 4, 6, 9, 12], effort=[1, 2, 3, 5, 7])

showInstructions(text = ["Take a break. Press space when ready to continue."])

runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='mixed', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[2, 4, 6, 9, 12], effort=[1, 2, 3, 5, 7])

showInstructions(text = ["That's the end of the decision making task. Press space when ready to continue."])


''' post choice task effort questions '''
showInstructions(text = ["Now you'll answer a few questions about the math task."])

effortQuestions = ['How much effort did add 0 require?', 'How much effort did add 1 require?', 'How much effort did add 2 require?', 'How much effort did add 3 require?', 'How much effort did add 5 require?', 'How much effort did add 7 require?']
random.shuffle(effortQuestions)

presentQuestions(questionName='effortFrustrateReport', questionList=effortQuestions, blockType='post', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['none at all', 'very much'])

''' frustrate questions '''
frustrateQuestions = ['How frustrating was add 0?', 'How frustrating was add 1?', 'How frustrating was add 2?', 'How frustrating was add 3?', 'How frustrating was add 5?', 'How frustrating was add 7?']
random.shuffle(frustrateQuestions)

presentQuestions(questionName='effortFrustrateReport', questionList=frustrateQuestions, blockType='post', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])


''' questionnaires '''
# showInstructions(text = ["Now you'll answer a few questions about yourself."])
# showAllQuestionnaires()

showInstructions(text = ["That's the end of the experiment. This is how much you have earned for yourself and {}.".format(charityChosen)])

''' notify credits/money earned '''
creditCsv = "{:03d}-{}-effortRewardChoice.csv".format(int(info['participant']), info['startTime'])
creditDf = pd.read_csv(creditCsv)
creditDf = creditDf.dropna(subset=['accUpdating', 'reward'])

creditSelfBaseline = creditDf.loc[(creditDf.beneficiary == 'self') & (creditDf.accUpdating == 1.0) & (creditDf.choiceText == 'baseline'), ].shape[0]
creditSelfEffortful = int(creditDf.loc[(creditDf.beneficiary == 'self') & (creditDf.accUpdating == 1.0) & (creditDf.choiceText == 'effortful'), 'reward'].sum())
creditSelf = creditSelfBaseline + creditSelfEffortful

creditCharityBaseline = creditDf.loc[(creditDf.beneficiary == 'charity') & (creditDf.accUpdating == 1.0) & (creditDf.choiceText == 'baseline'), ].shape[0]
creditCharityEffortful = int(creditDf.loc[(creditDf.beneficiary == 'charity') & (creditDf.accUpdating == 1.0) & (creditDf.choiceText == 'effortful'), 'reward'].sum())
creditCharity = creditCharityBaseline + creditCharityEffortful

moneySelf = 0.01 * creditSelf
moneyCharity = 0.01 * creditCharity

outputCsv = pd.DataFrame(index=range(0, 1))
outputCsv['email'] = info['email']
outputCsv['moneySelf'] = moneySelf
outputCsv['moneyCharity'] = moneyCharity
outputCsv['creditSelf'] = creditSelf
outputCsv['creditCharity'] = creditCharity
outputCsv['charityChosen'] = charityChosen

outputCsv.to_csv("{:03d}-{}-REWARDINFO.csv".format(int(info['participant']), info['startTime']), index=False)

# creditRewardInfoText = "{:03d}-{}-REWARDINFO.txt".format(int(info['participant']), info['startTime'])
# with open(creditRewardInfoText, "w") as textFile: #write to text file
#     textFile.write("email: {}; money self ${:.2f}; money charity ${:.2f}; credit self {}; credit charity {}".format(info['email'], moneySelf, moneyCharity, creditSelf, creditCharity))

"You've earned {} credits for yourself, and {} credits for charity.".format(creditSelf, creditCharity)
"These credits translate to the following: ${:.2f} for yourself, and ${:.2f} donated to your charity. We will email you your reward in the form of an Amazon voucher, and will help you donate to {}.".format(moneySelf, moneyCharity, charityChosen)

''' experiment end '''

showInstructions(text = ["That's the end of the experiment. Thanks so much for participating in our study!"])


if sendTTL:
    port.setData(255) # mark end of experiment

core.quit() # quit PsychoPy
