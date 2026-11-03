import datetime
from typing import Dict, List

class ErgonomicScheduler:
    def __init__(self, shift_hours: int = 8):
        self.shift_hours = shift_hours
        self.cycle_duration_mins = 30 # 20 sit + 8 stand + 2 move

    def generate_shift_timeline(self, start_time_str: str = "09:00") -> List[Dict[str, str]]:
        """Generates a block-by-block schedule for the workday."""
        start_time = datetime.datetime.strptime(start_time_str, "%H:%M")
        total_cycles = (self.shift_hours * 60) // self.cycle_duration_mins

        timeline = []
        current_time = start_time

        for _ in range(total_cycles):
            sit_time = current_time
            stand_time = sit_time + datetime.timedelta(minutes=20)
            move_time = stand_time + datetime.timedelta(minutes=8)
            end_time = move_time + datetime.timedelta(minutes=2)

            timeline.append({
                "Sit": f"{sit_time.strftime('%I:%M %p')} - {stand_time.strftime('%I:%M %p')}",
                "Stand": f"{stand_time.strftime('%I:%M %p')} - {move_time.strftime('%I:%M %p')}",
                "Move": f"{move_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
            })
            
            current_time = end_time
            
        return timeline

    def prescribe_targeted_movements(self, kinematic_data: Dict[str, float]) -> List[str]:
        """Maps specific kinematic failures to targeted physical stretches for the 2-minute move blocks."""
        movements = []
        
        if kinematic_data.get("neck", 0) > 20:
            movements.append("Cervical Retractions (Chin Tucks) to counter forward head posture.")
        
        if kinematic_data.get("trunk", 90) < 80:
            movements.append("Thoracic Extensions over the back of your chair to open the chest.")
            
        if kinematic_data.get("elbow", 90) < 75 or kinematic_data.get("elbow", 90) > 120:
            movements.append("Wrist flexor and extensor stretches to relieve forearm tension.")
            
        if kinematic_data.get("knee", 90) < 80:
            movements.append("Standing hip flexor stretches to open the anterior chain.")

        # Default movement if posture is optimal
        if not movements:
            movements.append("Brisk walking or unweighted squats to promote blood flow.")
            
        return movements

# Execution Block
if __name__ == "__main__":
    #Using data from phase 2 image
    user_angles = {
        "elbow": 95,
        "trunk": 85,
        "knee": 83,
        "neck": 24
    }

    scheduler = ErgonomicScheduler(shift_hours=4) #Testing a half-day shift

    print("\n--- TARGETED MOVEMENT PRESCRIPTION ---")
    prescriptions = scheduler.prescribe_targeted_movements(user_angles)
    for p in prescriptions:
        print(f"[*] {p}")

    print("\n--- DAILY 20-8-2 SCHEDULE ---")
    schedule = scheduler.generate_shift_timeline(start_time_str="08:00")
    for block in schedule[:3]: # Printing just the first 3 cycles to save space
        print(f"Sit: {block['Sit']} | Stand: {block['Stand']} | Move: {block['Move']}")