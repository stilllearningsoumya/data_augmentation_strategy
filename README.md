# Data Augmentation Strategy
A template for data augmentation to create multiuser data (example scripts are provided for 2 users only) from single user data.

### Synchronizing IMU 

```
Description : Generating synced data for a pair of users
positional arguments:
  USER_1                name of the first user
  USER_2                name of the second user

optional arguments:
  -h, --help            show this help message and exit
  --INPUT-DIR INPUT_DIR
                        path for the original data
  --OUTPUT-DIR OUTPUT_DIR
                        path for the output directory for storing synced data
  --SYNC-CRITERIA SYNC_CRITERIA
                        Method to be used for syncing data points. {'base' or 'sampling'}
  --SAMPLING-RATE SAMPLING_RATE
                        sampling rate for the e-watch sensor data, Default=50 Hz
  --VERBOSE             Enable printing logs for the process
  --OVERWRITE           Enable overwriting synced data points
```

Example:
```
python3 sync.py U1 U2 hammer saw --INPUT-DIR data/unmixed --OUTPUT-DIR data/mixed --OVERWRITE
```

### Augmenting Acoustic Signatures

Input the audio files and the coordinates in the code (comments are provided inline). The output will be the name of the `audio_<activity>_<distance to mic>.wav`. The activity will be the activity which is having a varying distance from the microphone.

To generate the augmented audio, run:
```
python3 room_audio.py
```
### Samples

IMU samples present in the directory: `data/unmixed/` (for unmixed) and `data/mixed/` (for synchronized with the script).

Audio samples present in the directory: `sources`