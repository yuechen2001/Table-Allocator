# Table Allocation Algorithm

This project implements an algorithm to solve the optimal table allocation problem for events where people have seating preferences.

## Problem Description

Given:
- X tables of size Y each
- Z people to be seated
- Each person can specify preferences of people they want to sit with
- Each preference can have a weight (strength of preference)

The algorithm aims to find the optimal allocation of people to tables that maximizes the total number of satisfied preferences.

## Project Structure

- `table_allocation.py`: Core algorithm implementation using simulated annealing
- `table_allocator.py`: Excel interface and test data generation
- `input_data/`: Directory for input Excel files
- `output_data/`: Directory for generated allocation results

## Excel Interface

### Input Format
The input Excel file should contain two sheets:

1. **Config Sheet**
   - NumTables: Number of available tables
   - TableSize: Size of each table
   - NumPeople: Total number of people to allocate

2. **Preferences Sheet**
   - Person: Name of the person
   - Preferences: Comma-separated list of people they prefer to sit with
   - PreferenceWeight: Weight/strength of the preferences (optional, default=1.0)

### Output Format
The program generates an Excel file with two sheets:

1. **Allocations Sheet**
   - Table: Assigned table number
   - Person: Name of the person

2. **Statistics Sheet**
   - Total Weighted Satisfaction
   - Satisfied Preferences
   - Total Possible Pairs
   - Satisfaction Rate (%)

## Usage

1. Generate test data (optional):
```python
python table_allocator.py --create-test-data
```

2. Place your input Excel files in the `input_data` directory

3. Run the allocator:
```python
python table_allocator.py
```

Results will be saved in the `output_data` directory with timestamps.

## Testing

The project includes several test scenarios to validate the algorithm's performance in different situations:

### Test Scenarios

1. **Wedding Scenario** (`wedding_scenario.xlsx`)
   - 10 people, 3 tables of size 4
   - Family relationships with weighted preferences
   - Tests handling of strong preferences (e.g., bride-groom must sit together)
   - Includes asymmetric family relationships

2. **Corporate Event** (`corporate_event.xlsx`)
   - 28 people, 5 tables of size 6
   - Department-based grouping (Sales, Engineering, Marketing, HR, Finance)
   - Tests handling of large groups
   - Demonstrates department cohesion while maintaining table size limits

3. **Class Reunion** (`class_reunion.xlsx`)
   - 18 people, 4 tables of size 5
   - Friend group preferences (Sports Team, Study Group, Theater Club, etc.)
   - Tests handling of overlapping social circles
   - Includes some people with fewer preferences

### Running Tests

1. Generate test data:
```python
python table_allocator.py --create-test-data
```

2. Process test scenarios:
```python
python table_allocator.py
```

3. Evaluate results:
   - Check `output_data` directory for results
   - Each result file includes:
     - Table assignments
     - Satisfaction statistics
     - Performance metrics

### Interpreting Results

The algorithm's performance can be evaluated using:

1. **Satisfaction Rate**: Percentage of preferences satisfied
   - Above 80%: Excellent
   - 60-80%: Good
   - Below 60%: May need parameter tuning

2. **Weighted Satisfaction**: Sum of satisfied preference weights
   - Higher weights indicate more important preferences were satisfied

3. **Distribution Balance**: Check if tables are evenly filled
   - Tables should be filled up to their size limit
   - No overflow or underflow should occur

### Adding Custom Test Cases

To create your own test scenario:

1. Copy one of the existing test files from `input_data`
2. Modify the Config sheet with your parameters
3. Update the Preferences sheet with your data
4. Run the allocator to process your test case

## Algorithm Approach

The solution uses a simulated annealing approach:
1. Start with a random allocation
2. Iteratively try to improve the solution by swapping people between tables
3. Accept improvements and occasionally accept worse solutions to escape local optima
4. Cool down the temperature to converge to a good solution

## Dependencies

Required Python packages:
```
pandas>=1.5.0
numpy>=1.21.0
networkx>=2.8.0
openpyxl>=3.0.0
