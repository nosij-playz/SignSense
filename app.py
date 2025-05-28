import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def fingers_up(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    pip_joints = [3, 6, 10, 14, 18]

    fingers = []

    wrist = hand_landmarks.landmark[0]
    thumb_tip = hand_landmarks.landmark[4]
    thumb_mcp = hand_landmarks.landmark[2]
    index_mcp = hand_landmarks.landmark[5]

    # Determine if hand is right or left based on wrist and index MCP x-coords
    if wrist.x < index_mcp.x:
        # Right hand
        if thumb_tip.x < thumb_mcp.x:
            fingers.append(1)
        else:
            fingers.append(0)
    else:
        # Left hand
        if thumb_tip.x > thumb_mcp.x:
            fingers.append(1)
        else:
            fingers.append(0)

    # Other fingers
    for tip_id, pip_id in zip(tips[1:], pip_joints[1:]):
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[pip_id].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

def recognize_gesture(hand_landmarks):
    fingers = fingers_up(hand_landmarks)
    total_fingers = sum(fingers)

    count_labels = {
        0: "FIST",
        1: "ONE",
        2: "TWO",
        3: "THREE",
        4: "FOUR",
        5: "FIVE",
        6:"SIX"
    }
    gesture = count_labels.get(total_fingers, str(total_fingers))

    def distance(p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    dist_thumb_index = distance(thumb_tip, index_tip)

    # OK gesture: thumb tip close to index tip + other fingers extended
    if dist_thumb_index < 0.05 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
        gesture = "OK"

    wrist = hand_landmarks.landmark[0]
    # Thumbs up: only thumb up and thumb tip above wrist
    if fingers == [1, 0, 0, 0, 0] and thumb_tip.y < wrist.y:
        gesture = "THUMBS UP"

    # Super (V sign): index and middle fingers up, others down
    if fingers == [0, 1, 1, 0, 0]:
        gesture = "SUPER"

    return gesture

def get_hand_label(hand_landmarks):
    wrist = hand_landmarks.landmark[0]
    index_mcp = hand_landmarks.landmark[5]
    if wrist.x < index_mcp.x:
        return "Right Hand"
    else:
        return "Left Hand"

cap = cv2.VideoCapture(0)
with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)  # Mirror image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = recognize_gesture(hand_landmarks)
                hand_label = get_hand_label(hand_landmarks)
                text = f"{hand_label}: {gesture}"
                cv2.putText(frame, text, (30, 60), cv2.FONT_HERSHEY_SIMPLEX,
                            1.5, (0, 0, 255), 3, cv2.LINE_AA)

        cv2.imshow("Finger Count & Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
