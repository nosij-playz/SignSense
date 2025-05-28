import cv2
import mediapipe as mp
import math

class SIGNSENSER:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(max_num_hands=max_num_hands,
                                         min_detection_confidence=min_detection_confidence)

    def fingers_up(self, hand_landmarks):
        tips = [4, 8, 12, 16, 20]
        pip_joints = [3, 6, 10, 14, 18]
        fingers = []

        wrist = hand_landmarks.landmark[0]
        thumb_tip = hand_landmarks.landmark[4]
        thumb_mcp = hand_landmarks.landmark[2]
        index_mcp = hand_landmarks.landmark[5]

        # Determine if hand is right or left
        if wrist.x < index_mcp.x:
            fingers.append(1 if thumb_tip.x < thumb_mcp.x else 0)  # Right hand
        else:
            fingers.append(1 if thumb_tip.x > thumb_mcp.x else 0)  # Left hand

        for tip_id, pip_id in zip(tips[1:], pip_joints[1:]):
            fingers.append(1 if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[pip_id].y else 0)

        return fingers

    def recognize_gesture(self, hand_landmarks):
        fingers = self.fingers_up(hand_landmarks)
        total_fingers = sum(fingers)

        count_labels = {
            0: "FIST",
            1: "ONE",
            2: "TWO",
            3: "THREE",
            4: "FOUR",
            5: "FIVE",
            6: "SIX"
        }

        gesture = count_labels.get(total_fingers, str(total_fingers))

        def distance(p1, p2):
            return math.hypot(p1.x - p2.x, p1.y - p2.y)

        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        dist_thumb_index = distance(thumb_tip, index_tip)

        if dist_thumb_index < 0.05 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            gesture = "OK"

        wrist = hand_landmarks.landmark[0]
        if fingers == [1, 0, 0, 0, 0] and thumb_tip.y < wrist.y:
            gesture = "THUMBS UP"

        if fingers == [0, 1, 1, 0, 0]:
            gesture = "SUPER"

        return gesture

    def get_hand_label(self, hand_landmarks):
        wrist = hand_landmarks.landmark[0]
        index_mcp = hand_landmarks.landmark[5]
        return "Right Hand" if wrist.x < index_mcp.x else "Left Hand"

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                gesture = self.recognize_gesture(hand_landmarks)
                hand_label = self.get_hand_label(hand_landmarks)
                text = f"{hand_label}: {gesture}"
                cv2.putText(frame, text, (30, 60), cv2.FONT_HERSHEY_SIMPLEX,
                            1.5, (0, 0, 255), 3, cv2.LINE_AA)
        return frame

    def run(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = self.process_frame(frame)
            cv2.imshow("Finger Count & Gesture Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
