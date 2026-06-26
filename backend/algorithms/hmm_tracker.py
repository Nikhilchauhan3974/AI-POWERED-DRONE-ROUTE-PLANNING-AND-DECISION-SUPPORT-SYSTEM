import numpy as np
from typing import List, Tuple, Dict, Any

class HMMTracker:
    """
    Hidden Markov Model (HMM) for tracking a dynamic obstacle (e.g., rogue drone)
    under sensor uncertainty (e.g., fog/storms).
    Uses Forward Algorithm (Variable Elimination) to maintain a belief state.
    """
    def __init__(self, grid_cols: int, grid_rows: int):
        self.cols = grid_cols
        self.rows = grid_rows
        # Initial belief: uniform distribution across the entire grid
        self.belief = np.ones((self.rows, self.cols)) / (self.rows * self.cols)
        
    def _transition_model(self, x: int, y: int) -> List[Tuple[int, int, float]]:
        """Defines how the obstacle moves. Simplified: random walk to adjacent cells."""
        neighbors = []
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (0,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                neighbors.append((nx, ny))
                
        prob = 1.0 / len(neighbors)
        return [(nx, ny, prob) for nx, ny in neighbors]
        
    def _sensor_model(self, true_x: int, true_y: int, observed_x: int, observed_y: int) -> float:
        """
        Probability of observing (observed_x, observed_y) given true state (true_x, true_y).
        Sensor is noisy: higher probability if observation is close to true state.
        """
        dist = abs(true_x - observed_x) + abs(true_y - observed_y)
        if dist == 0:
            return 0.6 # 60% chance of correct reading
        elif dist == 1:
            return 0.1 # 10% chance for each of the 4 adjacent cells
        else:
            return 0.0 # 0% chance otherwise (simplified for speed)

    def time_update(self):
        """Forward step 1: Predict next state based on transition model."""
        new_belief = np.zeros((self.rows, self.cols))
        
        for y in range(self.rows):
            for x in range(self.cols):
                if self.belief[y, x] > 0:
                    transitions = self._transition_model(x, y)
                    for nx, ny, prob in transitions:
                        new_belief[ny, nx] += self.belief[y, x] * prob
                        
        self.belief = new_belief

    def observation_update(self, observed_x: int, observed_y: int):
        """Forward step 2: Update belief based on new sensor observation."""
        for y in range(self.rows):
            for x in range(self.cols):
                prob_obs_given_state = self._sensor_model(x, y, observed_x, observed_y)
                self.belief[y, x] *= prob_obs_given_state
                
        # Normalize
        total_prob = np.sum(self.belief)
        if total_prob > 0:
            self.belief /= total_prob
            
    def get_most_likely_position(self) -> Tuple[int, int]:
        """Returns the (x, y) with the highest probability."""
        y, x = np.unravel_index(np.argmax(self.belief), self.belief.shape)
        return int(x), int(y)
