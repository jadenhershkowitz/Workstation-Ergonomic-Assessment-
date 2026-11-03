import streamlit as st
import os
from Phase_1 import ErgonomicRulesEngine
from Phase_2 import process_image
from Phase_3 import ErgonomicScheduler
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Kinematic Workstation Audit", layout="wide")
st.title("Workstation Ergonomics & Kinematic Assessment")
st.write("Upload a side-profile photo of your desk setup to receive an automate RULA biomechanical audit.")

# 2. File Uploader
uploaded_file = st.file_uploader("Choose an image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save the uploaded file temporarily so OpenCV can read it
    temp_filename = "temp_uploaded.jpg"
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.info("Running MediaPipe Kinematic Engine...")

    # 3. Run Phase 2 Vision Engine
    angles = process_image(temp_filename)

    if angles:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Pose Extraction Map")
            # Phase 2 auto-saves the annotated image as output_skeleton.jpg
            if os.path.exists("output_skeleton.jpg"):
                image = Image.open("output_skeleton.jpg")
                st.image(image, use_column_width=True)

        with col2:
            st.subheader("Ergonomic Rules Audit")
            # 4. Run Phase 1 rules engine
            rules_engine = ErgonomicRulesEngine()
            audit = rules_engine.evaluate_posture(angles)

            # Color-coded overall status
            if audit["overall_status"] == "Pass":
                st.success("Overall Status: Optimal Alignment")
            elif audit["overall_status"] == "Warning":
                st.warning("Overall Status: Acceptable with Strain Warnings")
            else:
                st.error("Overall Status: High Risk Detected")

            st.write("**Priority Hardware Adjustments:**")
            for action in audit["priority_actions"]:
                st.write(f"- 🔧 {action}")

            st.write("**Joint Breakdown Data:**")
            st.json(audit["joint_breakdown"])

        st.divider()

        # 5. Run Phase 3 Scheduling Engine
        st.subheader("Targeted Micro-Breaks (20-8-2 Rule)")
        scheduler = ErgonomicScheduler(shift_hours=8)
        movements = scheduler.prescribe_targeted_movements(angles)

        for move in movements:
            st.info(f"🏃 {move}")

    else:
        st.error("Could not detect a clear human pose. Please ensure the full side profile is visible.")

    # Clean temp file
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

            