# -*- coding: UTF8 -*-

import shelve
import os


class Database:

    """
    This class is a low-level interface to a database.
    Low-level because it does not make any verification and is pretty bare bones
    - it just sends raw "commands" to the database object.

    Usual database structure:

    self.db = dict{
        "column1": dict{
            "value1": value,
            "value2": value,
            "value3": value,
        },
        "column2": list[
            "value1",
            "value2",
        ]
    }

    """

    def __init__(self, db_name: str, columns: dict):
        """
        Structure of "columns":

        dict{
            "column1": list,
            "column2": dict,
            "column3": tuple,
        }

        :param str db_name: Name of the database.
        :param dict{str: type} columns: Uni-dimensional dictionary with each "key: value" pair representing
        "column_name": type_of_column. "type_of_column" must be a type object (dict, list, tuple, set, etc).
        """
        self.db_name = db_name
        self.db = self.__get_db(self.db_name)
        self.db_columns = list(columns.keys())
        for column in columns:
            if not self.column_exists(column):
                self.db[column] = (columns[column])()
        self.db.sync()

    def __del__(self):
        self.db.close()

    def __get_db(self, db_name: str) -> shelve.DbfilenameShelf:
        """
        Returns a DB object.
        \
        Creates the subdirectories for the file if it doesn't exist already.

        :param str db_name: The relative database path (as the data will be stored in a file).
        :return shelve.DbfilenameShelf: A database object.
        """
        try:
            db = shelve.open(db_name)
        except FileNotFoundError:
            os.mkdir("/".join(db_name.split("/")[:-1]))
            db = shelve.open(db_name)
        return db

    def insert_new_column(self, column_name: str, column_type: type) -> None:
        """
        Adds a new column to the database structure.

        :param str column_name: The name of the new column.
        :param type column_type: Its type as a type object (dict, list, tuple, etc.)
        """
        if column_type == dict:
            ins = {column_name: {}}
        elif column_type == list:
            ins = {column_name: []}
        elif column_type == tuple:
            ins = {column_name: ()}
        else:
            raise TypeError(f"Invalid column type: {column_type} for new column named \"{column_name}\"")
        self.db_columns.append(column_name)
        self.db.update(ins)

    def column_exists(self, column: str) -> bool:
        """
        Checks if the column exists in the database.

        :param str column: A column name.
        :return bool: True if it does, False otherwise.
        """
        return column in self.db

    def key_exists(self, column: str, key: str) -> bool:
        """
        Checks if `key` exists in `column`.

        :param str column: The column to parse.
        :param str key: The key to search for.
        :return bool: True if it exists, False otherwise.
        """
        # assert self.column_exists(column)
        # assert type(key) == str
        return key in self.db[column]

    def insert_dict(self, column: str, pair: dict) -> None:
        """
        Adds a new value to a column in the database.
        Used when the column's type is dict.
        The column must exist. This check must be done beforehand.

        :param str column: A column name.
        :param dict pair: A dictionary.
        """
        cl = self.db[column]
        # assert type(cl) == dict
        cl.update(pair)
        self.db[column] = cl
        self.db.sync()

    def insert_list(self, column: str, value) -> None:
        """
        Adds a new value to a column in the database.
        Used when the column's type is list.
        The column must exist. This check must be done beforehand.

        :param str column: A column name.
        :param value: A value to add. Can be of any type.
        """
        cl = self.db[column]
        # assert type(cl) == list
        cl.append(value)
        self.db[column] = cl
        self.db.sync()

    def update(self, column: str, key: str, value) -> None:
        """
        Updates a field in the database.

        :param str column: A column name.
        :param str key: A key.
        :param value: The new value.
        """
        # assert self.column_exists(column)
        # assert self.key_exists(column, key)
        cl = self.db[column]  # Get a copy of the column.
        cl[key] = value  # Alters the copy.
        self.db[column] = cl  # Replace the original by the copy.
        self.db.sync()  # Update the database.

    def query_column(self, search_column: str) -> any:
        """
        Returns the whole content of a column.

        :param str search_column: A column name.
        :return: The value of the column.
        """
        # assert self.column_exists(search_column)
        return self.db[search_column]

    def query(self, search_column: str, search_key: str) -> any:
        """
        Queries the value from column -> key.
        Both column and key must exist in the DB.

        :param str search_column: A column name.
        :param str search_key: A key.
        """
        # assert self.column_exists(search_column)
        # assert self.key_exists(search_column, search_key)
        return self.db[search_column][search_key]
