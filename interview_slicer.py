__author__ = 'kristian'


from pydub import AudioSegment

sound = AudioSegment.from_wav("/Users/kristian/Dropbox/Data/interviews_audio/sysmo/sliced/rolfe20140611_09.34.20.wav")


sound_length = len(sound) #/ (1000*60)

five_min = 300000
current = 1

while (current+five_min) <= sound_length:
    print ".."
    start = current
    bit = sound[start:(start+five_min)]
    bit.export("/path/to/new/"+(current/1000)+".mp3", format="mp3")
    current = current+five_min


print "Done!"



#
# # len() and slicing are in milliseconds
# halfway_point = len(sound) / 2
# second_half = sound[halfway_point:]

# Concatenation is just adding
# second_half_3_times = second_half + second_half + second_half

# writing mp3 files is a one liner
# second_half_3_times.export("/path/to/new/file.mp3", format="mp3")