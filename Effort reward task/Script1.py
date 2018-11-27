"""
Written by Hause Lin
Tested in PsychoPy 1.90.2 (MacOS)
Last modified by Hause Lin 26-11-18 3:27 PM hauselin@gmail.com
"""

import pandas as pd
import numpy as np
import random, os, time
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import visual, core, event, data, gui, logging, parallel, monitors, sound
from scipy import stats
pd.set_option('display.max_colwidth', 60, 'display.expand_frame_repr', False, 'display.max_rows', 20)

# set DEBUG mode: if True, participant ID will be 999 and display will not be fullscreen. If False, will have to provide participant ID and will be in fullscreen mode
DEBUG = False
qualtricsDebriefLink = 'https://utorontopsych.az1.qualtrics.com/jfe/form/SV_6R7pk1abC6oyIq9'
# qualtricsDebriefLink = None
sendTTL = False # whether to send TTL pulses to acquisition computer
parallelPortAddress = 49168 # set parallel port address (EEG3: 49168, EEG1: 57360)
screenRefreshRate = 60 # screen refresh rate
monitor = 'iMac' # display name (set up beforehand in PsychoPy preferences/settings)
# monitor = 'BehavioralLab'
stimulusDir = 'Stimuli' + os.path.sep  # stimulus directory/folder/path
event.globalKeys.add(key="escape", func=core.quit, modifiers=["ctrl"]) # Ctrl+Esc to quit at any point without saving data

# EXPERIMENT SET UP
info = {} # create empty dictionary to store stuff

if DEBUG:
    fullscreen = False #set fullscreen variable = False
    # logging.console.setLevel(logging.DEBUG)
    info['participant'] = random.randint(999, 999) #let 999 = debug participant no.
    info['age'] = 18
else: #if DEBUG is not False... (or True)
    fullscreen = True #set full screen
    # logging.console.setLevel(logging.WARNING)
    info['participant'] = '' #dict key to store participant no.
    info['age'] = ''
    # present dialog to collect info
    dlg = gui.DlgFromDict(info) #create a dialogue box (function gui)
    if not dlg.OK: # if dialogue response is NOT OK, quit
        core.quit()

# change type
info['participant'] = int(info['participant'])
info['age'] = int(info['age'])
info['scriptDate'] = "191018"  # when was script last modified
info['screenRefreshRate'] = screenRefreshRate

info['fixationS'] = 1.5 # fixation cross duration (seconds)
info['fixationFrames'] = int(info['fixationS'] * screenRefreshRate) # fixation cross (frames)

#info['postFixationFrames'] = 36 #frames (600ms)
#info['postFixationFrames'] = np.arange(36, 43, 1) #36 frames to 42 frames (600 ms to 700ms)
# post fixation frame number to be drawn from exponential distribution (36 to 42 frames)
# f = stats.expon.rvs(size=10000, scale=0.035, loc=0.3) * 100
# f = np.around(f)
# f = f[f <= 43] # max
# f = f[f >= 36] # min
# info['postFixationFrames'] = f

info['targetS'] = 4  # how long stimulus is shown
info['targetFrames'] = info['targetS'] * screenRefreshRate

info['blockEndPauseS'] = 0.75 # seconds
info['blockEndPauseFrames'] = int(info['blockEndPauseS'] * screenRefreshRate) # frames
info['feedbackTimeS'] = 1.0 # seconds
info['feedbackTimeFrames'] = int(info['feedbackTimeS'] * screenRefreshRate) # frames

info['startTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #create str of current date/time
info['endTime'] = '' # to be saved later on

# intertrial interval (drawn from exponential distribution)
seconds = stats.expon.rvs(size=10000, scale=0.4)  # exponential distribution
# seconds = np.around(seconds/0.05) * 0.05  # round to nearest 0.05
seconds = seconds[seconds <= 0.9]  # max
seconds = seconds[seconds >= 0.4]  # min
info['ITIDurationS'] = seconds

globalClock = core.Clock() # create and start global clock to track OVERALL elapsed time
ISI = core.StaticPeriod(screenHz=screenRefreshRate) # function for setting inter-trial interval later

# create window to draw stimuli on
win = visual.Window(size=(900, 600), fullscr=fullscreen, units='norm', monitor=monitor, colorSpace='rgb', color=(-1, -1, -1))
#create mouse
mouse = event.Mouse(visible=False, win=win)
mouse.setVisible(0) # make mouse invisible

if qualtricsDebriefLink is not None:
    import webbrowser
    webURL = qualtricsDebriefLink + "?participant=" + str(info['participant']) # open using default web browser
    webbrowser.open_new(webURL)

try:
    feedbackTwinkle = sound.Sound(stimulusDir + 'twinkle.wav')
    feedbackTwinkle.setVolume(0.1)
except:
    pass

if sendTTL:
    port = parallel.ParallelPort(address=parallelPortAddress)
    port.setData(0) #make sure all pins are low

def runDotMotionBlock(taskName='dotMotion', blockType='', demandSelectionEffortLevel=None, effortLevel=None, trials=[5, 5], dotDirections=[0, 90, 180, 270], nDots=[25, 500], coherence=[0.2, 0.2], dotFrames=[3, 3], speed=[0.01, 0.01], dotSize=[3, 3], fieldSize=[1, 1], feedback=False, falseFeedback=False, saveData=True, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.0, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False):
    '''Run a block of trials.
    blockType: custom name of the block; if blockType is set to 'practice', then no TTLs will be sent and the number of trials to run will be determined by argument supplied to parameter practiceTrials.
    feedback: whether feedback is presented or not
    saveData = whether to save data to csv file
    practiceTrials: no. of practice trials to run
    titrate: whether to adjust difficulty of task based on performance; if set to True, subsequent targetFrames (max response time) for subsequent blocks will be affected
    rtMaxS: max rt (in seconds); default is None, which takes value from info['targetS']; if a value is provided, default will be overwritten
    blockMaxTimeSeconds: end block if overall time of BLOCK (in seconds) has passed
    experimentMaxTimeSeconds: end block if overall time of EXPERIMENT (in seconds) has passed
    feedbackS: no. of seconds to show feedback
    rewardSchedule: how frequently to show feedback (after 1/2/3 etc. consecutive trials)
    feedbackSound: whether to play feedback twinkle
    pauseAfterMissingNTrials: pause task if missed N responses
    '''

    global info
    info[taskName] = pd.DataFrame()

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], taskName) # saved after each trial

    mouse.setVisible(0) #make mouse invisible

    # Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True

    # set up dataframe with individual trials
    trialsInBlock = pd.DataFrame()

    for j in range(len(trials)):
        tempTrials = pd.DataFrame(index=np.arange(int(trials[j])))
        tempTrials['effortLevel'] = j
        trialsInBlock = pd.concat([trialsInBlock, tempTrials]).reset_index(drop=True)
    # print(trialsInBlock)

    for j in range(len(trials)):
        trialsInBlock.loc[trialsInBlock.effortLevel == j, "nDots"] = int(nDots[j])
        trialsInBlock.loc[trialsInBlock.effortLevel == j, "coherence"] = coherence[j]
        trialsInBlock.loc[trialsInBlock.effortLevel == j, "dotFrames"] = int(dotFrames[j])
        trialsInBlock.loc[trialsInBlock.effortLevel == j, "speed"] = speed[j]
        trialsInBlock.loc[trialsInBlock.effortLevel == j, "dotSize"] = dotSize[j]
        trialsInBlock.loc[trialsInBlock.effortLevel == j, "fieldSize"] = fieldSize[j]
    # print(trialsInBlock)

    trialsInBlock['dotDirections'] = np.random.choice(dotDirections, np.sum(trials), replace=True)  # randomly assign dots to move left, right, up, or down on each trial
    trialsInBlock = trialsInBlock.reindex(np.random.permutation(trialsInBlock.index)).reset_index(drop=True)  # shuffle
    # print(trialsInBlock)

    # generate false feedback
    trialsInBlock['accFalse'] = np.nan
    effortLevelAccRates = [0.90, 0.45, 0.23, 0.12, 0.06, 0.03, 0.01]  # prob of getting correct responses at each effort level
    for j in range(len(trials)):  # for each effort level
        # j = 1
        tempN = sum(trialsInBlock.effortLevel == j)  # number of trials
        tempAcc = effortLevelAccRates[j]  # false accurate prob

        # solution 1: random
        tempFalseAcc = np.random.choice([1, 0], size=tempN, p=[tempAcc, 1-tempAcc])
        trialsInBlock.loc[trialsInBlock.effortLevel == j, "accFalse"] = tempFalseAcc
    # print(trialsInBlock)

    # store info in dataframe
    trialsDf = pd.DataFrame(index=np.arange(np.sum(trials)))  # create empty dataframe to store trial info
    trialsDf = pd.concat([trialsDf, trialsInBlock], axis=1) # join dataframes
    # print trialsDf

    if demandSelectionEffortLevel is not None:
        trialsDf = trialsDf[trialsDf.effortLevel == demandSelectionEffortLevel]
        trialsDf = trialsDf.reindex(np.random.permutation(trialsDf.index)).reset_index(drop=True)  # shuffle

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
    trialsDf['refreshRate'] = screenRefreshRate
    trialsDf['fixationFrames'] = info['fixationFrames']
    trialsDf['fixationS'] = info['fixationS']

    # store parameter arguments into dataframe
    trialsDf['trialNo'] = range(1, trialsDf.shape[0] + 1) # add trialNo
    trialsDf['blockType'] = blockType # add blockType
    trialsDf['task'] = taskName
    if rtMaxS is not None:
        rtMaxS = float(rtMaxS)
        trialsDf['targetS'] = rtMaxS
        trialsDf['targetFrames'] = int(rtMaxS * screenRefreshRate)

    # create variables to store data later
    trialsDf['blockNumber'] = 0 # add blockNumber
    trialsDf['elapsedTime'] = np.nan
    trialsDf['resp'] = None
    trialsDf['rt'] = np.nan
    trialsDf['iti'] = np.nan
    trialsDf['responseTTL'] = np.nan
    # trialsDf['choice'] = np.nan
    trialsDf['overallTrialNum'] = 0 # cannot use np.nan because np.nan is a float, not int!
    trialsDf['keypress'] = None
    trialsDf['acc'] = 0
    trialsDf['creditsEarned'] = 0

    # running accuracy and rt
    runningTallyAcc = []
    runningTallyRt = []
    rewardScheduleTrackerAcc = 0

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
    # [1.0,-1,-1] is red; #[1, 1, 1] is white; [-.3, -.3, -.3] is grey
    fixation = visual.TextStim(win=win, units='norm', height=0.15, ori=0, name='target', text='+', font='Verdana', colorSpace='rgb255', color=[255, 255, 255], opacity=1)

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
                targetFramesCurrentTrial = int(rtMaxS * screenRefreshRate)  # try using parameter argument rtMaxS
            except:
                try:
                    targetFramesCurrentTrial = int(info['targetFrames']) # try reading from info dictionary
                except:
                    targetFramesCurrentTrial = 180 # if all the above fails, set rt dealine to 180 frames (3 seconds)
        ''' DO NOT EDIT END '''

        #1: draw and show fixation
        effortSymbol = int((thisTrial['effortLevel'] + 1)) * "/"
        fixation.setText(effortSymbol)
        try:
            fixation.setColor(info['thisTrialColourCue'], 'rgb255')
        except:
            fixation.setColor((255, 255, 255), 'rgb255')
        fixation.setAutoDraw(True) #draw fixation on next flips
        for frameN in range(info['fixationFrames']):
            win.flip()
        fixation.setAutoDraw(False) #stop showing fixation

        #3: draw stimuli
        dotPatch = visual.DotStim(win, color=(0.9, 0.9, 0.9), dir=int(thisTrial['dotDirections']), dotSize=int(thisTrial['dotSize']), nDots=int(thisTrial['nDots']), fieldShape='circle', fieldPos=(0.0, 0.0), fieldSize=int(thisTrial['fieldSize']), dotLife=int(thisTrial['dotFrames']), signalDots='different', noiseDots='position', speed=thisTrial['speed'], coherence=thisTrial['coherence']) # noiseDots='direction',  # do the noise dots follow random- 'walk', 'direction', or 'position'
        dotPatch.setAutoDraw(True)

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
                keys = event.getKeys(keyList=['left', 'right', 'up', 'down', 'backslash', 'bracketright'])
                if len(keys) > 0 and trialsDf.loc[i, 'resp'] is None: #if a response has been made
                    trialsDf.loc[i, 'rt'] = respClock.getTime() #store RT
                    trialsDf.loc[i, 'resp'] = keys[0] #store response in pd df
                    trialsDf.loc[i, 'keypress'] = keys[0]

                    if keys[0] == 'left' and int(thisTrial['dotDirections']) == 180:
                        if sendTTL and not blockType == 'practice':
                            port.setData(251) # correct response
                        trialsDf.loc[i, 'acc'] = 1
                    elif keys[0] == 'right' and int(thisTrial['dotDirections']) == 0:
                        if sendTTL and not blockType == 'practice':
                            port.setData(251) # correct response
                        trialsDf.loc[i, 'acc'] = 1
                    elif keys[0] == 'up' and int(thisTrial['dotDirections']) == 90:
                        if sendTTL and not blockType == 'practice':
                            port.setData(251) # correct response
                        trialsDf.loc[i, 'acc'] = 1
                    elif keys[0] == 'down' and int(thisTrial['dotDirections']) == 270:
                        if sendTTL and not blockType == 'practice':
                            port.setData(251) # correct response
                        trialsDf.loc[i, 'acc'] = 1
                    else:
                        if sendTTL and not blockType == 'practice':
                            port.setData(250) #incorrect response
                        trialsDf.loc[i, 'acc'] = 0

                    # save responseTTL
                    if trialsDf.loc[i, 'acc'] == 1:
                        trialsDf.loc[i, 'responseTTL'] = 251
                    elif trialsDf.loc[i, 'acc'] == 0:
                        trialsDf.loc[i, 'responseTTL'] = 250

                    dotPatch.setAutoDraw(False) #remove stimuli from screen
                    win.flip() #clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            trialsDf.loc[i, 'acc'] = 0 # change according for each experiment (0 or np.nan)
            trialsDf.loc[i, 'rt'] = np.nan
            dotPatch.setAutoDraw(False)
            win.flip() #clear screen (remove stuff from screen)

        # append to running accuracy and rt
        runningTallyAcc.append(trialsDf.loc[i, 'acc'])
        runningTallyRt.append(trialsDf.loc[i, 'rt'])

        if sendTTL and not blockType == 'practice':
            port.setData(0) #parallel port: set all pins to low

        trialsDf.loc[i, 'elapsedTime'] = globalClock.getTime() #store total elapsed time in seconds
        trialsDf.loc[i, 'endTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #store current time
        iti = round(random.choice(info['ITIDurationS']), 2) #randomly select an ITI duration
        trialsDf.loc[i, 'iti'] = iti #store ITI duration

        ''' DO NOT EDIT BEGIN '''
        # if any special keys pressed
        if trialsDf.loc[i, 'resp'] == 'backslash':
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] = None
            trialsDf.loc[i, 'keypress'] = None
            if saveData: #if saveData argument is True, then APPEND current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                info[taskName] = info[taskName].append(trialsDf[i:i+1]).reset_index(drop=True)
                np.save("{:03d}-{}-pythonBackup.npy".format(info['participant'], info['startTime']), info)
            win.close()
            core.quit()
        elif trialsDf.loc[i, 'resp'] == 'bracketright':# skip to next block
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'acc'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'resp'] == None
            trialsDf.loc[i, 'keypress'] = None
            win.flip()
            if saveData: #if saveData argument is True, then append current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                info[taskName] = info[taskName].append(trialsDf[i:i+1]).reset_index(drop=True)
                np.save("{:03d}-{}-pythonBackup.npy".format(info['participant'], info['startTime']), info)
            return None

        ''' DO NOT EDIT END '''

        # ISI.complete() #end inter-trial interval

        # collect task ratings
        if collectRating:
            for frameN in range(18):
                win.flip()
            ratingsDf = pd.DataFrame()
            if trialsDf.loc[i, 'resp'] is not None:  # if no response made
                taskQuestions = ["That was the '{}' task. How confident are you of your answer?".format(effortSymbol),
                                 "That was the '{}' task. How much effort did it require?".format(effortSymbol),
                                 "So far, do you feel you're doing well on tasks with the '{}' symbol?".format(effortSymbol)]
                ratingsDf = presentQuestions(questionName=taskName+'_ratings', questionList=taskQuestions, blockType='', saveData=False, rtMaxS=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1, 9], scaleAnchorText=['not at all', 'very much'])

            try:
                ratingsDf_tojoin = ratingsDf[['questionText', 'resp', 'rt']].copy()  # select columns
                ratingsDf_tojoin.columns = "ratingConfidence_" + ratingsDf_tojoin.columns  # rename columns
                for j in ratingsDf_tojoin.columns:  # add columns to trialsDf
                    trialsDf.loc[i, j] = ratingsDf_tojoin.loc[0, j] # confidence

                ratingsDf_tojoin = ratingsDf[['questionText', 'resp', 'rt']].copy()  # select columns
                ratingsDf_tojoin.columns = "ratingEffort_" + ratingsDf_tojoin.columns  # rename columns
                for j in ratingsDf_tojoin.columns:  # add columns to trialsDf
                    trialsDf.loc[i, j] = ratingsDf_tojoin.loc[1, j] # effort

            except:
                columnsToSave_newNames = ['ratingConfidence_' + x for x in ['questionText', 'resp', 'rt']] + ['ratingEffort_' + x for x in ['questionText', 'resp', 'rt']]
                for j in columnsToSave_newNames:  # add columns to trialsDf
                    trialsDf.loc[i, j] = np.nan

            ratingsDf = pd.DataFrame()  # clear dataframe for next trial

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header=True if i == 0 and writeHeader else False, mode='a', index=False) #write header only if index i is 0 AND block is 1 (first block)y
            info[taskName] = info[taskName].append(trialsDf[i:i+1]).reset_index(drop=True)

        # real feedback for trial
        if feedback:
            feedbackFrames = int(feedbackS * screenRefreshRate)
            #stimuli
            accuracyFeedback = visual.TextStim(win=win, units='norm', colorSpace='rgb', color=[1, 1, 1], font='Verdana', text='', height=0.07, wrapWidth=1.4, pos=[0.0, 0.0])

            for frameN in range(18):
                win.flip()

            if trialsDf.loc[i, 'acc'] == 1: # if correct on this trial
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
                        for frameN in range(feedbackFrames):
                            accuracyFeedback.draw()
                            win.flip()
                else: # reward on every trial
                    trialsDf.loc[i, 'creditsEarned'] = 1
                    if feedbackSound:
                        try:
                            feedbackTwinkle.play()
                        except:
                            pass
                    for frameN in range(feedbackFrames):
                        accuracyFeedback.draw()
                        win.flip()
            # elif trialsDf.loc[i, 'resp'] is None and blockType == 'practice':
            elif trialsDf.loc[i, 'resp'] is None:
                accuracyFeedback.setText('respond faster')
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            # elif trialsDf.loc[i, 'acc'] == 0 and blockType == 'practice':
            elif trialsDf.loc[i, 'acc'] == 0:
                accuracyFeedback.setText('wrong')
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            else:
                pass

        # FALSE feedback for trial
        if falseFeedback:
            feedbackFrames = int(feedbackS * screenRefreshRate)
            #stimuli
            accuracyFeedback = visual.TextStim(win=win, units='norm', colorSpace='rgb', color=[1, 1, 1], font='Verdana', text='', height=0.07, wrapWidth=1.4, pos=[0.0, 0.0])

            for frameN in range(18):
                win.flip()

            if trialsDf.loc[i, 'resp'] is None:
                accuracyFeedback.setText('respond faster')
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            elif trialsDf.loc[i, 'accFalse'] == 1: # if correct on this trial
                accuracyFeedback.setText(random.choice(["1 point"]))
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
                        for frameN in range(feedbackFrames):
                            accuracyFeedback.draw()
                            win.flip()
                else: # reward on every trial
                    trialsDf.loc[i, 'creditsEarned'] = 1
                    if feedbackSound:
                        try:
                            feedbackTwinkle.play()
                        except:
                            pass
                    for frameN in range(feedbackFrames):
                        accuracyFeedback.draw()
                        win.flip()
            elif trialsDf.loc[i, 'accFalse'] == 0:
                accuracyFeedback.setText('0 points')
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            else:
                pass

        # ITI
        for frameN in range(int(iti * screenRefreshRate)):
            win.flip()

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

    # end of block
    for frameN in range(30):
        win.flip() #wait at the end of the block

    if saveData: # save info at the end of block
        np.save("{:03d}-{}-pythonBackup.npy".format(info['participant'], info['startTime']), info)

    return trialsDf # return dataframe


def runDemandSelection(taskName='demandSelection', blockType='', trials=[1, 1, 1], trialTypes=['0_1', '0_2', '1_2'], feedback=False, falseFeedback=False, saveData=True, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.0, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False):
    '''Run a block of trials.
    blockType: custom name of the block; if blockType is set to 'practice', then no TTLs will be sent and the number of trials to run will be determined by argument supplied to parameter practiceTrials.
    feedback: whether feedback is presented or not
    saveData = whether to save data to csv file
    practiceTrials: no. of practice trials to run
    titrate: whether to adjust difficulty of task based on performance; if set to True, subsequent targetFrames (max response time) for subsequent blocks will be affected
    rtMaxS: max rt (in seconds); default is None, which takes value from info['targetS']; if a value is provided, default will be overwritten
    blockMaxTimeSeconds: end block if overall time of BLOCK (in seconds) has passed
    experimentMaxTimeSeconds: end block if overall time of EXPERIMENT (in seconds) has passed
    feedbackS: no. of seconds to show feedback
    rewardSchedule: how frequently to show feedback (after 1/2/3 etc. consecutive trials)
    feedbackSound: whether to play feedback twinkle
    pauseAfterMissingNTrials: pause task if missed N responses
    '''

    global info
    info[taskName] = pd.DataFrame()

    # csv filename to store data
    filename = "{:03d}-{}-{}.csv".format(int(info['participant']), info['startTime'], taskName) # saved after each trial

    mouse.setVisible(0) #make mouse invisible

    # Write header to csv or not? Default is not to write header. Try to read csv file from working directory. If fail to read csv (it hasn't been created yet), then the csv has to be created for the study and the header has to be written.
    writeHeader = False
    try: #try reading csv file dimensions (rows = no. of trials)
        pd.read_csv(filename)
    except: #if fail to read csv, then it's trial 1
        writeHeader = True

    # set up dataframe with individual trials
    trialsInBlock = pd.DataFrame()

    for j in range(len(trialTypes)):
        tempTrials = pd.DataFrame(index=np.arange(int(trials[j])))
        tempTrials['trialType'] = trialTypes[j]
        taskEffortList = [int(trialTypes[j][0]), int(trialTypes[j][2])]
        for k in range(int(trials[j])):  # for each trial in this condition, shuffle left right tasks
            random.shuffle(taskEffortList)
            tempTrials.loc[k, 'task1'] = int(taskEffortList[0])
            tempTrials.loc[k, 'task2'] = int(taskEffortList[1])
        trialsInBlock = pd.concat([trialsInBlock, tempTrials]).reset_index(drop=True)
    # trialsInBlock

    # random shuffle trials
    trialsInBlock = trialsInBlock.reindex(np.random.permutation(trialsInBlock.index)).reset_index(drop=True)  # shuffle
    # print trialsInBlock

    # specify number of trials per condition (choice, performance, no reward)
    # pseudorandomly slot norewardTest trials into other trials
    if blockType in ['neutral', 'choice', 'performance']:
        totalTrials = trialsInBlock.shape[0]
        trials_per_condition = {}
        if blockType == "neutral":
            trials_per_condition['choice'] = 20
            trials_per_condition['performance'] = 20
            trials_per_condition['norewardTest'] = 20
        elif blockType == "choice":
            trials_per_condition['choice'] = 28
            trials_per_condition['performance'] = 12
            trials_per_condition['norewardTest'] = 20
        elif blockType == "performance":
            trials_per_condition['choice'] = 12
            trials_per_condition['performance'] = 28
            trials_per_condition['norewardTest'] = 20

        # create vector/column indicating
        tempConditionsList = [[x] * trials_per_condition[x] for x in trials_per_condition.keys()]
        tempConditionsList2 = tempConditionsList[0] + tempConditionsList[1] + tempConditionsList[2]
        random.shuffle(tempConditionsList2)
        trialsInBlock['trialCondition'] = tempConditionsList2

        # put in separate dataframes
        df_norewardTest = trialsInBlock.loc[trialsInBlock['trialCondition'] == "norewardTest", :].reset_index(drop=True)
        df_choicePerformance = trialsInBlock.loc[trialsInBlock['trialCondition'] != "norewardTest", :].reset_index(
            drop=True)

        # generate row indices for norewardTest trials
        trialIndex_norewardTest = np.linspace(start=random.sample([0, 1, 2], 1)[0], stop=
        random.sample([totalTrials - 1, totalTrials - 2, totalTrials - 3], 1)[0],
                                              num=trials_per_condition['norewardTest'])
        trialIndex_norewardTest = trialIndex_norewardTest.astype(int)

        for x in range(len(trialIndex_norewardTest)):
            if x > 0 and x < (len(trialIndex_norewardTest) - 1):
                trialIndex_norewardTest[x] = trialIndex_norewardTest[x] + random.sample([-1, 0, 1], 1)[0]
        print(trialIndex_norewardTest)  # randomized norewardTest trial indices

        # slot norewardTest trials pseudorandomly into df_choicePerformance
        # generate reward per trial
        trialsInBlockNew = pd.DataFrame()
        for x in range(totalTrials):
            if x in trialIndex_norewardTest:
                tempTrials = df_norewardTest.iloc[[0]]
                df_norewardTest.drop([0], inplace=True)  # remove selected trial
                df_norewardTest.reset_index(drop=True, inplace=True)  # reset index
                trialsInBlockNew = pd.concat([trialsInBlockNew, tempTrials]).reset_index(drop=True)
            else:
                tempTrials = df_choicePerformance.iloc[[0]]
                df_choicePerformance.drop([0], inplace=True)  # remove selected trial
                df_choicePerformance.reset_index(drop=True, inplace=True)  # reset index
                trialsInBlockNew = pd.concat([trialsInBlockNew, tempTrials]).reset_index(drop=True)

        trialsInBlockNew['falseReward'] = np.nan
        trialsInBlock = trialsInBlockNew
    elif blockType == 'neutralPractice':
        trialsInBlock['trialCondition'] = "norewardTest"
    elif blockType == 'choicePractice':
        trialsInBlock['trialCondition'] = "choice"
    elif blockType == 'performancePractice':
        trialsInBlock['trialCondition'] = "performance"
    else:
        trialsInBlock['trialCondition'] = blockType
        trialsInBlock['falseReward'] = np.nan
    # print(trialsInBlock)
    # print(trialsInBlock.groupby(['trialCondition']).agg(['count']))

    # store info in dataframe
    trialsDf = pd.DataFrame(index=np.arange(np.sum(trials)))  # create empty dataframe to store trial info
    trialsDf = pd.concat([trialsDf, trialsInBlock], axis=1)  # join dataframes
    # print trialsDf

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
    trialsDf['refreshRate'] = screenRefreshRate
    trialsDf['fixationFrames'] = info['fixationFrames']
    trialsDf['fixationS'] = info['fixationS']

    # store parameter arguments into dataframe
    trialsDf['trialNo'] = range(1, trialsDf.shape[0] + 1) # add trialNo
    trialsDf['blockType'] = blockType # add blockType
    trialsDf['task'] = taskName
    if rtMaxS is not None:
        rtMaxS = float(rtMaxS)
        trialsDf['targetS'] = rtMaxS
        trialsDf['targetFrames'] = int(rtMaxS * screenRefreshRate)

    # create variables to store data later
    trialsDf['blockNumber'] = 0  # add blockNumber
    trialsDf['elapsedTime'] = np.nan
    trialsDf['resp'] = None
    trialsDf['choice'] = np.nan
    trialsDf['rt'] = np.nan
    trialsDf['iti'] = np.nan
    trialsDf['responseTTL'] = np.nan
    # trialsDf['choice'] = np.nan
    trialsDf['overallTrialNum'] = 0  # cannot use np.nan because np.nan is a float, not int!
    trialsDf['keypress'] = None
    trialsDf['choiceLowHighEffort'] = 0
    trialsDf['creditsEarned'] = 0
    trialsDf['accFalseDotMotion'] = np.nan  # to keep track of false feedback

    # running accuracy and rt
    runningTallyAcc = []
    runningTallyRt = []
    rewardScheduleTrackerAcc = 0

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

    # print trialsDf

    # create stimuli that are constant for entire block
    # draw stimuli required for this block
    # [1.0,-1,-1] is red; #[1, 1, 1] is white; [-.3, -.3, -.3] is grey
    fixation = visual.TextStim(win=win, units='norm', height=0.15, ori=0, name='fixation', text='+', font='Verdana', colorSpace='rgb255', color=[150, 150, 150], opacity=1)
    leftOption = visual.TextStim(win=win, units='norm', height=0.15, ori=0, name='leftOption', text='+', font='Verdana', colorSpace='rgb255', color=[255, 255, 255], opacity=1, pos=(-0.2, 0.06))
    rightOption = visual.TextStim(win=win, units='norm', height=0.15, ori=0, name='rightOption', text='+', font='Verdana', colorSpace='rgb255', color=[255, 255, 255], opacity=1, pos=(0.2, 0.06))

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
                targetFramesCurrentTrial = int(rtMaxS * screenRefreshRate)  # try using parameter argument rtMaxS
            except:
                try:
                    targetFramesCurrentTrial = int(info['targetFrames']) # try reading from info dictionary
                except:
                    targetFramesCurrentTrial = 180 # if all the above fails, set rt dealine to 180 frames (3 seconds)
        ''' DO NOT EDIT END '''

        # set colour cue (reward or no reward) for this trial
        if thisTrial['trialCondition'] in ["choice", "performance"]:
            thisTrialColourCue = (170, 140, 230)  # pink
            fixation.setText("$")
        elif thisTrial['trialCondition'] == "norewardTest":
            thisTrialColourCue = (80, 170, 240)  # blue
            fixation.setText("o")
        else:
            thisTrialColourCue = (255, 255, 255) # white
            fixation.setText("+")
        info['thisTrialColourCue'] = thisTrialColourCue

        fixation.setColor(thisTrialColourCue, 'rgb255')
        leftOption.setColor(thisTrialColourCue, 'rgb255')
        rightOption.setColor(thisTrialColourCue, 'rgb255')

        #1: draw and show fixation
        fixation.setAutoDraw(True)
        for frameN in range(info['fixationFrames']):
            win.flip()
        fixation.setAutoDraw(False) #stop showing fixation

        #3: draw stimuli
        leftOptionEffortSymbol = int(thisTrial['task1'] + 1) * "/"
        rightOptionEffortSymbol = int(thisTrial['task2'] + 1) * "/"
        leftOption.setText(leftOptionEffortSymbol)
        rightOption.setText(rightOptionEffortSymbol)
        
        leftOption.setAutoDraw(True) #draw fixation on next flips
        rightOption.setAutoDraw(True)  # draw fixation on next flips

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
                keys = event.getKeys(keyList=['left', 'right', 'backslash', 'bracketright'])
                if len(keys) > 0 and trialsDf.loc[i, 'resp'] is None: #if a response has been made
                    trialsDf.loc[i, 'rt'] = respClock.getTime() #store RT
                    trialsDf.loc[i, 'resp'] = keys[0] #store response in pd df
                    trialsDf.loc[i, 'keypress'] = keys[0]

                    if keys[0] == 'left' and thisTrial['task1'] > thisTrial['task2']:
                        if sendTTL and not blockType == 'practice':
                            port.setData(251)
                        trialsDf.loc[i, 'choiceLowHighEffort'] = 1
                        trialsDf.loc[i, 'choice'] = thisTrial['task1']
                    elif keys[0] == 'right' and thisTrial['task2'] > thisTrial['task1']:
                        if sendTTL and not blockType == 'practice':
                            port.setData(251)
                        trialsDf.loc[i, 'choiceLowHighEffort'] = 1
                        trialsDf.loc[i, 'choice'] = thisTrial['task2']
                    elif keys[0] == 'left' and thisTrial['task1'] < thisTrial['task2']:
                        if sendTTL and not blockType == 'practice':
                            port.setData(250)
                        trialsDf.loc[i, 'choiceLowHighEffort'] = 0
                        trialsDf.loc[i, 'choice'] = thisTrial['task1']
                    elif keys[0] == 'right' and thisTrial['task2'] < thisTrial['task1']:
                        if sendTTL and not blockType == 'practice':
                            port.setData(250)
                        trialsDf.loc[i, 'choiceLowHighEffort'] = 0
                        trialsDf.loc[i, 'choice'] = thisTrial['task2']
                    else:
                        if sendTTL and not blockType == 'practice':
                            port.setData(249) #invalid response
                        trialsDf.loc[i, 'choiceLowHighEffort'] = np.nan

                    # save responseTTL
                    if trialsDf.loc[i, 'choice'] == np.max([thisTrial['task1'], thisTrial['task2']]):
                        trialsDf.loc[i, 'responseTTL'] = 251 # chose high effort
                    elif trialsDf.loc[i, 'choice'] == np.min([thisTrial['task1'], thisTrial['task2']]):
                        trialsDf.loc[i, 'responseTTL'] = 250 # chose low effort
                    elif np.isnan(trialsDf.loc[i, 'choice']):
                        trialsDf.loc[i, 'responseTTL'] = 249 # invalid response

                    leftOption.setAutoDraw(False) #remove stimuli from screen
                    rightOption.setAutoDraw(False)
                    win.flip() #clear screen (remove stuff from screen)
                    break #break out of the for loop when response has been made (ends trial and moves on to intertrial interval)
            win.flip()

        #if not response has been made within allowed time, remove stimuli and record accuracay
        if trialsDf.loc[i, 'resp'] is None: #if no response made
            trialsDf.loc[i, 'choiceLowHighEffort'] = np.nan # change according for each experiment (0 or np.nan)
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'choice'] = np.nan
            leftOption.setAutoDraw(False)  # remove stimuli from screen
            rightOption.setAutoDraw(False)
            win.flip() #clear screen (remove stuff from screen)

        # generate false feedback
        if falseFeedback:
            if trialsDf.loc[i, 'trialCondition'] == "choice" and trialsDf.loc[i, 'choiceLowHighEffort'] == 0:
                trialsDf.loc[i, 'falseReward'] = abs(np.random.normal(loc=2.0, scale=0.5, size=1))
            elif trialsDf.loc[i, 'trialCondition'] == "choice" and trialsDf.loc[i, 'choiceLowHighEffort'] == 1:
                trialsDf.loc[i, 'falseReward'] = abs(np.random.normal(loc=4.0, scale=0.5, size=1))
            elif trialsDf.loc[i, 'trialCondition'] == "performance" and trialsDf.loc[i, 'choiceLowHighEffort'] == 0:
                trialsDf.loc[i, 'falseReward'] = abs(np.random.normal(loc=4.0, scale=0.5, size=1))
            elif trialsDf.loc[i, 'trialCondition'] == "performance" and trialsDf.loc[i, 'choiceLowHighEffort'] == 1:
                trialsDf.loc[i, 'falseReward'] = abs(np.random.normal(loc=2.0, scale=0.5, size=1))

            # if trialsDf.loc[i, 'choiceLowHighEffort'] == 0:  # easier option chosen
            #     trialsDf.loc[i, 'accFalseDotMotion'] = np.random.choice([1, 0], size=1, p=[0.90, 0.10])
            # elif trialsDf.loc[i, 'choiceLowHighEffort'] == 1:  # harder option chosen
            #     trialsDf.loc[i, 'accFalseDotMotion'] = np.random.choice([1, 0], size=1, p=[0.45, 0.55])

        # append to running accuracy and rt
        runningTallyAcc.append(trialsDf.loc[i, 'choiceLowHighEffort'])
        runningTallyRt.append(trialsDf.loc[i, 'rt'])

        if sendTTL and not blockType == 'practice':
            port.setData(0) #parallel port: set all pins to low

        trialsDf.loc[i, 'elapsedTime'] = globalClock.getTime() #store total elapsed time in seconds
        trialsDf.loc[i, 'endTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #store current time
        iti = round(random.choice(info['ITIDurationS']), 2) #randomly select an ITI duration
        trialsDf.loc[i, 'iti'] = iti #store ITI duration

        ''' DO NOT EDIT BEGIN '''
        # if any special keys pressed
        if trialsDf.loc[i, 'resp'] in ['backslash', 'bracketright']:
            trialsDf.loc[i, 'responseTTL'] = np.nan
            trialsDf.loc[i, 'choice'] = np.nan
            trialsDf.loc[i, 'choiceLowHighEffort'] = np.nan
            trialsDf.loc[i, 'rt'] = np.nan
            trialsDf.loc[i, 'keypress'] = None
            if saveData: #if saveData argument is True, then APPEND current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header=True if i == 0 and writeHeader else False, mode='a', index=False) #write header only if index i is 0 AND block is 1 (first block)
                info[taskName] = info[taskName].append(trialsDf[i:i+1]).reset_index(drop=True)
                np.save("{:03d}-{}-pythonBackup.npy".format(info['participant'], info['startTime']), info)
            if trialsDf.loc[i, 'resp'] == 'bracketright':
                trialsDf.loc[i, 'resp'] = None
                win.flip()
                return None
            elif trialsDf.loc[i, 'resp'] == 'backslash':
                trialsDf.loc[i, 'resp'] = None
                win.close()
                core.quit()
        ''' DO NOT EDIT END '''

        '''RUN DOT MOTION TASK'''
        taskDf = pd.DataFrame()  # clear dataframe for next trial
        if trialsDf.loc[i, 'resp'] is not None:
            effortTaskIndex = int(trialsDf.loc[i, 'choice'])
            taskDf = runDotMotionBlock(taskName='dst_dotMotion_trials', blockType=i+1, demandSelectionEffortLevel=effortTaskIndex, effortLevel=list(range(difficultyLevels)), trials=[1]*difficultyLevels, dotDirections=[0, 90, 180, 270], nDots=info['nDots'], coherence=info['coherence'], dotFrames=info['dotFrames'], speed=info['speed'], dotSize=info['dotSize'], fieldSize=info['fieldSize'], feedback=False, falseFeedback=False, saveData=False, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.0, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

        columnsToSave = ['effortLevel', 'nDots', 'coherence', 'dotFrames', 'speed', 'dotSize', 'fieldSize', 'dotDirections', 'resp', 'rt', 'acc']
        columnsToSave_newNames = ["dotMotion_" + x for x in columnsToSave]

        try:
            taskDf_tojoin = taskDf[columnsToSave] # select columns
            taskDf_tojoin.columns = columnsToSave_newNames  # rename columns
            for j in columnsToSave_newNames: # add columns to trialsDf
                trialsDf.loc[i, j] = taskDf_tojoin.loc[0, j]
        except:
            for j in columnsToSave_newNames: # add columns to trialsDf
                trialsDf.loc[i, j] = np.nan

        if np.isnan(trialsDf.loc[i, 'dotMotion_rt']):
            trialsDf.loc[i, 'falseReward'] = np.nan

        # print trialsDf
        taskDf = pd.DataFrame()  # clear dataframe for next trial
        '''end dot motion task'''

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header=True if i == 0 and writeHeader else False, mode='a', index=False) #write header only if index i is 0 AND block is 1 (first block)
            info[taskName] = info[taskName].append(trialsDf[i:i+1]).reset_index(drop=True)
        # ISI.complete() #end inter-trial interval

        # feedback for trial
        if feedback:
            feedbackFrames = int(feedbackS * screenRefreshRate)
            #stimuli
            accuracyFeedback = visual.TextStim(win=win, units='norm', colorSpace='rgb', color=[1, 1, 1], font='Verdana', text='', height=0.07, wrapWidth=1.4, pos=[0.0, 0.0])

            for frameN in range(18):
                win.flip()

            if trialsDf.loc[i, 'dotMotion_acc'] == 1: # if correct on this trial
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
                        for frameN in range(feedbackFrames):
                            accuracyFeedback.draw()
                            win.flip()
                else: # reward on every trial
                    trialsDf.loc[i, 'creditsEarned'] = 1
                    if feedbackSound:
                        try:
                            feedbackTwinkle.play()
                        except:
                            pass
                    for frameN in range(feedbackFrames):
                        accuracyFeedback.draw()
                        win.flip()
            # elif trialsDf.loc[i, 'resp'] is None and blockType == 'practice':
            elif trialsDf.loc[i, 'resp'] is None:
                accuracyFeedback.setText('respond faster')
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            elif np.isnan(trialsDf.loc[i, 'dotMotion_rt']):
                accuracyFeedback.setText('respond faster')
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            elif trialsDf.loc[i, 'dotMotion_acc'] == 0:
                accuracyFeedback.setText('wrong')
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            else:
                pass

        # FALSE feedback for trial
        if falseFeedback:
            feedbackFrames = int(feedbackS * screenRefreshRate)
            # stimuli
            accuracyFeedback = visual.TextStim(win=win, units='norm', colorSpace='rgb', color=[1, 1, 1], font='Verdana', text='', height=0.07, wrapWidth=1.4, pos=[0.0, 0.0])

            for frameN in range(18):
                win.flip()

            if trialsDf.loc[i, 'resp'] is None or np.isnan(trialsDf.loc[i, 'dotMotion_rt']):
                accuracyFeedback.setText('respond faster')
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            elif trialsDf.loc[i, "trialCondition"] == "choice" and trialsDf.loc[i, 'falseReward'] >= 0:
                optionChosenSymbol = int((trialsDf.loc[i, "choiceLowHighEffort"] + 1)) * '/'
                accuracyText = "your CHOICE of {} earned you {:.1f} points".format(optionChosenSymbol, trialsDf.loc[i, 'falseReward'])
                accuracyFeedback.setText(accuracyText)
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            elif trialsDf.loc[i, "trialCondition"] == "performance" and trialsDf.loc[i, 'falseReward'] >= 0:
                accuracyText = "your PERFORMANCE earned you {:.1f} points".format(trialsDf.loc[i, 'falseReward'])
                accuracyFeedback.setText(accuracyText)
                for frameN in range(feedbackFrames):
                    accuracyFeedback.draw()
                    win.flip()
            # elif trialsDf.loc[i, 'accFalseDotMotion'] == 1:  # if correct on this trial
            #     accuracyFeedback.setText(random.choice(["+1 point"]))
            #     if rewardSchedule is not None:
            #         rewardScheduleTrackerAcc += 1  # update tracker
            #         if rewardScheduleTrackerAcc == rewardSchedule:
            #             rewardScheduleTrackerAcc = 0  # reset to 0
            #             trialsDf.loc[i, 'creditsEarned'] = 1
            #             if feedbackSound:
            #                 try:
            #                     feedbackTwinkle.play()
            #                 except:
            #                     pass
            #             for frameN in range(feedbackFrames):
            #                 accuracyFeedback.draw()
            #                 win.flip()
            #     else:  # reward on every trial
            #         trialsDf.loc[i, 'creditsEarned'] = 1
            #         if feedbackSound:
            #             try:
            #                 feedbackTwinkle.play()
            #             except:
            #                 pass
            #         for frameN in range(feedbackFrames):
            #             accuracyFeedback.draw()
            #             win.flip()
            # elif trialsDf.loc[i, 'accFalseDotMotion'] == 0:
            #     accuracyFeedback.setText('0 points')
            #     for frameN in range(feedbackFrames):
            #         accuracyFeedback.draw()
            #         win.flip()
            else:
                pass

        # ITI
        for frameN in range(int(iti * screenRefreshRate)):
            win.flip()

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

    # end of block
    for frameN in range(30):
        win.flip() #wait at the end of the block

    if saveData: # save info at the end of block
        np.save("{:03d}-{}-pythonBackup.npy".format(info['participant'], info['startTime']), info)

    return trialsDf # return dataframe


def presentQuestions(questionName='questionnaireName', questionList=['Question 1?', 'Question 2?'], blockType='', saveData=True, rtMaxS=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1,9], scaleAnchorText=['not at all', 'very much'], showAnchors=True):

    global info
    info[questionName] = pd.DataFrame()
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
    if rtMaxS is None:
        trialsDf['targetS'] = 600
        trialsDf['targetFrames'] = trialsDf['targetS'] * screenRefreshRate
    else:
        rtMaxS = float(rtMaxS)
        trialsDf['targetS'] = rtMaxS
        trialsDf['targetFrames'] = rtMaxS * screenRefreshRate

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
    questionText = visual.TextStim(win=win, units='norm', height=0.06, name='target', text='INSERT QUESTION HERE', font='Verdana', colorSpace='rgb', color=[1, 1, 1], opacity=1, pos=(0, 0.2))

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
                keys = event.getKeys(keyList=keysAccepted)
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

        # ITIT
        for frameN in range(int(iti * screenRefreshRate)):
            win.flip()

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
                info[questionName] = info[questionName].append(trialsDf[i:i + 1]).reset_index(drop=True)
            win.close()
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
                info[questionName] = info[questionName].append(trialsDf[i:i + 1]).reset_index(drop=True)
            return None

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
            info[questionName] = info[questionName].append(trialsDf[i:i + 1]).reset_index(drop=True)
        ''' DO NOT EDIT END '''

    instructText.setAutoDraw(False)
    scaleAnchorPointsText.setAutoDraw(False)
    scaleAnchorTextLeftText.setAutoDraw(False)
    scaleAnchorTextRightText.setAutoDraw(False)

    for frameN in range(info['blockEndPauseFrames']):
        win.flip() #wait at the end of the block

    if saveData: # save info at the end of block
        np.save("{:03d}-{}-pythonBackup.npy".format(info['participant'], info['startTime']), info)

    return trialsDf


def showInstructions(text, timeBeforeAutomaticProceed=0, timeBeforeShowingSpace =0):
    '''Show instructions.
    text: Provide a list with instructions/text to present. One list item will be presented per page.
    timeBeforeAutomaticProceed: The time in seconds to wait before proceeding automatically.
    timeBeforeShowingSpace: The time in seconds to wait before showing 'Press space to continue' text.
    '''
    mouse.setVisible(0)
    event.clearEvents()

    # 'Press space to continue' text for each 'page'
    continueText = visual.TextStim(win=win, units='norm', colorSpace='rgb', color=[1, 1, 1], font='Verdana', text="Press space to continue", height=0.04, wrapWidth=1.4, pos=[0.0, 0.0])
    # instructions to be shown
    instructText = visual.TextStim(win=win, units='norm', colorSpace='rgb', color=[1, 1, 1], font='Verdana', text='DEFAULT', height=0.08, wrapWidth=1.4, pos=[0.0, 0.5])

    for i in range(len(text)): # for each item/page in the text list
        instructText.text = text[i] # set text for each page
        if timeBeforeAutomaticProceed == 0 and timeBeforeShowingSpace == 0:
            while not event.getKeys(keyList=['space']):
                continueText.draw(); instructText.draw(); win.flip()
                if event.getKeys(keyList=['backslash']):
                    win.close()
                    core.quit()
                elif event.getKeys(['bracketright']): #if press 7, skip to next block
                    return None
        elif timeBeforeAutomaticProceed != 0 and timeBeforeShowingSpace == 0:
            # clock to calculate how long to show instructions
            # if timeBeforeAutomaticProceed is not 0 (e.g., 3), then each page of text will be shown 3 seconds and will proceed AUTOMATICALLY to next page
            instructTimer = core.Clock()
            while instructTimer.getTime() < timeBeforeAutomaticProceed:
                if event.getKeys(keyList=['backslash']):
                    win.close()
                    core.quit()
                elif event.getKeys(['bracketright']):
                    return None
                instructText.draw(); win.flip()
        elif timeBeforeAutomaticProceed == 0 and timeBeforeShowingSpace != 0:
            instructTimer = core.Clock()
            while instructTimer.getTime() < timeBeforeShowingSpace:
                if event.getKeys(keyList=['backslash']):
                    win.close()
                    core.quit()
                elif event.getKeys(['bracketright']):
                    return None
                instructText.draw(); win.flip()
            win.flip(); event.clearEvents()

    instructText.setAutoDraw(False)
    continueText.setAutoDraw(False)

    for frameN in range(info['blockEndPauseFrames']):
        win.flip() # wait at the end of the block

















###############################################
###############################################
###############################################
###############################################
###############################################
''' START EXPERIMENT HERE '''
def startExperimentSection():
    pass

# define dot motion task parameters
info['nDots'] = [10, 500]
info['dotSize'] = [3, 3]
info['fieldSize'] = [1.0, 1.0]
info['coherence'] = [0.05, 0.05]
# info['coherence'] = [1, 1]  # 100% coherence for testing purposes
info['dotFrames'] = [3, 3]
info['speed'] = [0.01, 0.01]
difficultyLevels = len(info['nDots'])








showInstructions(text=
["Click the left mouse button when you're ready. Then press space to begin.",
 "You'll do several tasks in this experiment. Different tasks will be represented by different symbols: /, //, \ etc.",
 "Try to learn and remember what task each symbol refers to. These symbols will tell you the difficulty level of the upcoming task.",
 "One task is the dot motion detection task. You'll see a cloud of dots moving in random directions, but SOME of them will move in one consistent direction (left, right, up, or down).",
 "When the dots are moving, you have up to 3 seconds to indicate the apparent motion of the cloud of dots by pressing the arrow keys.",
 "DO NOT WAIT until the dots have been removed from the display before you respond. If you didn't respond in time, you'll see the message 'respond faster'.",
 "Sometimes, after you've responded, you'll be asked to indicate how confident you are in your responses and how much effort the task required.",
 "Let's try a few relatively easy examples.",
 "Put your hand on the arrow keys now."
])

# PRACTICE EASY trials with 80% coherence coherence (2 effort levels; 5 reps effort level)
runDotMotionBlock(taskName='dotMotionPracticeEasy', blockType='dotMotionPracticeEasy', trials=[5]*difficultyLevels, dotDirections=[0, 90, 180, 270], nDots=info['nDots'], coherence=[0.8, 0.8], dotFrames=info['dotFrames'], speed=info['speed'], dotSize=info['dotSize'], fieldSize=info['fieldSize'], feedback=True, falseFeedback=False, saveData=True, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.0, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

showInstructions(text=
 ["Now let's practice the actual tasks, which will be more challenging!",
  "In this section, you'll receive points if you respond correctly, and no points if you respond incorrectly."
  ])

# PHASE 1: PRACTICE ACTUAL trials (5 reps per effort level)
runDotMotionBlock(taskName='dotMotionPracticeActual', blockType='dotMotionPracticeActual', trials=[5]*difficultyLevels, dotDirections=[0, 90, 180, 270], nDots=info['nDots'], coherence=info['coherence'], dotFrames=info['dotFrames'], speed=info['speed'], dotSize=info['dotSize'], fieldSize=info['fieldSize'], feedback=False, falseFeedback=True, saveData=True, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.5, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

showInstructions(text=
 ["That's the end of practice. Let's begin the actual task now. In the next section, you won't receive feedback for your performance. If the task feels difficult, just keep trying your best and you'll definitely get better over time."
  ])

# PHASE 1: ACTUAL forced choice trials (2 effort levels; 5 reps per effort level)
runDotMotionBlock(taskName='dotMotionForced', blockType='dotMotionForced', trials=[5]*difficultyLevels, dotDirections=[0, 90, 180, 270], nDots=info['nDots'], coherence=info['coherence'], dotFrames=info['dotFrames'], speed=info['speed'], dotSize=info['dotSize'], fieldSize=info['fieldSize'], feedback=False, falseFeedback=False, saveData=True, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.5, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

# PHASE 1: PRACTICE demand selection without feedback (no choice/performance/no-reward manipulation yet!)
showInstructions(text=
["Now you get to decide which task you prefer to do.",
 "You'll first see two symbols (e.g., / and //) on the left and right of the display. Each symbol represents a task you could do. For example, if you prefer to do the task represented by the symbol on the left of the display, press the left arrow key.",
 "Use the left and right arrow keys to indicate which task you prefer to do.",
 "You'll then do the task you've chosen. Again, use the arrow keys to respond when doing the task.",
 "Let's practice."
])

runDemandSelection(taskName='dotMotionDSTPractice', blockType='dotMotionDSTPractice', trials=[5]*1, trialTypes=['0_1'], feedback=False, falseFeedback=False, saveData=False, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.5, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

# PHASE 1: ACTUAL demand selection without feedback (no choice/performance/no-reward manipulation yet!)
showInstructions(text=["You've finished the practice task. Now, you'll do the actual task."])

runDemandSelection(taskName='dotMotionDSTActual', blockType='dotMotionDSTActual', trials=[20]*1, trialTypes=['0_1'], feedback=False, falseFeedback=False, saveData=True, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.5, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

# PHASE 2: PRACTICE demand selection (reward performance)
showInstructions(text=
["In the next section, you can receive points/rewards for your decisions and task performance.",
 "Different cues ($ or o) and colors will indicate whether reward is available in the next decision. Let's practice to make things clear.",
 "In this practice round, you'll receive rewards based on your TASK PERFORMANCE. If your performance is good, you'll receive more rewards. Your performance is based on a weighted combination of your reaction time and accuracy, so try to respond accurately and quickly to earn as much rewards as you can."
 ])

runDemandSelection(taskName='dotMotionDSTPractice', blockType='performancePractice', trials=[10]*1, trialTypes=['0_1'], feedback=False, falseFeedback=True, saveData=False, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.5, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

# PHASE 2: PRACTICE demand selection (reward choice)
showInstructions(text=
["In the next practice round, you'll receive rewards based on your CHOICE OF TASK (e.g., choosing task /) rather than performance.",
 "Again, try to earn as much rewards as you can."
 ])

runDemandSelection(taskName='dotMotionDSTPractice', blockType='choicePractice', trials=[10]*1, trialTypes=['0_1'], feedback=False, falseFeedback=True, saveData=False, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.5, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

# PHASE 2: PRACTICE demand selection (no reward)
showInstructions(text=["In the next practice round, you won't receive rewards."])

runDemandSelection(taskName='dotMotionDSTPractice', blockType='neutralPractice', trials=[5]*1, trialTypes=['0_1'], feedback=False, falseFeedback=True, saveData=False, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.5, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

# PHASE 2: Actual neutral block
showInstructions(text=
["That's the end of the practice rounds. Let's begin the actual task now.",
 "Remember that different cues will tell you whether rewards will be available in the next decision. You can earn rewards for either good task performance or choice, but you'll only know whether you've been rewarded for performance or choice after completing the task you've chosen.",
 "Try to earn as much rewards as you can in this round."])

# neutral
runDemandSelection(taskName='dotMotionDST', blockType='neutral', trials=[60]*1, trialTypes=['0_1'], feedback=False, falseFeedback=True, saveData=True, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.5, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

showInstructions(text=["You've completed this round."])

def run_dotMotionDST_choiceBlocks():
    showInstructions(text=[
    "Whenever you're ready, you can begin the next round. The rewards may have changed in the next round, but again, try to earn as much rewards as you can."
    ])
    # PHASE 2: Actual choice block
    runDemandSelection(taskName='dotMotionDST', blockType='choice', trials=[60]*1, trialTypes=['0_1'], feedback=False, falseFeedback=True, saveData=True, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.5, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

    showInstructions(text=["You've completed this round."])

def run_dotMotionDST_performanceBlocks():
    showInstructions(text=[
    "Whenever you're ready, you can begin the next round. The rewards may have changed in the next round, but again, try to earn as much rewards as you can."
    ])
    # PHASE 2: Actual performance block
    runDemandSelection(taskName='dotMotionDST', blockType='performance', trials=[60]*1, trialTypes=['0_1'], feedback=False, falseFeedback=True, saveData=True, practiceTrials=5, titrate=False, rtMaxS=3, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.5, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, collectRating=False)

    showInstructions(text=["You've completed this round."])

if info['participant'] % 2 == 0:
    run_dotMotionDST_choiceBlocks()
    run_dotMotionDST_performanceBlocks()
else:
    run_dotMotionDST_performanceBlocks()
    run_dotMotionDST_choiceBlocks()

showInstructions(text=["You've finished all the tasks in the study."])

taskQuestions = ["Overall, how confident were you of your responses?", "Overall, how well do you think you've done?", "Overall, how much did you enjoy the tasks?"]
presentQuestions(questionName='taskPerceptions', questionList=taskQuestions, blockType='finalQuestions', saveData=True, rtMaxS=None, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, scaleAnchors=[1, 9], scaleAnchorText=['not at all', 'very much'])

showInstructions(text=["You'll now answer a few questions using a web browser."])

win.close()
core.quit() # quit PsychoPy