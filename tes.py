import wave
import numpy as np

# הגדרות
num_channels = 1  # מספר ערוצים (1 = מונו, 2 = סטריאו)
sample_width = 2  # גודל דגימה בבתים (2 = 16-bit)
frame_rate = 44100  # קצב דגימה
duration = 5  # משך הקובץ בשניות

# יצירת תדר סינוס
t = np.linspace(0, duration, int(frame_rate * duration), endpoint=False)
frequency = 440  # תדר של 440 הרץ (לָה)
audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

# כתיבת הקובץ
with wave.open('output.wav', 'w') as wf:
    wf.setnchannels(num_channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(frame_rate)
    wf.writeframes(audio_data.tobytes())
