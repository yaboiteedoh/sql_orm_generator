
class SQLiteTable:
    def __init__(self):
        self.db_dir = 'path'
        self.dataclass = None
        self._table_name = 'base'
        self._group_keys = {}
        self._object_keys = {}
        self._test_data = {}

    
    #------------------------------------------------------# 


    def init_db(self):
        pass


    #::::::::::::::::::::::::::::::::::::::::::::::::::::::# 


    def _dataclass_row_factory(self, cur, row):
        fields = [column[0] for column in cur.description]
        as_dict = {key: value for key, value in zip(fields, row)}
        return self.dataclass(**as_dict)


    def _reset_table(self):
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = f'DROP TABLE {self._table_name}'
            cur.execute(sql)

        self.init_db()


    def _setup_testing_data(self):
        test_encyclopedia = []

        test_encyclopedia.append(
            [
                self.dataclass(**obj)
                for obj in self._test_data
            ]
        )

        test_encyclopedia.append({})
        for key in self._group_keys:
            flag = None

            if not flag:
                options = {obj[key] for obj in self._test_data}
                results = {value: [] for value in options}

                for obj in self._test_data:
                    value = obj[key]
                    results[value].append(obj)

                test_encyclopedia[1][key] = [options, results]

        return test_encyclopedia

    
    def _test(self, results):
        results.write(f'\ntesting {self._table_name} table')
        data = self._setup_testing_data()
        
        test_objects = data[0]

        results.write(f'\n\ttesting {self._table_name}.add(), {self._table_name}.read_all(), {self._table_name}.read_by_rowid')
        self._test_global_funcs(results, test_objects)

        for key, func in self._group_keys.items():
            results.write(f'\n\ttesting {self._table_name}.read_by_{key}()')
            self._test_group_read(func, results, *data[1][key])

        for key, func in self._object_keys.items():
            results.write(f'\n\ttesting {self._table_name}.read_by_{key}()')
            self._test_obj_read(func, results, key)


    def _test_global_funcs(self, results, test_objects):
        for obj, data in zip(test_objects, self._test_data):
            data['rowid'] = self.add(obj)
        
        db_objs = self.read_all()
        self._compare_data(results, self._test_data, db_objs)

        self._test_obj_read(self.read_by_rowid, results, 'rowid')

    
    def _test_group_read(self, func, results, options, values):
        for value in options:
            data_list = values[value]
            db_objs = func(value)
            self._compare_data(results, data_list, db_objs)


    def _test_obj_read(self, func, results, key):
        for obj in self._test_data:
            response = func(obj[key]).as_dict
            self._compare_items(results, obj, response)


    def _compare_data(self, results, data_list, objects_list):
        for i, tup in enumerate(zip(data_list, objects_list)):
            data, obj = tup
            obj = obj.as_dict
            self._compare_items(results, data, obj, i)


    @staticmethod
    def _compare_items(results, data, obj, i=None):
        for key, value in data.items():
            if value != obj[key]:
                error_message = f'''
                    (~)ERROR in test object {i}: key {key}
                        (~~)request value: {value}
                        (~~)type: {type(value)}
                        (~~)object value: {obj[key]}
                        (~~)type: {type(obj[key])}
                '''
                error_message =error_message.replace("    ", "")
                error_message = error_message.replace("(~)", "\t\t")
                error_message = error_message.replace("(~~)", "\t\t\t")
                results.write(error_message)


###############################################################################
