"""
Test data generation utilities.
"""

import pandas as pd
import os

def generate_class_reunion_preferences():
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

def generate_corporate_preferences():
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
            weights.append(2.0)
    
    return {
        'Person': people,
        'Preferences': preferences,
        'PreferenceWeight': weights
    }

def generate_school_club_preferences():
    """Generate preferences for school club event scenario"""
    people = []
    preferences = []
    weights = []
    
    people_data = [
        {'Person': 'Alice', 'Preferences': 'Bob, Charlie, David', 'PreferenceWeight': 3},
        {'Person': 'Bob', 'Preferences': 'Alice, Charlie, David', 'PreferenceWeight': 3},
        {'Person': 'Charlie', 'Preferences': 'Alice, Bob, David', 'PreferenceWeight': 3},
        {'Person': 'David', 'Preferences': 'Alice, Bob, Charlie', 'PreferenceWeight': 3},
        {'Person': 'Eve', 'Preferences': 'Frank, Grace', 'PreferenceWeight': 2},
        {'Person': 'Frank', 'Preferences': 'Eve, Grace', 'PreferenceWeight': 2},
        {'Person': 'Grace', 'Preferences': 'Eve, Frank', 'PreferenceWeight': 2},
        {'Person': 'Heidi', 'Preferences': 'Ivan, Judy', 'PreferenceWeight': 1},
        {'Person': 'Ivan', 'Preferences': 'Heidi, Judy', 'PreferenceWeight': 1},
        {'Person': 'Judy', 'Preferences': 'Heidi, Ivan', 'PreferenceWeight': 1},
        # Add more people to reach 30
    ]
    # Fill up to 30 people with random preferences
    for i in range(10, 30):
        people_data.append({'Person': f'Person_{i}', 'Preferences': '', 'PreferenceWeight': 1})
    
    for person in people_data:
        people.append(person['Person'])
        preferences.append(person['Preferences'])
        weights.append(person['PreferenceWeight'])
    
    return {
        'Person': people,
        'Preferences': preferences,
        'PreferenceWeight': weights
    }

def generate_test_data():
    """
    Generate test Excel files for different scenarios and return their paths.
    """
    os.makedirs('input_data', exist_ok=True)

    test_files = []

    # Existing scenarios
    test_files.append(generate_class_reunion_scenario())
    test_files.append(generate_corporate_event_scenario())
    test_files.append(generate_school_club_event_scenario())

    return test_files


def generate_class_reunion_scenario():
    """
    Generate a test scenario for a class reunion event and return the file path.
    """
    class_reunion_data = generate_class_reunion_preferences()
    class_reunion_df = pd.DataFrame(class_reunion_data)

    config_data = {
        'NumTables': [4],
        'TableSize': [5],
        'NumPeople': [14]
    }
    config_df = pd.DataFrame(config_data)

    output_file = 'input_data/class_reunion_scenario.xlsx'
    with pd.ExcelWriter(output_file) as writer:
        config_df.to_excel(writer, sheet_name='Config', index=False)
        class_reunion_df.to_excel(writer, sheet_name='Preferences', index=False)

    return output_file


def generate_corporate_event_scenario():
    """
    Generate a test scenario for a corporate event and return the file path.
    """
    corporate_data = generate_corporate_preferences()
    corporate_df = pd.DataFrame(corporate_data)

    config_data = {
        'NumTables': [5],
        'TableSize': [6],
        'NumPeople': [30]
    }
    config_df = pd.DataFrame(config_data)

    output_file = 'input_data/corporate_event_scenario.xlsx'
    with pd.ExcelWriter(output_file) as writer:
        config_df.to_excel(writer, sheet_name='Config', index=False)
        corporate_df.to_excel(writer, sheet_name='Preferences', index=False)

    return output_file


def generate_school_club_event_scenario():
    """
    Generate a test scenario for a school club event and return the file path.
    """
    config_data = {
        'NumTables': [5],
        'TableSize': [6],
        'NumPeople': [30]
    }
    preferences_data = generate_school_club_preferences()
    preferences_df = pd.DataFrame(preferences_data)

    config_df = pd.DataFrame(config_data)

    output_file = 'input_data/school_club_event_scenario.xlsx'
    with pd.ExcelWriter(output_file) as writer:
        config_df.to_excel(writer, sheet_name='Config', index=False)
        preferences_df.to_excel(writer, sheet_name='Preferences', index=False)

    return output_file


def validate_output_data(output_file: str):
    """
    Validate the output Excel file format.
    """
    # Check allocations
    df_alloc = pd.read_excel(output_file, sheet_name='Allocations')
    assert 'Table' in df_alloc.columns, "Allocations sheet missing Table column"
    assert 'Person' in df_alloc.columns, "Allocations sheet missing Person column"
    
    # Check table summary
    df_summary = pd.read_excel(output_file, sheet_name='Table Summary')
    assert 'Table' in df_summary.columns, "Table Summary sheet missing Table column"
    assert 'NumPeople' in df_summary.columns, "Table Summary sheet missing NumPeople column"
    
    # Check satisfaction metrics
    df_metrics = pd.read_excel(output_file, sheet_name='Satisfaction Metrics')
    assert 'Metric' in df_metrics.columns, "Satisfaction Metrics sheet missing Metric column"
    assert 'Value' in df_metrics.columns, "Satisfaction Metrics sheet missing Value column"


if __name__ == "__main__":
    test_files = generate_test_data()
    for file in test_files:
        validate_output_data(file)
