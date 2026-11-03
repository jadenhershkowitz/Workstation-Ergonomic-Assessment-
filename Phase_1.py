from typing import Dict, Any, List

class ErgonomicRulesEngine:
    def __init__(self):
        # Thresholds defined as (min_angle, max_angle)
        self.thresholds = {
            "elbow": {
                "optimal": (90, 105),
                "acceptable": [(75, 89), (106, 120)]
            },
            "trunk": {
                "optimal": (90, 110),
                "acceptable": [(80, 89), (111, 120)]
            },
            "knee": {
                "optimal": (90, 105),
                "acceptable": [(80, 89), (106, 115)]
            },
            "neck": {
                "optimal": (0, 10),
                "acceptable": [(11, 20)]
            }
        }

        # Deterministic mapping for hardware adjustments based on specific deviations
        self.corrective_actions = {
            "elbow_acute": "Raise chair height or lower desk height to open the elbow angle.",
            "elbow_obtuse": "Lower chair height or move keyboard closer to reduce reaching.",
            "trunk_acute": "Bring monitor closer or increase UI scaling to prevent leaning forward.",
            "trunk_obtuse": "Decrease backrest recline to maintain a more upright posture.",
            "knee_acute": "Raise chair height to prevent knees from resting higher than hips.",
            "knee_obtuse": "Lower chair height or use a footrest to fully support the feet.",
            "neck_flexion": "Raise monitor so the top third of the screen is at eye level."
        }

    def _check_zone(self, joint: str, angle: float) -> str:
        """Categorizes an angle into Optimal, Acceptable, or High Risk."""
        bounds = self.thresholds.get(joint)
        if not bounds:
            return "Unknown"

        opt_min, opt_max = bounds["optimal"]
        if opt_min <= angle <= opt_max:
            return "Optimal"

        for acc_min, acc_max in bounds["acceptable"]:
            if acc_min <= angle <= acc_max:
                return "Acceptable"

        return "High Risk"

    def _get_recommendation(self, joint: str, angle: float, status: str) -> str:
        """Retrieves the specific hardware adjustment if the joint is not Optimal."""
        if status == "Optimal":
            return "Alignment is good. Maintain current position."

        opt_min, opt_max = self.thresholds[joint]["optimal"]
        
        if joint == "elbow":
            return self.corrective_actions["elbow_acute"] if angle < opt_min else self.corrective_actions["elbow_obtuse"]
        elif joint == "trunk":
            return self.corrective_actions["trunk_acute"] if angle < opt_min else self.corrective_actions["trunk_obtuse"]
        elif joint == "knee":
            return self.corrective_actions["knee_acute"] if angle < opt_min else self.corrective_actions["knee_obtuse"]
        elif joint == "neck":
            # Neck extension (looking up) is rare at desks, but flexion (looking down) is common
            return self.corrective_actions["neck_flexion"] if angle > opt_max else "Adjust monitor height to neutral."

        return "Adjust workstation to bring joint closer to 90 degrees."

    def evaluate_posture(self, measured_angles: Dict[str, float]) -> Dict[str, Any]:
        """
        Takes a dictionary of calculated angles and returns a full ergonomic audit.
        Example input: {'elbow': 72.5, 'trunk': 95.0, 'knee': 85.0, 'neck': 22.1}
        """
        audit_report = {
            "overall_status": "Pass",
            "joint_breakdown": {},
            "priority_actions": []
        }

        high_risk_count = 0

        for joint, angle in measured_angles.items():
            status = self._check_zone(joint, angle)
            recommendation = self._get_recommendation(joint, angle, status)

            if status == "High Risk":
                high_risk_count += 1
                audit_report["overall_status"] = "Fail"
                audit_report["priority_actions"].append(recommendation)
            elif status == "Acceptable" and audit_report["overall_status"] != "Fail":
                audit_report["overall_status"] = "Warning"

            audit_report["joint_breakdown"][joint] = {
                "measured_angle": round(angle, 1),
                "status": status,
                "recommendation": recommendation
            }

        return audit_report

# Example execution to test the logic
if __name__ == "__main__":
    engine = ErgonomicRulesEngine()
    
    # Mock data representing someone slumped forward looking at a low laptop
    mock_kinematic_data = {
        "elbow": 72.0,  # Acute (High Risk)
        "trunk": 75.5,  # Leaning forward (High Risk)
        "knee": 95.0,   # Good (Optimal)
        "neck": 25.0    # Looking down (High Risk)
    }
    
    report = engine.evaluate_posture(mock_kinematic_data)
    
    import json
    print(json.dumps(report, indent=2))