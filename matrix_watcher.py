"""
kaneki_watcher.py
-----------------
Watches your webcam. If YOUR face disappears OR a stranger appears
for more than TRIGGER_DELAY seconds, a warning window appears.
Type the cancel code within WARNING_DURATION seconds to abort.
Otherwise, kaneki_countdown.exe launches.

TERMINAL COMMANDS (type anytime while running):
  pause   -> disable the watcher until you resume
  resume  -> re-enable the watcher
  status  -> check if watcher is active or paused
  quit    -> stop the watcher entirely

Put this file in the SAME folder as kaneki_countdown.exe.
"""

import cv2
import os
import sys
import time
import subprocess
import threading
import numpy as np
import tkinter as tk

#  SETTINGS
TRIGGER_DELAY        = 5       # seconds of no-face/stranger before warning
WARNING_DURATION     = 5       # seconds to type cancel code before launch
CANCEL_CODE          = "redpill"  # code to cancel warning
CAMERA_INDEX         = 0
ENROLL_FRAMES        = 60
CONFIDENCE_THRESHOLD = 70
FACE_DATA_FILE       = "matrix_owner.yml"
EXE_NAME             = "matrix_countdown.exe"
# --

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
FACE_FILE = os.path.join(BASE_DIR, FACE_DATA_FILE)
EXE_PATH  = os.path.join(BASE_DIR, EXE_NAME)

detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Shared state
paused       = False
running      = True


def get_face_roi(frame):
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, scaleFactor=1.1,
                                      minNeighbors=5, minSize=(80, 80))
    return gray, faces


# ENROLLMENT

def capture_session(cap, label):
    print(f"\n  {label}")
    print("Press SPACE TO CAPTURE, Q to skip.\n")
    samples, capturing, count = [], False, 0

    while True:
        ret, frame = cap.read()
        if not ret:
            # retry instead of breaking immediately
            time.sleep(0.05)
            continue

        gray, faces = get_face_roi(frame)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            if capturing and count < ENROLL_FRAMES:
                roi = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
                samples.append(roi)
                count += 1
                cv2.putText(frame, f"Capturing {count}/{ENROLL_FRAMES}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if not capturing:
            cv2.putText(frame, f"{label} — SPACE TO CAPTURE, Q to skip",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2)
        else:
            cv2.putText(frame, f">> CAPTURING BIOMETRIC DATA [{count}/{ENROLL_FRAMES}]",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow(">> INITIALIZING BIOMETRIC SIGNATURE", frame)
        key = cv2.waitKey(30) & 0xFF

        if key == ord(' '):
            capturing = True
        elif key == ord('q'):
            break

        if count >= ENROLL_FRAMES:
            print(f">> Captured {count} frames!")
            break

    print(f">> Done | {len(samples)} frames captured.")
    return samples


def enroll():
    print("\nENROLLMENT: 2 sessions")
    print("Session 1: WITHOUT glasses")
    print("Session 2: WITH glasses  (Q to skip)\n")

    # Open camera fresh with a small delay to let it initialize
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(2)  # give camera time to fully open

    # Warmup — read and discard frames until we get a valid one
    for _ in range(30):
        cap.read()
        time.sleep(0.05)

    if not cap.isOpened():
        print("ERROR: Could not open camera. Close any app using it and try again.")
        sys.exit(1)

    all_samples  = []
    all_samples += capture_session(cap, "Session 1 — Without glasses")
    print("\n Put your glasses on, then press SPACE...")
    all_samples += capture_session(cap, "Session 2 — With glasses")
    cap.release()
    cv2.destroyAllWindows()

    if not all_samples:
        print("No face captured. Try again.")
        sys.exit(1)

    print(f"\n   Training on {len(all_samples)} total frames...")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(all_samples, np.zeros(len(all_samples), dtype=np.int32))
    recognizer.save(FACE_FILE)
    print(f"Enrolled! Saved to {FACE_FILE}\n")
    return recognizer


def load_recognizer():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(FACE_FILE)
    return recognizer


# WARNING WINDOW

class WarningWindow:
    def __init__(self, on_cancel, on_timeout):
        self.on_cancel  = on_cancel
        self.on_timeout = on_timeout
        self._remaining = WARNING_DURATION

        self.root = tk.Tk()
        self.root.title("Warning")
        self.root.configure(bg="black")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.overrideredirect(True)

        w, h = 480, 240
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        tk.Label(self.root, text=">> UNAUTHORIZED ENTITY DETECTED",
                 fg="red", bg="black",
                 font=("Courier", 16, "bold")).pack(pady=(20, 4))
        tk.Label(self.root, text=">> ENTER AUTHORIZATION CODE:",
                 fg="yellow", bg="black",
                 font=("Courier", 11)).pack()

        self.timer_label = tk.Label(self.root,
                 text=f">> LOCK IN {self._remaining}s",
                 fg="red", bg="black",
                 font=("Courier", 13, "bold"))
        self.timer_label.pack(pady=6)

        self.code_var = tk.StringVar()
        entry = tk.Entry(self.root, textvariable=self.code_var,
                         show="*", fg="white", bg="black",
                         insertbackground="white",
                         font=("Courier", 14), width=20,
                         bd=0, highlightthickness=1,
                         highlightcolor="red")
        entry.pack(pady=4)
        entry.focus_set()
        entry.bind("<KeyRelease>", self._check_code)

        self.status_label = tk.Label(self.root, text="",
                 fg="red", bg="black",
                 font=("Courier", 10))
        self.status_label.pack()

        self._tick()
        self.root.mainloop()

    def _tick(self):
        if self._remaining <= 0:
            self.root.destroy()
            self.on_timeout()
            return
        self.timer_label.config(text=f">> LOCK IN {self._remaining}s")
        self._remaining -= 1
        self.root.after(1000, self._tick)

    def _check_code(self, event=None):
        if self.code_var.get() == CANCEL_CODE:
            self.root.destroy()
            self.on_cancel()


# LAUNCHER 

def launch_kaneki():
    """Launch countdown and WAIT for it to finish before returning."""
    if os.path.exists(EXE_PATH):
        
        print(">> MATRIX INTERFACE ACTIVE")
        print(">> AWAITING AUTHENTICATION INPUT")
        proc = subprocess.Popen([EXE_PATH])
        proc.wait()  # block until countdown fully finishes
    else:
        print(f"Warning: Could not find {EXE_PATH}")


#TERMINAL COMMAND LISTENER 

def command_listener():
    global paused, running
    print("\n  Commands: 'pause' | 'resume' | 'status' | 'quit'\n")

    while running:
        try:
            cmd = input().strip().lower()
        except EOFError:
            break

        if cmd == "pause":
            if paused:
                print("  Already paused.")
            else:
                paused = True
                print(">> WATCHER PAUSED")
                print(">> MONITORING SUSPENDED")
                print("     Type 'resume' to turn it back on.\n")

        elif cmd == "resume":
            if not paused:
                print("  Already active.")
            else:
                paused = False
                print(">> WATCHER RESUMED")
                print(">> MONITORING ACTIVE")

        elif cmd == "status":
            
            state = "PAUSED" if paused else "ACTIVE"
            print(f">> STATUS: {state}\n")

        elif cmd == "quit":
            print(">> SYSTEM SHUTDOWN INITIATED")
            running = False
            os._exit(0)

        else:
            print(f">> Unknown command: '{cmd}'")
            print(">> Try: pause | resume | status | quit\n")


#  WATCHER 

def watch(recognizer):
    global paused, running

    print(">> SYSTEM INITIALIZED")
    print(">> MATRIX LOCK PROTOCOL ENABLED")
    print(">> WATCHER ACTIVE")
    print(f"[CONFIG] Trigger: {TRIGGER_DELAY}s | Warning: {WARNING_DURATION}s")
    print(f"[SECURITY] Cancel code configured: {CANCEL_CODE}")

    cap          = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    alert_start  = None
    warning_open = False

    def open_warning():
        nonlocal warning_open, alert_start
        warning_open = True

        def on_cancel():
            nonlocal warning_open, alert_start
            warning_open = False
            alert_start  = None
            
            print("\n>> ACCESS GRANTED")
            print(">> LOCK ABORTED")

        def on_timeout():
            nonlocal warning_open, alert_start
            alert_start = None
            
            print("\n>> LOCK SEQUENCE INITIATED")
            print(">> MATRIX INTERFACE LOADING...")
            launch_kaneki()  # blocks until countdown + black screen done
            warning_open = False
            
            print(">> ACCESS GRANTED")
            print(">> SYSTEM UNLOCKED")
            print(">> WATCHER RESUMING...\n")

        WarningWindow(on_cancel, on_timeout)
    while running:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        #  If paused, skip all detection 
        if paused:
            alert_start  = None
            warning_open = False
            time.sleep(0.5)
            continue

        gray, faces   = get_face_roi(frame)
        owner_present = False

        if len(faces) == 0:
            status = "NO FACE"
        else:
            for (x, y, w, h) in faces:
                roi = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
                label, confidence = recognizer.predict(roi)
                if label == 0 and confidence < CONFIDENCE_THRESHOLD:
                    owner_present = True
                    break
            status = "OWNER " if owner_present else "STRANGER "

        if owner_present:
            alert_start = None
        else:
            if not warning_open:
                if alert_start is None:
                    alert_start = time.time()
                elapsed   = time.time() - alert_start
                remaining = max(0, TRIGGER_DELAY - elapsed)
                print(f"\r>> SCAN: {status} | LOCK IN {remaining:.1f}s ",
                end="", flush=True)
                if elapsed >= TRIGGER_DELAY:
                    print("\n>> ALERT: UNAUTHORIZED PRESENCE DETECTED")
                if elapsed >= TRIGGER_DELAY:
                    alert_start = None
                    t = threading.Thread(target=open_warning, daemon=True)
                    t.start()

        time.sleep(0.15)

    cap.release()


#  ENTRY POINT 
if __name__ == "__main__":
    try:
        _ = cv2.face.LBPHFaceRecognizer_create()
    except AttributeError:
        print(" Missing opencv-contrib-python.")
        print("   Run:  pip install opencv-contrib-python")
        sys.exit(1)

    if not os.path.exists(FACE_FILE):
        print("No face data found — starting enrollment.")
        recognizer = enroll()
        print("Enrollment complete! Starting watcher...")
    else:
        print(f"Face data loaded from {FACE_FILE}")
        
        recognizer = load_recognizer()

    # Start command listener AFTER enrollment so input() does not
    # block the camera window from receiving keypresses
    t = threading.Thread(target=command_listener, daemon=True)
    t.start()

    watch(recognizer)
