# Table Allocation Algorithm

A smart tool to create optimal seating arrangements for your events by considering people's seating preferences.

## Quick Start Guide (For Event Planners)

### What This Tool Does
This tool helps you create the best possible seating arrangements for your events (weddings, corporate events, class reunions, etc.) by:
- Considering who people want to sit with
- Making sure tables don't exceed their capacity
- Maximizing everyone's satisfaction with their seating

### How to Use
1. **Prepare Your Input**
   Create an Excel file with two sheets:

   Sheet 1 - Named "Config":
   | NumTables | TableSize | NumPeople |
   |-----------|-----------|-----------|
   | 5         | 8         | 40        |

   Sheet 2 - Named "Preferences":
   | Person      | Preferences                  | PreferenceWeight |
   |-------------|------------------------------|------------------|
   | John Smith  | Jane Doe, Bob Johnson       | 1.0             |
   | Jane Doe    | John Smith, Sarah Williams  | 1.0             |

   - `PreferenceWeight`: Use higher numbers (like 2.0) for stronger preferences

2. **Get Your Results**
   - Place your Excel file in the `input_data` folder
   - Run the program
   - Find your seating plan in the `output_data` folder

3. **Understanding Results**
   The output Excel file will contain three sheets:

   Sheet 1 - "Allocations":
   | Table | Person |
   |-------|--------|
   | 1     | John   |
   | 1     | Mike   |
   | 1     | Tom    |
   | 1     | Sarah  |
   | 1     | Peter  |
   | 2     | Sam    |
   | 2     | James  |
   | 2     | Oliver |
   | 2     | Mary   |
   | 2     | Sophie |
   | 3     | Lisa   |
   | 3     | David  |
   | 3     | Alex   |
   | 3     | Emma   |

   Sheet 2 - "Table Summary":
   | Table | NumPeople |
   |-------|-----------|
   | 1     | 5         |
   | 2     | 5         |
   | 3     | 4         |
   | 4     | 0         |

   Sheet 3 - "Satisfaction Metrics":
   | Metric                  | Value    |
   |------------------------|----------|
   | Total Satisfaction     | 42.5     |
   | Maximum Possible Score | 50.0     |
   | Satisfaction Rate      | 85.0%    |
   | Rating                 | Excellent |

   This shows:
   - Each person's assigned table
   - Number of people at each table
   - Overall satisfaction metrics
   - Quality rating of the solution

### Tips for Best Results
- Use weights (1.0 - 3.0) to indicate preference strength
  - 1.0: "Would like to sit together"
  - 2.0: "Should sit together" (e.g., close friends)
  - 3.0: "Must sit together" (e.g., couples)
- Keep preferences realistic (3-4 per person is ideal)

## Using the Executable

### How to Use
1. **Prepare Your Input**
   Create an Excel file with two sheets as described above.

2. **Place the Excel File**
   - Save your Excel file in a `input_data` folder.

3. **Run the Executable**
   - Double-click the executable file to run it.

4. **Retrieve Your Results**
   - Find your results in the `output_data` folder.
   - Open the output Excel file to see your table allocations.

## Technical Documentation

### Algorithm Details

The solution implements a simulated annealing algorithm with adaptive temperature control:

1. **Solution**
   - Each iteration:
     - Selects two random people from different tables
     - Calculates satisfaction delta for potential swap
     - Accepts/rejects based on:
       - Better solutions: Always accepted
       - Worse solutions: Accepted with probability exp(-Δ/T)
         - Δ: Satisfaction decrease
         - T: Current temperature

2. **Adaptive Temperature Control**
   - Initial temperature: 100.0
   - Monitors acceptance rate
   - Dynamic temperature adjustment:
     - Cools when accepting too many suboptimal moves
     - Reheats if acceptance rate drops too low
   - Termination at minimum temperature (0.01) or max iterations

3. **Satisfaction Scoring**
   - Weighted preference satisfaction
   - Normalized for mutual preferences
   - Higher weights prioritize certain arrangements

### Project Structure

```
table-allocator/
├── table_allocator/
│   ├── core.py         # Core allocation algorithm
│   ├── excel_io.py     # Excel file handling
│   ├── main.py         # Main processing logic
│   └── utils/
│       └── test_data.py
├── tests/
│   └── test_table_allocation.py
├── input_data/         # Place Excel files here
├── output_data/        # Results will appear here
├── requirements.txt
└── run.py             # Run this file
```

The program uses:
- `core.py` for the allocation algorithm
- `excel_io.py` for file operations
- `main.py` for process coordination
- `test_data.py` for sample data generation

### Building the Project

#### Creating the Executable
The project can be packaged into a standalone executable using PyInstaller:

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Create the Executable**
   ```bash
   pyinstaller --onefile run.py
   ```

3. **Executable Location**
   - The executable will be created in the `dist` directory
   - Package the executable with:
     - An empty `input_data` directory
     - An empty `output_data` directory
     - A copy of the README for instructions

4. **Rebuilding Required**
   Rebuild the executable when updating:
   - Core algorithm changes
   - Error handling improvements
   - Input/output format changes
   - Dependencies

### Development Setup

1. **Environment Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install package in development mode
   pip install -e .
   ```

2. **Dependencies**
   ```
   pandas>=1.5.0
   numpy>=1.21.0
   networkx>=2.8.0
   openpyxl>=3.0.0
   ```

### Testing

1. **Test Scenarios**
   The test suite includes:
   - Basic allocation test (3 tables, 12 people)
   - School club event (4 tables, 16 people)
   - Wedding seating (5 tables, 40 people)
   - Empty table handling
   - Strong preferences (couples, groups)

2. **Generate Test Data**
   ```bash
   python run.py --create-test
   ```
   This creates sample Excel files in `input_data` with different scenarios.

3. **Run Tests**
   ```bash
   python tests/test_table_allocation.py -v
   ```
   This runs all tests with verbose output showing:
   - Test case descriptions
   - Allocation results
   - Satisfaction scores
   - Any errors or failures

3. **Performance Metrics**
   - Satisfaction Rate:
     - \>80%: Excellent
     - 60-80%: Good
     - <60%: May need parameter tuning
