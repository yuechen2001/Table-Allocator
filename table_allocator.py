import pandas as pd
import numpy as np
from table_allocation import TableAllocator
import os
from datetime import datetime

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
            min_temperature=0.01,
            max_iterations=10000
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

def process_all_input_files():
    """Process all Excel files in the input_data directory"""
    # Create output directory if it doesn't exist
    if not os.path.exists('output_data'):
        os.makedirs('output_data')
    
    # Process each input file
    input_dir = 'input_data'
    if os.path.exists(input_dir):
        for filename in os.listdir(input_dir):
            if filename.endswith('.xlsx'):
                input_file = os.path.join(input_dir, filename)
                allocator = ExcelTableAllocator(input_file)
                allocator.solve_and_save()


if __name__ == "__main__":
    process_all_input_files()
