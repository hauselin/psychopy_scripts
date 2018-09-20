library(tidyverse); library(data.table); library(broom); library(dtplyr); library(lme4); library(lmerTest); library(ggbeeswarm); library(cowplot)

setwd('/Users/Hause/Dropbox/Working Projects/Effort/Scripts/v3/')

df1 <- tbl_dt(fread("103-2018-02-15-12-31-52-updateTraining.csv")) # choice task
df2 <- tbl_dt(fread("103-2018-02-15-12-31-52-mentalMathUpdating.csv")) # actual performance
df1[, acc := as.numeric(acc)]
df2[, acc := as.numeric(acc)]

df1[, .(rt, acc, overallTrialNum, accEffortTask, rtEffortTask)]
df1[!is.na(rt), .(rt, acc, overallTrialNum, accEffortTask, rtEffortTask)]

a <- df1[blockType != "practice", .(choiceText, rt, overallTrialNum, rtEffortTask, accEffortTask, blockNumber)]
b <- df2[blockType != "practice", .(overallTrialNum = mean(as.numeric(blockType), na.rm = T), rt = mean(rt, na.rm = T), acc = mean(acc, na.rm = T)), by = .(blockType)]
b <- b[overallTrialNum %in% c(a[, overallTrialNum])]

a
b

# compare means (should return EXACTLY THE SAME value)
a[, .(rtEffortTask = mean(rtEffortTask, na.rm = T), accEffortTask = mean(accEffortTask, na.rm = T))]
b[, .(rt = mean(rt, na.rm = T), acc = mean(acc, na.rm = T))]





df2[, .(colour, congruency, correctKey)] %>% arrange(correctKey) %>% print(n = Inf)




x <- tbl_dt(data.table(p = 1:20, condition = c("control", 'training'), taskOrder = c("us", "us", "su", "su")))
x
x[taskOrder == "us" & condition == "control", p] %% 4
x[taskOrder == "us" & condition == 'training', p] %% 4

x[taskOrder == "su" & condition == "control", p] %% 4
x[taskOrder == "su" & condition == 'training', p] %% 4




a <- data_frame(trialType = c(rep('congruent', 120), rep("incongruent", 60), rep("neutral", 30)))
sample_n(a, nrow(a)) %>% print(n = Inf)












filesinDir <- list.files(full.names = T) # get relative paths to all files/directories in raw data folder
filesToRead <- filesinDir[grep(pattern = "effortTraining.csv", x = filesinDir)] # find matching files to read
length(filesToRead)

#### read all data into R ####
dataRaw <- lapply(1:length(filesToRead), function(x) tbl_dt(fread(filesToRead[x]))) # read all matching files and store in a list
dataRaw <- tbl_dt(rbindlist(dataRaw)) # convert that list of dataframe to one dataframe

data <- copy(dataRaw) # make a copy of the data
data <- data[blockType != 'practice']







