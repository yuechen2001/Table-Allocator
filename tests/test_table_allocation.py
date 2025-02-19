import unittest
import random
import networkx as nx
import pandas as pd
import os
from table_allocation import TableAllocator
from table_allocator import ExcelTableAllocator

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
        self.assertEqual(allocated_people, self.allocator.people)
        
        # Check no person is allocated multiple times
        total_allocations = sum(len(table) for table in allocation.values())
        self.assertEqual(total_allocations, len(self.allocator.people))


class TestExcelIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data directory once for all tests."""
        cls.test_data_dir = "test_data"
        if not os.path.exists(cls.test_data_dir):
            os.makedirs(cls.test_data_dir)
            
    def setUp(self):
        """Set up test instance."""
        self.test_cases = self._generate_test_cases()
        
    def _generate_class_reunion_preferences(self):
        """Generate preferences for class reunion scenario"""
        groups = {
            'SportTeam': ['John', 'Mike', 'Sarah', 'Tom'],
            'StudyGroup': ['Emma', 'Lisa', 'David', 'Alex'],
            'TheaterClub': ['Sophie', 'James', 'Oliver'],
            'Others': ['Sam', 'Peter', 'Mary']
        }
        
        people = []
        preferences = []
        weights = []
        
        for group, members in groups.items():
            for person in members:
                people.append(person)
                group_preferences = [m for m in members if m != person]
                preferences.append(', '.join(group_preferences))
                weights.append(2.0 if group != 'Others' else 1.0)
        
        return {
            'Person': people,
            'Preferences': preferences,
            'PreferenceWeight': weights
        }
        
    def _generate_corporate_preferences(self):
        """Generate preferences for corporate event scenario"""
        departments = {
            'Engineering': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'Marketing': ['Eve', 'Frank', 'Grace'],
            'Sales': ['Henry', 'Ivy', 'Jack'],
            'Management': ['Karen', 'Larry', 'Monica']
        }
        
        people = []
        preferences = []
        weights = []
        
        # Add intra-department preferences
        for dept, members in departments.items():
            for person in members:
                people.append(person)
                dept_preferences = [m for m in members if m != person]
                preferences.append(', '.join(dept_preferences))
                weights.append(1.5)  # Moderate preference for department colleagues
                
        return {
            'Person': people,
            'Preferences': preferences,
            'PreferenceWeight': weights
        }
        
    def _generate_test_cases(self):
        """Generate all test cases"""
        return {
            'wedding_scenario.xlsx': {
                'config': {
                    'NumTables': [3],
                    'TableSize': [4],
                    'NumPeople': [10]
                },
                'preferences': {
                    'Person': [
                        'Bride', 'Groom', 'BrideMother', 'BrideFather',
                        'GroomMother', 'GroomFather', 'BrideSister',
                        'GroomBrother', 'BrideFriend', 'GroomFriend'
                    ],
                    'Preferences': [
                        'Groom, BrideMother, BrideFather',
                        'Bride, GroomMother, GroomFather',
                        'Bride, BrideFather',
                        'Bride, BrideMother',
                        'Groom, GroomFather',
                        'Groom, GroomMother',
                        'Bride, BrideMother',
                        'Groom, GroomFather',
                        'Bride, BrideSister',
                        'Groom, GroomBrother'
                    ],
                    'PreferenceWeight': [2.0] * 10
                }
            },
            'class_reunion.xlsx': {
                'config': {
                    'NumTables': [4],
                    'TableSize': [4],
                    'NumPeople': [14]
                },
                'preferences': self._generate_class_reunion_preferences()
            },
            'corporate_event.xlsx': {
                'config': {
                    'NumTables': [4],
                    'TableSize': [4],
                    'NumPeople': [13]
                },
                'preferences': self._generate_corporate_preferences()
            }
        }
        
    def test_excel_file_creation(self):
        """Test that Excel test files can be created successfully."""
        for filename, data in self.test_cases.items():
            filepath = os.path.join(self.test_data_dir, filename)
            
            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Write config sheet
                pd.DataFrame(data['config']).to_excel(writer, sheet_name='Config', index=False)
                
                # Write preferences sheet
                pd.DataFrame(data['preferences']).to_excel(writer, sheet_name='Preferences', index=False)
            
            # Verify file exists and can be read
            self.assertTrue(os.path.exists(filepath))
            
            # Try to load it with ExcelTableAllocator
            allocator = ExcelTableAllocator(filepath)
            self.assertIsNotNone(allocator.config_df)
            self.assertIsNotNone(allocator.preferences_df)
            
    def test_excel_data_processing(self):
        """Test that Excel data is processed correctly."""
        for filename, expected_data in self.test_cases.items():
            filepath = os.path.join(self.test_data_dir, filename)
            
            # Create the file first
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                pd.DataFrame(expected_data['config']).to_excel(writer, sheet_name='Config', index=False)
                pd.DataFrame(expected_data['preferences']).to_excel(writer, sheet_name='Preferences', index=False)
            
            # Load and process the file
            allocator = ExcelTableAllocator(filepath)
            
            # Verify configuration
            self.assertEqual(allocator.config_df['NumTables'].iloc[0], expected_data['config']['NumTables'][0])
            self.assertEqual(allocator.config_df['TableSize'].iloc[0], expected_data['config']['TableSize'][0])
            self.assertEqual(allocator.config_df['NumPeople'].iloc[0], expected_data['config']['NumPeople'][0])
            
            # Verify preferences
            self.assertEqual(len(allocator.preferences_df), len(expected_data['preferences']['Person']))
            
    def test_allocation_results(self):
        """Test that allocations from Excel input are valid."""
        for filename in self.test_cases.keys():
            filepath = os.path.join(self.test_data_dir, filename)
            
            # Create the file first if it doesn't exist
            if not os.path.exists(filepath):
                self.test_excel_file_creation()
            
            # Process the file and generate allocation
            allocator = ExcelTableAllocator(filepath)
            output_file = os.path.join(self.test_data_dir, f"output_{filename}")
            allocator.solve_and_save(output_file)
            
            # Verify output file exists
            self.assertTrue(os.path.exists(output_file))
            
    @classmethod
    def tearDownClass(cls):
        """Clean up test files after all tests are done."""
        import shutil
        if os.path.exists(cls.test_data_dir):
            shutil.rmtree(cls.test_data_dir)


if __name__ == '__main__':
    unittest.main()
