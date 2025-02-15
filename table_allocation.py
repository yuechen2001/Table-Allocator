from collections import defaultdict
import networkx as nx
from typing import List, Dict, Set, Tuple
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
    
    def solve_with_simulated_annealing(self, initial_temperature: float = 100.0,
                                     cooling_rate: float = 0.995,
                                     min_temperature: float = 0.01,
                                     iterations_per_temp: int = 100) -> Dict[int, Set[str]]:
        """
        Solve the table allocation problem using simulated annealing.
        
        Args:
            initial_temperature (float): Starting temperature
            cooling_rate (float): Rate at which temperature decreases
            min_temperature (float): Minimum temperature before stopping
            iterations_per_temp (int): Number of iterations at each temperature
            
        Returns:
            Dict[int, Set[str]]: Final table allocations
        """
        # Initialize with random allocation
        current_tables = self._initialize_random_allocation()
        current_score = self._calculate_satisfaction_score(current_tables)
        best_tables = [table.copy() for table in current_tables]
        best_score = current_score
        
        temperature = initial_temperature
        
        while temperature > min_temperature:
            for _ in range(iterations_per_temp):
                # Get random swap candidates
                table1_idx, person1, table2_idx, person2 = self._get_random_swap_candidates(current_tables)
                
                # Calculate change in score
                delta = self._try_swap(current_tables, person1, table1_idx, person2, table2_idx)
                
                # Accept or reject the swap based on simulated annealing criteria
                if delta > 0 or random.random() < math.exp(delta / temperature):
                    self._perform_swap(current_tables, person1, table1_idx, person2, table2_idx)
                    current_score += delta
                    
                    # Update best solution if necessary
                    if current_score > best_score:
                        best_tables = [table.copy() for table in current_tables]
                        best_score = current_score
            
            temperature *= cooling_rate
        
        return {i: table for i, table in enumerate(best_tables)}
