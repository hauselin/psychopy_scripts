# Last modified by Hause Lin 08-02-18 11:18 AM hauselin@gmail.com

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
    # logging.console.setLevel(logging.DEBUG)
    info['participant'] = random.choice([102]) #let 999 = debug participant no.
    info['email'] = 'xxx@gmail.com'
    info['age'] = 18
else: #if DEBUG is not False... (or True)
    fullscreen = True #set full screen
    # logging.console.setLevel(logging.WARNING)
    info['participant'] = '' #dict key to store participant no.
    info['email'] = ''
    info['age'] = ''
    # present dialog to collect info
    dlg = gui.DlgFromDict(info) #create a dialogue box (function gui)
    if not dlg.OK: #if dialogue response is NOT OK, quit
        #moveFiles(dir = 'Data')
        core.quit()

''' DO NOT EDIT BEGIN '''
info['participant'] = int(info['participant'])
info['age'] = int(info['age'])
info['email'] = str(info['email'])

# assign conditions and task order based on participant number
if info['participant'] % 2 == 1: # if odd number, control
    info['expCondition'] = 'control'
    if info['participant'] % 4 == 1:
        info['taskOrder'] = 'update-switch'
    elif info['participant'] % 4 == 3:
        info['taskOrder'] = 'switch-update'
elif info['participant'] % 2 == 0: # if even number, training
    info['expCondition'] = 'training'
    if info['participant'] % 4 == 2:
        info['taskOrder'] = 'update-switch'
    elif info['participant'] % 4 == 0:
        info['taskOrder'] = 'switch-update'

''' DO NOT EDIT BEGIN '''

# randomly assign colour cue for switching task (blue or white) for each participant
randomColourAssignmentToStimulus = random.choice([{'letter': 'white', 'number': 'blue'}, {'letter': 'blue', 'number': 'white'}]) # randomly assign number/letter to blue/white

# empty lists to append dataframes later on
dataStroopAll = pd.DataFrame()
dataSwitchingAll = pd.DataFrame()
dataUpdatingAll = pd.DataFrame()
dataEffortRewardChoiceAll = pd.DataFrame()
dataSwitchTrainingAll = pd.DataFrame()
dataUpdateTrainingAll = pd.DataFrame()

info['scriptDate'] = "080218"
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

if sendTTL:
    port = parallel.ParallelPort(address = parallelPortAddress)
    port.setData(0) #make sure all pins are low





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



def runStroopBlock(taskName='stroop3colours', blockType='', congruentTrials=18, incongruentTrials=6, feedback=False, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=120, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackFrames=60, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, practiceHelp=False):
    '''Run a block of trials.
    blockType: custom name of the block; if blockType is set to 'practice', then no TTLs will be sent and the number of trials to run will be determined by argument supplied to parameter practiceTrials.
    congruentTrials: number of congruent trials to present (ideally multiples of 3)
    incongruentTrials: number of incongruent trials to present (ideally multiples of 6)
    feedback: whether feedback is presented or not
    saveData = whether to save data to csv file
    practiceTrials: no. of practice trials to run
    titrate: whether to adjust difficulty of task based on performance; if set to True, subsequent targetFrames (max response time) for subsequent blocks will be affected
    rtmaxFrames: max rt (in frames); default is None, which takes value from info['targetFrames']; if a value is provided, default will be overwritten
    blockMaxTimeSeconds: end block if overall time of BLOCK (in seconds) has passed
    experimentMaxTimeSeconds: end block if overall time of EXPERIMENT (in seconds) has passed
    feedbackFrames: no. of frames to show feedbackTime
    rewardSchedule: how frequently to show feedback (after 1/2/3 etc. consecutive trials)
    feedbackSound: whether to play feedback twinkle
    pauseAfterMissingNTrials: pause task if missed N responses
    practiceHelp: whether to show what key to press
    '''

    global dataStroopAll

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], taskName) # saved after each trial
    filenamebackup = "{:03d}-{}-{}-backup.csv".format(int(info['participant']), info['startTime'], taskName) # saved after each block

    mouse.setVisible(0) #make mouse invisible

    # Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True

    '''GENERATE TRIALS FOR STROOP TASK'''
    colours = ['red', 'green', 'yellow']
    words = ['red', 'green', 'yellow']
    colourWordCombi = [(c, w) for c in colours for w in words] # all combinations

    stroopCombi = pd.DataFrame(colourWordCombi)
    stroopCombi.columns = ['word', 'colour'] # column names

    # determine congruency
    stroopCombi.loc[stroopCombi['word'] == stroopCombi['colour'], 'congruency'] = 'congruent'
    stroopCombi.loc[stroopCombi['word'] != stroopCombi['colour'], 'congruency'] = 'incongruent'

    # determine correct response
    stroopCombi.loc[stroopCombi['colour'] == 'red', 'correctKey'] = 'r' # or r
    stroopCombi.loc[stroopCombi['colour'] == 'green', 'correctKey'] = 'g' # or g
    stroopCombi.loc[stroopCombi['colour'] == 'yellow', 'correctKey'] = 'y' # or y

    # congruent and incongruent trials
    stroopCon = stroopCombi[stroopCombi.congruency == 'congruent']
    stroopCon = stroopCon.reset_index(drop=True)
    stroopIncon = stroopCombi[stroopCombi.congruency == 'incongruent']
    stroopIncon = stroopIncon.reset_index(drop=True)

    if incongruentTrials == 0: # if all trials are to be congruent trials
        reps = int(np.ceil(float(congruentTrials) / stroopCon.shape[0]))
        trialsInBlock = pd.concat([stroopCon] * reps, ignore_index=True)  # repeat trials
        trialsInBlock = trialsInBlock.sample(n=congruentTrials, replace=False).reset_index(drop=True)  # trials in this block

    elif congruentTrials == 0: # if all trials are to be incongruent trials
        reps = int(np.ceil(float(incongruentTrials) / stroopIncon.shape[0]))
        trialsInBlock = pd.concat([stroopIncon] * reps, ignore_index=True)  # repeat trials
        trialsInBlock = trialsInBlock.sample(n=incongruentTrials, replace=False).reset_index(drop=True)  # trials in this block

    else: # mix of congruent and incongruent trials
        reps = int(np.ceil(float(congruentTrials) / stroopCon.shape[0]))  # no. of reps of congruent trials
        trialsInBlock = pd.concat([stroopCon] * reps, ignore_index=True)  # repeat trials
        trialsInBlockCongruent = trialsInBlock.sample(n=congruentTrials, replace=False).reset_index(drop=True)  # trials in this block

        reps = int(np.ceil(float(incongruentTrials) / stroopIncon.shape[0]))  # no. of reps of incongruent trials
        trialsInBlock = pd.concat([stroopIncon] * reps, ignore_index=True)  # repeat trials
        trialsInBlockIncongruent = trialsInBlock.sample(n=incongruentTrials, replace=False).reset_index(drop=True)  # trials in this block

        trialsInBlock = pd.concat([trialsInBlockCongruent, trialsInBlockIncongruent])

    trialsInBlock = trialsInBlock.reset_index(drop=True)  # reset row index
    trialsInBlock = trialsInBlock.reindex(np.random.permutation(trialsInBlock.index))  # random shuffle trials
    trialsInBlock = trialsInBlock.reset_index(drop=True)  # reset row index

    trialsDf = pd.DataFrame(index=np.arange(trialsInBlock.shape[0])) # create empty dataframe to store trial info

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
    trialsDf['startTime'] = info['startTime']
    trialsDf['endTime'] = info['endTime']
    trialsDf['fixationFrames'] = info['fixationFrames']
    trialsDf['expCondition'] = info['expCondition']
    trialsDf['taskOrder'] = info['taskOrder']

    # store parameter arguments into dataframe
    trialsDf['trialNo'] = range(1, len(trialsDf) + 1) # add trialNo
    trialsDf['blockType'] = blockType # add blockType
    trialsDf['task'] = taskName
    trialsDf['postFixationFrames'] = np.nan
    if rtMaxFrames is not None:
        trialsDf['targetFrames'] = rtMaxFrames

    # create variables to store data later
    trialsDf['blockNumber'] = 0 # add blockNumber
    trialsDf['elapsedTime'] = np.nan
    trialsDf['resp'] = None
    trialsDf['rt'] = np.nan
    trialsDf['iti'] = np.nan
    trialsDf['responseTTL'] = np.nan
    trialsDf['choice'] = np.nan
    trialsDf['overallTrialNum'] = 0 # cannot use np.nan because it's a float, not int!
    trialsDf['acc'] = 0
    trialsDf['creditsEarned'] = 0

    # running accuracy and rt
    runningTallyAcc = []
    runningTallyRt = []
    rewardScheduleTrackerAcc = 0

    trialsDf = pd.concat([trialsDf, trialsInBlock], axis=1)

    #if this is a practice block
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
    fixation = visual.TextStim(win=win, units='norm', height=0.12, ori=0, name='target', text='+', font='Courier New Bold', colorSpace='rgb', color=[-.3, -.3, -.3], opacity=1)

    stroopStimulus = visual.TextStim(win = win, units = 'norm', height = 0.14, ori = 0, name = 'target', text = 'insertStroopWordHere', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    cueText1 = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = 'red:R', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.185, 0.21))

    cueText2 = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = 'green:G', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.0, 0.21))

    cueText3 = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = 'yellow:Y', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.185, 0.21))

    helpText = visual.TextStim(win = win, units = 'norm', height = 0.06, ori = 0, name = 'target', text = 'insertHelpText', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.0, 0.35))

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

        # #1: draw and show fixation
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
        stroopStimulus.setText(thisTrial['word'])
        stroopStimulus.setColor(thisTrial['colour'])
        stroopStimulus.setAutoDraw(True)

        cueText1.setColor('white')
        cueText2.setColor('white')
        cueText3.setColor('white')

        # if only 1 incongruent trial, highlight/colour answer
        try:
            if incongruentTrials == 1 and thisTrial['colour'] == 'red':
                cueText1.setColor('red') # make cue red
            elif incongruentTrials == 1 and thisTrial['colour']== 'green':
                cueText2.setColor('green') # make cue green
            elif incongruentTrials == 1 and thisTrial['colour'] == 'yellow':
                cueText3.setColor('yellow') # make cue yellow
            else:
                cueText1.setColor('white')
                cueText2.setColor('white')
                cueText3.setColor('white')
        except:
            cueText1.setColor('white')
            cueText2.setColor('white')
            cueText3.setColor('white')

        cueText1.setAutoDraw(True) # draw all
        cueText2.setAutoDraw(True) # draw all
        cueText3.setAutoDraw(True) # draw all

        if practiceHelp:
            helpText.setText("Press {}".format(thisTrial['correctKey'].upper()))
            helpText.setAutoDraw(True)

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
                keys = event.getKeys(keyList = ['r', 'g', 'y', 'backslash', 'bracketright'])
                if len(keys) > 0 and trialsDf.loc[i, 'resp'] is None: #if a response has been made
                    trialsDf.loc[i, 'rt'] = respClock.getTime() #store RT
                    trialsDf.loc[i, 'resp'] = keys[0] #store response in pd df

                    if keys[0] == 'r' and thisTrial['correctKey'] == 'r':
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1
                    elif keys[0] == 'g' and thisTrial['correctKey'] == 'g':
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1
                    elif keys[0] == 'y' and thisTrial['correctKey'] == 'y':
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
                    stroopStimulus.setAutoDraw(False); helpText.setAutoDraw(False)
                    # cueText1.setAutoDraw(False)
                    # cueText2.setAutoDraw(False)
                    # cueText3.setAutoDraw(False)
                    win.flip() #clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            trialsDf.loc[i, 'acc'] = 0 # change according for each experiment (0 or np.nan)
            trialsDf.loc[i, 'rt'] = np.nan
            stroopStimulus.setAutoDraw(False)
            helpText.setAutoDraw(False)
            # cueText1.setAutoDraw(False); cueText2.setAutoDraw(False); cueText3.setAutoDraw(False)
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
        # if any special keys pressed
        if trialsDf.loc[i, 'resp'] == 'backslash':
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] = None
            if saveData: #if saveData argument is True, then APPEND current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataStroopAll = dataStroopAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataStroopAll.to_csv(filenamebackup, index=False)
            core.quit()
        elif trialsDf.loc[i, 'resp'] == 'bracketright':# skip to next block
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] == None
            cueText1.setAutoDraw(False)
            cueText2.setAutoDraw(False)
            cueText3.setAutoDraw(False)
            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataStroopAll = dataStroopAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataStroopAll.to_csv(filenamebackup, index=False)
            return None

        ''' DO NOT EDIT END '''

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            dataStroopAll = dataStroopAll.append(trialsDf[i:i+1]).reset_index(drop=True)

        ISI.complete() #end inter-trial interval

        # feedback for trial
        if feedback:
            #stimuli
            accuracyFeedback = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'acc'] == 1: # if correct on this trial

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
                            win.flip()
                else: # reward on every trial

                    trialsDf.loc[i, 'creditsEarned'] = 1
                    if feedbackSound:
                        try:
                            feedbackTwinkle.play()
                        except:
                            pass
                    for frameN in range(info['feedbackTime']):
                        accuracyFeedback.draw()
                        win.flip()
            elif trialsDf.loc[i, 'resp'] is None and blockType == 'practice':
                accuracyFeedback.setText('respond faster')
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            elif trialsDf.loc[i, 'acc'] == 0 and blockType == 'practice':
                accuracyFeedback.setText('wrong')
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            else:
                pass

        # if missed too many trials, pause the task
        if pauseAfterMissingNTrials is not None:
            try:
                if trialsDf.loc[i-(pauseAfterMissingNTrials-1):i, "rt"].isnull().sum() == pauseAfterMissingNTrials: # if the last three trials were NaNs (missed)
                    # print("missed too many trials")
                    cueText1.setAutoDraw(False)
                    cueText2.setAutoDraw(False)
                    cueText3.setAutoDraw(False)
                    helpText.setAutoDraw(False)
                    showInstructions(text=["Try to respond accurately and quickly."])
                else:
                    pass
            except:
                pass

    cueText1.setAutoDraw(False)
    cueText2.setAutoDraw(False)
    cueText3.setAutoDraw(False)
    helpText.setAutoDraw(False)

    # end of block
    for frameN in range(30):
        win.flip() #wait at the end of the block

    # append data to global dataframe
    dataStroopAll.to_csv(filenamebackup, index=False)

    return trialsDf # return dataframe



def stroopTask():
    showInstructions(text =
    ["You'll see the words red, green, yellow, presented in red, green, or yellow font. The words will often be presented in a font color that doesn't match the word itself. For example, the word red might be in yellow font.",
    "You'll have to indicate the font colour it is printed in, ignoring the word itself.",
    "Use the keys R, G, Y to indicate red, green, and yellow font colors respectively.",
    "Let's do a few practice trials now. Place your fingers on R G Y."
    ])
    runStroopBlock(taskName='stroop3colours', blockType='practice', congruentTrials=3, incongruentTrials=3, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=1200, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackFrames=60, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, practiceHelp=True)

    showInstructions(text=["Now you'll do a more realistic practice."])
    runStroopBlock(taskName='stroop3colours', blockType='practice', congruentTrials=3, incongruentTrials=3, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=120, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackFrames=60, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, practiceHelp=False)

    showInstructions(text=["Now you'll do the actual task. You won't receive feedback from now on."])
    core.wait(1)
    # outcome measure (180 trials: 120 congruent, 60 incongruent)
    runStroopBlock(taskName='stroop3colours', blockType='actual', congruentTrials=60, incongruentTrials=30, feedback=False, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=120, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackFrames=60, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=3, practiceHelp=False)

    runStroopBlock(taskName='stroop3colours', blockType='actual', congruentTrials=60, incongruentTrials=30, feedback=False, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=120, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackFrames=60, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=3, practiceHelp=False)








stroopTask()
