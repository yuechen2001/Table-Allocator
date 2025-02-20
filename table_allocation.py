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
        """
        Add preferences for a person.
        
        Args:
            person (str): Name of the person
            preferences (List[str]): List of people they prefer to sit with
            weight (float): Weight of the preference (default: 1.0)
        """
        self.people.add(person)
        for pref in preferences:
            self.people.add(pref)
            self.preference_graph.add_edge(person, pref, weight=weight)
            
    def _initialize_random_allocation(self) -> List[Set[str]]:
        """
        Create an initial random allocation of people to tables.
        
        Returns:
            List[Set[str]]: List of sets representing table allocations
        """
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
        """
        Calculate the total weighted satisfaction score for the current allocation.
        
        Args:
            tables (List[Set[str]]): Current table allocation
            
        Returns:
            float: Total weighted satisfaction score
        """
        score = 0.0
        for table in tables:
            for person in table:
                for other in table:
                    if person != other and self.preference_graph.has_edge(person, other):
                        score += self.preference_graph[person][other]['weight']
        return score / 2  # Divide by 2 as each preference is counted twice
    
    def _get_random_swap_candidates(self, tables: List[Set[str]]) -> Tuple[int, str, int, str]:
        """
        Get random candidates for swapping.
        
        Returns:
            Tuple[int, str, int, str]: (table1_idx, person1, table2_idx, person2)
        """
        table1_idx = random.randrange(self.num_tables)
        table2_idx = random.randrange(self.num_tables)
        while table1_idx == table2_idx or not tables[table1_idx] or not tables[table2_idx]:
            table1_idx = random.randrange(self.num_tables)
            table2_idx = random.randrange(self.num_tables)
            
        person1 = random.choice(list(tables[table1_idx]))
        person2 = random.choice(list(tables[table2_idx]))
        
        return table1_idx, person1, table2_idx, person2
    
    def _try_swap(self, tables: List[Set[str]], person1: str, table1_idx: int, 
                  person2: str, table2_idx: int) -> float:
        """
        Calculate the change in satisfaction score if two people were to swap tables.
        
        Returns:
            float: Change in satisfaction score (positive means improvement)
        """
        # Calculate current satisfaction for affected tables
        current_score = (
            sum(self.preference_graph[person1][other]['weight'] 
                for other in tables[table1_idx] if self.preference_graph.has_edge(person1, other)) +
            sum(self.preference_graph[person2][other]['weight'] 
                for other in tables[table2_idx] if self.preference_graph.has_edge(person2, other))
        )
        
        # Calculate new satisfaction after potential swap
        new_score = (
            sum(self.preference_graph[person1][other]['weight'] 
                for other in tables[table2_idx] if self.preference_graph.has_edge(person1, other)) +
            sum(self.preference_graph[person2][other]['weight'] 
                for other in tables[table1_idx] if self.preference_graph.has_edge(person2, other))
        )
        
        return new_score - current_score
    
    def _perform_swap(self, tables: List[Set[str]], person1: str, table1_idx: int,
                     person2: str, table2_idx: int) -> None:
        """
        Perform the swap operation between two people.
        """
        tables[table1_idx].remove(person1)
        tables[table2_idx].remove(person2)
        tables[table1_idx].add(person2)
        tables[table2_idx].add(person1)
    
    def _generate_initial_solution(self) -> List[Set[str]]:
        """
        Generate an initial random allocation of people to tables.
        
        Returns:
            List[Set[str]]: List of sets representing table allocations
        """
        people_list = list(self.people)
        random.shuffle(people_list)
        tables = [set() for _ in range(self.num_tables)]
        
        person_idx = 0
        for table_idx in range(self.num_tables):
            while len(tables[table_idx]) < self.table_size and person_idx < len(people_list):
                tables[table_idx].add(people_list[person_idx])
                person_idx += 1
                
        return tables
    
    def _generate_neighbor(self, current_solution: List[Set[str]]) -> List[Set[str]]:
        """
        Generate a neighbor solution by swapping two people.
        
        Args:
            current_solution (List[Set[str]]): Current table allocation
            
        Returns:
            List[Set[str]]: Neighbor table allocation
        """
        table1_idx, person1, table2_idx, person2 = self._get_random_swap_candidates(current_solution)
        new_solution = [table.copy() for table in current_solution]
        new_solution[table1_idx].remove(person1)
        new_solution[table2_idx].remove(person2)
        new_solution[table1_idx].add(person2)
        new_solution[table2_idx].add(person1)
        
        return new_solution
    
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
            
        Returns:
            float: New temperature
        """
        if len(accepted_moves) < window_size:
            return temperature
            
        acceptance_rate = sum(accepted_moves[-window_size:]) / window_size
        
        if acceptance_rate > target_acceptance_rate:
            # Cool down if accepting too many moves
            return temperature * 0.95
        elif acceptance_rate < reheat_threshold:
            # Reheat if accepting too few moves
            return min(temperature * 1.5, initial_temperature)
        else:
            # Gradual cooling
            return temperature * 0.99
    
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
            random_seed: Optional seed for random number generation (used in testing)
        
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
        temp_history = [temperature] if return_temp_history else None
        window_size = 100  # Window for tracking acceptance rate
        
        for _ in range(max_iterations):
            # Generate neighbor solution
            new_solution = self._generate_neighbor(current_solution)
            new_score = self._calculate_satisfaction_score(new_solution)
            
            # Calculate acceptance probability
            delta = new_score - current_score
            acceptance_prob = min(1.0, math.exp(delta / temperature))
            
            # Accept or reject the new solution
            accepted = random.random() < acceptance_prob
            if accepted:
                current_solution = new_solution
                current_score = new_score
                
                if current_score > best_score:
                    best_solution = current_solution.copy()
                    best_score = current_score
            
            # Track move acceptance and adjust temperature
            accepted_moves.append(1 if accepted else 0)
            if len(accepted_moves) > window_size:
                accepted_moves.pop(0)
                
            temperature = self._adjust_temperature(
                temperature=temperature,
                accepted_moves=accepted_moves,
                window_size=window_size,
                initial_temperature=initial_temperature
            )
            
            if return_temp_history:
                temp_history.append(temperature)
            
            # Stop if temperature is too low
            if temperature < min_temperature:
                break
        
        result = {i: table for i, table in enumerate(best_solution)}
        return (result, temp_history) if return_temp_history else result
