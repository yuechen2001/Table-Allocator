"""
Excel input/output handling for table allocation.
"""

import pandas as pd
import os
from datetime import datetime
from .core import TableAllocator

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
        try:
            # Try to read the Excel file
            self.preferences_df = pd.read_excel(self.input_file, sheet_name='Preferences')
            self.config_df = pd.read_excel(self.input_file, sheet_name='Config')
            self._validate_input_data()
        except FileNotFoundError:
            raise ValueError(f"Input file not found: {self.input_file}")
        except pd.errors.EmptyDataError:
            raise ValueError(f"Input file is empty: {self.input_file}")
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
        
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
            preferences = [p.strip() for p in str(row['Preferences']).split(',')]
            weight = float(row['PreferenceWeight']) if not pd.isna(row['PreferenceWeight']) else 1.0
            allocator.add_preference(row['Person'], preferences, weight=weight)
            
        return allocator
    
    def solve_and_save(self, output_file: str = None) -> None:
        """
        Solve the table allocation problem and save results to Excel.
        
        Args:
            output_file (str, optional): Output file path. If not provided, will generate one.
        """
        if output_file is None:
            # Generate output filename based on input filename
            base_name = os.path.basename(self.input_file)
            output_file = os.path.join('output_data', f'result_{base_name}')

        # Get allocator and solve
        allocator = self.process_preferences()
        allocation = allocator.solve_with_simulated_annealing()
        
        # Calculate satisfaction metrics
        total_score = allocator._calculate_satisfaction_score([set(table) for table in allocation.values()])
        max_possible_score = sum(weight for _, _, weight in allocator.preference_graph.edges.data('weight'))
        satisfaction_rate = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        # Prepare allocation data
        rows = []
        for table_num, people in allocation.items():
            for person in people:
                rows.append({'Table': table_num, 'Person': person})
        
        # Create allocations sheet
        allocations_df = pd.DataFrame(rows)
        
        # Create table summary
        table_summary = []
        for table_num in range(1, self.config_df.iloc[0]['NumTables'] + 1):
            people_at_table = len(allocation.get(table_num, set()))
            table_summary.append({
                'Table': table_num,
                'NumPeople': people_at_table
            })
        summary_df = pd.DataFrame(table_summary)
        
        # Create satisfaction metrics
        metrics_df = pd.DataFrame([
            {'Metric': 'Total Satisfaction Score', 'Value': f'{total_score:.2f}'},
            {'Metric': 'Maximum Possible Score', 'Value': f'{max_possible_score:.2f}'},
            {'Metric': 'Satisfaction Rate', 'Value': f'{satisfaction_rate:.1f}%'},
            {'Metric': 'Rating', 'Value': 'Excellent' if satisfaction_rate > 80 else 'Good' if satisfaction_rate > 60 else 'Needs Review'}
        ])
        
        # Save to Excel
        with pd.ExcelWriter(output_file) as writer:
            allocations_df.to_excel(writer, sheet_name='Allocations', index=False)
            summary_df.to_excel(writer, sheet_name='Table Summary', index=False)
            metrics_df.to_excel(writer, sheet_name='Satisfaction Metrics', index=False)
