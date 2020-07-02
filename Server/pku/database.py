# -*- coding: UTF8 -*-

import shelve


class Database:

    """
    Database structure:

    self.db = dict{
        "column1": dict[
            "value1": value,
            "value2": value,
            "value3": value,
        ],
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

        :param str db_name:
        :param dict{str: type} columns: Unidimensional dictionary with each "key: value" pair representing
        "column_name": type_of_column. "type_of_column" must be a type object (dict, list, tuple, set, etc).
        """
        self.db_name = db_name
        self.db = shelve.open(self.db_name)
        self.db_columns = list(columns.keys())
        for column in columns:
            if not self.column_exists(column):
                self.db[column] = (columns[column])()
        self.db.sync()

    def __del__(self):
        self.db.close()

    def column_exists(self, column: str) -> bool:
        """
        Checks if the column "column" exists in the database.

        :param str column:
        :return bool: True if it does, False otherwise.
        """
        return column in self.db

    def key_exists(self, column: str, key: str) -> bool:
        """
        Checks if the key "key" exists in the column "column".

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

        :param str column:
        :param dict pair:
        :return None:
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

        :param str column:
        :param value:
        :return None:
        """
        cl = self.db[column]
        # assert type(cl) == list
        cl.append(value)
        self.db[column] = cl
        self.db.sync()

    def update(self, column: str, key: str, value) -> None:
        """
        :param str column:
        :param str key:
        :param value:
        :return:
        """
        # assert self.column_exists(column)
        # assert self.key_exists(column, key)
        cl = self.db[column]
        cl[key] = value
        self.db[column] = cl
        self.db.sync()

    def query_column(self, search_column: str):
        """
        Returns the whole content of a column.
        Usually, it will be of type dict or list.

        :param str search_column:
        :return: The value of the column.
        """
        # assert self.column_exists(search_column)
        return self.db[search_column]

    def query(self, search_column: str, search_key: str):
        """
        Queries the value from column -> key.
        Both column and key must exist in the DB.

        :param str search_column:
        :param str search_key:
        """
        # assert self.column_exists(search_column)
        # assert self.key_exists(search_column, search_key)
        return self.db[search_column][search_key]
