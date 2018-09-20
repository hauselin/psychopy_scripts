'''
'''

import pandas as pd
import numpy as np
import scipy as sp
import random, os, time
from psychopy import visual, core, event, data, gui, logging, parallel, monitors

# set DEBUG mode: if True, participant ID will be 999 and display will not be fullscreen. If False, will have to provide participant ID and will be in fullscreen mode
DEBUG = True
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
info = {} #create empty dictionary to store stuff

if DEBUG:
    fullscreen = False #set fullscreen variable = False
    logging.console.setLevel(logging.DEBUG)
    info['participant'] = 999 #let 999 = debug participant no.
else: #if DEBUG is not False... (or True)
    fullscreen = True #set full screen
    logging.console.setLevel(logging.WARNING)
    info['participant'] = '' #dict key to store participant no.
    #present dialog to collect info
    dlg = gui.DlgFromDict(info) #create a dialogue box (function gui)
    if not dlg.OK: #if dialogue response is NOT OK, quit
        #moveFiles(dir = 'Data')
        core.quit()

info['participant'] = int(info['participant'])
info['task'] = 'shiftingLetterNumber' #task name
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

globalClock = core.Clock() # create and start global clock to track OVERALL elapsed time
ISI = core.StaticPeriod(screenHz = 60) # function for setting inter-trial interval later

# create window to draw stimuli on
win = visual.Window(size = (800, 600), fullscr = fullscreen, units = 'norm', monitor = monitor, colorSpace = 'rgb', color = (-1, -1, -1))
#create mouse
mouse = event.Mouse(visible = False, win = win)
mouse.setVisible(0) # make mouse invisible

# create base filename to store data
filename = "%03d-%s-%s.csv" %(int(info['participant']), info['startTime'], info['task'])
# create name for logfile
logFilename = "%03d-%s-%s" %(int(info['participant']), info['startTime'], info['task'])
logfile = logging.LogFile(logFilename + ".log", filemode = 'w', level = logging.EXP) #set logging information (core.quit() is required at the end of experiment to store logging info!!!)
#logging.console.setLevel(logging.DEBUG) #set COSNSOLE logging level

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

    #'Press space to continue' text for each 'page'
    continueText = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = "Press space to continue", height = 0.04, wrapWidth = 1.4, pos = [0.0, 0.0])
    #instructions to be shown
    instructText = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = 'DEFAULT', height = 0.08, wrapWidth = 1.4, pos = [0.0, 0.5])

    for i in range(len(text)): #for each item/page in the text list
        instructText.text = text[i] #set text for each page
        if timeBeforeAutomaticProceed == 0 and timeBeforeShowingSpace == 0: #if
            while not event.getKeys(keyList = ['space']):
                continueText.draw(); instructText.draw(); win.flip()
                if event.getKeys(keyList = ['0']):
                    #moveFiles(dir = 'Data')
                    core.quit()
                elif event.getKeys(['7']): #if press 7, skip to next block
                    return None
        elif timeBeforeAutomaticProceed != 0 and timeBeforeShowingSpace == 0:
            #clock to calculate how long to show instructions
            #if timeBeforeAutomaticProceed is not 0 (e.g., 3), then each page of text will be shown 3 seconds and will proceed AUTOMATICALLY to next page
            instructTimer = core.Clock()
            while instructTimer.getTime() < timeBeforeAutomaticProceed:
                if event.getKeys(keyList = ['0']):
                    #moveFiles(dir = 'Data')
                    core.quit()
                elif event.getKeys(['7']): #if press 7, skip to next block
                    return None
                instructText.draw(); win.flip()
        elif timeBeforeAutomaticProceed == 0 and timeBeforeShowingSpace != 0:
            instructTimer = core.Clock()
            while instructTimer.getTime() < timeBeforeShowingSpace:
                if event.getKeys(keyList = ['0']):
                    #moveFiles(dir = 'Data')
                    core.quit()
                elif event.getKeys(['7']): #if press 7, skip to next block
                    return None
                instructText.draw(); win.flip()
            win.flip(); event.clearEvents() #clear events to ensure if participants press space before 'press space to continue' text appears, their response won't be recorded

    instructText.setAutoDraw(False)
    continueText.setAutoDraw(False)

    for frameN in range(info['blockEndPause']):
        win.flip() #wait at the end of the block

def runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='', trials=10, feedback=False, saveData=True, practiceTrials=10, switchProportion = 0.3, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None):
    '''Run a block of trials.
    blockType: custom name of the block; if blockType is set to 'practice', then no TTLs will be sent and the number of trials to run will be determined by argument supplied to parameter practiceTrials.
    trials: number of times to repeat each unique trial
    feedback: whether feedback is presented or not
    saveData = whether to save data to csv file
    practiceTrials: no. of practice trials to run
    switchProportion: proportion of trials to switch
    titrate: whether to adjust difficulty of task based on performance; if set to True, subsequent targetFrames (max response time) for subsequent blocks will be affected
    rtmaxFrames: max rt (in frames); default is None, which takes value from info['targetFrames']; if a value is provided, default will be overwritten
    blockMaxTimeSeconds: end block if specified time (in seconds) has passed
    '''

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
        trialsDf = trialsDf[0:practiceTrials] # practice trials to present

    #store info in dataframe
    trialsDf['participant'] = int(info['participant'])
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
    trialsDf['blockNumber'] = 0 # add blockNumber
    trialsDf['elapsedTime'] = np.nan
    trialsDf['resp'] = None
    trialsDf['rt'] = np.nan
    trialsDf['iti'] = np.nan
    trialsDf['responseTTL'] = np.nan
    trialsDf['choice'] = np.nan
    trialsDf['overallTrialNum'] = 0 #cannot use np.nan because it's a float, not int!
    trialsDf['acc'] = np.nan

    '''generate trials for shifting task '''
    letters = ["A", "E", "U", "F", "G", "K"]
    numbers = [2, 3, 4, 6, 7, 8]
    letternumberTuple = [(l, n) for l in letters for n in numbers] # all letter/number combinations
    # concatenate letter and number
    letternumber = []
    for ln in letternumberTuple:
        letternumber.append(ln[0] + str(ln[1]))
    random.shuffle(letternumber) # shuffle
    letternumber = np.random.choice(letternumber, size=trials, replace=True)
    questions = [random.choice(['letter', 'number'])] * trials # define initial question
    trialsToSwitch = int(np.floor(trials * switchProportion)) # no. of trials to switch
    if trialsToSwitch >= trials:
        trialsToSwitch = trials - 1
    switches = ([1] * trialsToSwitch) + ([0] * (trials - trialsToSwitch - 1)) # generate switch indices (exclude first trial)
    random.shuffle(switches) # shuffle switche indices (exclude first trial)
    switches = [0] + switches # add first trial (don't switch)
    # assign question for each trial based on switching
    for idx, switchI in enumerate(switches):
        if idx > 0: # skip first trial
            # print(idx)
            if switchI == 1 and questions[idx-1] == 'number':
                questions[idx] = 'letter'
            elif switchI == 1 and questions[idx-1] == 'letter':
                questions[idx] = 'number'
            elif switchI == 1 and questions[idx-1] == 'number':
                questions[idx] = 'letter'
            elif switchI == 0 and questions[idx-1] == 'letter':
                questions[idx] = 'letter'
            elif switchI == 0 and questions[idx-1] == 'number':
                questions[idx] = 'number'
    # assign colour cue for trial type (set as global variable)
    if 'randomColourAssignmentToStimulus' not in globals(): # if variable doesn't exist, randomly assign it
        global randomColourAssignmentToStimulus
        randomColourAssignmentToStimulus = random.choice([{'letter': 'white', 'number': 'pink'}, {'letter': 'pink', 'number': 'white'}]) # randomly assign number/letter to pink/white

    # assign pink/white to number/letter
    colourCue = []
    for idx, questionI in enumerate(questions):
        if questionI == 'number':
            colourCue.append(randomColourAssignmentToStimulus['number'])
        elif questionI == 'letter':
            colourCue.append(randomColourAssignmentToStimulus['letter'])
    # assign response based on question
    correctAnswer = []
    correctKey = []
    for idx, questionI in enumerate(questions):
        if questions[idx] == 'letter':
            if letternumber[idx][0] in ["A", "E", "U"]:
                correctAnswer.append('vowel')
                correctKey.append('v')
            elif letternumber[idx][0] in ["F", "G", "K"]:
                correctAnswer.append('consonant')
                correctKey.append('c')
        elif questions[idx] == 'number':
            if int(letternumber[idx][1]) in [2, 3, 4]:
                correctAnswer.append('smaller')
                correctKey.append(',')
            elif int(letternumber[idx][1]) in [6, 7, 8]:
                correctAnswer.append('bigger')
                correctKey.append('.')
    # store info in dataframe
    trialsDf['letternumber'] = letternumber
    trialsDf['trials'] = trials
    trialsDf['switchProportion'] = switchProportion
    trialsDf['switches'] = trialsToSwitch
    trialsDf['switch'] = switches
    trialsDf['question'] = questions
    trialsDf['colourCue'] = colourCue
    trialsDf['correctAnswer'] = correctAnswer
    trialsDf['correctKey'] = correctKey

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

    letternumberStimulus = visual.TextStim(win = win, units = 'norm', height = 0.14, ori = 0, name = 'target', text = '0000', font = 'Courier New', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    cueText = visual.TextStim(win = win, units = 'norm', height = 0.04, ori = 0, name = 'target', text = '0000', font = 'Courier New', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.0, 0.15))

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

        # if there's a max time for this block, then end block when time's up
        if blockMaxTimeSeconds is not None:
            try:
                firstTrial = pd.read_csv(filename).head(1).reset_index()
                finalTrial = pd.read_csv(filename).tail(1).reset_index()
                if finalTrial.loc[0, 'elapsedTime'] - firstTrial.loc[0, 'elapsedTime'] >= blockMaxTimeSeconds:
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
        if thisTrial['colourCue'] == 'pink':
            letternumberStimulus.setColor([1.0,0.6,0.6]) # pink
            cueText.setColor([1.0,0.6,0.6]) # pink
        elif thisTrial['colourCue'] == 'white':
            letternumberStimulus.setColor([1, 1, 1]) # white
            cueText.setColor([1, 1, 1]) # white

        letternumberStimulus.setText(thisTrial['letternumber'])
        cueText.setText(thisTrial['question'])

        letternumberStimulus.setAutoDraw(True)
        cueText.setAutoDraw(True)

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

        for frameN in range(trialsDf.loc[i, 'targetFrames']):
            if frameN == 0: #on first frame/flip/refresh
                if sendTTL and not blockType == 'practice':
                    win.callOnFlip(port.setData, int(thisTrial['TTLStim']))
                else:
                    pass
                ##print "First frame in Block %d Trial %d OverallTrialNum %d" %(blockNumber, i + 1, trialsDf.loc[i, 'overallTrialNum'])
                ##print "Stimulus TTL: %d" %(int(thisTrial['TTLStim']))
            else:
                keys = event.getKeys(keyList = ['c', 'v', 'comma', 'period', '0', '7'])
                if len(keys) > 0: #if a response has been made
                    trialsDf.loc[i, 'rt'] = respClock.getTime() #store RT
                    trialsDf.loc[i, 'resp'] = keys[0] #store response in pd df

                    if keys[0] == 'c' and thisTrial['correctKey'] == 'c':
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1
                    elif keys[0] == 'v' and thisTrial['correctKey'] == 'v':
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1
                    elif keys[0] == 'comma' and thisTrial['correctKey'] == ',':
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1
                    elif keys[0] == 'period' and thisTrial['correctKey'] == '.':
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1
                    else:
                        if sendTTL and not blockType == 'practice':
                            port.setData(16) #incorrect response
                        trialsDf.loc[i, 'responseTTL'] = 16
                        trialsDf.loc[i, 'acc'] = 0
                    #remove stimulus from screen
                    letternumberStimulus.setAutoDraw(False); cueText.setAutoDraw(False)
                    win.flip() #clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            trialsDf.loc[i, 'acc'] = 0
            letternumberStimulus.setAutoDraw(False); cueText.setAutoDraw(False)
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
        if trialsDf.loc[i, 'resp'] == '0':
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'resp'] = None
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            #moveFiles(dir = 'Data')
            core.quit() #quit when '0' has been pressed
        elif trialsDf.loc[i, 'resp'] == '7':#if press 7, skip to next block
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'resp'] == None
            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            return None

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
        ''' DO NOT EDIT END '''

        ISI.complete() #end inter-trial interval

        #feedback for trial
        if feedback:
            #stimuli
            accuracyFeedback = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Courier New', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            reactionTimeFeedback = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Courier New', text = '', height = 0.05, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'acc'] == 1:
                accuracyFeedback.setText(random.choice(["Well done!", "Great job!", "Excellent!", "Amazing!", "Doing great!"]))
                for frameN in range(info['feedbackTime']):
                    accuracyFeedback.draw()
                    # reactionTimeFeedback.draw()
                    win.flip()
            elif trialsDf.loc[i, 'resp'] is None:
                accuracyFeedback.setText('Respond faster!')
                for frameN in range(info['feedbackTime']):
                    accuracyFeedback.draw()
                    win.flip()
            elif trialsDf.loc[i, 'acc'] == 0:
                accuracyFeedback.setText('Wrong!')
                for frameN in range(info['feedbackTime']):
                    accuracyFeedback.draw()
                    win.flip()

    for frameN in range(info['blockEndPause']):
        win.flip() #wait at the end of the block

def showTaskInstructions():
    showInstructions(text =
    ["", # black screen at the beginning
    "In this task, you'll have to do mental math.",
    "You'll see a string of numbers, presented one at a time.",
    "You have to add 3 to each number, and remember the new number. For example, 4 becomes 7, 0 becomes 3, 7 becomes 0, 8 becomes 1, and 9 becomes 2.",
    "After that, you'll be shown two options and you have to indicate which is the correct answer.",
    "For example, if you saw 3093 (presented 1 digit at a time), you might see 6326 and 6336. You'll have to indicate that 6326 is the correct answer.",
    "Use the F and J keys to indicate the correct answer.",
    "Press F if you think the left option is the correct one, and J if you think the right option is correct.",
    "You'll receive feedback if you're doing well (which can sometimes require more than just getting one answer correct)!"])

def showBlockBeginInstructions():
    showInstructions(text =
    ["Place your fingers on F and J."
    #"{:.1f} seconds to respond.".format(float(info['targetFrames']) / 60),
    ])

def showBlockEndInstructions():
    showInstructions(text =
    ["Take a break. Press space when ready to continue."])

def showWaitForRAInstructions():
    #new block instructions (check eye tracker)
    showInstructions(timeBeforeAutomaticProceed = 9999, text =
    ["Before you continue, we'll check whether all equipment and systems are in place. Please wait while we check everything. We'll let you know if they are any issues."
    ]) #RA has to press 7 to continue





##############################################################################
if sendTTL:
    port.setData(0) # make sure all pins are low before experiment

# showTaskInstructions() # instructions for the task

# showBlockBeginInstructions()

runShiftingLetterNumberBlock(blockType='actual', trials=20, feedback=True, saveData=True, practiceTrials=5, switchProportion=0.5, titrate=True, rtMaxFrames=180, blockMaxTimeSeconds=5)

runShiftingLetterNumberBlock(blockType='actual', trials=20, feedback=True, saveData=True, practiceTrials=5, switchProportion=0.5, titrate=True, rtMaxFrames=180, blockMaxTimeSeconds=5)

'''
showInstructions(text = #finish practice trial instructions
["Finished practice. From now on, you'll start the actual experiment and won't any receive feedback.",
"If you have any questions, please ask the research assistant now."
])
'''

if sendTTL:
    port.setData(255) # mark end of experiment

core.quit() # quit PsychoPy
