import unittest

from .permissions import Permissions
from .telegram import TelegramBot
from .channels import Channels
from .commands import Commands
from .database import Database
from .config import Config
from .utils import Utils
from .core import Core


class TestChannels(unittest.TestCase):

    def setUp(self):
        self.bot = TelegramBot()
        self.obj = Channels(self.bot)
        self.test_chat_id = "12345"

    def tearDown(self):
        del self.obj
        del self.bot

    def _add(self) -> None:
        all_channels_before = self.obj.list_all_channels()
        active_channels_before = self.obj.list_active_channels()

        self.obj.add(self.test_chat_id)

        all_channels_after = self.obj.list_all_channels()
        active_channels_after = self.obj.list_active_channels()

        self.assertListEqual(all_channels_before + [self.test_chat_id], all_channels_after)
        self.assertListEqual(active_channels_before + [self.test_chat_id], active_channels_after)

    def test_disable(self):
        self._add()

        all_channels_before = self.obj.list_all_channels()
        active_channels_before = self.obj.list_active_channels()

        self.obj.disable(self.test_chat_id)

        all_channels_after = self.obj.list_all_channels()
        active_channels_after = self.obj.list_active_channels()

        active_channels_before.remove(self.test_chat_id)

        self.assertListEqual(all_channels_before, all_channels_after)
        self.assertListEqual(active_channels_before, active_channels_after)

    def test_broadcast(self):
        pass

    def test_list_active_channels(self):
        pass

    def test_list_all_channels(self):
        pass


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.valid_types = (type(None), str)

    def test_invalid(self):
        resp = Commands.invalid()
        self.assertIsInstance(resp, self.valid_types)

    def test_help(self):
        resp = Commands.help()
        self.assertIsInstance(resp, str)

    def test_target_port(self):
        resp = Commands.target_port()
        self.assertIsInstance(resp, str)

    def test_add_perm(self):
        pass

    def test_remove_perm(self):
        pass

    def test_generate(self):
        resp = Commands.generate()
        self.assertIsInstance(resp, str)

    def test_status(self):
        resp = Commands.status()
        self.assertIsInstance(resp, str)

    def test_print_config(self):
        resp = Commands.print_config()
        self.assertIsInstance(resp, str)

    def test_print_broadcast_list(self):
        resp = Commands.print_broadcast_list()
        self.assertIsInstance(resp, str)

    def test_forget(self):
        resp = Commands.forget("123456")
        self.assertIsInstance(resp, self.valid_types)

    def test_list_groups_members(self):
        resp = Commands.list_groups_members()
        self.assertIsInstance(resp, str)

    def test_start(self):
        pass

    def test_stop(self):
        pass

    def test_shutdown(self):
        pass


class TestCore(unittest.TestCase):

    def test_generate_new_sequence(self):
        seq1 = Core.generate_new_sequence()
        seq2 = Core.generate_new_sequence()

        seq3 = Core.generate_new_sequence(num=7)
        seq4 = Core.generate_new_sequence(num=9)

        seq5 = Core.generate_new_sequence(num=2, seed=12345)
        seq6 = Core.generate_new_sequence(num=2, seed=12345)

        self.assertNotEqual(seq1, seq2)  # Could potentially happen with normal behavior, but is very unlikely.
        self.assertEqual(len(seq1), Config.sequences_length)

        self.assertEqual(len(seq3), 7)
        self.assertEqual(len(seq4), 9)

        self.assertEqual(seq5, seq6)

    def test_set_open_sequence(self):
        pass

    def test_configure_knockd(self):
        pass


class TestDatabase(unittest.TestCase):

    def test_create_db(self):
        pass

    def test_insert_new_column(self):
        pass

    def test_column_exists(self):
        pass

    def test_key_exists(self):
        pass

    def test_insert_dict(self):
        pass

    def test_insert_list(self):
        pass

    def test_update(self):
        pass

    def test_query_column(self):
        pass

    def test_query(self):
        pass


class TestPermissions(unittest.TestCase):

    def setUp(self):
        self.perms = Permissions()

    def test_set_telegram_admins(self):
        self.assertTrue(self.perms.is_group_valid("admin"))

    def test_user_exists(self):
        pass

    def test_get_group_members(self):
        pass

    def test_get_valid_groups(self):
        pass

    def test_is_group_valid(self):
        pass

    def test_create_user(self):
        pass

    def _add_user_to_group(self, user_id: str, group: str) -> None:
        self.perms.add_user_to_group(user_id, group)

    def test_remove_user_from_group(self):
        """
        Will test both add and remove.
        """
        user_id = "12345"
        group = "admin"

        group_before_add = self.perms.get_group_members(group)

        self._add_user_to_group(user_id, group)

        group_after_add = self.perms.get_group_members(group)
        group_before_remove = group_after_add

        self.perms.remove_user_from_group(user_id, group)

        group_after_remove = self.perms.get_group_members(group)

        # Make sure add works
        self.assertNotEqual(group_before_add, group_after_add)
        # Make sure remove works
        self.assertNotEqual(group_before_remove, group_after_remove)
        # Extra assert to test both (will pass if both are broken)
        self.assertEqual(group_before_add, group_after_remove)

    def test_get_groups_permissions(self):
        pass

    def test_is_user_allowed(self):
        pass


class TestTelegramBot(unittest.TestCase):

    def test___set_identifier(self):
        pass

    def test___set_token(self):
        pass

    def test___is_token_valid(self):
        pass

    def test_get_updates(self):
        pass

    def test_send_message(self):
        pass


class TestUtils(unittest.TestCase):

    def test_start_service(self):
        pass

    def test_stop_service(self):
        pass

    def test_restart_service(self):
        pass

    def test_install_package(self):
        pass

    def test_filter_port_list(self):
        pass


if __name__ == "__main__":
    unittest.main()
