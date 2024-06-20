# 20.05.24

import csv
import logging


# Internal utilities
from Src.Util._jsonConfig import config_manager


# Variable
CREATE_REPORT = config_manager.get_bool('M3U8_DOWNLOAD', 'create_report')


class SimpleDBManager:
    def __init__(self, filename, columns):
        """
        Initialize a new database manager.

        Args:
            - filename (str): The name of the CSV file containing the database.
            - columns (list): List of database columns.
        """
        self.filename = filename
        self.db = []
        self.columns = columns
        logging.info("Database manager initialized.")

    def load_database(self):
        """
        Load the database from the specified CSV file.
        If the file doesn't exist, initialize a new database.
        """
        try:
            with open(self.filename, 'r', newline='') as file:
                reader = csv.reader(file)
                self.db = list(reader)
                logging.info(f"Database {self.filename} loaded successfully.")

        except FileNotFoundError:
            logging.warning(f"File {self.filename} not found, creating a new database...")
            self.initialize_database()

    def initialize_database(self, columns=None, rows=None):
        """
        Initialize a new database with specified columns and rows.
        
        Args:
            - columns (list, optional): List of database columns. If not specified, uses the columns provided in the constructor.
            - rows (list, optional): List of database rows. Each row should be a list of values. If not specified, the database will be empty.
        """
        self.db = [self.columns]
        if rows:
            for row_data in rows:
                self.add_row_to_database(row_data)
                
        logging.info("Database initialized successfully.")

    def add_row_to_database(self, *row_data):
        """
        Add a new row to the database.

        Args:
            - row_data (list): List of values for the new row.
        """
        self.db.append(list(row_data))
        logging.info("New row added to the database.")

    def add_column_to_database(self, column_name, default_value=''):
        """
        Add a new column to the database.

        Args:
            - column_name (str): Name of the new column.
            - default_value (str, optional): Default value to be inserted in cells of the new column. Default is an empty string.
        """
        for row in self.db:
            row.append(default_value)
        self.db[0][-1] = column_name
        logging.info(f"New column '{column_name}' added to the database.")

    def update_row_in_database(self, row_index, new_row_data):
        """
        Update an existing row in the database.

        Args:
            - row_index (int): Index of the row to update.
            - new_row_data (list): List of the new values for the updated row.
        """
        self.db[row_index] = new_row_data
        logging.info(f"Row {row_index} of the database updated.")

    def remove_row_from_database(self, column_index: int, search_value) -> list:
        """
        Remove a row from the database based on a specific column value.

        Args:
            - column_index (int): Index of the column to search in.
            - search_value: The value to search for in the specified column.

        Returns:
            list: The removed row from the database, if found; otherwise, an empty list.
        """
        
        # Find the index of the row with the specified value in the specified column
        row_index = None
        for i, row in enumerate(self.db):
            if row[column_index] == search_value:
                row_index = i
                break
        
        # If the row with the specified value is found, remove it
        remove_row = []
        if row_index is not None:
            remove_row = self.db[row_index]
            del self.db[row_index]
            logging.info(f"Row at index {row_index} with value {search_value} in column {column_index} removed from the database.")
        else:
            logging.warning(f"No row found with value {search_value} in column {column_index}. Nothing was removed from the database.")

        return remove_row

    def remove_column_from_database(self, col_index):
        """
        Remove a column from the database.

        Args:
            - col_index (int): Index of the column to remove.
        """
        for row in self.db:
            del row[col_index]
        logging.info(f"Column {col_index} of the database removed.")

    def save_database(self):
        """
        Save the database to the CSV file specified in the constructor.
        """
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.db)
        logging.info("Database saved to file.")

    def print_database_as_sql(self):
        """
        Print the database in SQL format to the console.
        """
        max_lengths = [max(len(str(cell)) for cell in col) for col in zip(*self.db)]
        line = "+-" + "-+-".join("-" * length for length in max_lengths) + "-+"
        print(line)
        print("| " + " | ".join(f"{cell:<{length}}" for cell, length in zip(self.db[0], max_lengths)) + " |")
        print(line)
        for row in self.db[1:]:
            print("| " + " | ".join(f"{cell:<{length}}" for cell, length in zip(row, max_lengths)) + " |")
        print(line)
        logging.info("Database printed as SQL.")

    def search_database(self, column_index, value):
        """
        Search the database for rows matching the specified value in the given column.

        Args:
            - column_index (int): Index of the column to search on.
            - value (str): Value to search for.

        Returns:
            list: List of rows matching the search.
        """
        results = []
        for row in self.db[1:]:
            if row[column_index] == value:
                results.append(row)
        logging.info(f"Database searched for value '{value}' in column {column_index}. Found {len(results)} matches.")
        return results

    def sort_database(self, column_index):
        """
        Sort the database based on values in the specified column.

        Args:
            - column_index (int): Index of the column to sort on.
        """
        self.db[1:] = sorted(self.db[1:], key=lambda x: x[column_index])
        logging.info(f"Database sorted based on column {column_index}.")

    def filter_database(self, column_index, condition):
        """
        Filter the database based on a condition on the specified column.

        Args:
            - column_index (int): Index of the column to apply the condition on.
            - condition (function): Condition function to apply on the values of the column. Should return True or False.

        Returns:
            list: List of rows satisfying the condition.
        """
        results = [self.db[0]]  # Keep the header row
        for row in self.db[1:]:
            if condition(row[column_index]):
                results.append(row)
        logging.info(f"Filter applied on column {column_index}. Found {len(results) - 1} rows satisfying the condition.")
        return results




# Output
if CREATE_REPORT:
    report_table = SimpleDBManager("riepilogo.csv", ["Date", "Name", "Size"])
    report_table.load_database()
    report_table.save_database()
else:
    report_table = None