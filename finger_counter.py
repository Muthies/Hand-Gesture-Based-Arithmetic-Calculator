import cv2
import mediapipe as mp

# Initialize Mediapipe Hand Detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Function to count fingers
def count_fingers(hand_landmarks):
    if not hand_landmarks:
        return 0

    landmarks = hand_landmarks.landmark
    fingers = []

    # Thumb: Check if the tip is on the left/right of the hand
    fingers.append(landmarks[4].x < landmarks[3].x)

    # Other fingers: Check if the tip is above the middle joint
    fingers.extend([landmarks[tip].y < landmarks[tip - 2].y for tip in [8, 12, 16, 20]])

    return fingers.count(True)

# Main application logic
def main():
    cap = cv2.VideoCapture(0)
    finger_values = []  # Store the values for addition/subtraction
    mode = None  # Current operation mode

    print("Instructions:")
    print("- Press '1' for Showing Numbers mode.")
    print("- Press '2' for Addition mode.")
    print("- Press '3' for Subtraction mode.")
    print("- Press 'c' to clear values.")
    print("- Press 'q' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame for a mirror view
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape

        # Process the frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        finger_count = 0
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                finger_count = count_fingers(hand_landmarks)
                cv2.putText(frame, f"Fingers: {finger_count}", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the current mode
        cv2.putText(frame, f"Mode: {mode}", (10, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Perform actions based on the mode
        if mode == "Show Numbers":
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        elif mode in ["Addition", "Subtraction"]:
            if finger_count not in finger_values and finger_count != 0:
                finger_values.append(finger_count)
                print(f"Captured: {finger_count}")

            if len(finger_values) == 2:
                if mode == "Addition":
                    result = sum(finger_values)
                    print(f"Addition Result: {result}")
                elif mode == "Subtraction":
                    result = finger_values[0] - finger_values[1]
                    print(f"Subtraction Result: {result}")

                # Display the result and reset
                cv2.putText(frame, f"Result: {result}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                finger_values = []
                mode = None

        # Display instructions
        cv2.putText(frame, "Press '1'=Show, '2'=Add, '3'=Sub, 'c'=Clear, 'q'=Quit", (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit
            break
        elif key == ord('1'):  # Show Numbers
            mode = "Show Numbers"
        elif key == ord('2'):  # Addition
            mode = "Addition"
            finger_values = []
        elif key == ord('3'):  # Subtraction
            mode = "Subtraction"
            finger_values = []
        elif key == ord('c'):  # Clear
            finger_values = []
            mode = None

        # Display the frame
        cv2.imshow("Finger Operations", frame)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
