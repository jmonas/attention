import subprocess
import json
import time

from hume import HumeBatchClient
from hume.models.config import FaceConfig
from hume import BatchJobStatus

with open('config.json') as config_file:
    config = json.load(config_file)
client = HumeBatchClient(config['API_KEY'])
config = FaceConfig()

def send_notification(title, message):
    applescript_command = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", applescript_command])

def capture_image(path):
    # This command overwrites the existing image file with the new photo
    subprocess.run(["imagesnap", path])


def main():
    target_emotions = ["Boredom", "Concentration", "Tiredness"]
    THRESHOLD = 0.6
    while True:
        path = "images/img.jpg"
        capture_image(path)
        print("Captured img")
        job = client.submit_job(None, [config], files=[path])
        print(job)
        print("Running...")

        while job.get_status() != BatchJobStatus.COMPLETED:
            time.sleep(10)
        
        print("job recieved")
        predictions = job.get_predictions()


        send_notification_flag = False
        try:
            all_emotions = predictions[0]["results"]["predictions"][0]["models"]["face"]["grouped_predictions"][0]["predictions"][0]["emotions"]
        except:
            continue
        for emotion in all_emotions:
            if emotion["name"] in target_emotions:
                if emotion["score"] > THRESHOLD:
                    send_notification_flag = True
                    print(emotion)

        if send_notification_flag:
            send_notification("Attention", "Drink some coffee!")
            print("notification sent! \n")

        

        time.sleep(10)

if __name__ == "__main__":
    main()