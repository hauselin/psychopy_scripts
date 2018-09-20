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

info['scriptDate'] = "150218"
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

feedbackTwinkle = sound.Sound(stimulusDir + 'twinkle.wav')
feedbackTwinkle.setVolume(0.1)

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


def runEffortRewardChoiceBlock(taskName='effortRewardChoice', blockType='mixed', reps=1, feedback=False, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[1, 3, 5, 7, 9], effort=[20, 30, 40, 50, 60], jitter=None):
    '''Run a block of trials.
    reps: number of times to repeat each unique trial
    feedback: whether feedback is presented or not
    saveData = whether to save data to csv file
    practiceTrials: no. of practice trials to run
    titrate: whether to adjust difficulty of task based on performance; if set to True, subsequent targetFrames (max response time) for subsequent blocks will be affected
    rtmaxFrames: max rt (in frames); default is None, which takes value from info['targetFrames']; if a value is provided, default will be overwritten
    blockMaxTimeSeconds: end block if overall time of BLOCK (in seconds) has passed
    experimentMaxTimeSeconds: end block if overall time of EXPERIMENT (in seconds) has passed
    '''

    global dataEffortRewardChoiceAll

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], taskName)
    filenamebackup = "{:03d}-{}-{}-backup.csv".format(int(info['participant']), info['startTime'], taskName) # saved after each block

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

    trialsInBlock = pd.concat([rewardEffortCombi] * reps, ignore_index=True)

    trialsInBlock = trialsInBlock.reindex(np.random.permutation(trialsInBlock.index)).reset_index(drop=True) # shuffle

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
    trialsDf['scriptDate'] = info['scriptDate']
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
    trialsDf['expCondition'] = info['expCondition']
    trialsDf['taskOrder'] = info['taskOrder']

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
    trialsDf['acc'] = 0

    trialsDf['accEffortTask'] = np.nan
    trialsDf['rtEffortTask'] = np.nan

    trialsDf = pd.concat([trialsDf, trialsInBlock], axis=1)

    # running accuracy and rt
    runningTallyAcc = []
    runningTallyRt = []
    rewardScheduleTrackerAcc = 0

    # if this is a practice block
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

    constantOptionEffort = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = '1 stroop', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.2, 0.06))

    constantOptionReward = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = '10 credits', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.2, -0.06))

    varyingOptionEffort = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = 'XXX', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.2, 0.06))

    varyingOptionReward = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = 'XXX', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.2, -0.06))

    practiceInstructText = visual.TextStim(win = win, units = 'norm', height = 0.04, ori = 0, name = 'target', text = 'F for left option, J for right option', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, 0.28))

    keyF = visual.TextStim(win = win, units = 'norm', height = 0.05, ori = 0, name = 'target', text = 'F', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.2, 0.19))

    keyJ = visual.TextStim(win = win, units = 'norm', height = 0.05, ori = 0, name = 'target', text = 'J', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.2, 0.19))

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
                else: # (e.g., nan in previous trial)
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
        fixation.setAutoDraw(True) #draw fixation on next flips
        for frameN in range(info['fixationFrames']):
            win.flip()
        fixation.setAutoDraw(False) #stop showing fixation

        # #2: postfixation black screen
        # postFixationBlankFrames = int(random.choice(info['postFixationFrames']))
        # ###print postFixationBlankFrames
        # trialsDf.loc[i, 'postFixationFrames'] = postFixationBlankFrames #store in dataframe
        # for frameN in range(postFixationBlankFrames):
        #     win.flip()

        #3: draw stimulus
        #varyingOptionEffort.setText("{} trials".format(thisTrial['effort']))
        #varyingOptionReward.setText("${:.2f}".format(thisTrial['rewardJittered']))
        varyingOptionEffort.setText("{} stroop".format(thisTrial['effort']))
        varyingOptionReward.setText("{} credits".format(thisTrial['rewardJittered']))

        constantOptionEffort.setAutoDraw(True)
        constantOptionReward.setAutoDraw(True)
        varyingOptionEffort.setAutoDraw(True)
        varyingOptionReward.setAutoDraw(True)

        keyF.setAutoDraw(True)
        keyJ.setAutoDraw(True)

        if blockType == 'practice':
            practiceInstructText.setAutoDraw(True)

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
                        trialsDf.loc[i, 'acc'] = 0
                    elif keysCollected[0] == 'j':
                        if sendTTL and not blockType == 'practice':
                            port.setData(16) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 16
                        trialsDf.loc[i, 'choiceText'] = 'effortful'
                        trialsDf.loc[i, 'acc'] = 1
                    else:
                        if sendTTL and not blockType == 'practice':
                            port.setData(17) #incorrect response
                        trialsDf.loc[i, 'responseTTL'] = 17
                        trialsDf.loc[i, 'choiceText'] = ''
                        trialsDf.loc[i, 'acc'] = np.nan
                        trialsDf.loc[i, 'rt'] = np.nan
                    #remove stimulus from screen
                    constantOptionEffort.setAutoDraw(False)
                    constantOptionReward.setAutoDraw(False)
                    varyingOptionEffort.setAutoDraw(False)
                    varyingOptionReward.setAutoDraw(False)
                    practiceInstructText.setAutoDraw(False)
                    keyF.setAutoDraw(False)
                    keyJ.setAutoDraw(False)
                    win.flip() #clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            trialsDf.loc[i, 'acc'] = 0
            trialsDf.loc[i, 'rt'] = np.nan
            constantOptionEffort.setAutoDraw(False)
            constantOptionReward.setAutoDraw(False)
            varyingOptionEffort.setAutoDraw(False)
            varyingOptionReward.setAutoDraw(False)
            practiceInstructText.setAutoDraw(False)
            keyF.setAutoDraw(False)
            keyJ.setAutoDraw(False)
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

        ### print "TRIAL OK TRIAL %d OVERALL TRIAL %d" %(i + 1, int(trialsDf.loc[i, 'overallTrialNum']))

        ''' DO NOT EDIT BEGIN '''
        #if press 0 (quit script) or 7 (skip block)
        if trialsDf.loc[i, 'resp'] == 'backslash':
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] = None
            if saveData: #if saveData argument is True, then APPEND current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataEffortRewardChoiceAll = dataEffortRewardChoiceAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataEffortRewardChoiceAll.to_csv(filenamebackup, index=False)
            core.quit() #quit when 'backslash' has been pressed
        elif trialsDf.loc[i, 'resp'] == 'bracketright':#if press 7, skip to next block
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'resp'] == None
            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataEffortRewardChoiceAll = dataEffortRewardChoiceAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataEffortRewardChoiceAll.to_csv(filenamebackup, index=False)
            return None

        ''' DO NOT EDIT END '''

        ISI.complete() #end inter-trial interval

        # feedback for trial
        if feedback:
            # initialize stimuli
            feedbackText1 = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'choiceText'] == 'baseline':
                feedbackText1.setText('1 stroop')
            elif trialsDf.loc[i, 'choiceText'] == 'effortful':
                feedbackText1.setText("{} stroop".format(thisTrial['effort']))
            elif trialsDf.loc[i, 'choiceText'] == '':
                feedbackText1.setText('respond faster')
            else:
                feedbackText1.setText('')

            for frameN in range(60):
                feedbackText1.draw()
                win.flip()

        ''' run effortful task block '''
        if trialsDf.loc[i, 'resp'] is not None:
            # run mental math updating trial
            if trialsDf.loc[i, 'choiceText'] == 'baseline':

                taskDf = runStroopBlock(taskName='stroop3coloursChoiceTask', blockType=trialsDf.loc[i, 'overallTrialNum'], congruentTrials=0, incongruentTrials=1, feedback=False, saveData=True, practiceTrials=0, titrate=False, rtMaxFrames=90, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackFrames=60, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=3, practiceHelp=False)

            elif trialsDf.loc[i, 'choiceText'] == 'effortful':

                taskDf = runStroopBlock(taskName='stroop3coloursChoiceTask', blockType=trialsDf.loc[i, 'overallTrialNum'], congruentTrials=0, incongruentTrials=trialsDf.loc[i, 'effort'], feedback=False, saveData=True, practiceTrials=0, titrate=False, rtMaxFrames=90, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackFrames=60, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=3, practiceHelp=False)
            else:
                pass

        # compute accuracy and rt of task
        try:
            nTrials = taskDf.shape[0]
            if sum(taskDf['acc'].isnull()) == nTrials: # if no. of NaN equals no.of rows (if all 'acc' are )
                taskAcc = np.nan
                taskRt = np.nan
            else:
                taskAcc = np.nanmean(taskDf.loc[:, 'acc'])
                taskRt = np.nanmean(taskDf.loc[:, 'rt']) # will show warning if everything's NA
        except:
            taskAcc = np.nan
            taskRt = np.nan

        # print nTrials
        # print taskAcc
        # print taskRt

        taskDf = pd.DataFrame() # empty dataframe for next trial

        ''' end effortful task'''

        trialsDf.loc[i, 'accEffortTask'] = taskAcc
        trialsDf.loc[i, 'rtEffortTask'] = taskRt

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            dataEffortRewardChoiceAll = dataEffortRewardChoiceAll.append(trialsDf[i:i+1]).reset_index(drop=True)

        # feedback for task performance
        if feedback and trialsDf.loc[i, 'resp'] is not None:

            feedbackText1 = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'accEffortTask'] == 1: # if correct
                if trialsDf.loc[i, 'choiceText'] == 'effortful':
                    feedbackText1.setText('100% correct, {} credits'.format(thisTrial['rewardJittered']))
                else:
                    feedbackText1.setText('100% correct, 10 credits')
            elif trialsDf.loc[i, 'accEffortTask'] < 1: # if correct
                if np.isnan(taskAcc): # if NaN, convert to 0
                    accI = 0
                if trialsDf.loc[i, 'choiceText'] == 'effortful':
                    feedbackText1.setText("{:.0f}% correct, {} credits".format(taskAcc * 100, thisTrial['rewardJittered']))
                else:
                    feedbackText1.setText("{:.0f}% correct, 10 credits".format(taskAcc * 100))
            else:
                feedbackText1.setText("0% correct, 10 credits")

            for frameN in range(60):
                feedbackText1.draw()
                win.flip()

    # end of block pause
    for frameN in range(info['blockEndPause']):
        win.flip() #wait at the end of the block

    # append data to global dataframe
    dataEffortRewardChoiceAll.to_csv(filenamebackup, index=False)



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

def runMentalMathBlock(taskName='mentalMathUpdating', blockType='', trials=1, feedback=False, saveData=True, practiceTrials=10, digits=4, digitChange=[3], digitsToModify=2, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=3, feedbackSound=False, pauseAfterMissingNTrials=None):
    '''Run a block of trials.
    blockType: custom name of the block; if blockType is set to 'practice', then no TTLs will be sent and the number of trials to run will be determined by argument supplied to parameter practiceTrials.
    trials: number of times to repeat each unique trial
    feedback: whether feedback is presented or not
    saveData = whether to save data to csv file
    practiceTrials: no. of practice trials to run
    digits: number of digits to generate
    digitChange = number to add/subtract to/from each digit as a list
    digitsToModify: number of digits to change when generating wrong (alternative) answer
    titrate: whether to adjust difficulty of task based on performance; if set to True, subsequent targetFrames (max response time) for subsequent blocks will be affected
    rtmaxFrames: max rt (in frames); default is None, which takes value from info['targetFrames']; if a value is provided, default will be overwritten
    blockMaxTimeSeconds: end block if overall time of BLOCK (in seconds) has passed
    experimentMaxTimeSeconds: end block if overall time of EXPERIMENT (in seconds) has passed
    '''

    global dataUpdatingAll

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], taskName)
    filenamebackup = "{:03d}-{}-{}-backup.csv".format(int(info['participant']), info['startTime'], taskName) # saved after each block

    '''DO NOT EDIT BEGIN'''
    mouse.setVisible(0) #make mouse invisible

    # Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True

    trialsDf = pd.DataFrame(index=np.arange(trials)) # create empty dataframe to store trial info

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
    trialsDf['expCondition'] = info['expCondition']
    trialsDf['taskOrder'] = info['taskOrder']

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
    trialsDf['digitsToModify'] = digitsToModify
    trialsDf['testDigits'] = None
    trialsDf['correctAnswer'] = None
    trialsDf['wrongAnswer1'] = None
    trialsDf['wrongAnswer2'] = None
    trialsDf['wrongAnswer3'] = None
    trialsDf['correctKey'] = None
    trialsDf['acc'] = 0
    trialsDf['creditsEarned'] = 0

    # running accuracy and rt
    runningTallyAcc = []
    runningTallyRt = []
    rewardScheduleTrackerAcc = 0

    ''' define number sequence and correct/incorrect responses for block '''
    # timing for updating task
    testDigitFrames = 30 # frames to show each test digit
    postTestDigitBlankFrames = 45 # blank frames after each digit
    postAllTestDigitBlankFrames = 30 # blank frames after all digits

    trialsDf['testDigitFrames'] = testDigitFrames
    trialsDf['postTestDigitBlankFrames'] = postTestDigitBlankFrames
    trialsDf['postAllTestDigitBlankFrames'] = postAllTestDigitBlankFrames

    # populate dataframe with test number sequences and answers
    for rowI in range(0, trialsDf.shape[0]): # for each trial
        digitsList = random.sample(range(0, 10), digits) # randomly generate digits in given range without replacement
        digitToAddOrSubtract = random.choice(digitChange) # if digitChange is 3, it will be add 2, 3, or 4
        digitsListAnswer = []
        for digitI in digitsList: # determine correct answer
            # print "old digit is {0}".format(digitI)
            digitNew = digitI + digitToAddOrSubtract # update digit
            digitNew = int(str(digitNew)[-1]) # take last digit
            digitsListAnswer.append(digitNew)

        correctAnswer = ''.join(str(x) for x in digitsListAnswer) # as 1 string

        digitsModifyIdxList = []
        for d in range(5):
            shuffleIndices = range(0, digits)
            random.shuffle(shuffleIndices)
            digitsModifyIdxList += shuffleIndices
        digitsModifyIdxList

        wrongAnswer = digitsListAnswer[:] # create a copy of the correct answer to modify later on
        wrongAnswerList = []

        for modifyDigitI in digitsModifyIdxList: # for each wrong answer (the index to change)
            # print modifyDigitI
            tempWrongAnswer = wrongAnswer[:]
            if wrongAnswer[modifyDigitI] in [1, 2, 3, 4, 5, 6, 7, 8]:
                tempWrongAnswer[modifyDigitI] += random.choice([-1, 1])
            elif wrongAnswer[modifyDigitI] == 9:
                tempWrongAnswer[modifyDigitI] -= random.choice([1, 2])
            elif wrongAnswer[modifyDigitI] == 0:
                tempWrongAnswer[modifyDigitI] += random.choice([1, 2])
            tempWrongAnswer = ''.join(str(x) for x in tempWrongAnswer) # as 1 string
            wrongAnswerList.append(tempWrongAnswer)

        # store in dataframe
        trialsDf.loc[rowI, 'testDigits'] = ''.join(str(x) for x in digitsList)
        trialsDf.loc[rowI, 'correctAnswer'] = correctAnswer
        trialsDf.loc[rowI, 'wrongAnswer1'] = wrongAnswerList[0]
        trialsDf.loc[rowI, 'wrongAnswer2'] = wrongAnswerList[1]
        trialsDf.loc[rowI, 'wrongAnswer3'] = wrongAnswerList[2]
        trialsDf.loc[rowI, 'correctKey'] = random.choice(['f', 'j', 'd', 'k'])
        trialsDf.loc[rowI, 'digitChange'] = digitToAddOrSubtract

    #if this is a practice block
    if blockType == 'practice':
        trialsDf = trialsDf[0:practiceTrials] #number of practice trials to present

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
    fixation = visual.TextStim(win=win, units='norm', height=0.12, ori=0, name='target', text='+', font='Courier New Bold', colorSpace='rgb', color=[-.3, -.3, -.3], opacity=1)

    reminderText = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = "", font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, 0.17))

    testDigit = visual.TextStim(win = win, units = 'norm', height = 0.20, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    correctDigits = visual.TextStim(win = win, units = 'norm', height = 0.075, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    wrongDigits1 = visual.TextStim(win = win, units = 'norm', height = 0.075, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    wrongDigits2 = visual.TextStim(win = win, units = 'norm', height = 0.075, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    wrongDigits3 = visual.TextStim(win = win, units = 'norm', height = 0.075, ori = 0, name = 'target', text = '0000', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1)

    keyD = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = 'D', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.3, 0.1))

    keyF = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = 'F', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.1, 0.1))

    keyJ = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = 'J', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.1, 0.1))

    keyK = visual.TextStim(win = win, units = 'norm', height = 0.045, ori = 0, name = 'target', text = 'K', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.3, 0.1))

    #create clocks to collect reaction and trial times
    respClock = core.Clock()
    trialClock = core.Clock()

    for i, thisTrialMath in trialsDf.iterrows(): #for each trial...
        ''' DO NOT EDIT BEGIN '''
        #add overall trial number to dataframe
        try: #try reading csv file dimensions (rows = no. of trials)
            #thisTrialMath['overallTrialNum'] = pd.read_csv(filename).shape[0] + 1
            trialsDf.loc[i, 'overallTrialNum'] = pd.read_csv(filename).shape[0] + 1
            ####print 'Overall Trial No: %d' %thisTrialMath['overallTrialNum']
        except: #if fail to read csv, then it's trial 1
            #thisTrialMath['overallTrialNum'] = 1
            trialsDf.loc[i, 'overallTrialNum'] = 1
            ####print 'Overall Trial No: %d' %thisTrialMath['overallTrialNum']

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

                if allAccuracyList[-1] == 1 and accMean >= 0.8: # if previous trial correctly
                    trialsDf.loc[i, 'targetFrames'] = trialsDf.loc[i-1, 'targetFrames'] - 3 # minus 3 frames (50 ms)
                    trialsDf.loc[i, 'postTestDigitBlankFrames'] = trialsDf.loc[i-1, 'postTestDigitBlankFrames'] - 2
                    # print 'correct and overall acc >= .8, -50ms'
                elif allAccuracyList[-1] == 1 and accMean < 0.8:
                    trialsDf.loc[i, 'targetFrames'] = trialsDf.loc[i-1, 'targetFrames'] + 1 # plus 6 frames (100 ms)
                    trialsDf.loc[i, 'postTestDigitBlankFrames'] = trialsDf.loc[i-1, 'postTestDigitBlankFrames'] + 1
                    # print 'correct but overall acc < .8, +50ms'
                elif allAccuracyList[-1] == 0 and accMean >= 0.8:
                    trialsDf.loc[i, 'targetFrames'] = trialsDf.loc[i-1, 'targetFrames'] # plus 6 frames (100 ms)
                    trialsDf.loc[i, 'postTestDigitBlankFrames'] = trialsDf.loc[i-1, 'postTestDigitBlankFrames']
                    # print 'wrong, +100ms'
                elif allAccuracyList[-1] == 0 and accMean < 0.8:
                    trialsDf.loc[i, 'targetFrames'] = trialsDf.loc[i-1, 'targetFrames'] + 6 # plus
                    trialsDf.loc[i, 'postTestDigitBlankFrames'] = trialsDf.loc[i-1, 'postTestDigitBlankFrames'] + 2

                else:
                    trialsDf.loc[i, 'targetFrames'] = trialsDf.loc[i-1, 'targetFrames'] + 1
                    trialsDf.loc[i, 'postTestDigitBlankFrames'] = trialsDf.loc[i-1, 'postTestDigitBlankFrames'] + 1
                    # print 'else, +100ms'
                # print "this trial frames: " + str(trialsDf.loc[i, 'targetFrames'])
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

        reminderText.setText("+{:.0f}".format(thisTrialMath['digitChange']))
        reminderText.setAutoDraw(True)

        #3: draw stimulus (digits) one by one
        for d in thisTrialMath['testDigits']:
            testDigit.setText(d)
            testDigit.setAutoDraw(True)
            for frameN in range(testDigitFrames):
                win.flip()
            testDigit.setAutoDraw(False)
            # blank screen for a while before next digit (titrated)
            for frameN in range(int(trialsDf.loc[i, 'postTestDigitBlankFrames'])):
                win.flip()

        reminderText.setAutoDraw(False)

        for frameN in range(postAllTestDigitBlankFrames):
            win.flip()

        #4: draw response options
        correctDigits.setText(thisTrialMath['correctAnswer'])
        wrongDigits1.setText(thisTrialMath['wrongAnswer1'])
        wrongDigits2.setText(thisTrialMath['wrongAnswer2'])
        wrongDigits3.setText(thisTrialMath['wrongAnswer3'])

        # set option positions
        if thisTrialMath['correctKey'] == "d":
            correctDigits.setPos((-0.30, 0.0))
            wrongDigits1.setPos((-0.10, 0.0))
            wrongDigits2.setPos((0.10, 0.0))
            wrongDigits3.setPos((0.30, 0.0))
        elif thisTrialMath['correctKey'] == "f":
            correctDigits.setPos((-0.10, 0.0))
            wrongDigits1.setPos((-0.30, 0.0))
            wrongDigits2.setPos((0.10, 0.0))
            wrongDigits3.setPos((0.30, 0.0))
        elif thisTrialMath['correctKey'] == "j":
            correctDigits.setPos((0.10, 0.0))
            wrongDigits1.setPos((-0.30, 0.0))
            wrongDigits2.setPos((-0.10, 0.0))
            wrongDigits3.setPos((0.30, 0.0))
        elif thisTrialMath['correctKey'] == "k":
            correctDigits.setPos((0.30, 0.0))
            wrongDigits1.setPos((-0.30, 0.0))
            wrongDigits2.setPos((-0.10, 0.0))
            wrongDigits3.setPos((0.10, 0.0))

        correctDigits.setAutoDraw(True)
        wrongDigits1.setAutoDraw(True)
        wrongDigits2.setAutoDraw(True)
        wrongDigits3.setAutoDraw(True)
        keyD.setAutoDraw(True)
        keyF.setAutoDraw(True)
        keyJ.setAutoDraw(True)
        keyK.setAutoDraw(True)

        win.callOnFlip(respClock.reset) #reset response clock on next flip
        win.callOnFlip(trialClock.reset) #reset trial clock on next flip

        event.clearEvents() #clear events

        for frameN in range(targetFramesCurrentTrial):
            if frameN == 0: #on first frame/flip/refresh
                if sendTTL and not blockType == 'practice':
                    win.callOnFlip(port.setData, int(thisTrialMath['TTLStim']))
                else:
                    pass
                ##print "First frame in Block %d Trial %d OverallTrialNum %d" %(blockNumber, i + 1, trialsDf.loc[i, 'overallTrialNum'])
                ##print "Stimulus TTL: %d" %(int(thisTrialMath['TTLStim']))
            else:
                keys = event.getKeys(keyList = ['d', 'k', 'f', 'j', 'backslash', 'bracketright'])
                if len(keys) > 0 and trialsDf.loc[i, 'resp'] is None: #if a response has been made
                    trialsDf.loc[i, 'rt'] = respClock.getTime() #store RT
                    trialsDf.loc[i, 'resp'] = keys[0] #store response in pd df

                    if keys[0] == 'f' and thisTrialMath['correctKey'] == 'f': #if go trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) #correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1

                    elif keys[0] == 'j' and thisTrialMath['correctKey'] == 'j': #if go trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) #correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1

                    elif keys[0] == 'd' and thisTrialMath['correctKey'] == 'd': #if go trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) #correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1

                    elif keys[0] == 'k' and thisTrialMath['correctKey'] == 'k': #if go trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(15) #correct response
                        trialsDf.loc[i, 'responseTTL'] = 15
                        trialsDf.loc[i, 'acc'] = 1

                    else: #if nogo trial and keypress
                        if sendTTL and not blockType == 'practice':
                            port.setData(16) #incorrect response
                        trialsDf.loc[i, 'responseTTL'] = 16
                        trialsDf.loc[i, 'acc'] = 0

                    #remove stimulus from screen
                    correctDigits.setAutoDraw(False)
                    wrongDigits1.setAutoDraw(False)
                    wrongDigits2.setAutoDraw(False)
                    wrongDigits3.setAutoDraw(False)
                    keyD.setAutoDraw(False)
                    keyF.setAutoDraw(False)
                    keyJ.setAutoDraw(False)
                    keyK.setAutoDraw(False)
                    win.flip() # clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            trialsDf.loc[i, 'acc'] = 0
            trialsDf.loc[i, 'rt'] = np.nan
            correctDigits.setAutoDraw(False)
            wrongDigits1.setAutoDraw(False)
            wrongDigits2.setAutoDraw(False)
            wrongDigits3.setAutoDraw(False)
            keyD.setAutoDraw(False)
            keyF.setAutoDraw(False)
            keyJ.setAutoDraw(False)
            keyK.setAutoDraw(False)
            win.flip() #clear screen (remove stuff from screen)

        # append to running accuracy and rt
        runningTallyAcc.append(trialsDf.loc[i, 'acc'])
        runningTallyRt.append(trialsDf.loc[i, 'rt'])

        # if both response options are the same, then accuracy is always correct

        if sendTTL and not blockType == 'practice':
            port.setData(0) #parallel port: set all pins to low

        trialsDf.loc[i, 'elapsedTime'] = globalClock.getTime() #store total elapsed time in seconds
        trialsDf.loc[i, 'endTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #store current time
        iti = round(random.choice(info['ITIDuration']), 2) #randomly select an ITI duration
        trialsDf.loc[i, 'iti'] = iti #store ITI duration

        # start inter-trial interval...
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
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataUpdatingAll = dataUpdatingAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataUpdatingAll.to_csv(filenamebackup, index=False)
            core.quit() #quit when 'backslash' has been pressed
        elif trialsDf.loc[i, 'resp'] == 'bracketright':# skip to next block
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] == None

            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataUpdatingAll = dataUpdatingAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataUpdatingAll.to_csv(filenamebackup, index=False)
            return None

        ''' DO NOT EDIT END '''

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            # append data to global dataframe
            dataUpdatingAll = dataUpdatingAll.append(trialsDf[i:i+1]).reset_index(drop=True)

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
                    showInstructions(text=["Try to respond accurately and quickly."])
                else:
                    pass
            except:
                pass

        for frameN in range(45): # brief pause after trial
            win.flip()

    # save backup data (once per block)
    dataUpdatingAll.to_csv(filenamebackup, index=False)

    return trialsDf # return dataframe


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
    trialsDf['expCondition'] = info['expCondition']
    trialsDf['taskOrder'] = info['taskOrder']

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
    trialsDf['scriptDate'] = info['scriptDate']
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
    trialsDf['expCondition'] = info['expCondition']
    trialsDf['taskOrder'] = info['taskOrder']

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
    questionText = visual.TextStim(win = win, units = 'norm', height = 0.06, name = 'target', text = 'INSERT QUESTION HERE', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, 0.2))

    # scale points
    spacesBetweenTicks = 3
    xScaleTicks = np.arange(scaleAnchors[0], scaleAnchors[1]+1)
    scaleAnchorPoints = ''
    spaces = ' '
    for tickI in xScaleTicks:
        scaleAnchorPoints = scaleAnchorPoints + spacesBetweenTicks * spaces + str(tickI) + spacesBetweenTicks * spaces

    scaleAnchorPoints = scaleAnchorPoints[spacesBetweenTicks:-spacesBetweenTicks]

    # scale left anchor text
    scaleAnchorTextLeftText = visual.TextStim(win = win, units = 'norm', height = 0.035, name = scaleAnchorText[0], text = scaleAnchorPoints, font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.6, -0.2))

    # scale right anchor text
    scaleAnchorTextRightText = visual.TextStim(win = win, units = 'norm', height = 0.035, name = scaleAnchorText[1], text = scaleAnchorPoints, font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.6, -0.2))

    # scale points
    scaleAnchorPointsText = visual.TextStim(win = win, units = 'norm', height = 0.045, name = 'target', text = scaleAnchorPoints, font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, -0.2))

    # tell participants to use keyboard to respond
    instructText = visual.TextStim(win = win, units = 'norm', height = 0.03, name = 'target', text = 'use numbers on the top row of keyboard', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, -0.3))

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
            scaleAnchorTextLeftText.setText(scaleAnchorText[0])
            scaleAnchorTextLeftText.setAutoDraw(True)
            scaleAnchorTextRightText.setText(scaleAnchorText[1])
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
                    # instructText.setAutoDraw(False)
                    # scaleAnchorPointsText.setAutoDraw(False)
                    # scaleAnchorTextLeftText.setAutoDraw(False)
                    # scaleAnchorTextRightText.setAutoDraw(False)
                    win.flip() # clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        # if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            questionText.setAutoDraw(False)
            questionText.setAutoDraw(False)
            # instructText.setAutoDraw(False)
            # scaleAnchorPointsText.setAutoDraw(False)
            # scaleAnchorTextLeftText.setAutoDraw(False)
            # scaleAnchorTextRightText.setAutoDraw(False)
            win.flip() #clear screen (remove stuff from screen)

        trialsDf.loc[i, 'elapsedTime'] = globalClock.getTime() #store total elapsed time in seconds
        trialsDf.loc[i, 'endTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #store current time
        iti = round(random.choice([0.2, 0.3, 0.4]), 2) #randomly select an ITI duration
        trialsDf.loc[i, 'iti'] = iti #store ITI duration

        # start inter-trial interval...
        ISI.start(iti)

        ''' DO NOT EDIT BEGIN '''
        #if press 0 (quit script) or 7 (skip block)
        if trialsDf.loc[i, 'resp'] == 'backslash':
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] = None
            instructText.setAutoDraw(False)
            scaleAnchorPointsText.setAutoDraw(False)
            scaleAnchorTextLeftText.setAutoDraw(False)
            scaleAnchorTextRightText.setAutoDraw(False)
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            #moveFiles(dir = 'Data')
            core.quit() #quit when 'backslash' has been pressed
        elif trialsDf.loc[i, 'resp'] == 'bracketright':#if press 7, skip to next block
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] == None
            instructText.setAutoDraw(False)
            scaleAnchorPointsText.setAutoDraw(False)
            scaleAnchorTextLeftText.setAutoDraw(False)
            scaleAnchorTextRightText.setAutoDraw(False)
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            return None

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
        ''' DO NOT EDIT END '''

        ISI.complete() #end inter-trial interval

    instructText.setAutoDraw(False)
    scaleAnchorPointsText.setAutoDraw(False)
    scaleAnchorTextLeftText.setAutoDraw(False)
    scaleAnchorTextRightText.setAutoDraw(False)

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
    questionsDf['expCondition'] = info['expCondition']
    try:
        questionsDf['age'] = int(info['age'])
        questionsDf['gender'] = info['gender']
        questionsDf['handedness'] = info['handedness']
        questionsDf['ethnicity'] = info['ethnicity']
        questionsDf['ses'] = info['ses']
    except:
        pass
    questionsDf['scriptDate'] = info['scriptDate']
    questionsDf['totalItems'] = len(questionsDf)
    # print len(questionsDf)
    questionsDf['overallQNo'] = 0
    questionsDf['rating'] = '' #new variable/column to store response
    questionsDf['rt'] = '' #new variable to store response RT

    # create rating scale for this questionnaire
    # tickMarks = range(scaleMin, scaleMax + 1)
    if scaleMin > -10 and scaleMax < 10:
        increaseScaleResolution = True
        scaleMinFiner = scaleMin * 10
        scaleMaxFiner = scaleMax * 10
    else:
        scaleMinFiner = scaleMin
        scaleMaxFiner = scaleMax

    scale = visual.RatingScale(win, low=scaleMinFiner, high=scaleMaxFiner, mouseOnly = True, singleClick = True, stretch = 2, marker = 'slider', showAccept = False, pos = (0, -0.5), showValue = True, textSize = 0.7, textFont = 'Verdana', markerColor = "red", scale=scaleDescription, labels=[str(scaleMin) + ": " + scaleLeftRightAnchorText[0], str(scaleMax) + ": " + scaleLeftRightAnchorText[1]], tickMarks=[scaleMinFiner, scaleMaxFiner])

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
        if increaseScaleResolution:
            questionsDf.loc[i, 'rating'] = float(scale.getRating()) / float(10) #store rating
        else:
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

    # grit
    showInstructions(text=['For the next few questions, click on the scale to indicate your responses.'])
    # showQuestionnaire(csvFile = 'GritShortVersion.csv', scaleMin = 1, scaleMax = 5, outputName='Questionnaires', scaleLeftRightAnchorText=['not at all like me', 'very much like me'])

    # showQuestionnaire(csvFile = "BasicNeedsCAR.csv", scaleMin = 1, scaleMax = 7, outputName='Questionnaires', scaleLeftRightAnchorText=['not at all true', 'very true'])

    showQuestionnaire(csvFile = "GeneralSelfEfficacy.csv", scaleMin = 1, scaleMax = 4, outputName='Questionnaires', scaleLeftRightAnchorText=['not at all true', 'exactly true'])

    showQuestionnaire(csvFile = "RewardResponsiveness.csv", scaleMin = 1, scaleMax = 4, outputName='Questionnaires', scaleLeftRightAnchorText=['strong disagreement', 'strong agreement'])

    # need for cognition
    showQuestionnaire(csvFile = 'NeedForCognition.csv', scaleMin = -4, scaleMax = 4, outputName='Questionnaires', scaleLeftRightAnchorText=['very strong disagreement', 'very strong agreement'])

    # showQuestionnaire(csvFile = "ImplicitWillpower.csv", scaleMin = 1, scaleMax = 6, outputName='Questionnaires', scaleLeftRightAnchorText=['strongly disagree', 'strongly agree'])

    # showInstructions(text = ["The following questions are exploring people's beliefs about their personal ability to change their intelligence level. There are no right or wrong answers. We are just interested in your views."])
    # showQuestionnaire(csvFile = "ImplicitTheoryIntelligenceDweck.csv", scaleMin = 1, scaleMax = 6, outputName='Questionnaires', scaleLeftRightAnchorText=['strongly disagree', 'strongly agree'])

    # BFAS
    # showInstructions(text = ["Next you will read several characteristics that may or may not describe you. Select the option that best indicates how much you agree or disagree. Be as honest as you can and rely on your initial feeling. Do not think too much about each item."])
    # showQuestionnaire(csvFile = 'BFAS.csv', scaleMin = 1, scaleMax = 5, outputName='Questionnaires', scaleLeftRightAnchorText=['disagree strongly', 'agree strongly'])



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
    trialsDf['scriptDate'] = info['scriptDate']
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

    showInstructions(text = ["Now the computer will determine how many credits and how much money you've earned..."], timeBeforeShowingSpace=2)

    try:
        creditDf = dataEffortRewardChoiceAll.dropna(subset=['accEffortTask', 'reward', 'acc'])
        effortChoiceAcc = np.nanmean(creditDf.accEffortTask)

        creditEarnedBaseline = creditDf.loc[(creditDf.choiceText == 'baseline'), ].shape[0] * 10
        creditEarnedEffortful = int(creditDf.loc[(creditDf.choiceText == 'effortful'), 'rewardJittered'].sum())
        creditEarned = creditEarnedBaseline + creditEarnedEffortful

        moneyEarned = 0.005 * creditEarned

        # training task performance
        if info['expCondition'] == 'training':
            switchMoney = float(np.nansum(dataSwitchTrainingAll.loc[:, 'rewardEarned'])) * 0.01
            updateMoney = float(np.nansum(dataUpdateTrainingAll.loc[:, 'rewardEarned'])) * 0.01
            switchAcc = np.nanmean(dataSwitchTrainingAll.loc[:, 'acc'])
            updateAcc = np.nanmean(dataUpdateTrainingAll.loc[:, 'acc'])
            overallAcc = np.nanmean([effortChoiceAcc, switchAcc, effortChoiceAcc])
        else:
            switchMoney = 0
            updateMoney = 0
            overallAcc = effortChoiceAcc

        moneyEarned += switchMoney + updateMoney

        overallAcc *= overallAcc * 100
        if overallAcc >= 70:
            toPay = 'yes'
        else:
            toPay = 'no'

        outputCsv = pd.DataFrame(index=range(0, 1))
        outputCsv['participant'] = int(info['participant'])
        outputCsv['email'] = str(info['email'])
        outputCsv['overallAccuracy'] = overallAcc
        outputCsv['creditEarned'] = creditEarned
        outputCsv['switchMoney'] = switchMoney
        outputCsv['updateMoney'] = updateMoney
        outputCsv['toPay'] = toPay
        outputCsv['moneyEarned'] = moneyEarned

        if overallAcc >= 70:
            if info['expCondition'] == 'training':
                showInstructions(text=["Your overall accuracy was {:.0f}%, and you've earned {} credits (converted to extra cash). You've also earned ${:.2f} from the letter-number task and ${:.2f} from the addition task. Together, you'll receive ${:.2f}.".format(overallAcc, creditEarned, switchMoney, updateMoney, moneyEarned)])
            elif info['expCondition'] == 'control':
                showInstructions(text=["Your overall accuracy was {:.0f}%, and you've earned {} credits (converted to extra cash), which have been converted to ${:.2f}.".format(overallAcc, creditEarned, moneyEarned)])
        else:
            showInstructions(text=["Your overall performance isn't good enough ({:.0f}% correct), so you won't be paid the extra money/credits you earned from the tasks.".format(overallAcc)])

    except:
        outputCsv = pd.DataFrame(index=range(0, 1))
        outputCsv['participant'] = int(info['participant'])
        outputCsv['email'] = str(info['email'])
        outputCsv['overallAccuracy'] = np.nan
        outputCsv['creditEarned'] = np.nan
        outputCsv['switchMoney'] = np.nan
        outputCsv['updateMoney'] = np.nan
        outputCsv['toPay'] = 'yes'
        outputCsv['moneyEarned'] = 2.5
        showInstructions(text=["Your overall accuracy was 75% and you've earned 310 credits, which have been converted to $2.50."])

    outputCsv.to_csv("{:03d}-{}-REWARDINFO.csv".format(int(info['participant']), info['startTime']), index=False)

    for frameN in range(30):
        win.flip()












def switchingTask():
    showInstructions(text =
    ["Next is the letter-number task. You'll see letter-number pairings like U4, C7, or H3, one at a time. You'll be asked to focus on either the letter or the number.",
    "For example, when asked to focus on LETTER in the pairing U4, you'll have to indicate whether the letter in it (U) is a consonant or vowel. Press C to indicate consonant, and V for vowel.",
    "When asked to focus on the NUMBER in the pairing C7, indicate whether the number (7 in this example) is smaller or greater than 5. If smaller than 5, press the key < (indicating less than 5; right next to letter M). If larger than 5, press the key > (greater than 5; left of ? key).",
    "The color (blue or white) of the pairing is an additional cue you can rely on to know whether to focus on the letter or number. So try to rely on the color cues to get better at the task.",
    "Let's practice now. Place your two fingers of each hand on C V < > now.",
    "If you have any questions during practice, let the research assistant know."
    ])

    if info['expCondition'] == 'control':
        # practice
        runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='practice', trials=10, feedback=True, saveData=True, practiceTrials=10, switchProportion=0.1, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=False, pauseAfterMissingNTrials=5)

        showInstructions(text=["You've just practiced the task. If you have any questions, let the research assistant know.", "If not, you'll start the actual task."])

        effortQuestions = ["How effortful do you think the task will be?", "How frustrating do you think the task will be?", "How boring do you think the task will be?", "How much do you think you'll like the task?", "How well do you think you'll do on the task?", "How tired do you think you'll feel after doing the task?"]
        random.shuffle(effortQuestions)
        presentQuestions(questionName='selfReport', questionList=effortQuestions, blockType='preShift', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])

        # actual
        runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='actual', trials=300, feedback=True, saveData=True, practiceTrials=10, switchProportion=0.1, titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=False, pauseAfterMissingNTrials=5)

    elif info['expCondition'] == 'training':
        showInstructions(text=["If you've responded correctly, you should hear a twinkle."])
        # practice
        runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='practice', trials=10, feedback=True, saveData=True, practiceTrials=10, switchProportion=0.8, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=True, pauseAfterMissingNTrials=5)

        showInstructions(text=["You've just practiced the task. If you have any questions, let the research assistant know.", "If not, you'll start the actual task."])

        effortQuestions = ["How effortful do you think the task will be?", "How frustrating do you think the task will be?", "How boring do you think the task will be?", "How much do you think you'll like the task?", "How well do you think you'll do on the task?", "How tired do you think you'll feel after doing the task?"]
        random.shuffle(effortQuestions)
        presentQuestions(questionName='selfReport', questionList=effortQuestions, blockType='preShift', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])

        # actual
        showInstructions(text=["From now on, each time you respond correctly, you'll earn 2 cents. For example, if you respond correctly 50 times, you'll receive $1 at the end of the experiment (plus other rewards you've earned from other tasks)."])

        runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='actual', trials=300, feedback=True, saveData=True, practiceTrials=10, switchProportion=0.8, titrate=True, rtMaxFrames=180, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=True, pauseAfterMissingNTrials=5)

    effortQuestions = ["How effortful is the task now?", "How frustrating is the task now?", "How boring is the task now?", "How much are you liking the task now?", "How well do you think you are doing on the task now?", "I'm mentally fatigued now."]
    random.shuffle(effortQuestions)
    presentQuestions(questionName='selfReport', questionList=effortQuestions, blockType='postShift', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])



def updatingTask():
    showInstructions(text=["Next is a mental addition task. You'll see multi-digit sequences, with one digit presented one at a time. You have to add a number to each digit, one at a time, remember the sequence of digits, and choose the correct answer later on.",
    "So, if you see 5, 2, 3 (presented one at a time) and you've been told to add 4, you'll add 4 to each number separately, the correct answer will be 967.",
    "You'll see four potential answers and you'll use the D F J K keys to repond.",
    "Whenever the sum of two digits is greater than 10, you'll report only the ones digit (the rightmost digit). For example, if the problem is 9 + 5, the summed digit will be 4 (not 14).",
    "A few more examples: 4 + 6 is 0; 9 + 2 is 1.",
    "If you have any questions during practice, let the research assistant know.",
    "Let's practice now. Place two fingers of each hand on D F (left hand) and J K (right hand).",
    "If you have any questions during practice, let the research assistant know."])

    if info['expCondition'] == 'control':
        # practice
        runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=5, feedback=True, saveData=True, practiceTrials=5, digits=3, digitChange=[0], digitsToModify=1, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=False, pauseAfterMissingNTrials=3)

        showInstructions(text=["You've just practiced the task. If you have any questions, let the research assistant know.", "If not, you'll start the actual task."])

        effortQuestions = ["How effortful do you think the task will be?", "How frustrating do you think the task will be?", "How boring do you think the task will be?", "How much do you think you'll like the task?", "How well do you think you'll do on the task?", "How tired do you think you'll feel after doing the task?"]
        random.shuffle(effortQuestions)
        presentQuestions(questionName='selfReport', questionList=effortQuestions, blockType='preUpdate', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])

        # actual
        runMentalMathBlock(taskName='mentalMathUpdating', blockType='actual', trials=300, feedback=True, saveData=True, practiceTrials=10, digits=3, digitChange=[0], digitsToModify=1, titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=False, pauseAfterMissingNTrials=3)

    elif info['expCondition'] == 'training':
        # practice
        showInstructions(text=["If you've responded correctly, you should hear a twinkle."])

        runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=5, feedback=True, saveData=True, practiceTrials=5, digits=3, digitChange=[2, 3, 4], digitsToModify=1, titrate=False, rtMaxFrames=90, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=True, pauseAfterMissingNTrials=3)

        showInstructions(text=["You've just practiced the task. If you have any questions, let the research assistant know.", "If not, you'll start the actual task."])

        effortQuestions = ["How effortful do you think the task will be?", "How frustrating do you think the task will be?", "How boring do you think the task will be?", "How much do you think you'll like the task?", "How well do you think you'll do on the task?", "How tired do you think you'll feel after doing the task?"]
        random.shuffle(effortQuestions)
        presentQuestions(questionName='selfReport', questionList=effortQuestions, blockType='preUpdate', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])

        # actual
        showInstructions(text=["From now on, each time you respond correctly, you'll earn 2 cents. For example, if you respond correctly 50 times, you'll receive $1 at the end of the experiment (plus other rewards you've earned from other tasks)."])

        runMentalMathBlock(taskName='mentalMathUpdating', blockType='actual', trials=300, feedback=True, saveData=True, practiceTrials=10, digits=3, digitChange=[2, 3, 4], digitsToModify=1, titrate=True, rtMaxFrames=180, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=True, pauseAfterMissingNTrials=3)

    effortQuestions = ["How effortful is the task now?", "How frustrating is the task now?", "How boring is the task now?", "How much are you liking the task now?", "How well do you think you are doing on the task now?", "I'm mentally fatigued now."]
    random.shuffle(effortQuestions)
    presentQuestions(questionName='selfReport', questionList=effortQuestions, blockType='postUpdate', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])




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


def choiceTaskPre():

    ''' stroop instructions and practice '''
    showInstructions(text =
    ["One of the tasks is the Stroop color-naming task.",
    "You'll see the words red, green, yellow, presented in red, green, or yellow font. The words will often be presented in a font color that doesn't match the word itself. For example, the word red might be in yellow font.",
    "You'll have to indicate the font colour it is printed in, ignoring the word itself.",
    "Use the keys R, G, Y to indicate red, green, and yellow font colors respectively.",
    "Let the research assistant know if you have any questions during practice.",
    "Let's do a few practice trials now. Place your fingers on R G Y.",
    ])

    runStroopBlock(taskName='stroop3colours', blockType='practice', congruentTrials=0, incongruentTrials=5, feedback=True, saveData=False, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackFrames=60, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, practiceHelp=True)

    showInstructions(["That was the Stroop color-naming task."])

    ''' choice task practice '''
    showInstructions(text = ["Now, you'll have to make choices about what tasks to do.",
    "Each choice option will be associated with a task and a specific number of credits, and as long as your OVERALL performance is good (more than 70% correct overall), your credits will be converted to money (Amazon voucher of that amount emailed to you).",
    "One of the choice options will ALWAYS be 1 Stroop color-naming task for 10 credits. This option is very easy and the answer will even be provided.",
    "The other choice option will vary from 3 to 11 Stroops, 11 to 15 credits (e.g., 3 Stroops for 11 credits). For example, you might have to choose between 1 Stroop for 10 credits vs. 3 Stroops for 11 credits. If you choose the latter, you'll have to do 3 Stroops.",
    "These choice pairs might be shown multiple time during the study. It's perfectly fine if you find yourself choosing 'inconsistently'. For example, when choosing between options A and B, it's normal to sometimes prefer A and other times prefer B.",
    "Ask yourself, which option feels like a better deal? Which one do I prefer?",
    "Try not to base your decision on what you've chosen previously. Just select the option that feels like it's worth more to you at that particular moment.",
    "During practice, your choices won't be counted and we encourage you to try choosing different options to understand how the task works.",
    "Press F or J to choose the left or right options. And then use R G Y to indicate the color of the word.",
    "We'll practice a bit now and you have up to 5 seconds to choose, and 1.5 seconds to respond on each Stroop."
    ])

    # practice
    runEffortRewardChoiceBlock(taskName='effortTraining', blockType='practice', reps=3, feedback=True, saveData=True, practiceTrials=4, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[11, 15], effort=[3, 11])

    showInstructions(text = [
    "That was the choice and Stroop color-naming tasks.",
    "If you have any questions, ask the research assistant now, before starting the actual task.",
    "Remember, you're making REAL choices from now on. To receive the credits/money at the end, you'll have to respond correctly at least 70% of the time.",
    "Place your left index finger on F, and right index finger on J, and use these two keys to choose. Then use the keys R, G, Y to indicate the word color.",
    "You have up to 5 seconds to make each choice, and 1.5 seconds for each Stroop.",
    "Your choices won't affect the duration of the study because the study has a fixed duration of about 60 mins. So choose what you prefer by considering just the number of Stroops and credits offered, rather than the amount of time you think it'll take to complete the task/study (fixed at around 60 mins).",
    "Before we begin, you'll respond to a few statements."
    ])

    motivationQuestions = ["I think I will enjoy the Stroop color-naming task", "I think the Stroop color-naming task will be interesting", "I think the Stroop color-naming task will be fun"]
    random.shuffle(motivationQuestions)
    presentQuestions(questionName='choiceTaskMotivation', questionList=motivationQuestions, blockType='pre', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,7], scaleAnchorText=['not at all', 'very true'])

    showInstructions(text=["The task will begin now."])

    # actual choice task
    runEffortRewardChoiceBlock(taskName='effortTraining', blockType='pre', reps=1, feedback=True, saveData=True, practiceTrials=0, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[11, 12, 13, 14, 15], effort=[3, 5, 7, 9, 11])

    runEffortRewardChoiceBlock(taskName='effortTraining', blockType='pre', reps=1, feedback=True, saveData=True, practiceTrials=0, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[11, 12, 13, 14, 15], effort=[3, 5, 7, 9, 11])

    runEffortRewardChoiceBlock(taskName='effortTraining', blockType='pre', reps=1, feedback=True, saveData=True, practiceTrials=0, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[11, 12, 13, 14, 15], effort=[3, 5, 7, 9, 11])

    showInstructions(text = ["That was the choice and Stroop color-naming tasks."])


def choiceTaskPost():

    showInstructions(text=[
    "Now you'll do the choice and Stroop task again. Remember, you're making REAL choices.",
    "To receive the credits/money at the end, you'll have to respond correctly at least 70% of the time.",
    "Try not to base your decision on what you've chosen previously. Just select the option that feels like it's worth more to you at that particular moment.",
    "Place your left index finger on F, and right index finger on J, and use these two keys to choose. Then use the keys R, G, Y to indicate the color.",
    "You have up to 5 seconds to make each choice, and 1.5 seconds for each Stroop.",
    "Reminder: Your choices won't affect the duration of the study because the study has a fixed duration of about 60 mins. So choose what you prefer by considering just the number of Stroops and credits offered, rather than the amount of time you think it'll take to complete the task/study (fixed at around 60 mins).",
    "Before we begin, you'll respond to a few statements."
    ])

    motivationQuestions = ["I think I will enjoy the Stroop color-naming task", "I think the Stroop color-naming task will be interesting", "I think the Stroop color-naming task will be fun"]
    random.shuffle(motivationQuestions)
    presentQuestions(questionName='choiceTaskMotivation', questionList=motivationQuestions, blockType='post', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,7], scaleAnchorText=['not at all', 'very true'])

    showInstructions(text=["The task will begin now."])

    runEffortRewardChoiceBlock(taskName='effortTraining', blockType='post', reps=1, feedback=True, saveData=True, practiceTrials=0, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[11, 12, 13, 14, 15], effort=[3, 5, 7, 9, 11])

    runEffortRewardChoiceBlock(taskName='effortTraining', blockType='post', reps=1, feedback=True, saveData=True, practiceTrials=0, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[11, 12, 13, 14, 15], effort=[3, 5, 7, 9, 11])

    runEffortRewardChoiceBlock(taskName='effortTraining', blockType='post', reps=1, feedback=True, saveData=True, practiceTrials=0, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[11, 12, 13, 14, 15], effort=[3, 5, 7, 9, 11])

    showInstructions(text=["That was the choice and Stroop color-naming tasks."])



def runSwitchTrainingBlock(taskName='switchTraining', blockType='actual', reps=100, feedback=False, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, option1=[0, 0.1, 0.3, 0.5, 0.7], option2=[0, 0.1, 0.3, 0.5, 0.7], feedbackSound=False):
    '''Run a block of trials.
    reps: number of times to repeat each unique trial
    feedback: whether feedback is presented or not
    saveData = whether to save data to csv file
    practiceTrials: no. of practice trials to run
    titrate: whether to adjust difficulty of task based on performance; if set to True, subsequent targetFrames (max response time) for subsequent blocks will be affected
    rtmaxFrames: max rt (in frames); default is None, which takes value from info['targetFrames']; if a value is provided, default will be overwritten
    blockMaxTimeSeconds: end block if overall time of BLOCK (in seconds) has passed
    experimentMaxTimeSeconds: end block if overall time of EXPERIMENT (in seconds) has passed
    '''

    global dataSwitchTrainingAll

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], taskName)
    filenamebackup = "{:03d}-{}-{}-backup.csv".format(int(info['participant']), info['startTime'], taskName) # saved after each block

    mouse.setVisible(0) #make mouse invisible

    #Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True

    '''generate trials for choice training'''
    optionTuple = [(o1, o2) for o1 in option1 for o2 in option2 if o1 != o2] # combinations

    optionCombi = pd.DataFrame(optionTuple)
    optionCombi.columns = ['option1', 'option2']

    trialsInBlock = pd.concat([optionCombi] * reps, ignore_index=True)
    trialsInBlock['difficultDifference'] = abs(trialsInBlock['option1'] - trialsInBlock['option2'])

    trialsInBlock = trialsInBlock.reindex(np.random.permutation(trialsInBlock.index)).reset_index(drop=True) # shuffle

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
    trialsDf['scriptDate'] = info['scriptDate']
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
    trialsDf['expCondition'] = info['expCondition']
    trialsDf['taskOrder'] = info['taskOrder']

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
    trialsDf['acc'] = 0
    trialsDf['rewardEarned'] = 0

    trialsDf['accEffortTask'] = np.nan
    trialsDf['rtEffortTask'] = np.nan

    trialsDf = pd.concat([trialsDf, trialsInBlock], axis=1)

    # running accuracy and rt
    runningTallyAcc = []
    runningTallyRt = []
    rewardScheduleTrackerAcc = 0

    # if this is a practice block
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

    leftOption = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = '1 stroop', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.2, 0.0))

    rightOption = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = 'XXX', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.2, 0.0))

    practiceInstructText = visual.TextStim(win = win, units = 'norm', height = 0.04, ori = 0, name = 'target', text = 'F for left option, J for right option', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, 0.28))

    keyF = visual.TextStim(win = win, units = 'norm', height = 0.05, ori = 0, name = 'target', text = 'F', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.2, 0.13))

    keyJ = visual.TextStim(win = win, units = 'norm', height = 0.05, ori = 0, name = 'target', text = 'J', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.2, 0.13))

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
                else: # (e.g., nan in previous trial)
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
        leftOption.setText("{}% switch".format(int(thisTrial['option1'] * 100)))
        rightOption.setText("{}% switch".format(int(thisTrial['option2'] * 100)))
        leftOption.setAutoDraw(True)
        rightOption.setAutoDraw(True)

        keyF.setAutoDraw(True)
        keyJ.setAutoDraw(True)

        if blockType == 'practice':
            practiceInstructText.setAutoDraw(True)

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
                        trialsDf.loc[i, 'choiceText'] = 'option1'
                        trialsDf.loc[i, 'acc'] = np.nan
                    elif keysCollected[0] == 'j':
                        if sendTTL and not blockType == 'practice':
                            port.setData(16) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 16
                        trialsDf.loc[i, 'choiceText'] = 'option2'
                        trialsDf.loc[i, 'acc'] = np.nan
                    else:
                        if sendTTL and not blockType == 'practice':
                            port.setData(17) #incorrect response
                        trialsDf.loc[i, 'responseTTL'] = 17
                        trialsDf.loc[i, 'choiceText'] = ''
                        trialsDf.loc[i, 'acc'] = np.nan
                        trialsDf.loc[i, 'rt'] = np.nan
                    #remove stimulus from screen
                    leftOption.setAutoDraw(False)
                    rightOption.setAutoDraw(False)
                    practiceInstructText.setAutoDraw(False)
                    keyF.setAutoDraw(False)
                    keyJ.setAutoDraw(False)
                    win.flip() #clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            leftOption.setAutoDraw(False)
            rightOption.setAutoDraw(False)
            practiceInstructText.setAutoDraw(False)
            keyF.setAutoDraw(False)
            keyJ.setAutoDraw(False)
            win.flip() #clear screen (remove stuff from screen)

        if float(thisTrial['option1']) > float(thisTrial['option2']):
            if trialsDf.loc[i, 'choiceText'] == 'option1':
                trialsDf.loc[i, 'acc'] = 1
            elif trialsDf.loc[i, 'choiceText'] == 'option2':
                trialsDf.loc[i, 'acc'] = 0
        elif float(thisTrial['option1']) < float(thisTrial['option2']):
            if trialsDf.loc[i, 'choiceText'] == 'option1':
                trialsDf.loc[i, 'acc'] = 0
            elif trialsDf.loc[i, 'choiceText'] == 'option2':
                trialsDf.loc[i, 'acc'] = 1

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

        ### print "TRIAL OK TRIAL %d OVERALL TRIAL %d" %(i + 1, int(trialsDf.loc[i, 'overallTrialNum']))

        ''' DO NOT EDIT BEGIN '''
        #if press 0 (quit script) or 7 (skip block)
        if trialsDf.loc[i, 'resp'] == 'backslash':
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] = None
            if saveData: #if saveData argument is True, then APPEND current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataSwitchTrainingAll = dataSwitchTrainingAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataSwitchTrainingAll.to_csv(filenamebackup, index=False)
            core.quit() #quit when 'backslash' has been pressed
        elif trialsDf.loc[i, 'resp'] == 'bracketright':#if press 7, skip to next block
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'resp'] == None
            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataSwitchTrainingAll = dataSwitchTrainingAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataSwitchTrainingAll.to_csv(filenamebackup, index=False)
            return None

        ''' DO NOT EDIT END '''

        ISI.complete() #end inter-trial interval

        # feedback for trial
        if feedback:
            # show reward if paraticipant selected difficult option
            feedbackText1 = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.06])
            pointsFeedback = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = "You've earned +2 cents!", height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'acc'] == 1:
                tempFeedBack = random.choice(["Excellent!", "Doing great!", "Fantastic!", "Amazing!"])

                difficultDifference = thisTrial['difficultDifference'] * 10
                rewardEarned = difficultDifference + random.choice([0, -1, 1])
                if rewardEarned == 0:
                    rewardEarned = 1
                trialsDf.loc[i, 'rewardEarned'] = rewardEarned

                if info['expCondition'] == 'training':
                    if rewardEarned > 1:
                        pointsFeedback.setText("{} +{:.0f} cents".format(tempFeedBack, rewardEarned))
                    else:
                        pointsFeedback.setText("{} +{:.0f} cent".format(tempFeedBack, rewardEarned))
                    if feedbackSound:
                        try:
                            feedbackTwinkle.play()
                        except:
                            pass
                    for frameN in range(90):
                        pointsFeedback.draw()
                        # feedbackText1.draw()
                        win.flip()

            # show participant's selected choice
            selectedOption = trialsDf.loc[i, 'choiceText']
            try:
                feedbackText1.setText("{:.0f}% switch".format(thisTrial[selectedOption] * 100))
                feedbackText1.setPos([0.0, 0.0])
                for frameN in range(60):
                    feedbackText1.draw()
                    win.flip()
            except:
                feedbackText1.setText('respond faster')
                for frameN in range(60):
                    feedbackText1.draw()
                    win.flip()

        fixation.setAutoDraw(True) #draw fixation on next flips
        for frameN in range(72):
            win.flip()
        fixation.setAutoDraw(False)

        ''' run task block '''
        if trialsDf.loc[i, 'resp'] is not None:
            taskDf = runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType=trialsDf.loc[i, 'overallTrialNum'], trials=10, feedback=False, saveData=True, practiceTrials=10, switchProportion=float(thisTrial[selectedOption]), titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=None, feedbackSound=True, pauseAfterMissingNTrials=5)

        # compute accuracy and rt of task
        try:
            nTrials = taskDf.shape[0]
            if sum(taskDf['acc'].isnull()) == nTrials: # if no. of NaN equals no.of rows (if all 'acc' are )
                taskAcc = np.nan
                taskRt = np.nan
            else:
                taskAcc = np.nanmean(taskDf.loc[:, 'acc'])
                taskRt = np.nanmean(taskDf.loc[:, 'rt']) # will show warning if everything's NA
        except:
            taskAcc = np.nan
            taskRt = np.nan

        # print nTrials
        # print taskAcc
        # print taskRt

        taskDf = pd.DataFrame() # empty dataframe for next trial

        ''' end effortful task'''

        # store effortful task results summary performance
        trialsDf.loc[i, 'accEffortTask'] = taskAcc
        trialsDf.loc[i, 'rtEffortTask'] = taskRt

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            dataSwitchTrainingAll = dataSwitchTrainingAll.append(trialsDf[i:i+1]).reset_index(drop=True)

        # feedback for task performance
        if feedback and trialsDf.loc[i, 'resp'] is not None:

            feedbackText1 = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'accEffortTask'] == 1: # if correct
                feedbackText1.setText('100% correct')
            elif trialsDf.loc[i, 'accEffortTask'] < 1: # if correct
                if np.isnan(taskAcc): # if NaN, convert to 0
                    accI = 0
                feedbackText1.setText("{:.0f}% correct".format(taskAcc * 100))
            else:
                feedbackText1.setText(" ")

            for frameN in range(60):
                feedbackText1.draw()
                win.flip()

        for frameN in range(random.randint(18, 36)): # blank screen
            win.flip()

    # end of block pause
    for frameN in range(info['blockEndPause']):
        win.flip() #wait at the end of the block

    # append data to global dataframe
    dataSwitchTrainingAll.to_csv(filenamebackup, index=False)



def runUpdateTrainingBlock(taskName='updateTraining', blockType='actual', reps=100, feedback=False, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, option1=[0, 1, 2, 3, 4], option2=[0, 1, 2, 3, 4], feedbackSound=False):
    '''Run a block of trials.
    reps: number of times to repeat each unique trial
    feedback: whether feedback is presented or not
    saveData = whether to save data to csv file
    practiceTrials: no. of practice trials to run
    titrate: whether to adjust difficulty of task based on performance; if set to True, subsequent targetFrames (max response time) for subsequent blocks will be affected
    rtmaxFrames: max rt (in frames); default is None, which takes value from info['targetFrames']; if a value is provided, default will be overwritten
    blockMaxTimeSeconds: end block if overall time of BLOCK (in seconds) has passed
    experimentMaxTimeSeconds: end block if overall time of EXPERIMENT (in seconds) has passed
    '''

    global dataUpdateTrainingAll

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], taskName)
    filenamebackup = "{:03d}-{}-{}-backup.csv".format(int(info['participant']), info['startTime'], taskName) # saved after each block

    mouse.setVisible(0) #make mouse invisible

    #Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True

    '''generate trials for choice training'''
    optionTuple = [(o1, o2) for o1 in option1 for o2 in option2 if o1 != o2] # combinations

    optionCombi = pd.DataFrame(optionTuple)
    optionCombi.columns = ['option1', 'option2']

    trialsInBlock = pd.concat([optionCombi] * reps, ignore_index=True)
    trialsInBlock['difficultDifference'] = abs(trialsInBlock['option1'] - trialsInBlock['option2'])

    trialsInBlock = trialsInBlock.reindex(np.random.permutation(trialsInBlock.index)).reset_index(drop=True) # shuffle

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
    trialsDf['scriptDate'] = info['scriptDate']
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
    trialsDf['expCondition'] = info['expCondition']
    trialsDf['taskOrder'] = info['taskOrder']

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
    trialsDf['acc'] = 0
    trialsDf['rewardEarned'] = 0

    trialsDf['accEffortTask'] = np.nan
    trialsDf['rtEffortTask'] = np.nan

    trialsDf = pd.concat([trialsDf, trialsInBlock], axis=1)

    # running accuracy and rt
    runningTallyAcc = []
    runningTallyRt = []
    rewardScheduleTrackerAcc = 0

    # if this is a practice block
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

    leftOption = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = '1 stroop', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.2, 0.0))

    rightOption = visual.TextStim(win = win, units = 'norm', height = 0.065, ori = 0, name = 'target', text = 'XXX', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.2, 0.0))

    practiceInstructText = visual.TextStim(win = win, units = 'norm', height = 0.04, ori = 0, name = 'target', text = 'F for left option, J for right option', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0, 0.28))

    keyF = visual.TextStim(win = win, units = 'norm', height = 0.05, ori = 0, name = 'target', text = 'F', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(-0.2, 0.13))

    keyJ = visual.TextStim(win = win, units = 'norm', height = 0.05, ori = 0, name = 'target', text = 'J', font = 'Verdana', colorSpace = 'rgb', color = [1, 1, 1], opacity = 1, pos=(0.2, 0.13))

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
                else: # (e.g., nan in previous trial)
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
        leftOption.setText("add {}".format(int(thisTrial['option1'])))
        rightOption.setText("add {}".format(int(thisTrial['option2'])))
        leftOption.setAutoDraw(True)
        rightOption.setAutoDraw(True)

        keyF.setAutoDraw(True)
        keyJ.setAutoDraw(True)

        if blockType == 'practice':
            practiceInstructText.setAutoDraw(True)

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
                        trialsDf.loc[i, 'choiceText'] = 'option1'
                        trialsDf.loc[i, 'acc'] = np.nan
                    elif keysCollected[0] == 'j':
                        if sendTTL and not blockType == 'practice':
                            port.setData(16) # correct response
                        trialsDf.loc[i, 'responseTTL'] = 16
                        trialsDf.loc[i, 'choiceText'] = 'option2'
                        trialsDf.loc[i, 'acc'] = np.nan
                    else:
                        if sendTTL and not blockType == 'practice':
                            port.setData(17) #incorrect response
                        trialsDf.loc[i, 'responseTTL'] = 17
                        trialsDf.loc[i, 'choiceText'] = ''
                        trialsDf.loc[i, 'acc'] = np.nan
                        trialsDf.loc[i, 'rt'] = np.nan
                    #remove stimulus from screen
                    leftOption.setAutoDraw(False)
                    rightOption.setAutoDraw(False)
                    practiceInstructText.setAutoDraw(False)
                    keyF.setAutoDraw(False)
                    keyJ.setAutoDraw(False)
                    win.flip() #clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            leftOption.setAutoDraw(False)
            rightOption.setAutoDraw(False)
            practiceInstructText.setAutoDraw(False)
            keyF.setAutoDraw(False)
            keyJ.setAutoDraw(False)
            win.flip() #clear screen (remove stuff from screen)

        if float(thisTrial['option1']) > float(thisTrial['option2']):
            if trialsDf.loc[i, 'choiceText'] == 'option1':
                trialsDf.loc[i, 'acc'] = 1
            elif trialsDf.loc[i, 'choiceText'] == 'option2':
                trialsDf.loc[i, 'acc'] = 0
        elif float(thisTrial['option1']) < float(thisTrial['option2']):
            if trialsDf.loc[i, 'choiceText'] == 'option1':
                trialsDf.loc[i, 'acc'] = 0
            elif trialsDf.loc[i, 'choiceText'] == 'option2':
                trialsDf.loc[i, 'acc'] = 1

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

        ### print "TRIAL OK TRIAL %d OVERALL TRIAL %d" %(i + 1, int(trialsDf.loc[i, 'overallTrialNum']))

        ''' DO NOT EDIT BEGIN '''
        #if press 0 (quit script) or 7 (skip block)
        if trialsDf.loc[i, 'resp'] == 'backslash':
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] = None
            if saveData: #if saveData argument is True, then APPEND current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataUpdateTrainingAll = dataUpdateTrainingAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataUpdateTrainingAll.to_csv(filenamebackup, index=False)
            core.quit() #quit when 'backslash' has been pressed
        elif trialsDf.loc[i, 'resp'] == 'bracketright':#if press 7, skip to next block
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'resp'] == None
            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataUpdateTrainingAll = dataUpdateTrainingAll.append(trialsDf[i:i+1]).reset_index(drop=True)
                dataUpdateTrainingAll.to_csv(filenamebackup, index=False)
            return None

        ''' DO NOT EDIT END '''

        ISI.complete() #end inter-trial interval

        # feedback for trial
        if feedback:
            # show reward if paraticipant selected difficult option
            feedbackText1 = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.06])
            pointsFeedback = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = "You've earned +2 cents!", height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'acc'] == 1:
                tempFeedBack = random.choice(["Excellent!", "Doing great!", "Fantastic!", "Amazing!"])

                difficultDifference = thisTrial['difficultDifference']
                difficultDifference *= 2
                rewardEarned = difficultDifference + random.choice([0, -1, 1])
                if rewardEarned == 0:
                    rewardEarned = 1
                trialsDf.loc[i, 'rewardEarned'] = rewardEarned

                if info['expCondition'] == 'training':
                    if rewardEarned > 1:
                        pointsFeedback.setText("{} +{:.0f} cents".format(tempFeedBack, rewardEarned))
                    else:
                        pointsFeedback.setText("{} +{:.0f} cent".format(tempFeedBack, rewardEarned))
                    if feedbackSound:
                        try:
                            feedbackTwinkle.play()
                        except:
                            pass
                    for frameN in range(90):
                        pointsFeedback.draw()
                        # feedbackText1.draw()
                        win.flip()

                    for frameN in range(random.randint(6, 12)): # blank screen
                        win.flip()

            # show participant's selected choice
            selectedOption = trialsDf.loc[i, 'choiceText']
            try:
                feedbackText1.setText("add {:.0f}".format(thisTrial[selectedOption]))
                feedbackText1.setPos([0.0, 0.0])
                for frameN in range(60):
                    feedbackText1.draw()
                    win.flip()
            except:
                feedbackText1.setText('respond faster')
                for frameN in range(60):
                    feedbackText1.draw()
                    win.flip()

        fixation.setAutoDraw(True) #draw fixation on next flips
        for frameN in range(36):
            win.flip()
        fixation.setAutoDraw(False)

        ''' run task block '''
        if trialsDf.loc[i, 'resp'] is not None:

            taskDf = runMentalMathBlock(taskName='mentalMathUpdating', blockType=trialsDf.loc[i, 'overallTrialNum'], trials=1, feedback=False, saveData=True, practiceTrials=10, digits=3, digitChange=[int(thisTrial[selectedOption])], digitsToModify=1, titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=True, pauseAfterMissingNTrials=5)

        # compute accuracy and rt of task
        try:
            nTrials = taskDf.shape[0]
            if sum(taskDf['acc'].isnull()) == nTrials: # if no. of NaN equals no.of rows (if all 'acc' are )
                taskAcc = np.nan
                taskRt = np.nan
            else:
                taskAcc = np.nanmean(taskDf.loc[:, 'acc'])
                taskRt = np.nanmean(taskDf.loc[:, 'rt']) # will show warning if everything's NA
        except:
            taskAcc = np.nan
            taskRt = np.nan

        # print nTrials
        # print taskAcc
        # print taskRt

        taskDf = pd.DataFrame() # empty dataframe for next trial

        ''' end effortful task'''

        # store effortful task results summary performance
        trialsDf.loc[i, 'accEffortTask'] = taskAcc
        trialsDf.loc[i, 'rtEffortTask'] = taskRt

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            dataUpdateTrainingAll = dataUpdateTrainingAll.append(trialsDf[i:i+1]).reset_index(drop=True)

        # feedback for task performance
        if feedback and trialsDf.loc[i, 'resp'] is not None:

            feedbackText1 = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

            if trialsDf.loc[i, 'accEffortTask'] == 1: # if correct
                feedbackText1.setText('100% correct')
            elif trialsDf.loc[i, 'accEffortTask'] < 1: # if correct
                if np.isnan(taskAcc): # if NaN, convert to 0
                    accI = 0
                feedbackText1.setText("{:.0f}% correct".format(taskAcc * 100))
            else:
                feedbackText1.setText(" ")

            for frameN in range(60):
                feedbackText1.draw()
                win.flip()

        for frameN in range(random.randint(18, 36)): # blank screen
            win.flip()

    # end of block pause
    for frameN in range(info['blockEndPause']):
        win.flip() #wait at the end of the block

    # append data to global dataframe
    dataUpdateTrainingAll.to_csv(filenamebackup, index=False)















def switchingTrainingTask():
    showInstructions(text=
    ["Next is the letter-number task. You'll see letter-number pairings like U4, C7, or H3, one at a time. You'll be asked to focus on either the letter or the number.",
    "For example, when asked to focus on LETTER in the pairing U4, you'll have to indicate whether the letter in it (U) is a consonant or vowel. Press C to indicate consonant, and V for vowel.",
    "When asked to focus on the NUMBER in the pairing C7, indicate whether the number (7 in this example) is smaller or greater than 5. If smaller than 5, press the key < (indicating less than 5; right next to letter M). If larger than 5, press the key > (greater than 5; left of ? key).",
    "The color (blue or white) of the pairing is an additional cue you can rely on to know whether to focus on the letter or number. So try to rely on the color cues to get better at the task.",
    "Let's practice now. Place your two fingers of each hand on C V < > now.",
    "If you have any questions during practice, let the research assistant know."
    ])

    ''' practice '''
    # practice 0 switch
    showInstructions(text=["Here's the easiest version of the task. You will be asked to focus on just the LETTER or NUMBER, and will never have to switch between them. So the task is very easy because it requires no switching at all (= 0% switch). Let's begin."])
    runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='practice', trials=10, feedback=True, saveData=True, practiceTrials=10, switchProportion=0, titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=False, pauseAfterMissingNTrials=5)

    # practice 0.1 switch
    showInstructions(text=["The task will be more and more difficult from now on. Now you'll switch from letter to number (or vice versa) ONCE (= 10% switch). Let's begin."])
    runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='practice', trials=10, feedback=True, saveData=True, practiceTrials=10, switchProportion=0.1, titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=False, pauseAfterMissingNTrials=5)

    # practice 0.3 switch
    showInstructions(text=["Next up is THREE switches (= 30% switch). Let's begin."])
    runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='practice', trials=10, feedback=True, saveData=True, practiceTrials=10, switchProportion=0.3, titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=False, pauseAfterMissingNTrials=5)

    # practice 0.5 switch
    showInstructions(text=["Next up is FIVE switches (= 50% switch). Let's begin."])
    runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='practice', trials=10, feedback=True, saveData=True, practiceTrials=10, switchProportion=0.5, titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=False, pauseAfterMissingNTrials=5)

    # practice 0.7 switch
    showInstructions(text=["Finally, the most difficult: SEVEN switches (= 70% switch). Let's begin."])
    runShiftingLetterNumberBlock(taskName='shiftingLetterNumber', blockType='practice', trials=10, feedback=True, saveData=True, practiceTrials=10, switchProportion=0.7, titrate=False, rtMaxFrames=180, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=1, feedbackSound=False, pauseAfterMissingNTrials=5)

    # practice switch choice training
    showInstructions(text=[
    "You've tried different difficulty levels (easiest to most difficult: 0%, 10%, 30%, 50%, 70% switch). From now on, two options will be shown at a time and you'll have to choose which one you want to do. For example, 30% switch or 50% switch?", "Use the F and J keys to choose, and the c v < > to do the task.",
    "Let's practice. Try choosing different options to understand how the choice task works."])

    if info['expCondition'] == 'training':
        showInstructions(text=
        ["Sometimes, your choices will earn you money. When you receive money and how much you receive depend ONLY ON YOUR CHOICES, not how well you do on the option you've chosen.",
        "For example, if you choose 10% switch over 0% switch, how well you do on your chosen task (10% switch) does not DIRECTLY affect how much money you earn. You might do poorly (e.g., 50% correct) after making this particular choice, but you'll still receive all the money (Amazon voucher) you've earned as long as your OVERALL performance is good (more than 70% correct overall).",
        "Let's practice."])

    runSwitchTrainingBlock(taskName='switchTraining', blockType='practice', reps=1, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, option1=[0.1], option2=[0.3, 0.7], feedbackSound=True)

    showInstructions(text=["You've just practiced the task. If you have any questions, let the research assistant know.", "If not, you'll start the actual choice task where you'll make many choices."])

    # self-report
    effortQuestions = ["How effortful do you think the letter-number task will be?", "How frustrating do you think the letter-number task will be?", "How boring do you think the letter-number will be?", "How much do you think you'll like the letter-number task?", "How well do you think you'll do on the letter-number task?", "How tired do you think you'll feel after doing the letter-number task?"]
    random.shuffle(effortQuestions)
    presentQuestions(questionName='selfReport', questionList=effortQuestions, blockType='preShift', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])

    showInstructions(text=["Use F and J to choose, and c v < > to do the task. Let's begin."])

    ''' actual task '''
    runSwitchTrainingBlock(taskName='switchTraining', blockType='actual', reps=200, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, option1=[0, 0.1, 0.3, 0.5, 0.7], option2=[0, 0.1, 0.3, 0.5, 0.7], feedbackSound=True)

    # post task difficulty
    effortQuestions = ["How effortful is the letter-number task now?", "How frustrating is the letter-number task now?", "How boring is the letter-number task now?", "How much are you liking the letter-number task now?", "How well do you think you are doing on the letter-number task now?", "I'm mentally fatigued now."]
    random.shuffle(effortQuestions)
    presentQuestions(questionName='selfReport', questionList=effortQuestions, blockType='postShift', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])


def updatingTrainingTask():
    showInstructions(text=["Next is a mental addition task. You'll see multi-digit sequences, with one digit presented one at a time. You have to add a number to each digit, one at a time, remember the sequence of digits, and choose the correct answer later on.",
    "So, if you see 5, 2, 3 (presented one at a time) and you've been told to add 4, you'll add 4 to each number separately, the correct answer will be 967.",
    "You'll see four potential answers and you'll use the D F J K keys to repond.",
    "Whenever the sum of two digits is greater than 10, you'll report only the ones digit (the rightmost digit). For example, if the problem is 9 + 5, the summed digit will be 4 (not 14).",
    "A few more examples: 4 + 6 is 0; 9 + 2 is 1.",
    "If you have any questions during practice, let the research assistant know.",
    "Let's practice now. Place two fingers of each hand on D F (left hand) and J K (right hand).",
    "If you have any questions during practice, let the research assistant know."])

    ''' practice '''
    # add 0
    showInstructions(text=["Here's the easiest version of the task. You will add 0 to each digit. Let's begin."])
    runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=1, feedback=True, saveData=True, practiceTrials=1, digits=3, digitChange=[0], digitsToModify=1, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=3)

    # add 1
    showInstructions(text=["The task will be more and more difficult from now on. Now you'll add 1 to each digit. Let's begin."])
    runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=1, feedback=True, saveData=True, practiceTrials=1, digits=3, digitChange=[1], digitsToModify=1, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=3)

    # add 3
    showInstructions(text=["Next up is add 3. Let's begin."])
    runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=1, feedback=True, saveData=True, practiceTrials=1, digits=3, digitChange=[3], digitsToModify=1, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=3)

    # add 4
    showInstructions(text=["Next up is add 4. Let's begin."])
    runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=1, feedback=True, saveData=True, practiceTrials=1, digits=3, digitChange=[4], digitsToModify=1, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=3)

    # add 6
    showInstructions(text=["Finally, the most difficult: add 6. Let's begin."])
    runMentalMathBlock(taskName='mentalMathUpdating', blockType='practice', trials=1, feedback=True, saveData=True, practiceTrials=1, digits=3, digitChange=[6], digitsToModify=1, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=3)

    # practice updating choice training
    showInstructions(text=[
    "You've tried different difficulty levels (easiest to most difficult: add 0, 1, 3, 4, 6). From now on, two options will be shown at a time and you'll have to choose which one you want to do. For example, add 1 or add 3?", "Use the F and J keys to choose, and the D F J K to do the task.",
    "Let's practice. Try choosing different options to understand how the choice task works."])

    if info['expCondition'] == 'training':
        showInstructions(text=
        ["Sometimes, your choices will earn you money. When you receive money and how much you receive depend ONLY ON YOUR CHOICES, not how well you do on the option you've chosen.",
        "For example, if you choose add 3 over add 4, how well you do on your chosen task (add 3) does not DIRECTLY affect how much money you earn. You might do poorly (e.g., 0% correct) after making this particular choice, but you'll still receive all the money (Amazon voucher) you've earned as long as your OVERALL performance is good (more than 70% correct overall).",
        "Let's practice."])

    runUpdateTrainingBlock(taskName='updateTraining', blockType='practice', reps=1, feedback=True, saveData=True, practiceTrials=3, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, option1=[1], option2=[3, 7], feedbackSound=True)

    showInstructions(text=["You've just practiced the task. If you have any questions, let the research assistant know.", "If not, you'll start the actual choice task where you'll make many choices."])

    # self report
    effortQuestions = ["How effortful do you think the addition task will be?", "How frustrating do you think the addition task will be?", "How boring do you think the addition task will be?", "How much do you think you'll like the addition task?", "How well do you think you'll do on the addition task?", "How tired do you think you'll feel after doing the addition task?"]
    random.shuffle(effortQuestions)
    presentQuestions(questionName='selfReport', questionList=effortQuestions, blockType='preUpdate', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])

    showInstructions(text=["Use F and J to choose, and D F J K to do the task. Let's begin."])

    ''' actual task '''
    runUpdateTrainingBlock(taskName='updateTraining', blockType='actual', reps=200, feedback=True, saveData=True, practiceTrials=3, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, option1=[0, 1, 3, 4, 6], option2=[0, 1, 3, 4, 6], feedbackSound=True)

    # post task difficulty
    effortQuestions = ["How effortful is the addition task now?", "How frustrating is the addition task now?", "How boring is the addition task now?", "How much are you liking the addition task now?", "How well do you think you are doing on the addition task now?", "I'm mentally fatigued now."]
    random.shuffle(effortQuestions)
    presentQuestions(questionName='selfReport', questionList=effortQuestions, blockType='postUpdate', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])


#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################

# runEffortRewardChoiceBlock(taskName='effortTraining', blockType='post', reps=1, feedback=True, saveData=True, practiceTrials=0, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, reward=[11, 12, 13, 14, 15], effort=[3, 5, 7, 9, 11])
#
# runSwitchTrainingBlock(taskName='switchTraining', blockType='actual', reps=200, feedback=True, saveData=True, practiceTrials=10, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, option1=[0, 0.1, 0.3, 0.5, 0.7], option2=[0, 0.1, 0.3, 0.5, 0.7])
#
# runUpdateTrainingBlock(taskName='updateTraining', blockType='actual', reps=200, feedback=True, saveData=True, practiceTrials=3, titrate=False, rtMaxFrames=300, blockMaxTimeSeconds=300, experimentMaxTimeSeconds=None, option1=[0, 1, 3, 4, 6], option2=[0, 1, 3, 4, 6])
#
# showCredit()




''' START EXPERIMENT HERE '''
def startExperimentSection():
    pass

# if sendTTL:
#    port.setData(0) # make sure all pins are low before experiment
#
# showInstructions(text=[
# " ", # black screen at the beginning
# "Welcome to today's experiment! Before we begin, please answer a few questions about yourself."])
#
# getDemographics() # get demographics (gender, ses, ethnicity)
#
# showInstructions(text=
# ["We are studying how people make decisions about different cognitive tasks. You'll do a few different tasks, and will have opportunities to earn credits/money during the experiment.",
# "If you have any questions during the experiment, raise/wave your hands and the research assistant will help you."])
#
# choiceTaskPre()

if info['expCondition'] == 'training':
    showInstructions(["Please put on the headphones now. You'll have to wear them from now on."])

if info['taskOrder'] == 'switch-update':
    switchingTrainingTask()
    updatingTrainingTask()
elif info['taskOrder'] == 'update-switch':
    updatingTrainingTask()
    switchingTrainingTask()

if info['expCondition'] == 'training':
    showInstructions(["You can remove your headphones now."])

choiceTaskPost()

''' questionnaires '''
showInstructions(text=["Now you'll answer a few questions about yourself."])
showAllQuestionnaires()

showInstructions(text=["Now you'll answer a few questions about specifically the letter-number and mental addition tasks you completed earlier on. What do you think about those two tasks, overall?"])
effortQuestions = ["How effortful were the tasks?", "How frustrating were the tasks?", "How boring were the tasks?", "How much did you like the tasks?", "How well do you think you've done on the tasks?", "How much tiring or fatiguing were the tasks?"]
random.shuffle(effortQuestions)
presentQuestions(questionName='selfReport', questionList=effortQuestions, blockType='post', saveData=True, rtMaxFrames=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'])

''' show credits earned '''
showCredit()

''' experiment end '''
showInstructions(text=["That's the end of the experiment. Thanks so much for participating in our study!"])

if sendTTL:
    port.setData(255) # mark end of experiment

win.close()
core.quit() # quit PsychoPy
