import pandas as pd
import numpy as np
import random, os, time
import itertools as it
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import visual, core, event, data, gui, logging, parallel, monitors, sound
from scipy import stats

# set DEBUG mode: if True, participant ID will be 999 and display will not be fullscreen. If False, will have to provide participant ID and will be in fullscreen mode
DEBUG = True
sendTTL = False # whether to send TTL pulses to acquisition computer
parallelPortAddress = 49168 # set parallel port address (EEG3: 49168, EEG1: 57360)
screenRefreshRate = 60 # screen refresh rate
monitor = 'iMac' # display name (set up beforehand in PsychoPy preferences/settings)
# monitor = 'BehavioralLab'
stimulusDir = 'Stimuli' + os.path.sep  # stimulus directory/folder/path

# EXPERIMENT SET UP
info = {} # create empty dictionary to store stuff
info['scriptDate'] = "141018"
info['screenRefreshRate'] = screenRefreshRate

if DEBUG:
    fullscreen = False #set fullscreen variable = False
    # logging.console.setLevel(logging.DEBUG)
    info['participant'] = random.randint(999, 999) #let 999 = debug participant no.
    info['age'] = 18
else: #if DEBUG is not False... (or True)
    fullscreen = True #set full screen
    # logging.console.setLevel(logging.WARNING)
    info['participant'] = '' #dict key to store participant no.
    info['participant'] = int(info['participant'])
    info['age'] = ''
    info['age'] = int(info['age'])
    # present dialog to collect info
    dlg = gui.DlgFromDict(info) #create a dialogue box (function gui)
    if not dlg.OK: # if dialogue response is NOT OK, quit
        core.quit()

# empty dataframes to append dataframes later on
dataframes = {}
dataframes['dotMotion'] = pd.DataFrame()

info['fixationS'] = 0.5
info['fixationFrames'] = int(info['fixationS'] * screenRefreshRate)

#info['postFixationFrames'] = 36 #frames (600ms)
#info['postFixationFrames'] = np.arange(36, 43, 1) #36 frames to 42 frames (600 ms to 700ms)
# post fixation frame number to be drawn from exponential distribution (36 to 42 frames)
f = stats.expon.rvs(size=10000, scale=0.035, loc=0.3) * 100
f = np.around(f)
f = f[f <= 43] # max
f = f[f >= 36] # min
info['postFixationFrames'] = f

info['targetS'] = 4
info['targetFrames'] = info['targetS'] * screenRefreshRate

info['blockEndPauseS'] = 0.2 # seconds
info['blockEndPauseFrames'] = int(info['blockEndPauseS'] * screenRefreshRate) # frames
info['feedbackTimeS'] = 1.0 # seconds
info['feedbackTimeFrames'] = int(info['feedbackTimeS'] * screenRefreshRate) # frames

info['startTime'] = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())) #create str of current date/time
info['endTime'] = '' # to be saved later on

# iti duration
seconds = stats.expon.rvs(size=10000, scale=0.4) # exponential distribution
seconds = np.around(seconds/0.05) * 0.05 # round to nearest 0.05
seconds = seconds[seconds <= 0.9] # max
seconds = seconds[seconds >= 0.4] # min
info['ITIDurationS'] = seconds

globalClock = core.Clock() # create and start global clock to track OVERALL elapsed time
ISI = core.StaticPeriod(screenHz=screenRefreshRate) # function for setting inter-trial interval later

# create window to draw stimuli on
win = visual.Window(size=(900, 600), fullscr=fullscreen, units='norm', monitor=monitor, colorSpace='rgb', color=(-1, -1, -1))
#create mouse
mouse = event.Mouse(visible=False, win=win)
mouse.setVisible(0) # make mouse invisible

feedbackTwinkle = sound.Sound(stimulusDir + 'twinkle.wav')
feedbackTwinkle.setVolume(0.1)

if sendTTL:
    port = parallel.ParallelPort(address=parallelPortAddress)
    port.setData(0) #make sure all pins are low

def runDotMotionBlock(taskName='dotMotion', blockType='', trials=10, effortProportion=[0.5, 0.5], dotDirections=[0, 180], nDots=[50, 500], coherence=[0.2, 0.2], dotFrames=[3, 3], speed=[0.01, 0.01], feedback=False, saveData=True, practiceTrials=5, titrate=False, rtMaxFrames=240, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.0, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, practiceHelp=False):
    '''Run a block of trials.
    blockType: custom name of the block; if blockType is set to 'practice', then no TTLs will be sent and the number of trials to run will be determined by argument supplied to parameter practiceTrials.
    feedback: whether feedback is presented or not
    saveData = whether to save data to csv file
    practiceTrials: no. of practice trials to run
    titrate: whether to adjust difficulty of task based on performance; if set to True, subsequent targetFrames (max response time) for subsequent blocks will be affected
    rtmaxFrames: max rt (in frames); default is None, which takes value from info['targetFrames']; if a value is provided, default will be overwritten
    blockMaxTimeSeconds: end block if overall time of BLOCK (in seconds) has passed
    experimentMaxTimeSeconds: end block if overall time of EXPERIMENT (in seconds) has passed
    feedbackS: no. of seconds to show feedback
    rewardSchedule: how frequently to show feedback (after 1/2/3 etc. consecutive trials)
    feedbackSound: whether to play feedback twinkle
    pauseAfterMissingNTrials: pause task if missed N responses
    practiceHelp: whether to show what key to press
    '''

    global dataframes

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

    # set up dataframe with individual trials
    trialsInBlock = pd.DataFrame(index=np.arange(trials))  # create empty dataframe to store trial info
    trialsInBlock['effortLevel'] = np.repeat([0, 1],
                                             [int(effortProportion[0] * trials), int(effortProportion[1] * trials)])
    # trialsInBlock

    for j in range(len(nDots)):
        trialsInBlock.loc[trialsInBlock.effortLevel == j, "nDots"] = int(nDots[j])
        trialsInBlock.loc[trialsInBlock.effortLevel == j, "coherence"] = coherence[j]
        trialsInBlock.loc[trialsInBlock.effortLevel == j, "dotFrames"] = int(dotFrames[j])
        trialsInBlock.loc[trialsInBlock.effortLevel == j, "speed"] = speed[j]
    # trialsInBlock

    trialsInBlock = trialsInBlock.reindex(np.random.permutation(trialsInBlock.index)).reset_index(drop=True)  # shuffle
    trialsInBlock['dotDirections'] = np.random.choice(dotDirections, trials, replace=True)
    # trialsInBlock

    # store info in dataframe
    trialsDf = pd.DataFrame(index=np.arange(trials))  # create empty dataframe to store trial info
    trialsDf = pd.concat([trialsDf, trialsInBlock], axis=1) # join dataframes

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
    trialsDf['fixationS'] = info['fixationS']

    # store parameter arguments into dataframe
    trialsDf['trialNo'] = range(1, trialsDf.shape[0] + 1) # add trialNo
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
    trialsDf['targetQuadrant'] = 0
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
    fixation = visual.TextStim(win=win, units='norm', height=0.12, ori=0, name='target', text='+', font='Courier New Bold', colorSpace='rgb', color=[-.3, -.3, -.3], opacity=1)

    # dotPatch = visual.DotStim(win, color=(1.0, 1.0, 1.0), dir=180, dotSize=4, nDots=100, fieldShape='circle', fieldPos=(0.0, 0.0), fieldSize=1, dotLife=3, signalDots='same', noiseDots='position',speed=0.01, coherence=0.3)

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

        #1: draw and show fixation
        fixation.setAutoDraw(True) #draw fixation on next flips
        for frameN in range(info['fixationFrames']):
            win.flip()
        fixation.setAutoDraw(False) #stop showing fixation

        #3: draw stimuli
        dotPatch = visual.DotStim(win, color=(1.0, 1.0, 1.0), dir=int(thisTrial['dotDirections']), dotSize=4, nDots=int(thisTrial['nDots']), fieldShape='circle', fieldPos=(0.0, 0.0), fieldSize=1, dotLife=int(thisTrial['dotFrames']), signalDots='same', noiseDots='position', speed=thisTrial['speed'], coherence=thisTrial['coherence'])
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
                keys = event.getKeys(keyList = ['f', 'j', 'v', 'n', 'backslash', 'bracketright'])
                if len(keys) > 0 and trialsDf.loc[i, 'resp'] is None: #if a response has been made
                    trialsDf.loc[i, 'rt'] = respClock.getTime() #store RT
                    trialsDf.loc[i, 'resp'] = keys[0] #store response in pd df
                    trialsDf.loc[i, 'keypress'] = keys[0]

                    if keys[0] == 'f' and trialsDf.loc[i, 'targetQuadrant'] == 1:
                        if sendTTL and not blockType == 'practice':
                            port.setData(251) # correct response
                        trialsDf.loc[i, 'acc'] = 1
                    elif keys[0] == 'j' and trialsDf.loc[i, 'targetQuadrant'] == 2:
                        if sendTTL and not blockType == 'practice':
                            port.setData(251) # correct response
                        trialsDf.loc[i, 'acc'] = 1
                    elif keys[0] == 'v' and trialsDf.loc[i, 'targetQuadrant'] == 3:
                        if sendTTL and not blockType == 'practice':
                            port.setData(251) # correct response
                        trialsDf.loc[i, 'acc'] = 1
                    elif keys[0] == 'n' and trialsDf.loc[i, 'targetQuadrant'] == 4:
                        if sendTTL and not blockType == 'practice':
                            port.setData(251) # correct response
                        trialsDf.loc[i, 'acc'] = 1
                    else:
                        if sendTTL and not blockType == 'practice':
                            port.setData(250) #incorrect response
                        trialsDf.loc[i, 'acc'] = 0

                    if trialsDf.loc[i, 'acc'] == 1:
                        trialsDf.loc[i, 'responseTTL'] = 251
                    elif trialsDf.loc[i, 'acc'] == 0:
                        trialsDf.loc[i, 'responseTTL'] = 250

                    #remove stimuli from screen
                    dotPatch.setAutoDraw(False)
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
            trialsDf.loc[i, 'keypress'] = None
            if saveData: #if saveData argument is True, then APPEND current row/trial to csv
                trialsDf[i:i+1].to_csv(filename, header = True if i == 0 and writeHeader else False, mode = 'a', index = False) #write header only if index i is 0 AND block is 1 (first block)
                dataframes['dotMotion'] = dataframes['dotMotion'].append(trialsDf[i:i+1]).reset_index(drop=True)
                dataframes['dotMotion'].to_csv(filenamebackup, index=False)
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
                dataframes['dotMotion'] = dataframes['dotMotion'].append(trialsDf[i:i+1]).reset_index(drop=True)
                dataframes['dotMotion'].to_csv(filenamebackup, index=False)
            return None

        ''' DO NOT EDIT END '''

        if saveData: #if saveData argument is True, then append current row/trial to csv
            trialsDf[i:i+1].to_csv(filename, header=True if i == 0 and writeHeader else False, mode='a', index=False) #write header only if index i is 0 AND block is 1 (first block)
            dataframes['dotMotion'] = dataframes['dotMotion'].append(trialsDf[i:i+1]).reset_index(drop=True)

        ISI.complete() #end inter-trial interval

        # feedback for trial
        if feedback:
            feedbackFrames = feedbackS * screenRefreshRate
            #stimuli
            accuracyFeedback = visual.TextStim(win = win, units = 'norm', colorSpace = 'rgb', color = [1, 1, 1], font = 'Verdana', text = '', height = 0.07, wrapWidth = 1.4, pos = [0.0, 0.0])

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
                    showInstructions(text=["Try to respond accurately and quickly."])
                else:
                    pass
            except:
                pass

    # end of block
    for frameN in range(30):
        win.flip() #wait at the end of the block

    # append data to global dataframe
    dataframes['dotMotion'].to_csv(filenamebackup, index=False)

    return trialsDf # return dataframe































###############################################
###############################################
###############################################
###############################################
###############################################




''' START EXPERIMENT HERE '''
def startExperimentSection():
    pass

runDotMotionBlock(taskName='dotMotion', blockType='', trials=10, effortProportion=[0.5, 0.5], dotDirections=[0, 180], nDots=[20, 500], coherence=[0.3, 0.3], dotFrames=[3, 3], speed=[0.01, 0.01], feedback=False, saveData=True, practiceTrials=5, titrate=False, rtMaxFrames=240, blockMaxTimeSeconds=None, experimentMaxTimeSeconds=None, feedbackS=1.0, rewardSchedule=None, feedbackSound=False, pauseAfterMissingNTrials=None, practiceHelp=False)




win.close()
core.quit() # quit PsychoPy
