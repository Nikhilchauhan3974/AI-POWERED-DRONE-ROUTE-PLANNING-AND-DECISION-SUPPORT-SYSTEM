from typing import List, Dict, Any, Optional, Tuple

class CSPScheduler:
    """
    Constraint Satisfaction Problem (CSP) solver for drone fleet scheduling.
    Uses Backtracking with Minimum Remaining Values (MRV) heuristic and Forward Checking.
    """
    def __init__(self, drones: List[str], stations: List[str], time_slots: List[int]):
        self.drones = drones
        self.stations = stations
        self.time_slots = time_slots
        
        # Domain: each drone must be assigned to a (station, time_slot)
        self.domains = {
            drone: [(s, t) for s in stations for t in time_slots]
            for drone in drones
        }
        
    def _is_consistent(self, assignment: Dict[str, Tuple[str, int]], var: str, value: Tuple[str, int]) -> bool:
        """Check if assigning value to var is consistent with current assignments."""
        station, time_slot = value
        
        # Constraint: No two drones can use the same station at the same time
        for assigned_var, assigned_val in assignment.items():
            if assigned_val == value:
                return False
                
        return True

    def _forward_check(self, unassigned_vars: List[str], var: str, value: Tuple[str, int]) -> bool:
        """
        Forward checking: Temporarily remove the assigned value from the domains 
        of all other unassigned variables. If any domain becomes empty, return False.
        """
        for other_var in unassigned_vars:
            if value in self.domains[other_var]:
                self.domains[other_var].remove(value)
                if not self.domains[other_var]:
                    return False
        return True
        
    def _select_unassigned_variable_mrv(self, assignment: Dict[str, Tuple[str, int]]) -> str:
        """Minimum Remaining Values (MRV) heuristic."""
        unassigned = [v for v in self.drones if v not in assignment]
        return min(unassigned, key=lambda var: len(self.domains[var]))

    def solve(self) -> Optional[Dict[str, Tuple[str, int]]]:
        """Solves the CSP and returns the assignment, or None if no solution exists."""
        return self._backtrack({})

    def _backtrack(self, assignment: Dict[str, Tuple[str, int]]) -> Optional[Dict[str, Tuple[str, int]]]:
        if len(assignment) == len(self.drones):
            return assignment

        var = self._select_unassigned_variable_mrv(assignment)
        
        # Keep a copy of domains for backtracking
        domains_copy = {v: list(d) for v, d in self.domains.items()}
        
        for value in self.domains[var]:
            if self._is_consistent(assignment, var, value):
                assignment[var] = value
                
                # Apply forward checking
                unassigned = [v for v in self.drones if v not in assignment]
                if self._forward_check(unassigned, var, value):
                    result = self._backtrack(assignment)
                    if result is not None:
                        return result
                        
                # Backtrack: Restore domains and remove assignment
                self.domains = {v: list(d) for v, d in domains_copy.items()}
                del assignment[var]
                
        return None
