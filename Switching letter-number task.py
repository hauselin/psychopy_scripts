'''
Written by Hause Lin, hauselin@gmail.com
Last modified by Hause Lin 05-03-18 3:33 PM hauselin@gmail.com

PsychoPy script for switching task.
Press ] to skip blocks, and \ to quit experiment. Set DEBUG = True on (line 25) if you want to run the experiment in non-fullscreen mode.

See lines 162 to 172 for description of task parameters you can potentially change.

Actual script/experiment starts from line 652.

To change task parameters, go to line 671 (practice block) and 676 (actual block).

'''

import pandas as pd
import numpy as np
import scipy as sp
import random, os, time
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import visual, core, event, data, gui, logging, parallel, monitors, sound
from scipy import stats

# set DEBUG mode: if True, participant ID will be 999 and display will not be fullscreen. If False, will have to provide participant ID and will be in fullscreen mode
DEBUG = False
sendTTL = False # whether to send TTL pulses to acquisition computer
parallelPortAddress = 49168 # set parallel port address (EEG3: 49168, EEG1: 57360)

# display name (set up beforehand in PsychoPy preferences/settings)
# monitor = 'EEG3Display'
monitor = 'iMac'
# monitor = 'BehavioralLab'
# monitor = 'MacBookAir'

stimulusDir = 'Stimuli' + os.path.sep # stimulus directory/folder/path

#EXPERIMENT SET UP
info = {} # create empty dictionary to store stuff

if DEBUG:
    fullscreen = False #set fullscreen variable = False
    # logging.console.setLevel(logging.DEBUG)
    info['participant'] = random.choice([102]) #let 999 = debug participant no.
    # info['email'] = 'xxx@gmail.com'
    # info['age'] = 18
else: #if DEBUG is not False... (or True)
    fullscreen = True #set full screen
    # logging.console.setLevel(logging.WARNING)
    info['participant'] = '' #dict key to store participant no.
    # info['email'] = ''
    # info['age'] = ''
    # present dialog to collect info
    dlg = gui.DlgFromDict(info) #create a dialogue box (function gui)
    if not dlg.OK: #if dialogue response is NOT OK, quit
        #moveFiles(dir = 'Data')
        core.quit()

''' DO NOT EDIT BEGIN '''
info['participant'] = int(info['participant'])
# info['age'] = int(info['age'])
# info['email'] = str(info['email'])

info['expCondition'] = "control"

''' DO NOT EDIT BEGIN '''

# randomly assign colour cue for switching task (blue or white) for each participant
randomColourAssignmentToStimulus = random.choice([{'letter': 'white', 'number': 'blue'}, {'letter': 'blue', 'number': 'white'}]) # randomly assign number/letter to blue/white

# empty lists to append dataframes later on
dataSwitchingAll = pd.DataFrame()
dataSwitchTrainingAll = pd.DataFrame()

info['scriptDate'] = "050318"
info['fixationFrames'] = 30 #frames
#info['postFixationFrames'] = 36 #frames (600ms)
#info['postFixationFrames'] = np.arange(36, 43, 1) #36 frames to 42 frames (600 ms to 700ms)
# post fixation frame number to be drawn from exponential distribution (36 to 42 frames)
f = sp.stats.expon.rvs(size=10000, scale=0.035, loc=0.3) * 100
f = np.around(f)
f = f[f <= 43] # max
f = f[f >= 36] # min
info['postFixationFrames'] = f
info['targetFrames'] = 180 #frames (at 60Hz, 60 frames = 1 second); max time to wait for response
info['blockEndPause'] = 12 #frames
info['feedbackTime'] = 42 #frames
info['startTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #create str of current date/time
info['endTime'] = '' # to be saved later on
# info['ITIDuration'] = np.arange(0.50, 0.81, 0.05) #a numpy array of ITI in seconds (to be randomly selected later for each trial)
seconds = sp.stats.expon.rvs(size=10000, scale=0.4) # exponential distribution
seconds = np.around(seconds/0.05) * 0.05 # round to nearest 0.05
seconds = seconds[seconds <= 0.9] # max
seconds = seconds[seconds >= 0.4] # min
info['ITIDuration'] = seconds

globalClock = core.Clock() # create and start global clock to track OVERALL elapsed time
ISI = core.StaticPeriod(screenHz = 60) # function for setting inter-trial interval later

# create window to draw stimuli on
win = visual.Window(size = (900, 600), fullscr = fullscreen, units = 'norm', monitor = monitor, colorSpace = 'rgb', color = (-1, -1, -1))
#create mouse
mouse = event.Mouse(visible = False, win = win)
mouse.setVisible(0) # make mouse invisible

try:
    feedbackTwinkle = sound.Sound(stimulusDir + 'twinkle.wav')
    feedbackTwinkle.setVolume(0.1)
except:
    pass

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

def runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='', trials=10, feedback=False, saveData=True, practiceTrials=10, switchProportion=0.3, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=3, feedbackSound=False, pauseAfterMissingNTrials=None):
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

    global dataSwitchingAll

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], taskName)
    filenamebackup = "{:03d}-{}-{}-backup.csv".format(int(info['participant']), info['startTime'], taskName) # saved after each block

    mouse.setVisible(0) #make mouse invisible

    # Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True

    trialsDf = pd.DataFrame(index=np.arange(trials)) # create empty dataframe to store trial info

    # store info in dataframe
    trialsDf['participant'] = int(info['participant'])
    try:
        trialsDf['age'] = int(info['age'])
        trialsDf['gender'] = info['gender']
        trialsDf['handedness'] = info['handedness']
        trialsDf['ethnicity'] = info['ethnicity']
        trialsDf['ses'] = info['ses']
    except:
        pass
    trialsDf['scriptDate'] = info['scriptDate']
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
    # trialsDf['expCondition'] = info['expCondition']
    # trialsDf['taskOrder'] = info['taskOrder']

    #create variables to store data later
    trialsDf['blockNumber'] = 0 # add blockNumber
    trialsDf['elapsedTime'] = np.nan
    trialsDf['resp'] = None
    trialsDf['rt'] = np.nan
    trialsDf['iti'] = np.nan
    trialsDf['responseTTL'] = np.nan
    trialsDf['choice'] = np.nan
    trialsDf['overallTrialNum'] = 0 #cannot use np.nan because it's a float, not int!
    trialsDf['acc'] = 0
    trialsDf['creditsEarned'] = 0

    # running accuracy and rt
    runningTallyAcc = []
    runningTallyRt = []
    rewardScheduleTrackerAcc = 0

    '''generate trials for shifting task '''
    letters = ["A", "E", "I", "U", "F", "G", "K", "H"]
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
        randomColourAssignmentToStimulus = random.choice([{'letter': 'white', 'number': 'blue'}, {'letter': 'blue', 'number': 'white'}]) # randomly assign number/letter to blue/white

    # assign blue/white to number/letter
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
            if letternumber[idx][0] in ["A", "E", "U", "O", "I"]:
                correctAnswer.append('vowel')
                correctKey.append('v')
            elif letternumber[idx][0] in ["F", "G", "K", "H"]:
                correctAnswer.append('consonant')
                correctKey.append('c')
        elif questions[idx] == 'number':
            if int(letternumber[idx][1]) in [0, 1, 2, 3, 4]:
                correctAnswer.append('smaller')
                correctKey.append(',')
            elif int(letternumber[idx][1]) in [6, 7, 8, 9]:
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

    #if this is a practice block
    if blockType == 'practice':
        trialsDf = trialsDf[0:practiceTrials] # practice trials to present

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
    fixation = visual.TextStim(win=win, units='norm', height=0.12, ori=0, name='target', text='+', font='Courier New Bold', colorSpace='rgb', color=[-.3, -.3, -.3], opacity=1)

    letternumberStimulus = visual.TextStim(win = win, units = 'norm', height = 0.14, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    cueText = visual.TextStim(win = win, units = 'norm', height = 0.06, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.0, 0.15))

    reminderText = visual.TextStim(win = win, units = 'norm', height = 0.04, ori = 0, name = 'target', text = "c  v  <  >", font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.0, 0.25))

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

        ''' DO NOT EDIT UNLESS YOU KNOW WHAT YOU'RE DOING '''
        # if titrating, determine stuff automatically
        if titrate:
            # determine response duration for this trial
            try:
                allAccuracyList = list(trialsDf.loc[:i-1, "acc"]) # all accuracy in this block in list
                accMean = np.nanmean(allAccuracyList) # mean accuracy in this block

                # print allAccuracyList
                # print 'previous trial acc: ' + str(allAccuracyList[-1])
                # print 'overall acc: ' + str(accMean)
                # print str(allAccuracyList[-1] == 1)

                if allAccuracyList[-1] == 1 and accMean >= 0.8: # if previous trial correctly
                    trialsDf.loc[i, 'targetFrames'] = trialsDf.loc[i-1, 'targetFrames'] - 3 # minus 3 frames (50 ms)
                    # print 'correct and overall acc >= .8, -50ms'
                elif allAccuracyList[-1] == 1 and accMean < 0.8:
                    trialsDf.loc[i, 'targetFrames'] = trialsDf.loc[i-1, 'targetFrames'] + 1 # plus 6 frames (100 ms)
                    # print 'correct but overall acc < .8, +50ms'
                elif allAccuracyList[-1] == 0 and accMean >= 0.8:
                    trialsDf.loc[i, 'targetFrames'] = trialsDf.loc[i-1, 'targetFrames']
                    # print 'wrong, +100ms'
                elif allAccuracyList[-1] == 0 and accMean < 0.8:
                    trialsDf.loc[i, 'targetFrames'] = trialsDf.loc[i-1, 'targetFrames'] + 6 # plus 6 frames (100 ms)
                    # print 'else, +100ms'
                else:
                    trialsDf.loc[i, 'targetFrames'] = trialsDf.loc[i-1, 'targetFrames'] + 1
                # print "this trial frames: "+ str(trialsDf.loc[i, 'targetFrames'])
            except:
                pass

        # determine targetFramesCurrentTrial (used as looping iterator later on)
        try:
            targetFramesCurrentTrial = int(trialsDf.loc[i, 'targetFrames']) # try reading from trialsDf
        except:
            try:
                targetFramesCurrentTrial = int(rtMaxFrames) # try using parameter argument rtMaxFrames
            except:
                try:
                    targetFramesCurrentTrial = int(info['targetFrames']) # try reading from info dictionary
                except:
                    targetFramesCurrentTrial = 180 # if all the above fails, set rt dealine to 180 frames (3 seconds)
        ''' DO NOT EDIT END '''

        #1: draw and show fixation
        # fixation.setAutoDraw(True) #draw fixation on next flips
        # for frameN in range(info['fixationFrames']):
        #     win.flip()
        # fixation.setAutoDraw(False) #stop showing fixation

        # #2: postfixation black screen
        # postFixationBlankFrames = int(random.choice(info['postFixationFrames']))
        # ###print postFixationBlankFrames
        # trialsDf.loc[i, 'postFixationFrames'] = postFixationBlankFrames #store in dataframe
        # for frameN in range(postFixationBlankFrames):
        #     win.flip()

        #3: draw stimulus
        if thisTrial['colourCue'] == 'blue':
            letternumberStimulus.setColor([-1, -1, 1]) # blue
            cueText.setColor([-1, -1, 1]) # blue
        elif thisTrial['colourCue'] == 'white':
            letternumberStimulus.setColor([1, 1, 1]) # white
            cueText.setColor([1, 1, 1]) # white

        letternumberStimulus.setText(thisTrial['letternumber'])
        cueText.setText(thisTrial['question'])

        reminderText.setAutoDraw(True)
        letternumberStimulus.setAutoDraw(True)
        cueText.setAutoDraw(True)

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
                keys = event.getKeys(keyList = ['c', 'v', 'comma', 'period', 'backslash', 'bracketright'])
                if len(keys) > 0 and trialsDf.loc[i, 'resp'] is None: #if a response has been made
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
                    letternumberStimulus.setAutoDraw(False)
                    cueText.setAutoDraw(False)
                    # reminderText.setAutoDraw(False)
                    win.flip() #clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            trialsDf.loc[i, 'acc'] = 0
            trialsDf.loc[i, 'rt'] = np.nan
            letternumberStimulus.setAutoDraw(False)
            cueText.setAutoDraw(False)
            # reminderText.setAutoDraw(False)
            win.flip() #clear screen (remove stuff from screen)

        # append to running accuracy and rt
        runningTallyAcc.append(trialsDf.loc[i, 'acc'])
        runningTallyRt.append(trialsDf.loc[i, 'rt'])

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
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] = None
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) # write header only if index i is 0 AND block is 1 (first block)
                dataSwitchingAll = dataSwitchingAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataSwitchingAll.to_csv(filenamebackup, index=False)
            core.quit() # quit when 'backslash' has been pressed
        elif trialsDf.loc[i, 'resp'] == 'bracketright':#skip to next block
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] == None
            reminderText.setAutoDraw(False)
            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataSwitchingAll = dataSwitchingAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataSwitchingAll.to_csv(filenamebackup, index=False)
            return None

        ''' DO NOT EDIT END '''

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            dataSwitchingAll = dataSwitchingAll.append(trialsDf[i:i+1]).reset_index(drop=True)

        ISI.complete() #end inter-trial interval

        #feedback for trial
        if feedback:
            #stimuli
            accuracyFeedback = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            pointsFeedback = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '+2 cents', height = 0.06, wrapWidth = 1.4, pos = [0.0, 0.1])

            if trialsDf.loc[i, 'acc'] == 1:

                if info['expCondition'] == "training":
                    accuracyFeedback.setText(random.choice(["well done", "great job", "excellent", "amazing", "doing great", "fantastic"]))
                else:
                    accuracyFeedback.setText(random.choice(["correct"]))

                if rewardSchedule is not None:
                    rewardScheduleTrackerAcc += 1 # update tracker
                    if rewardScheduleTrackerAcc == rewardSchedule:
                        rewardScheduleTrackerAcc = 0 # reset to 0
                        trialsDf.loc[i, 'creditsEarned'] = 1
                        if feedbackSound:
                            try:
                                feedbackTwinkle.play()
                            except:
                                pass
                        for frameN in range(info['feedbackTime']):
                            accuracyFeedback.draw()
                            if info['expCondition'] == 'training' and blockType != 'practice':
                                pointsFeedback.draw()
                            win.flip()
                else:
                    trialsDf.loc[i, 'creditsEarned'] = 1
                    if feedbackSound:
                        try:
                            feedbackTwinkle.play()
                        except:
                            pass
                    for frameN in range(info['feedbackTime']):
                        accuracyFeedback.draw()
                        if info['expCondition'] == 'training' and blockType != 'practice':
                            pointsFeedback.draw()
                        win.flip()
            elif trialsDf.loc[i, 'resp'] is None and blockType == 'practice':
                accuracyFeedback.setText('respond faster')
                for frameN in range(info['feedbackTime']):
                    accuracyFeedback.draw()
                    win.flip()
            elif trialsDf.loc[i, 'acc'] == 0 and blockType == 'practice':
                accuracyFeedback.setText('wrong')
                for frameN in range(info['feedbackTime']):
                    accuracyFeedback.draw()
                    win.flip()
            else:
                pass

        # if missed too many trials, pause the task
        if pauseAfterMissingNTrials is not None:
            try:
                if trialsDf.loc[i-(pauseAfterMissingNTrials-1):i, "rt"].isnull().sum() == pauseAfterMissingNTrials: # if the last three trials were NaNs (missed)
                    # print("missed too many trials")
                    reminderText.setAutoDraw(False)
                    letternumberStimulus.setAutoDraw(False)
                    cueText.setAutoDraw(False)
                    showInstructions(text=["Try to respond accurately and quickly."])
                else:
                    pass
            except:
                pass

    reminderText.setAutoDraw(False)

    for frameN in range(info['blockEndPause']):
        win.flip() #wait at the end of the block

    # append data to global dataframe
    dataSwitchingAll.to_csv(filenamebackup, index=False)

    return trialsDf # return dataframe





#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################

''' START EXPERIMENT HERE '''

if sendTTL:
   port.setData(0) # make sure all pins are low before experiment

showInstructions(text=[
" ", # black screen at the beginning
"Welcome to today's experiment!"])

showInstructions(text =
["Next is the letter-number task. You'll see letter-number pairings like U4, C7, or H3, one at a time. You'll be asked to focus on either the letter or the number.",
"For example, when asked to focus on LETTER in the pairing U4, you'll have to indicate whether the letter in it (U) is a consonant or vowel. Press C to indicate consonant, and V for vowel.",
"When asked to focus on the NUMBER in the pairing C7, indicate whether the number (7 in this example) is smaller or greater than 5. If smaller than 5, press the key < (indicating less than 5; right next to letter M). If larger than 5, press the key > (greater than 5; left of ? key).",
"The color (blue or white) of the pairing is an additional cue you can rely on to know whether to focus on the letter or number. So try to rely on the color cues to get better at the task.",
"Let's practice now. Place your two fingers of each hand on C V < > now.",
"If you have any questions during practice, let the research assistant know."
])

# practice
runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='practice', trials=10, feedback=True, saveData=True, practiceTrials=10, switchProportion=0.8, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=False, pauseAfterMissingNTrials=5)

showInstructions(text=["You've just practiced the task. If you have any questions, let the research assistant know.", "If not, you'll start the actual task."])

# actual
runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='actual', trials=300, feedback=True, saveData=True, practiceTrials=10, switchProportion=0.8, titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=False, pauseAfterMissingNTrials=5)

''' experiment end '''
showInstructions(text=["That's the end of the experiment. Thanks so much for participating in our study!"])

if sendTTL:
    port.setData(255) # mark end of experiment

win.close()
core.quit() # quit PsychoPy
