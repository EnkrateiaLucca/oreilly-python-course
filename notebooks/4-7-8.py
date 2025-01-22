import time

def timer(duration, message):
    print(message)
    time.sleep(duration)

def run_timers():
    for _ in range(4):
        timer(4, "Breath in!")
        timer(7, "Hold!")
        timer(8, "Breath out.")

    print("Finished")

run_timers()