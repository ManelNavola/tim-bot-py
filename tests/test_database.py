from unittest import TestCase

from db.database import load_test_database


class TestDatabase(TestCase):
    def setUp(self):
        self.db = load_test_database()
        self.db._cursor.execute("DELETE FROM testing")
        self.db._cursor.execute("INSERT INTO testing (int_id, text_id, data, number) VALUES (123, '123', '{}', "
                               "123123123123)")
        for i in range(50):
            index = i + 321
            self.db._cursor.execute(f"INSERT INTO testing (int_id, text_id, data, number) VALUES ({index}, '124', '{{"
                                   f"}}', 123123123123)")
        self.db._connection.commit()

    def test_insert_data(self):
        to_insert = {
            'int_id': 1,
            'text_id': '1',
            'data': '{ "hello": 3 }',
            'number': 999999999
        }
        self.db.insert_data('testing', to_insert)

        self.db._cursor.execute("SELECT data FROM testing WHERE int_id = 1 AND text_id = '1' AND number = 999999999")
        res = self.db._cursor.fetchone()
        self.assertDictEqual({k: v for k, v in res.items()}, {
            'data': {"hello": 3}
        })

    def test_get_row_data(self):
        columns = ['text_id', 'data', 'number']
        testing = self.db.get_row_data('testing', {
            'int_id': 123,
            'text_id': '123'
        }, columns)
        self.assertDictEqual({k: v for k, v in testing.items()}, {
            'text_id': '123',
            'data': {},
            'number': 123123123123
        })
        testing_multiple = self.db.get_row_data('testing', {
            'text_id': '124',
            'number': 123123123123
        }, limit=27)
        self.assertEqual(len(testing_multiple), 27)

    def test_update_data(self):
        update_with = {
            'number': 4,
            'data': {'christmas': True}
        }
        self.db.update_data('testing', {
            'text_id': '123'
        }, update_with)

        self.db._cursor.execute("SELECT number, data FROM testing WHERE text_id = '123'")
        res = self.db._cursor.fetchone()
        self.assertDictEqual({k: v for k, v in res.items()}, update_with)

    def test_delete_rows(self):
        self.db.delete_row('testing', {
            'int_id': 123
        })

        self.db._cursor.execute("SELECT * FROM testing WHERE int_id = 123")
        self.assertEqual(len(self.db._cursor.fetchall()), 0)
