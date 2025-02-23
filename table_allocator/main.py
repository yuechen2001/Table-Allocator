"""
Main entry point for the table allocator application.
"""

import os
import sys
from .excel_io import ExcelTableAllocator
from .utils.test_data import generate_test_data

def process_all_input_files(create_test_data=False):
    """
    Process all Excel files in the input_data directory
    
    Args:
        create_test_data (bool): If True, only create test data without processing
    """
    # Create output directory if it doesn't exist
    if not os.path.exists('output_data'):
        os.makedirs('output_data')
    
    if create_test_data:
        # Create test data only
        generate_test_data()
        print("Test data created in input_data directory")
        return
    
    # Process each input file
    input_dir = 'input_data'
    if os.path.exists(input_dir):
        processed_files = 0
        error_files = []
        
        for filename in os.listdir(input_dir):
            if filename.endswith('.xlsx'):
                input_file = os.path.join(input_dir, filename)
                try:
                    allocator = ExcelTableAllocator(input_file)
                    allocator.solve_and_save(os.path.join('output_data', f'result_{filename}'))
                    processed_files += 1
                    print(f"Successfully processed: {filename}")
                except Exception as e:
                    error_files.append((filename, str(e)))
                    print(f"Error processing {filename}: {str(e)}")
        
        # Print summary
        print(f"\nProcessing complete:")
        print(f"Successfully processed: {processed_files} files")
        if error_files:
            print(f"Failed to process {len(error_files)} files:")
            for filename, error in error_files:
                print(f"- {filename}: {error}")

def main():
    """Entry point for the command-line interface."""
    create_test_data = '--create-test-data' in sys.argv
    process_all_input_files(create_test_data)

if __name__ == "__main__":
    main()
