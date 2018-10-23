Written by Hause Lin hauselin@gmail.com

**Tested in PsychoPy 1.90.2 (MacOS)**

To run task, load `Script1.py` in PsychoPy coder. Then run the task. 

To skip a block, press ]

To quit, press \

For results, see [this repository](https://github.com/hauselin/effortPilots). 

### Pilot 1.1 (LATEST)

#### Task parameters

- 4 effort levels (effort levels coded 0, 1, 2, 3)
  - dots [coherence]: 10 [0.05], 50 [0.06], 250 [0.07], 500 [0.08]
  - coherent dots' display duration: 3 frames
- Feedback (correct/wrong) provided after every trial
- RT deadline is 4 s

#### Task flow

- Practice forced choice
  - 1 rep per effort level (coherent dots are shown for 12 frames/200 ms) (really easy practice rounds!)
  - 3 reps per effort level (coherent dots are shown for 3 frames/50 ms) (actual trials)
- Forced choice block
  - 10 reps per effort level; confidence and effort ratings after each trial (1-9 point scale), before task feedback
- Practice demand selection task
  - 1 rep each: 0 vs 1, 0 vs 2, 1 vs 2
- Actual demand selection task
  - 6 combinations: 0 vs 1, 0 vs 2, 0 vs 3, 1 vs 2, 1 vs 3, 2 vs 3
  - 10 reps per combination 

### Pilot 1 Task flow

* practice dot motion tasks: 3 easy dot motion trials with 0.4, 0.6, 0.8 coherence and 10, 100, 500 dots respectively (rate confidence and effort required after each trial; 9-point scale)
* actual dot motion tasks (to get confidence and effort ratings for each effort level): 3 effort levels with 10, 100, 500 dots (all 0.05 motion coherence; 5 reps each, so 15 trials in total) (confidence/effort rating after each trial)
* practice demand selection task (not collecting confidence/effort ratings)
* actual demand selection task: efforts 1vs2, 1vs3, 2vs3 (10 trials each) (not collecting confidence/effort ratings)
* belief of task feedback rating (once at the end of the experiment)
* RT deadline is 3s
