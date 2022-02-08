import argparse
import os
from datetime import time, timedelta, datetime
# import numpy as np
# import scipy.io.wavfile as wav
# from pydub import AudioSegment

CODE_TO_ACTIVITY = {
    18: 'Hammering',
    20: 'Saw In-Use'
}

def parser():
    parser = argparse.ArgumentParser(description="Generating synced data for a pair of users")
    parser.add_argument('USER_1', help='name of the first user')
    parser.add_argument('USER_2', help='name of the second user')
    parser.add_argument('ACT_1', help='activity for user 1 to be read from data, have to be one of {"saw", "hammer"}')
    parser.add_argument('ACT_2', help='activity for user 2 to be read from data, have to be one of {"saw", "hammer"}')
    parser.add_argument('--INPUT-DIR', help='path for the original data', default='./Data')
    parser.add_argument('--OUTPUT-DIR', help='path for the output directory for storing synced data', default='./Processed_Data')
    parser.add_argument('--VERBOSE', help='Enable printing logs for the process', action='store_true', default=False)
    parser.add_argument('--OVERWRITE', help='Enable overwriting synced data points', action='store_true', default=False)
    return parser.parse_args()

# def read_signal(file, NORM=False, verbose=False):
#     ''' read signal and normalize if the flag is passed.'''
#     rate, sig = wav.read(file)
#     assert sig.dtype == np.int16, 'Bad sample type: %r'%sig.dtype
#     if NORM : # convert to [-1.0, +1.0]
#         sig = np.float64(sig/np.max(np.abs(sig)))
#     if verbose: print(f'Signal Reading compelted:\nSignal Shape: {sig.shape}\nSample Rate: {rate}')
#     return rate, sig

# def write_signal(file_name, rate, sig, norm=False):
#     ''' Write signal with the given file path.'''
#     if norm :
#         sig = np.int16(sig/np.max(np.abs(sig)) * 32767)
#     wav.write(file_name, rate, sig)
#     print(f'Signal writing Completed:\nSignal Shape: {sig.shape}\nSample Rate: {rate}')

def readUserData(user_path, user_name, activity, verbose):
    print(f'[{user_name}] : Reading Original Data from path: {user_path}')
    
    # Reading Start End time for the user file specified
    try:
        time_stamp = []
        if verbose: print(f'----[{user_name}] : Reading starting/ending time markers')
        with open(os.path.join(user_path, f'{user_name}_{activity}_audio_record.csv')) as readFile:
            # for line in readFile:
            #     t = ':'.join(line.split(':')[1:]).strip('\t\n ')
            #     # checking for extra trailing zeros at the end of stamp
            #     segs = t.split('.')
            #     segs[-1] = segs[-1][:6] # if there are any extra trailing zeros
            #     while len(segs[-1]) < 6 : segs[-1] += '0' # adding padding zeros
            #     time_stamp.append('.'.join(segs))
            next(readFile)
            time_stamp = next(readFile).rstrip().split(',')

        # converting string into time objects, storing start_time, end_time for user activity
        # start_time, end_time = [time.fromisoformat(t) for t in time_stamp]
        start_time, end_time = [datetime.strptime(t, '%H:%M:%S.%f') for t in time_stamp]
    except (FileNotFoundError, IOError) as err:
        print(f'{err}')
    
    if verbose : print(f'        [start time]: {start_time}\n        [end time]: {end_time}')

    # reading eWatch Readings
    try:
        ewatch = []
        if verbose :  print(f'----[{user_name}] : Reading E-Watch readings')
        with open(os.path.join(user_path, user_name + '_sensor_'+ activity +'.txt')) as readFile:
            for line in readFile:
                tokens = line.strip().split('\t')
                values = [x.strip() for x in tokens[:3]]
                # segs = tokens[-1].split('_')
                # segs[-1] = segs[-1][:6]
                # while len(segs[-1]) < 6: segs[-1] += '0'
                # #time_stamp = segs[0] + ':' + segs[1] + ':' + segs[2] + '.' + segs[3]
                # #time_stamp = time.fromisoformat(time_stamp)
                # time_stamp = '_'.join(segs)
                time_stamp = datetime.strptime(tokens[-1], '%H_%M_%S_%f')
                values.append(time_stamp)
                ewatch.append(values)
    except Exception as e:
        print(f'{e}')
    print(f'----[{user_name}] : Reading E-Watch Sensors data for activity : \'{activity}\' is successfully\n\
        Total Readings : {len(ewatch)}\n\
        Start Time: {ewatch[0][-1].strftime("%H:%M:%S.%f")}\n\
        End Time: {ewatch[-1][-1].strftime("%H:%M:%S.%f")}')

    grounds = []
    with open(os.path.join(user_path, user_name +'_' + activity + '_grnd_truth.txt'), 'r') as readFile:
        for line in readFile:
            tokens = line.rstrip().split(',')
            gt_start = datetime.strptime(tokens[0], '%H_%M_%S_%f')
            gt_end = datetime.strptime(tokens[1], '%H_%M_%S_%f')
            grounds.append([gt_start, gt_end, CODE_TO_ACTIVITY[int(tokens[2])]])
    print(f'----[{user_name}] : Reading Ground Truth done successfully')
    return start_time, end_time, ewatch, grounds

def syncData(args, data1, data2):
    s1, e1, watch1, ground1 = data1
    s2, e2, watch2, ground2 = data2
    
    print(f'Total points in watch 1 [{args.USER_1}] readings: {len(watch1)}')
    print(f'Total points in watch 2 [{args.USER_2}] readings:', len(watch2)) 
    
    print('========================= STARTING SYNCING PROCESS ========================')
    print('::',s1 ," --> ", e1)
    print('start', watch1[0][-1])
    print('end', watch1[-1][-1])
    watch1 = [x for x in watch1 if x[-1] >= s1 and x[-1] <= e1]
    watch2 = [x for x in watch2 if x[-1] >= s2 and x[-1] <= e2]

    # ground1_filtered = []
    # for label in ground1:
    #     if label[1] <= s1:
    #         continue
    #     elif label[1] <= e1:
    #         if label[0] >= s1:
    #             ground1_filtered.append(label)
    #         else:
    #             ground1_filtered.append([s1, label[1], label[2]])
    #     elif label[1] > e1:
    #         if label[0] < s1:
    #             ground1_filtered.append([s1, e1, label[2]])
    #         else:
    #             ground1_filtered.append([label[0], e1, label[2]])


    # ground2_filtered = []
    # for label in ground2:
    #     if label[1] <= s2:
    #         continue
    #     elif label[1] <= e2:
    #         if label[0] >= s2:
    #             ground2_filtered.append(label)
    #         else:
    #             ground2_filtered.append([s2, label[1], label[2]])
    #     elif label[1] > e2:
    #         if label[0] < s2:
    #             ground2_filtered.append([s2, e2, label[2]])
    #         else:
    #             ground2_filtered.append([label[0], e2, label[2]])

    
    sync_watch_data_1 = [] #watch1 if s1 <= s2 else []
    sync_watch_data_2 = [] #watch2 if s2 < s1 else []
    
    # sync_ground_1 = []
    # sync_ground_2 = []
    FRT1 = watch1[0][-1] # front recording time for user 1
    FRT2 = watch2[0][-1] # front recording time for user 2

    BRT1 = watch1[-1][-1] # back recording time for user 1
    BRT2 = watch2[-1][-1] # back recording time for user 2
    
    GLOBAL_VIRTUAL_START_TIME = FRT1 if FRT1 <= FRT2 else FRT2
    GLOBAL_VIRTUAL_END_TIME = GLOBAL_VIRTUAL_START_TIME + (BRT1-FRT1) if BRT1-FRT1 < BRT2-FRT2 else GLOBAL_VIRTUAL_START_TIME + (BRT2 - FRT2)

    print(f'Global Virtual Start Time : {GLOBAL_VIRTUAL_START_TIME}')
    print(f'Gloabl Virtual End Time : {GLOBAL_VIRTUAL_END_TIME}')

    if GLOBAL_VIRTUAL_START_TIME == FRT2:
        for tokens in watch1:
            if tokens[-1] - FRT1 + GLOBAL_VIRTUAL_START_TIME > GLOBAL_VIRTUAL_END_TIME:
                break
            tokens[-1] = (tokens[-1] - FRT1 + GLOBAL_VIRTUAL_START_TIME).time()
            sync_watch_data_1.append(tokens)
        for tokens in watch2:
            if tokens[-1] > GLOBAL_VIRTUAL_END_TIME:
                break
            tokens[-1] = tokens[-1].time()
            sync_watch_data_2.append(tokens)

        # for tokens in ground1:
        #     if tokens[0] - FRT1 + GLOBAL_VIRTUAL_START_TIME < GLOBAL_VIRTUAL_START_TIME or tokens[1] - FRT1 + GLOBAL_VIRTUAL_START_TIME > GLOBAL_VIRTUAL_END_TIME:
        #         continue
        #     tokens[0] = (tokens[0] - FRT1 + GLOBAL_VIRTUAL_START_TIME).time()
        #     tokens[1] = (tokens[1] - FRT1 + GLOBAL_VIRTUAL_START_TIME).time()
        #     sync_ground_1.append(tokens)

        # for tokens in ground2:
        #     if tokens[0] < GLOBAL_VIRTUAL_START_TIME or tokens[1] > GLOBAL_VIRTUAL_END_TIME:
        #         continue
        #     tokens[0] = tokens[0].time()
        #     tokens[1] = tokens[1].time()
        #     sync_ground_2.append(tokens)
    else :
        for tokens in watch1:
            if tokens[-1] > GLOBAL_VIRTUAL_END_TIME:
                break
            tokens[-1] = tokens[-1].time()
            sync_watch_data_1.append(tokens)

        for tokens in watch2:
            if tokens[-1] - FRT2 + GLOBAL_VIRTUAL_START_TIME > GLOBAL_VIRTUAL_END_TIME:
                break
            tokens[-1] = (tokens[-1] - FRT2 + GLOBAL_VIRTUAL_START_TIME).time()
            sync_watch_data_2.append(tokens)

        # for tokens in ground1:
        #     if tokens[0] < GLOBAL_VIRTUAL_START_TIME or tokens[1] > GLOBAL_VIRTUAL_END_TIME:
        #         continue
        #     tokens[0] = tokens[0].time()
        #     tokens[1] = tokens[1].time()
        #     sync_ground_1.append(tokens)

        # for tokens in ground2:
        #     if tokens[0] - FRT2 + GLOBAL_VIRTUAL_START_TIME < GLOBAL_VIRTUAL_START_TIME or tokens[1] - FRT2 + GLOBAL_VIRTUAL_START_TIME > GLOBAL_VIRTUAL_END_TIME:
        #         continue
        #     tokens[0] = (tokens[0] - FRT2 + GLOBAL_VIRTUAL_START_TIME).time()
        #     tokens[1] = (tokens[1] - FRT2 + GLOBAL_VIRTUAL_START_TIME).time()
        #     sync_ground_2.append(tokens)

    print(f'\nTotal data points while doing activity in sync:\n\t[{args.USER_1}] watch 1: {len(sync_watch_data_1) } \n\t[{args.USER_2}] watch 2:', len(sync_watch_data_2))
    
    if args.VERBOSE:
        print('-------------')
        for line in sync_watch_data_1[:5]:
            print(line)
        print('.\n.\n.')
        print('-------------')
        for line in sync_watch_data_2[:5]:
            print(line)
        print('\n')

        print(f'\nTotal truth segments while doing activity in sync:\n\t[{args.USER_1}] watch 1: {len(sync_ground_1) } \n\t[{args.USER_2}] watch 2:', len(sync_ground_2))

        print('-------------')
        for line in sync_ground_1[:5]:
            print(line)
        print('.\n.\n.')
        print('-------------')
        for line in sync_ground_2[:5]:
            print(line)
        print('.\n.\n.')
    
    print('============================== SYNC COMPLETE ==============================')
    return sync_watch_data_1, sync_watch_data_2, GLOBAL_VIRTUAL_START_TIME, GLOBAL_VIRTUAL_END_TIME


def sync_ground_truths(args, ground1, ground2):
    FRT1 = ground1[0][0] # ground truths 1
    FRT2 = ground2[0][0] # ground truths 2

    GLOBAL_VIRTUAL_START_TIME = FRT1 if FRT1 <= FRT2 else FRT2

    sync_ground_1 = []
    sync_ground_2 = []

    if GLOBAL_VIRTUAL_START_TIME == FRT2:
        print(ground1[0])
        for tokens in ground1:
            # print(FRT1, type(FRT1))
            # print(GLOBAL_VIRTUAL_START_TIME, type(GLOBAL_VIRTUAL_START_TIME))
            # print(GLOBAL_VIRTUAL_START_TIME, type(GLOBAL_VIRTUAL_START_TIME))
            # print(tokens[0], type(tokens[0]))
            if tokens[0] - FRT1 + GLOBAL_VIRTUAL_START_TIME < GLOBAL_VIRTUAL_START_TIME:
                continue
            tokens[0] = (tokens[0] - FRT1 + GLOBAL_VIRTUAL_START_TIME).time()
            tokens[1] = (tokens[1] - FRT1 + GLOBAL_VIRTUAL_START_TIME).time()
            sync_ground_1.append(tokens)

        for tokens in ground2:
            if tokens[0] < GLOBAL_VIRTUAL_START_TIME:
                continue
            tokens[0] = tokens[0].time()
            tokens[1] = tokens[1].time()
            sync_ground_2.append(tokens)
    else :
        for tokens in ground1:
            if tokens[0] < GLOBAL_VIRTUAL_START_TIME:
                continue
            tokens[0] = tokens[0].time()
            tokens[1] = tokens[1].time()
            sync_ground_1.append(tokens)

        for tokens in ground2:
            if tokens[0] - FRT2 + GLOBAL_VIRTUAL_START_TIME < GLOBAL_VIRTUAL_START_TIME:
                continue
            tokens[0] = (tokens[0] - FRT2 + GLOBAL_VIRTUAL_START_TIME).time()
            tokens[1] = (tokens[1] - FRT2 + GLOBAL_VIRTUAL_START_TIME).time()
            sync_ground_2.append(tokens)
    return sync_ground_1, sync_ground_2


def writeSyncedData(args, data1, data2, ground1, ground2, GVSTS, GVETS):
    names = [args.USER_1, args.USER_2]
    names.sort()
    
    output_dir = os.path.join(os.path.abspath(args.OUTPUT_DIR), f'{args.USER_1}_{args.ACT_1}_{args.USER_2}_{args.ACT_2}')
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    
    write_path_1 = os.path.join(output_dir, args.USER_1 + '_ewatch_'+ args.ACT_1 + '.csv')
    write_path_2 = os.path.join(output_dir, args.USER_2 + '_ewatch_'+ args.ACT_2 + '.csv')

    write_ground_path_1 = os.path.join(output_dir, args.USER_1 + '_' + args.ACT_1 + '_grnd_truth.csv')
    write_ground_path_2 = os.path.join(output_dir, args.USER_2 + '_' + args.ACT_2 + '_grnd_truth.csv')

    if os.path.isfile(write_path_1) and not args.OVERWRITE:
        raise Exception(f"File already exists : {write_path_1}\n-->try adding \'--OVERWRITE\' flag")
    
    if os.path.isfile(write_path_2) and not args.OVERWRITE:
        raise Exception(f"File already exists: {write_path_2}\n-->try adding \'--OVERWRITE\' flag")

    # if os.path.isfile(write_ground_path_1) and not args.OVERWRITE:
    #     raise Exception(f"File already exists : {write_ground_path_1}\n-->try adding \'--OVERWRITE\' flag")

    # if os.path.isfile(write_ground_path_2) and not args.OVERWRITE:
    #     raise Exception(f"File already exists: {write_ground_path_2}\n-->try adding \'--OVERWRITE\' flag")

    with open(os.path.abspath(write_path_1), 'w') as writeFile:
        writeFile.write('x,y,z,time\n')
        for tokens in data1:
            tokens[-1] = tokens[-1].strftime('%H:%M:%S.%f')
            writeFile.write(','.join(tokens) + '\n')
    
    with open(write_path_2, 'w') as writeFile:
        writeFile.write('x,y,z,time\n')
        for tokens in data2:
            tokens[-1] = tokens[-1].strftime('%H:%M:%S.%f')
            writeFile.write(','.join(tokens) + '\n')


    with open(os.path.abspath(write_ground_path_1), 'w') as writeFile:
        writeFile.write('t1,t2,act\n')
        for tokens in ground1:
            print(tokens)
            tokens[0] = tokens[0].strftime('%H:%M:%S.%f')
            tokens[1] = tokens[1].strftime('%H:%M:%S.%f')
            tokens[2] = str(tokens[2])
            writeFile.write(','.join(tokens) + '\n')

    with open(os.path.abspath(write_ground_path_2), 'w') as writeFile:
        writeFile.write('t1,t2,act\n')
        for tokens in ground2:
            tokens[0] = tokens[0].strftime('%H:%M:%S.%f')
            tokens[1] = tokens[1].strftime('%H:%M:%S.%f')
            tokens[2] = str(tokens[2])
            writeFile.write(','.join(tokens) + '\n')

    if os.path.isfile(os.path.join(output_dir, 'global_audio_log.csv')) and not args.OVERWRITE:
        raise Exception(f"File already exists: {os.path.join(output_dir, 'global_audio_log.csv')}\n--> try adding \'--OVERWRITE\' flag")
    
    with open(os.path.join(output_dir, 'global_audio_log.csv'), 'w') as writeFile:
        writeFile.write('record_start,record_end\n')
        writeFile.write(f'{GVSTS.strftime("%H:%M:%S.%f")},{GVETS.strftime("%H:%M:%S.%f")}\n')

    print(f'Writin complete with following paths:\n{args.USER_1}: {write_path_1}\n{args.USER_2}: {write_path_2}\n\
        Global Record log: {os.path.join(output_dir, "global_audio_log.csv")}\nGround truth Paths;\n\tUser1 : {write_ground_path_1}\n\tUser2 : {write_ground_path_2}\n\n')

    # print('===========================  Writing Mixed Audio Files  =============================')
    # os.remove(os.path.join(output_dir, f'{args.USER_1}_{args.ACT_1}_{args.USER_2}_{args.ACT_2}_python.wav'))
    # if os.path.isfile(os.path.join(output_dir, f'{args.USER_1}_{args.ACT_1}_{args.USER_2}_{args.ACT_2}_python.wav')) and not args.OVERWRITE:
    #     raise Exception(f"File already exists: {os.path.join(output_dir, f'{args.USER_1}_{args.ACT_1}_{args.USER_2}_{args.ACT_2}_python.wav')}\n-->try adding \'--OVERWRITE\' flag")

    # user_1_data_path = os.path.join(os.path.abspath(args.INPUT_DIR), args.USER_1)
    # user_2_data_path = os.path.join(os.path.abspath(args.INPUT_DIR), args.USER_2)

    # rate1, sig1 = read_signal(os.path.join(user_1_data_path, f'{args.USER_1}_{args.ACT_1}.wav'))
    # rate2, sig2 = read_signal(os.path.join(user_2_data_path, f'{args.USER_2}_{args.ACT_2}.wav'))

    # min_length = len(sig1) if len(sig1) < len(sig2) else len(sig2)
    # if rate1 != rate2:
    #     raise Exception('Audio rates are different, can\'t be merged')

    # sound1 = AudioSegment.from_wav(os.path.join(user_1_data_path, f'{args.USER_1}_{args.ACT_1}.wav'))
    # sound2 = AudioSegment.from_wav(os.path.join(user_2_data_path, f'{args.USER_2}_{args.ACT_2}.wav'))
    # mixed = sound1.overlay(sound2)
    # sig_mixed = mixed[:min_length]
    # sig_mixed.export(os.path.join(output_dir, f'{args.USER_1}_{args.ACT_1}_{args.USER_2}_{args.ACT_2}_python.wav'), format="wav")

    # # mixed_sig = sig1[:min_length] + sig2[:min_length]

    # # write_signal(os.path.join(output_dir, f'{args.USER_1}_{args.ACT_1}_{args.USER_2}_{args.ACT_2}_python_scipy.wav'), rate1, mixed_sig)
    # print(f'Total data points in mixed audio written: {min_length}\n@rate : {rate1}')
    # mixed_rate, mixed_sig = read_signal(os.path.join(output_dir, f'{args.USER_1}_{args.ACT_1}_{args.USER_2}_{args.ACT_2}_python.wav'))
    # verf_rate, verf_sig = read_signal(os.path.join(output_dir, f'{args.USER_1}_{args.ACT_1}_{args.USER_2}_{args.ACT_2}.wav'))
    # print(len(mixed_sig), "::", len(verf_sig))
    # print(mixed_rate, "::", verf_rate)
    # print(mixed[:10], verf_sig[:10])


def main(args):
    # creating output directory if it doesn't exists
    if not os.path.isdir(args.OUTPUT_DIR):
        os.mkdir(args.OUTPUT_DIR)

    # declaring path for each user
    user_1_data_path = os.path.join(os.path.abspath(args.INPUT_DIR), args.USER_1)
    user_2_data_path = os.path.join(os.path.abspath(args.INPUT_DIR), args.USER_2)
    
    # calling utility functions to read the original data for the users
    print(f'================= READING DATA : {args.USER_1} :  {args.ACT_1} ====================')
    try:
        user_1_data = readUserData(user_1_data_path, args.USER_1, args.ACT_1, args.VERBOSE)
    except:
        print(f'{args.USER_1},{args.ACT_1}:Missing data')
        exit()
    print(f'================= READING DATA : {args.USER_2} : {args.ACT_2} ===================')
    try:
        user_2_data = readUserData(user_2_data_path, args.USER_2, args.ACT_2, args.VERBOSE)
    except:
        print(f'{args.USER_1},{args.ACT_1}:Missing data')
        exit()
    
    # calling to sync data for pair of users
    sync_data_1, sync_data_2,  GVSTS, GVETS = syncData(args, user_1_data, user_2_data)
    sync_ground_1, sync_ground_2 = sync_ground_truths(args, user_1_data[3], user_2_data[3])
    # writing synced data to the output directory
    writeSyncedData(args, sync_data_1, sync_data_2, sync_ground_1, sync_ground_2, GVSTS, GVETS)


    # act2 = 'hammer'
    # act1 = 'saw'

    # # declaring path for each user
    # user_1_data_path = os.path.join(os.path.abspath(args.INPUT_DIR), args.USER_1)
    # user_2_data_path = os.path.join(os.path.abspath(args.INPUT_DIR), args.USER_2)
    
    # # calling utility functions to read the original data for the users
    # user_1_data = readUserData(user_1_data_path, args.USER_1, act1, args.VERBOSE)
    # user_2_data = readUserData(user_2_data_path, args.USER_2, act2, args.VERBOSE)
    
    # # calling to sync data for pair of users
    # sync_data_1, sync_data_2 = syncData(user_1_data, user_2_data, args)
    
    # # writing synced data to the output directory
    # writeSyncedData(sync_data_1, sync_data_2, args, act1, act2)



if __name__ == '__main__':
    args = parser()
    main(args)
