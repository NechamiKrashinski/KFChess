import wave
import numpy as np

# הגדרות
num_channels = 1  # מספר ערוצים (1 = מונו)
sample_width = 2  # גודל דגימה בבתים (2 = 16-bit)
frame_rate = 44100  # קצב דגימה
duration = 0.1  # משך הקובץ בשניות (0.1 שניות)

# יצירת תדר של ניפוץ
t = np.linspace(0, duration, int(frame_rate * duration), endpoint=False)
frequency = 1000  # תדר של 1000 הרץ (צליל חד)
audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

# כתיבת הקובץ
with wave.open('pop_sound.wav', 'w') as wf:
    wf.setnchannels(num_channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(frame_rate)
    wf.writeframes(audio_data.tobytes())
