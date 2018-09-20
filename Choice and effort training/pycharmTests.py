import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# col width 15, don't wrap dataframe across pages
pd.set_option('display.max_colwidth', 15, 'display.expand_frame_repr', False, 'display.max_rows', 10)

info = {}
info['participant'] = 8
info

# assign conditions based on participant number and session
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

info


listToSave = []
listToSave.append(info)
with open('123Data.pkl', 'wb') as f:
    pickle.dump(listToSave, f)


with open('123Data.pkl', 'rb') as f:
    mynewlist = pickle.load(f)
mynewlist

with open('999-2018-01-09-13-37-49-stroop3colours.pkl') as f:
    mynewlist = pickle.load(f)







congruentTrials = 120
incongruentTrials = 60

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
stroopCombi.loc[stroopCombi['colour'] == 'red', 'correctKey'] = 'r'
stroopCombi.loc[stroopCombi['colour'] == 'green', 'correctKey'] = 'g'
stroopCombi.loc[stroopCombi['colour'] == 'yellow', 'correctKey'] = 'y'

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
trialsDf = pd.concat([trialsDf, trialsInBlock], axis=1)
trialsDf


dataStroop = pd.DataFrame()
dataStroop = dataStroop.append(trialsDf).reset_index(drop=True)
dataStroop

trialsDf = pd.DataFrame(index=np.arange(trialsInBlock.shape[0])) # create empty dataframe to store trial info
trialsDf = pd.concat([trialsDf, trialsInBlock], axis=1)
trialsDf

trialsDf.loc[:, 'participant'] = info['participant']

trialsDf.loc[0:1, 'congruency']


tempTrialsDf = pd.DataFrame()
trialIndicesUsed = []
trialsDf.shape[0]

i = 1
for i, thisTrial in trialsDf.iterrows(): #for each trial...
    if i == 0:
        sampledData = trialsDf.sample(1)
        trialIndicesUsed.append(sampledData.index[0])
        tempTrialsDf = tempTrialsDf.append(sampledData)
        tempTrialsDf = tempTrialsDf.reset_index(drop=True)
    elif i > 0:
        if tempTrialsDf.loc[i-1, 'congruency'] == 'incongruent':
            dataToSampleFrom = trialsDf.loc[trialsDf.congruency == 'congruent']
            for indexI in trialIndicesUsed:
                try:
                    dataToSampleFrom = dataToSampleFrom.drop(indexI)
                except:
                    pass
            sampledData = dataToSampleFrom.sample(1)
            trialIndicesUsed.append(sampledData.index[0])
        elif tempTrialsDf.loc[i-1, 'congruency'] == 'congruent':
            for indexI in trialIndicesUsed:
                try:
                    dataToSampleFrom = dataToSampleFrom.drop(indexI)
                except:
                    pass
            sampledData = dataToSampleFrom.sample(1)
            trialIndicesUsed.append(sampledData.index[0])




tempTrialsDf
trialIndicesUsed



import seaborn as sns
iris = sns.load_dataset("iris")

np.nanmean(iris.loc[1, "petal_length"])
np.nanmean(iris.loc[0, "petal_length"])

np.nanmean(iris['petal_length'])

sum(iris['petal_length'].isnull())

np.nanmean([np.nan])

np.isnan(np.nan)


pd.read_csv("004-2018-01-23-21-29-19-stroop3coloursChoiceTask.csv")


a = 3
a += 3 + 3

type(tempTrialsDf.shape[0])






















trialsDf = pd.read_csv("999-2018-01-09-20-30-32-stroop3colours.csv")
trialsDf


nMissedTrials = 3
try:
    if trialsDf.loc[i-(nMissedTrials-1):i, "rt"].isnull().sum() == nMissedTrials:
        print("missed too many trials")
        showInstructions(text=["That's the end of the experiment. Thanks so much for participating in our study!"])

    else:
        pass
except:
    pass


a = [None, None]
sum(a)

trialsDf.tail(nMissedTrials)['rt'].isnull().sum()

trialsDf[:]




def testGLobal():
    global a1
    a1 = 3
testGLobal()

a1






# running tally
df2 = pd.read_csv('999-2018-01-10-16-40-53-shiftingLetterNumber.csv')
df2.tail(3)['acc'].sum()




runningAccuracy = []
runningAccuracy.append(3)
runningAccuracy.append(5)
runningAccuracy

runningAccuracy.append(df2.loc[1, 'acc'])

np.nansum(runningAccuracy)
np.nansum(df2.tail(3)['acc'])



df3 = df2.copy()

df3 = df3.append(df3[1:2]).reset_index(drop=True)
df3




def taskA():
    print("task A")

def taskB():
    print("task B")
import random
a1 = taskA()
a2 = taskB()

tasks = [taskA, taskB]
tasks = [a1, a2]
random.shuffle(tasks)
tasks
[thisTask() for thisTask in tasks]

ratingOrder = range(len([4, 5, 6]))
random.shuffle(ratingOrder)
ratingOrder

taskRatings = ['mentalDemand', 'effort', 'frustration', 'bored', 'fatigue']
taskRatingsQuestions = [
['How mentally demanding was the video task?'],
["How hard did you have to work to watch the video?"],
["How insecure, discouraged, irritated, stressed, and annoyed were you when watching the video?"],
["How boring was the video task?"],
["I'm mentally fatigued now."]
]
taskRatingsAnchors = [
["very low", "very demanding"],
["very little", "very hard"],
["very little", "very high"],
["not boring", "very boring"],
["strongly disagree", "strongly agree"]
]

ratingOrder = range(len(taskRatings))
random.shuffle(ratingOrder)

for ratingI in ratingOrder:
    print ratingI
    print taskRatingsQuestions[ratingI]




















dataStroopAll = pd.read_csv("999-2018-01-25-15-26-41-stroop3colours.csv")




dataStroopAll.loc[:, 'acc']
dataStroopAll.loc[:, 'acc']

list(dataStroopAll.loc[:3, 'acc'])

type(np.array([dataStroopAll.acc]))

b1 = list(dataStroopAll.acc)
m = np.nanmean(b1)


np.nanmean([1, 2, 3])




np.nanmean(dataStroopAll.loc[:, 'acc'])
np.nanmean(dataStroopAll.loc[0, 'acc'])


float(dataStroopAll.loc[:, 'acc'].tail(1))









# generate random non-consecutive numbers
import random
random.randint(2, 10)
random.randrange(1, 10, 2)













taskDf = pd.read_csv("101-2018-01-31-23-04-51-stroop3coloursChoiceTask.csv")
np.nanmean(taskDf.loc[taskDf.loc[:, 'acc'].notnull(), 'acc'])
np.nanmean(taskDf.loc[:, 'acc'])
taskDf.loc[:, 'acc']




















trials = 12
switchProportion = 0.2
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
        elif letternumber[idx][0] in ["F", "G", "K"]:
            correctAnswer.append('consonant')
            correctKey.append('c')
    elif questions[idx] == 'number':
        if int(letternumber[idx][1]) in [0, 1, 2, 3, 4]:
            correctAnswer.append('smaller')
            correctKey.append(',')
        elif int(letternumber[idx][1]) in [6, 7, 8, 9]:
            correctAnswer.append('bigger')
            correctKey.append('.')

correctAnswer
correctKey
letternumber

trialsDf = pd.DataFrame(index=np.arange(trials)) # create empty dataframe to store trial info
trialsDf.loc[:, 'correctAnswer'] = correctAnswer
trialsDf['correctAnswer'] = correctAnswer














import pandas as pd
import numpy as np


reps = 10

'''generate trials for choice training'''
option1 = [0, 0.1, 0.3, 0.5, 0.7]
option2 = [0, 0.1, 0.3, 0.5, 0.7]
optionTuple = [(o1, o2) for o1 in option1 for o2 in option2 if o1 != o2] # combinations

option1 = [0, 1, 2, 3, 4]
option2 = [0, 1, 2, 3, 4]
optionTuple = [(o1, o2) for o1 in option1 for o2 in option2 if o1 != o2] # combinations

optionCombi = pd.DataFrame(optionTuple)
optionCombi.columns = ['option1', 'option2']

trialsInBlock = pd.concat([optionCombi] * reps, ignore_index=True)

trialsInBlock = trialsInBlock.reindex(np.random.permutation(trialsInBlock.index)).reset_index(drop=True) # shuffle





option1 = [0]
option2 = [1, 7]
optionTuple = [(o1, o2) for o1 in option1 for o2 in option2 if o1 != o2] # combinations

