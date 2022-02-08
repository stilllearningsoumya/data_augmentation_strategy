import numpy as np
import matplotlib.pyplot as plt
import pyroomacoustics as pra
from scipy.io import wavfile

def find_euclidean_dist(u,v):
    return (((u[0]-v[0])**2 + (u[1]-v[1])**2 + (u[2]-v[2])**2)**0.5)

room_dim = [50, 50, 50]  # meters

# import a mono wavfile as the source signal
# the sampling frequency should match that of the room
fs, audio2 = wavfile.read("sources/U1_hammer.wav")
fs, audio1 = wavfile.read("sources/U2_saw.wav")

print('Length of Audio 1 --> {} and Audio 2 --> {}'.format(len(audio1),len(audio2)))

#clip to equal length
if(len(audio1)>len(audio2)):
    audio1 = audio1[:len(audio2)]
else:
    audio2 = audio2[:len(audio1)] 

# Create the room
room = pra.ShoeBox(
    room_dim, fs=fs,
)

mic_pos = [4, 2.5, 1.2]
# define the locations of the microphones
mic_locs = np.c_[
     mic_pos# mic 1
]

#coordinates for the source
source1 = [14, 2.5, 1.2]
source2 = [2, 2.5, 1.2]

# place the source in the room
room.add_source(source1, signal=audio1) #hammer
room.add_source(source2, signal=audio2) #saw


# finally place the array in the room
room.add_microphone_array(mic_locs)

# Run the simulation (this will also build the RIR automatically)
room.simulate()

val = find_euclidean_dist(source1,mic_pos)
print("Dist to mic from the moving source",val)

room.mic_array.to_wav(
    f"audio_saw_{val}.wav",
    norm=True,
    bitdepth=np.int16,
)