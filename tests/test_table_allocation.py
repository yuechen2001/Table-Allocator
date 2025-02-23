import unittest
import random
import networkx as nx
import pandas as pd
import os
from table_allocator.core import TableAllocator
from table_allocator.excel_io import ExcelTableAllocator
from table_allocator.utils.test_data import generate_test_data, validate_output_data

class TestTableAllocation(unittest.TestCase):
    def setUp(self):
        """Set up a test instance before each test."""
        self.num_tables = 3
        self.table_size = 4
        self.num_people = 10
        self.allocator = TableAllocator(self.num_tables, self.table_size, self.num_people)
        
        # Add some test people and preferences
        self.people = [f'Person{i}' for i in range(self.num_people)]
        for person in self.people:
            self.allocator.people.add(person)
            # Add preferences for each person
            preferences = random.sample([p for p in self.people if p != person], 2)
            self.allocator.add_preference(person, preferences)

    def test_adaptive_temperature_behavior(self):
        """Test that temperature adapts based on solution quality."""
        # Create a more challenging test case
        allocator = TableAllocator(num_tables=3, table_size=4, num_people=9)
        
        # Add preferences that create local optima
        people = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9']
        
        # Group 1 prefers to sit together
        for p1 in ['P1', 'P2', 'P3']:
            others = [p2 for p2 in ['P1', 'P2', 'P3'] if p2 != p1]
            allocator.add_preference(p1, others, weight=2.0)
            
        # Group 2 prefers to sit together
        for p1 in ['P4', 'P5', 'P6']:
            others = [p2 for p2 in ['P4', 'P5', 'P6'] if p2 != p1]
            allocator.add_preference(p1, others, weight=2.0)
            
        # Group 3 prefers to sit together
        for p1 in ['P7', 'P8', 'P9']:
            others = [p2 for p2 in ['P7', 'P8', 'P9'] if p2 != p1]
            allocator.add_preference(p1, others, weight=2.0)
            
        # Add some cross-group preferences to create conflicts
        allocator.add_preference('P1', ['P4'], weight=3.0)
        allocator.add_preference('P4', ['P7'], weight=3.0)
        allocator.add_preference('P7', ['P1'], weight=3.0)
        
        _, temp_history = allocator.solve_with_simulated_annealing(
            initial_temperature=100.0,
            min_temperature=0.01,
            max_iterations=2000,
            return_temp_history=True
        )
        
        # Count temperature increases
        num_increases = sum(1 for i in range(1, len(temp_history)) if temp_history[i] > temp_history[i-1])
        self.assertGreater(num_increases, 0, "No temperature increases found")
        
        # Ensure we don't have too many increases
        self.assertLess(num_increases, len(temp_history) / 2, 
                      "Temperature increases more often than decreases")

    def test_algorithm_correctness(self):
        """Test that the algorithm finds optimal solution for a simple case."""
        # Create a simple problem where optimal solution is known
        allocator = TableAllocator(num_tables=2, table_size=3, num_people=6)
        
        # Create two groups of friends that should sit together
        group1 = ['A1', 'A2', 'A3']
        group2 = ['B1', 'B2', 'B3']
        
        # Add strong preferences within groups
        for group in [group1, group2]:
            for p1 in group:
                others = [p2 for p2 in group if p2 != p1]
                allocator.add_preference(p1, others, weight=2.0)
        
        # Add weak preferences between groups
        allocator.add_preference('A1', ['B1'], weight=0.5)
        allocator.add_preference('A2', ['B2'], weight=0.5)
        
        # Solve with fixed seed for deterministic behavior
        solution = allocator.solve_with_simulated_annealing(
            initial_temperature=100.0,
            min_temperature=0.01,
            max_iterations=1000,
            random_seed=42
        )
        
        # Convert solution to sets for easier comparison
        table_sets = [set(solution[i]) for i in range(2)]
        
        # Verify that groups are kept together (either configuration is optimal)
        group1_set = set(group1)
        group2_set = set(group2)
        
        self.assertTrue(
            (group1_set in table_sets and group2_set in table_sets) or
            (group1_set in table_sets and group2_set in table_sets),
            "Algorithm failed to keep strongly connected groups together"
        )
        
        # Calculate satisfaction score
        score = allocator._calculate_satisfaction_score([solution[i] for i in range(2)])
        
        # Debug output
        print("\nActual solution:")
        for i, table in solution.items():
            print(f"Table {i}: {table}")
        print(f"Score: {score}")
        
        # Known optimal score for this configuration
        # Each person has 2 preferences within their group with weight 2.0
        # Each person can only see 1 preference when groups are separated
        optimal_score = 6 * 1 * 2.0  # 6 people × 1 satisfied preference × 2.0 weight = 12.0
        
        # Allow for small deviation from optimal
        self.assertGreaterEqual(score, optimal_score * 0.95,
                              "Algorithm found significantly suboptimal solution")

    def _verify_allocation_validity(self, allocation):
        """Helper method to verify allocation constraints."""
        # Check all tables exist
        self.assertEqual(len(allocation), self.num_tables)
        
        # Check table sizes
        for table in allocation.values():
            self.assertLessEqual(len(table), self.table_size)
            
        # Check all people are allocated exactly once
        allocated_people = set()
        for table in allocation.values():
            allocated_people.update(table)
        self.assertEqual(len(allocated_people), self.num_people)

class TestExcelIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data directory once for all tests."""
        if not os.path.exists('input_data'):
            os.makedirs('input_data')
        if not os.path.exists('output_data'):
            os.makedirs('output_data')
        
    def setUp(self):
        """Set up test instance."""
        # Generate test data
        self.test_files = generate_test_data()
        
    def test_excel_file_creation(self):
        """Test that Excel test files can be created successfully."""
        for test_file in self.test_files:
            self.assertTrue(os.path.exists(test_file))
            
    def test_excel_data_processing(self):
        """Test that Excel data is processed correctly."""
        for test_file in self.test_files:
            allocator = ExcelTableAllocator(test_file)
            self.assertIsNotNone(allocator.preferences_df)
            self.assertIsNotNone(allocator.config_df)
            
    def test_allocation_results(self):
        """Test that allocations from Excel input are valid."""
        for test_file in self.test_files:
            allocator = ExcelTableAllocator(test_file)
            table_allocator = allocator.process_preferences()
            allocation = table_allocator.solve_with_simulated_annealing()
            
            # Check that all tables respect size limits
            config = allocator.config_df.iloc[0]
            table_size = int(config['TableSize'])
            for table in allocation.values():
                self.assertLessEqual(len(table), table_size)
            
            # Check that all people are allocated
            allocated_people = set()
            for table in allocation.values():
                allocated_people.update(table)
            self.assertEqual(len(allocated_people), len(table_allocator.people))
            
            # Validate the output data from output_data directory
            output_file = test_file.replace('input_data', 'output_data').replace('.xlsx', '_result.xlsx')
            allocator.solve_and_save(output_file)
            validate_output_data(output_file)

    @classmethod
    def tearDownClass(cls):
        """Clean up test files after all tests are done."""
        try:
            # Remove test input files
            if os.path.exists('input_data'):
                for file in os.listdir('input_data'):
                    if file.endswith('.xlsx'):
                        try:
                            os.remove(os.path.join('input_data', file))
                        except:
                            print(f"Warning: Could not remove test file: {file}")
                try:
                    os.rmdir('input_data')
                except:
                    print("Warning: Could not remove input_data directory")
            
            # Remove test output files
            if os.path.exists('output_data'):
                for file in os.listdir('output_data'):
                    if file.endswith('.xlsx'):
                        try:
                            os.remove(os.path.join('output_data', file))
                        except:
                            print(f"Warning: Could not remove output file: {file}")
                try:
                    os.rmdir('output_data')
                except:
                    print("Warning: Could not remove output_data directory")
        finally:
            # Ensure we don't propagate cleanup errors
            pass

if __name__ == '__main__':
    unittest.main()
