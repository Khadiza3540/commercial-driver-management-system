import winsound
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALARM_PATH = os.path.join(BASE_DIR, "assets", "alarm.wav")


def play_alarm():
    winsound.PlaySound(ALARM_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)


def stop_alarm():
    winsound.PlaySound(None, winsound.SND_PURGE)

#def play_alert():
    #play_alarm()