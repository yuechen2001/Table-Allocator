"""
Core implementation of the table allocation algorithm.
"""

import networkx as nx
from typing import List, Set, Dict, Tuple, Union
import random
import math

class TableAllocator:
    def __init__(self, num_tables: int, table_size: int, num_people: int):
        """
        Initialize the TableAllocator.
        
        Args:
            num_tables (int): Number of available tables
            table_size (int): Size of each table
            num_people (int): Total number of people to allocate
        """
        self.num_tables = num_tables
        self.table_size = table_size
        self.num_people = num_people
        self.preference_graph = nx.Graph()
        self.people = set()
        
    def add_preference(self, person: str, preferences: List[str], weight: float = 1.0) -> None:
        """Add preferences for a person."""
        self.people.add(person)
        for pref in preferences:
            self.people.add(pref)
            self.preference_graph.add_edge(person, pref, weight=weight)
            
    def solve_with_simulated_annealing(self, initial_temperature: float = 100.0,
                                     min_temperature: float = 0.01,
                                     max_iterations: int = 10000,
                                     return_temp_history: bool = False,
                                     random_seed: int = None) -> Union[Dict[int, Set[str]], Tuple[Dict[int, Set[str]], List[float]]]:
        """
        Solve the table allocation problem using simulated annealing with adaptive temperature.
        
        Args:
            initial_temperature: Starting temperature
            min_temperature: Minimum temperature to stop at
            max_iterations: Maximum number of iterations
            return_temp_history: Whether to return temperature history for analysis
            random_seed: Optional seed for random number generation
            
        Returns:
            If return_temp_history is False: Dictionary mapping table numbers to sets of people
            If return_temp_history is True: Tuple of (allocation dict, temperature history)
        """
        if random_seed is not None:
            random.seed(random_seed)
            
        current_solution = self._generate_initial_solution()
        current_score = self._calculate_satisfaction_score(current_solution)
        best_solution = current_solution.copy()
        best_score = current_score
        
        temperature = initial_temperature
        accepted_moves = []
        temp_history = [] if return_temp_history else None
        
        for iteration in range(max_iterations):
            if temperature < min_temperature:
                break
                
            # Generate neighbor solution
            neighbor = self._generate_neighbor(current_solution)
            neighbor_score = self._calculate_satisfaction_score(neighbor)
            
            # Calculate score difference
            delta = neighbor_score - current_score
            
            # Accept or reject the new solution
            if delta > 0 or random.random() < math.exp(delta / temperature):
                current_solution = neighbor
                current_score = neighbor_score
                accepted_moves.append(1)
                
                # Update best solution if needed
                if current_score > best_score:
                    best_solution = current_solution.copy()
                    best_score = current_score
            else:
                accepted_moves.append(0)
            
            # Adjust temperature
            temperature = self._adjust_temperature(
                temperature, accepted_moves,
                window_size=100,
                initial_temperature=initial_temperature
            )
            
            if return_temp_history:
                temp_history.append(temperature)
        
        # Convert solution to dictionary format
        result = {i: table for i, table in enumerate(best_solution)}
        
        if return_temp_history:
            return result, temp_history
        return result
    
    def _generate_initial_solution(self) -> List[Set[str]]:
        """Generate an initial random allocation of people to tables."""
        people_list = list(self.people)
        random.shuffle(people_list)
        tables = [set() for _ in range(self.num_tables)]
        
        person_idx = 0
        for table_idx in range(self.num_tables):
            while len(tables[table_idx]) < self.table_size and person_idx < len(people_list):
                tables[table_idx].add(people_list[person_idx])
                person_idx += 1
                
        return tables
    
    def _calculate_satisfaction_score(self, tables: List[Set[str]]) -> float:
        """Calculate the total weighted satisfaction score for the current allocation."""
        score = 0.0
        for table in tables:
            for person1 in table:
                for person2 in table:
                    if person1 < person2 and self.preference_graph.has_edge(person1, person2):
                        score += self.preference_graph[person1][person2]['weight']
        return score
    
    def _generate_neighbor(self, current_solution: List[Set[str]]) -> List[Set[str]]:
        """Generate a neighbor solution by swapping two people."""
        neighbor = [table.copy() for table in current_solution]
        table1_idx, person1, table2_idx, person2 = self._get_random_swap_candidates(neighbor)
        
        # Perform the swap
        neighbor[table1_idx].remove(person1)
        neighbor[table2_idx].remove(person2)
        neighbor[table1_idx].add(person2)
        neighbor[table2_idx].add(person1)
        
        return neighbor
    
    def _get_random_swap_candidates(self, tables: List[Set[str]]) -> Tuple[int, str, int, str]:
        """Get random candidates for swapping."""
        # Select first table and person
        table1_idx = random.randrange(self.num_tables)
        while not tables[table1_idx]:
            table1_idx = random.randrange(self.num_tables)
        person1 = random.choice(list(tables[table1_idx]))
        
        # Select second table and person
        table2_idx = random.randrange(self.num_tables)
        while not tables[table2_idx] or table2_idx == table1_idx:
            table2_idx = random.randrange(self.num_tables)
        person2 = random.choice(list(tables[table2_idx]))
        
        return table1_idx, person1, table2_idx, person2
    
    def _adjust_temperature(self, temperature: float, accepted_moves: List[int],
                          window_size: int, initial_temperature: float,
                          target_acceptance_rate: float = 0.3,
                          reheat_threshold: float = 0.1) -> float:
        """
        Adjust temperature based on acceptance rate of recent moves.
        
        Args:
            temperature: Current temperature
            accepted_moves: List of recent move acceptances (1 for accepted, 0 for rejected)
            window_size: Size of window for tracking acceptance rate
            initial_temperature: Starting temperature (used as cap for reheating)
            target_acceptance_rate: Target acceptance rate for moves
            reheat_threshold: Minimum acceptance rate before reheating
        """
        # Ensure window size doesn't exceed available moves
        effective_window = min(window_size, len(accepted_moves))
        if effective_window == 0:
            return temperature
            
        # Calculate acceptance rate over recent moves
        recent_acceptance_rate = sum(accepted_moves[-effective_window:]) / effective_window
        
        if recent_acceptance_rate > target_acceptance_rate:
            # Cool down if accepting too many moves
            temperature *= 0.95
        elif recent_acceptance_rate < reheat_threshold:
            # Reheat if acceptance rate is too low
            temperature = min(temperature * 1.1, initial_temperature)
            
        return temperature
