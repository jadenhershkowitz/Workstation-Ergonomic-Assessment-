import cv2
import mediapipe as mp
import numpy as np
import os

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    """
    Calculates the angle between three points (a, b, c) with 'b' as the vertex.
    Uses arctan2 to compute the angle in degrees.
    """
    a = np.array(a) # First point
    b = np.array(b) # Mid point (vertex)
    c = np.array(c) # End point
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def process_image(image_path):
    # Load image and convert color space for MediaPipe
    image = cv2.imread(image_path)
    #Safety check: Did OpenCV actually find it?
    if image is None:
        print(f"\n[!] Error: Could not find '{image_path}'")
        print("Here are the actual image files in your folder right now:")
        for file in os.listdir('.'):
            if file.lower().endswith(('.png','.jpg','.jpeg','.webp')):
                print(f" -> {file}")
        return None
    #convert color space for MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process the image to find pose landmarks
    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        results = pose.process(image_rgb)
        
        if not results.pose_landmarks:
            print("No pose detected.")
            return None
            
        landmarks = results.pose_landmarks.landmark
        
        # Get image dimensions for pixel coordinate conversion
        h, w, c = image.shape
        
        # Extract coordinates for the Left side (assuming a left-facing side profile)
        # In a production environment, you would dynamically select the side with higher visibility scores
        ear = [landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x * w, 
               landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y * h]
               
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w, 
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
                    
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * w, 
                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * h]
                 
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * w, 
                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * h]
                 
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * w, 
               landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * h]
               
        knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x * w, 
                landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y * h]
                
        ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * w, 
                 landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y * h]

        # Calculate joint angles
        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        trunk_angle = calculate_angle(shoulder, hip, knee)
        knee_angle = calculate_angle(hip, knee, ankle)
        
        # Neck angle requires a vertical reference vector originating from the shoulder
        vertical_ref = [shoulder[0], shoulder[1] - 100] 
        neck_angle = calculate_angle(ear, shoulder, vertical_ref)

        kinematic_data = {
            "elbow": elbow_angle,
            "trunk": trunk_angle,
            "knee": knee_angle,
            "neck": neck_angle
        }

        # Draw landmarks and skeleton
        mp_drawing.draw_landmarks(
            image, 
            results.pose_landmarks, 
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
        )

        # Overlay calculated text directly onto the image near the joints
        cv2.putText(image, f"Elbow: {int(elbow_angle)}", tuple(np.multiply(elbow, [1, 1]).astype(int)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, f"Trunk: {int(trunk_angle)}", tuple(np.multiply(hip, [1, 1]).astype(int)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, f"Knee: {int(knee_angle)}", tuple(np.multiply(knee, [1, 1]).astype(int)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, f"Neck: {int(neck_angle)}", tuple(np.multiply(ear, [1, 1]).astype(int)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

        # Save the result to a file
        cv2.imwrite("output_skeleton.jpg", image)
        print("Success! Processed image saved as 'output_skeleton.jpg'")

        return kinematic_data

# Example usage (assuming the Phase 1 ErgonomicRulesEngine is imported)
# angles = process_image('desk_posture_test.jpg')
# if angles:
#     engine = ErgonomicRulesEngine()
#     audit = engine.evaluate_posture(angles)
#     print(audit)
# 1. Make sure this string matches the EXACT name of your image file in the folder
if __name__ == "__main__":
    target_image = "Posture_Example.jpeg"

    print(f"Loading {target_image}...")

    # 2. Command the engine to process the image
    calculated_angles = process_image(target_image)

    if calculated_angles:
        print("Final Kinematic Angles Data:")
        print(calculated_angles)
    else:
        print("Failed to process image. Make sure the file exists and is named correctly.")