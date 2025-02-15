import pandas as pd
import numpy as np
from table_allocation import TableAllocator
import os
from datetime import datetime
import random

class ExcelTableAllocator:
    def __init__(self, input_file: str):
        """
        Initialize the Excel Table Allocator.
        
        Args:
            input_file (str): Path to the input Excel file
        """
        self.input_file = input_file
        self.preferences_df = None
        self.config_df = None
        self.load_excel_data()
        
    def load_excel_data(self):
        """Load data from Excel file"""
        # Read the configuration sheet
        self.config_df = pd.read_excel(self.input_file, sheet_name='Config')
        
        # Read the preferences sheet
        self.preferences_df = pd.read_excel(self.input_file, sheet_name='Preferences')
        
        # Validate the data
        self._validate_input_data()
        
    def _validate_input_data(self):
        """Validate the input data format"""
        # Check Config sheet
        required_config = {'NumTables', 'TableSize', 'NumPeople'}
        if not all(col in self.config_df.columns for col in required_config):
            raise ValueError(f"Config sheet must contain columns: {required_config}")
            
        # Check Preferences sheet
        required_prefs = {'Person', 'Preferences', 'PreferenceWeight'}
        if not all(col in self.preferences_df.columns for col in required_prefs):
            raise ValueError(f"Preferences sheet must contain columns: {required_prefs}")
    
    def process_preferences(self) -> TableAllocator:
        """Process preferences and create TableAllocator instance"""
        config = self.config_df.iloc[0]
        
        # Create TableAllocator instance
        allocator = TableAllocator(
            num_tables=int(config['NumTables']),
            table_size=int(config['TableSize']),
            num_people=int(config['NumPeople'])
        )
        
        # Add preferences for each person
        for _, row in self.preferences_df.iterrows():
            if pd.isna(row['Preferences']) or str(row['Preferences']).strip() == '':
                continue
                
            # Split preferences string into list
            preferences = [p.strip() for p in str(row['Preferences']).split(',')]
            weight = float(row['PreferenceWeight']) if not pd.isna(row['PreferenceWeight']) else 1.0
            
            allocator.add_preference(row['Person'], preferences, weight=weight)
            
        return allocator
    
    def solve_and_save(self, output_file: str = None):
        """
        Solve the allocation problem and save results to Excel
        
        Args:
            output_file (str, optional): Output Excel file path. If None, generates a default name.
        """
        # Process preferences and solve
        allocator = self.process_preferences()
        allocation = allocator.solve_with_simulated_annealing(
            initial_temperature=100.0,
            cooling_rate=0.995,
            iterations_per_temp=100
        )
        
        # Create results DataFrame
        results = []
        for table_num, people in allocation.items():
            for person in people:
                results.append({
                    'Table': f'Table {table_num + 1}',
                    'Person': person
                })
        results_df = pd.DataFrame(results)
        
        # Calculate satisfaction statistics
        stats = self._calculate_satisfaction_stats(allocator, allocation)
        stats_df = pd.DataFrame([stats])
        
        # Generate output filename if not provided
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'table_allocation_results_{timestamp}.xlsx'
        
        # Save to Excel
        with pd.ExcelWriter(output_file) as writer:
            results_df.to_excel(writer, sheet_name='Allocations', index=False)
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
        print(f"Results saved to: {output_file}")
        return output_file
    
    def _calculate_satisfaction_stats(self, allocator, allocation):
        """Calculate satisfaction statistics"""
        total_satisfaction = 0.0
        total_preferences = 0
        satisfied_preferences = 0
        
        for table in allocation.values():
            for person1 in table:
                for person2 in table:
                    if person1 < person2:
                        if allocator.preference_graph.has_edge(person1, person2):
                            weight = allocator.preference_graph[person1][person2]['weight']
                            total_satisfaction += weight
                            satisfied_preferences += 1
                        total_preferences += 1
        
        return {
            'Total Weighted Satisfaction': total_satisfaction,
            'Satisfied Preferences': satisfied_preferences,
            'Total Possible Pairs': total_preferences,
            'Satisfaction Rate (%)': (satisfied_preferences / total_preferences * 100) if total_preferences > 0 else 0
        }

def create_test_data():
    """Create test Excel files in the input_data directory"""
    test_cases = {
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
                'PreferenceWeight': [3.0] * 2 + [2.0] * 4 + [1.5] * 2 + [1.0] * 2
            }
        },
        'corporate_event.xlsx': {
            'config': {
                'NumTables': [5],
                'TableSize': [6],
                'NumPeople': [28]
            },
            'preferences': _generate_corporate_preferences()
        },
        'class_reunion.xlsx': {
            'config': {
                'NumTables': [4],
                'TableSize': [5],
                'NumPeople': [18]
            },
            'preferences': _generate_class_reunion_preferences()
        }
    }
    
    input_dir = 'input_data'
    os.makedirs(input_dir, exist_ok=True)
    
    for filename, data in test_cases.items():
        filepath = os.path.join(input_dir, filename)
        with pd.ExcelWriter(filepath) as writer:
            pd.DataFrame(data['config']).to_excel(writer, sheet_name='Config', index=False)
            pd.DataFrame(data['preferences']).to_excel(writer, sheet_name='Preferences', index=False)
        print(f"Created test file: {filename}")

def _generate_corporate_preferences():
    """Generate preferences for corporate event scenario"""
    departments = ['Sales', 'Engineering', 'Marketing', 'HR', 'Finance']
    people = []
    preferences = []
    weights = []
    
    for dept in departments:
        for i in range(5 if dept != 'HR' else 3):
            person = f'{dept}_{i+1}'
            people.append(person)
            dept_colleagues = [f'{dept}_{j+1}' for j in range(5 if dept != 'HR' else 3) if f'{dept}_{j+1}' != person]
            preferences.append(', '.join(dept_colleagues))
            weights.append(2.0)
    
    return {
        'Person': people,
        'Preferences': preferences,
        'PreferenceWeight': weights
    }

def _generate_class_reunion_preferences():
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

def process_all_input_files():
    """Process all Excel files in the input_data directory"""
    input_dir = 'input_data'
    output_dir = 'output_data'
    
    # Ensure directories exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each input file
    for filename in os.listdir(input_dir):
        if filename.endswith('.xlsx'):
            print(f"\nProcessing: {filename}")
            
            input_path = os.path.join(input_dir, filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f'result_{os.path.splitext(filename)[0]}_{timestamp}.xlsx'
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                allocator = ExcelTableAllocator(input_path)
                allocator.solve_and_save(output_path)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--create-test-data':
        create_test_data()
    else:
        process_all_input_files()
