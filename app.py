import asyncio
import csv
import threading
import websockets
import cv2 as cv
import mediapipe as mp
import itertools
import copy
from model import KeyPointClassifier
from collections import deque
import os
import subprocess


connected_clients = set()
gesture_queue = asyncio.Queue()


def register_registry():
    manifest_json = os.path.abspath(".") + "\\com.gs.app.json"
    reg_file_path = os.path.abspath(".") + "\\set-registry.reg"

    # Write registry content to file
    reg_content = f'''
    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\\Software\\Google\\Chrome\\NativeMessagingHosts\\com.gs.app]
    @="{manifest_json}"
    '''

    # Save the .reg file
    with open(reg_file_path, 'w') as file:
        file.write(reg_content)

    # Run the .reg file silently
    subprocess.run(["regedit", "/s", reg_file_path], shell=True)

    print("Registry key added successfully.")


def select_mode(key, mode):
    number = -1
    if 48 <= key <= 57:  # 0 ~ 9
        number = key - 48
    if key == 110:  # n
        mode = 0
    if key == 107:  # k
        mode = 1
    if key == 104:  # h
        mode = 2
    return number, mode


def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to a one-dimensional list
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list


def start_video_feed(loop):
    cap = cv.VideoCapture(0)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    keypoint_classifier = KeyPointClassifier()
    with open('model/keypoint_classifier/keypoint_classifier_label.csv',
              encoding='utf-8-sig') as f:
        keypoint_classifier_labels = csv.reader(f)
        keypoint_classifier_labels = [
            row[0] for row in keypoint_classifier_labels
        ]
    history_length = 16
    point_history = deque(maxlen=history_length)
    mode = 1
    while True:
        key = cv.waitKey(10)
        if key == 27:  # ESC
            break
        number, mode = select_mode(key, mode)
        ret, image = cap.read()
        if not ret:
            break
        image = cv.flip(image, 1)  # Mirror display
        debug_image = copy.deepcopy(image)

        # Detection implementation #############################################################
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        #  ####################################################################
        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # Landmark calculation
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)

                # Conversion to relative coordinates / normalized coordinates
                pre_processed_landmark_list = pre_process_landmark(landmark_list)
                hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                if hand_sign_id == 2:  # Point gesture
                    point_history.append(landmark_list[8])
                else:
                    point_history.append([0, 0])

                asyncio.run_coroutine_threadsafe(
                    gesture_queue.put(keypoint_classifier_labels[hand_sign_id]),
                    loop
                )
                print(keypoint_classifier_labels[hand_sign_id])
        else:
            point_history.append([0, 0])
        cv.imshow('Hand Gesture Recognition', debug_image)

    cap.release()
    cv.destroyAllWindows()


async def handler(websocket, path="/"):
    print("🔌 Client connected")
    connected_clients.add(websocket)

    try:
        while True:
            message = await gesture_queue.get()
            # if not websocket.closed:
            await websocket.send(message)
    #                 print(f"📤 Sent to client: {message}")
    #             else:
    #                 break

    except websockets.exceptions.ConnectionClosed:
        print("❌ Connection closed")
    finally:
        connected_clients.remove(websocket)


# -------------------------------
# Main Server Loop
# -------------------------------
async def main():
    print("🚀 WebSocket server running at ws://localhost:8765")

    # Get the main loop reference and pass to thread
    loop = asyncio.get_running_loop()
    video_thread = threading.Thread(target=start_video_feed, args=(loop,), daemon=True)
    video_thread.start()

    # Start the WebSocket server
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever


register_registry()
asyncio.run(main())
