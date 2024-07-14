import unreal
import mediapipe as mp
import os
import cv2


# Find the PumpCounter Actor
pump_counter_actor = None
actors = unreal.EditorLevelLibrary.get_all_level_actors()
for actor in actors:
    if actor.get_class().get_name() == "PumpCounter":
        pump_counter_actor = actor
        break


if pump_counter_actor:
    # Get the pump count
    pump_count = pump_counter_actor.get_editor_property('PumpCount')
    if pump_count > 120:
        messsage = "The BPM was too fast and killed the person. Try to stay in the range of 100 to 120 BPM. Your BPM was {pump_count}"
    elif pump_count < 100:
        messsage = "The BPM was too slow and the person wasn't saved. Try to stay in the range of 100 to 120 BPM. Your BPM was {pump_count}"
    else:
        message = "Congratualations. You saved the person long enough for the ambulance to come on time! You gave the person CPR at a rate of {pump_count} BPM."


    # Find the PumpCountWidget
    widgets = unreal.EditorUtilityLibrary.get_widgets_of_class(unreal.EditorUtilityLibrary.get_editor_world(), unreal.UserWidget)
    for widget in widgets:
        if widget.get_class().get_name() == "PumpCountWidget":
            pump_count_widget = widget
            break


    if pump_count_widget:
        # Update the text in the widget
        text_block = pump_count_widget.get_editor_property('PumpCountText')
        text_block.set_text(unreal.Text(message))
else:
    print("Pump Counter actor not found")




# Initialize the Take Recorder subsystem
take_recorder_subsystem = unreal.TakeRecorderSubsystem()


# Define the recording parameters
output_directory = "C:/Users/Akshat/Videos/CPR_Session"  # Change this to your desired output directory
take_name = "video"  # This will be the name of the MP4 file
video_bitrate = 10000  # Adjust the bitrate as needed


settings = unreal.TakeRecorderUserParameters()
settings.output_directory = unreal.DirectoryPath(output_directory)
settings.take_name = take_name
settings.video_bitrate = video_bitrate


# Ensure the output directory exists or create it
def create_output_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


# Start recording
def start_recording():
    print("Starting recording...")
    create_output_directory(output_directory)
    take_recorder_subsystem.start_recording(user_parameters=settings)


# Stop recording and get the video path
def stop_recording():
    print("Stopping recording...")
    take_recorder_subsystem.stop_recording()
    global mp4_path
    mp4_path = os.path.join(output_directory, f"{take_name}.mp4")
    print(f"Video saved at: {mp4_path}")


# Trigger the recording based on VR session events
def on_vr_session_start():
    start_recording()


def on_vr_session_end():
    stop_recording()




# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils


# Open the video file
cap = cv2.VideoCapture(mp4_path)


errors_counter = 0


def is_hand_in_center(hand_landmarks, frame_width, frame_height):
    # Get the x and y coordinates of the wrist (landmark 0)
    x = hand_landmarks.landmark[0].x * frame_width
    y = hand_landmarks.landmark[0].y * frame_height
    # Define the center region
    center_x_min = frame_width * 0.4
    center_x_max = frame_width * 0.6
    center_y_min = frame_height * 0.4
    center_y_max = frame_height * 0.6
    # Check if the hand is in the center region
    return center_x_min <= x <= center_x_max and center_y_min <= y <= center_y_max




while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break


    # Get the frame dimensions
    frame_height, frame_width, _ = frame.shape


    # Convert the BGR image to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    # Process the frame and detect hands
    results = hands.process(image)


    # Draw hand landmarks and check if hands are in the center
    if results.multi_hand_landmarks:
        hand_in_center = False
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            if is_hand_in_center(hand_landmarks, frame_width, frame_height):
                hand_in_center = True
        if not hand_in_center:
            errors_counter += 1
    else:
        errors_counter += 1


    # Display the counter on the frame
    cv2.putText(frame, f'Counter: {errors_counter}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)


    # Display the frame
    cv2.imshow('Hand Tracking', frame)


    if cv2.waitKey(10) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
