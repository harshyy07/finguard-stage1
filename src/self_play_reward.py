"""
Self-Play RL Environment for FinGuard using Algorithm 1 from paper.
- Uses Guard reward: +1.0 for correct, 0.0 for wrong, -0.5 for format error
- Uses Generator reward: exp(-(s - 0.5)^2 / (2 * sigma^2)), filtered if s in {0, 1}
"""

import math
from typing import Dict, Any, List

def calculate_guard_reward(predicted_label: str, target_label: str, is_format_valid: bool) -> float:
    """
    Equation (2):
      r_guard = 1.0  if y_i == y_hat
                0.0  if y_i != y_hat
               -0.5  if format error
    """
    if not is_format_valid:
        return -0.5
    return 1.0 if predicted_label.lower() == target_label.lower() else 0.0

def calculate_generator_reward(guard_predictions: List[str], target_label: str, sigma: float = 0.25) -> Dict[str, Any]:
    """
    Equation (3):
      s = 1/N * sum(1[y_i == y_hat])
      r_gen = exp(-(s - 0.5)^2 / (2 * sigma^2)) for 0 < s < 1
      discarded if s in {0, 1}
    """
    N = len(guard_predictions)
    if N == 0:
        return {"reward": 0.0, "accuracy_s": 0.0, "is_valid": False}
        
    correct_count = sum(1 for y in guard_predictions if y.lower() == target_label.lower())
    s = correct_count / N
    
    # Filter out trivial (s=1) or impossible/misaligned (s=0) samples
    if s <= 0.0 or s >= 1.0:
        return {
            "reward": 0.0,
            "accuracy_s": s,
            "is_valid": False,
            "reason": "Discarded: s in {0, 1} (trivial agreement or misalignment)"
        }
        
    reward = math.exp(-((s - 0.5) ** 2) / (2 * (sigma ** 2)))
    return {
        "reward": reward,
        "accuracy_s": s,
        "is_valid": True,
        "reason": "Retained for calibration"
    }
