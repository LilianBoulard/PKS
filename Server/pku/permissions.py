# -*- coding: UTF8 -*-

import logging

from .database import Database
from .config import Config


class Permissions:

    # This variable contains the permissions that can be used to set a command's rights.
    # They represent permissions sets, not groups.
    # First item is the name of the set, the second is a description (used nowhere, only informational).
    permission_sets = [
        ("manage_sequences", "Can manage new and old sequences."),
        ("modify_bot_behaviour", "Can take measures that have a direct impact on the bot's behaviour."),
        ("admin_access", "Can take drastic measures that can affect the whole system."),
    ]

    # This variables contains the groups and their associated sets of permissions.
    permission_groups = [
        {"guest": []},
        {"member": ["manage_sequences", ]},
        {"manager": ["manage_sequences", "modify_bot_behaviour", ]},
        {"admin": ["manage_sequences", "modify_bot_behaviour", "admin_access", ]},
    ]

    def __init__(self):
        self.db = PermissionsDatabase()

    def __del__(self):
        del self.db

    def set_telegram_admins(self) -> None:
        """
        Promote the system account (1) and the users defined in Config.telegram_user_admin_list as telegram admins.

        :return None:
        """
        self.add_user_to_group("1", "admin")  # 1 is the system account (arbitrary)
        for admin in Config.telegram_user_admin_list:
            self.add_user_to_group(str(admin), "admin")

    def user_exists(self, user_id: str) -> bool:
        """
        Checks if the user exists in the database.

        :param str user_id:
        :return bool: True if he does, False otherwise.
        """
        return self.db.key_exists(self.db.db_columns[0], user_id)

    def list_group_members(self, group: str) -> list:
        """
        Parses the database to find which users are part of a group, and return a list of these users.

        :param str group:
        :return list:
        """
        groups = []
        if group in self.get_valid_groups():
            all_users_raw = self.db.query_column(self.db.db_columns[0])
            all_users = all_users_raw.keys()
            for user in all_users:
                if group in all_users_raw[user]:
                    groups.append(user)
        return groups

    def get_valid_groups(self) -> list:
        """
        Returns a list of the valid groups defined by the attribute permission_groups.

        :return list:
        """
        return [v[0] for v in [list(g.keys()) for g in self.permission_groups]]

    def is_group_valid(self, group: str) -> bool:
        """
        Searches attribute "permission_groups" to check if the group specified is valid.

        :param str group:
        :return bool: True if the group is valid, False otherwise

        .. seealso: Permissions.get_valid_groups()
        """
        return group in self.get_valid_groups()

    def create_user(self, user_id) -> None:
        """
        .. seealso: PermissionsDatabase.create_user()

        :param str user_id:
        :return None:
        """
        self.db.create_user(user_id)

    def add_user_to_group(self, user_id: str, group: str) -> None:
        """
        Add a user to a group.

        :param str user_id:
        :param str group:
        :return None:
        """
        if not self.is_group_valid(group):
            return
        # Creates the user if it doesn't already exists in the database.
        if not self.user_exists(user_id):
            self.create_user(user_id)
        self.db.add_user_to_group(user_id, group)
        logging.info(f"User {user_id} added to group {group} successfully.")

    def remove_user_from_group(self, user_id: str, group: str) -> None:
        """
        Remove user from a group.

        :param str user_id:
        :param str group:
        :return None:
        """
        if not self.is_group_valid(group):
            return
        self.db.remove_user_from_group(user_id, group)
        logging.info(f"User {user_id} removed from group {group} successfully.")

    def get_groups_permissions(self, user_id: str) -> list:
        """
        Get a list of permissions granted by the user's groups membership.

        :param str user_id:
        :return list: A list of permissions granted by the groups the user is part of.
        """
        u_groups = self.db.list_groups(user_id)

        p_groups = ["none"]
        for permission_group in self.permission_groups:  # permission_group is a dict
            # group is the name of the group.
            group = list(permission_group.keys())[0]
            if group in u_groups:
                for pg in permission_group[group]:
                    p_groups.append(pg)

        return p_groups

    def is_user_allowed(self, user_id: str, needed_permissions: list) -> bool:
        """
        Will test if the user with precised id has sufficient permissions.

        :param str user_id:
        :param list needed_permissions: Must be a subset of attribute "permission_sets".
        :return bool: True if he does, False otherwise
        """

        # If the whitelist is not empty
        if len(Config.telegram_user_whitelist) > 0:
            # Terminate if the user is not part of it
            if user_id not in Config.telegram_user_whitelist:
                return False

        # Terminate if the user is in the blacklist
        if user_id in Config.telegram_user_blacklist:
            return False

        user_permissions = self.get_groups_permissions(user_id)

        # Checks if the user's permissions list contains the needed permissions (if one is the subset of the other).
        # If not, terminate.
        if not all([p in user_permissions for p in needed_permissions]):
            return False

        return True


class PermissionsDatabase(Database):

    """

    Database structure:

    permissions = dict{
        permissions = dict{
            "user1": ["admin", "manager"],
            "user2": ["guest"],
            "user3": ["guest"],
        }
    }

    """

    def __init__(self):
        super().__init__(
            "permissions.db",
            {
                "permissions": dict
            }
        )

    def list_groups(self, user_id: str) -> list:
        """
        Lists the groups "user_id" is part of.
        If the user does not exist in the database, returns an empty list.

        :param str user_id:
        :return list:
        """
        if self.key_exists(self.db_columns[0], user_id):
            val = self.query(self.db_columns[0], user_id)
            return val
        else:
            return []

    def create_user(self, user_id: str) -> None:
        """
        Creates a new user in the database.
        Does not care if it already exists ; this verification must be made beforehand.

        :param str user_id:
        :return None:
        """
        self.insert_dict(self.db_columns[0], {user_id: []})

    def add_user_to_group(self, user_id: str, group: str) -> None:
        """
        Adds "user_id" to "group".
        This user must already exist in the database and the group must be verified to be valid beforehand.
        This function takes care of removing duplicates (in case the user was already part of the group).

        :param str user_id:
        :param str group:
        :return None:
        """
        # Get a list of the groups he belongs to
        groups = self.list_groups(user_id)
        # Add the new group to this list
        groups.append(group)
        # Remove duplicates
        groups = list(dict.fromkeys(groups))
        # And update the database entry with the new groups.
        self.update(self.db_columns[0], user_id, groups)

    def remove_user_from_group(self, user_id: str, group: str) -> None:
        """
        Removes "user_id" from "group".
        This user must already exist in the database and the group must be verified to be valid beforehand.

        :param str user_id:
        :param str group:
        :return None:

        .. seealso: PermissionsDatabase.add_user_to_group()
        """
        groups = self.list_groups(user_id)
        # Remove the new group to this list
        groups = dict.fromkeys(groups)
        groups.pop(group)
        groups = list(groups)
        self.update(self.db_columns[0], user_id, groups)
