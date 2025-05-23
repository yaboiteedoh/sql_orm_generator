import sqlite3
from classes.classes import SQLiteTable
from classes.dataclasses import {{ table.dataclass }}


###############################################################################


class {{ table.dataclass }}sTable(SQLiteTable):
    def __init__(self, testing=False):
        if not testing: 
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'test.db'))
        
        self.dataclass = {{ table.dataclass }}
        self._table_name = '{{ table.name }}'

        self._list_keys = { {% for key in table.list_keys %}
            '{{ key.name }}': self.read_by_{{ key.name }},{% endfor %}
        }
        self._single_keys = {
            'rowid': self.read_by_rowid,{% for key in table.single_keys %}
            '{{ key.name }}': self.read_by_{{ key.name }},{% endfor %}
        }
        self._other_keys = [ {% for key in table.other_keys %}
            '{{ key.name }}',{% endfor %}
        ]
        self._group_keys = {
            'all': self.read_all,{% for group in table.key_groups %}
            '{{ group['name'] }}': self.read_by_{{ group['name'] }},{% endfor %}
        }
        self._filters = { {% for filter in table.filters %}
            '{{ filter['name'] }}': self.read_by_{{ filter['name'] }},{% endfor %}
        }


    #------------------------------------------------------# 


    def init_db(self):
            with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                CREATE TABLE {{ table.name }}({% for key in table.keys %}
                    {{ key.name }} {{ key.data_type }} {{ key.params }},{% endfor %}
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT{% if table.references %},
                    {% endif %}{% for key in table.keys %}{% if 'references' in key.classes.check %}
                    FOREIGN KEY({{ key.name }})
                        REFERENCES {{ key.classes.references }}{% endif %}{% endfor %}
                )
            '''
            cur.execute(sql)


    #------------------------------------------------------# 


    def add(self, {{ table.dataclass.lower() }}: dict) -> int:
        with sqlite3.connect(self.db_dir) as con:
        cur = con.cursor()
        sql = '''
            INSERT INTO {{ table.name }}({% for i, key in enumerate(table.keys) %}
                {{ key.name }}{% if i < table.length %},{% endif %}{% endfor %}
            )
            VALUES ({% for i, key in enumerate(table.keys) %}
                :{{ key.name }}{% if i < table.length %},{% endif %}{% endfor %}
            )
        '''
        cur.execute(sql, {{ table.dataclass.lower() }})
        return cur.lastrowid


    #------------------------------------------------------# 

    
    def read_all(self) -> list[{{ table.dataclass }}]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM {{ table.name }}'
            cur.execute(sql)
            return cur.fetchall()


    def read_by_rowid(self, rowid: int) -> {{ table.dataclass }}:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM {{ table.name }} WHERE rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone(){% for key in table.list_keys %}


    def read_by_{{ key.name }}(self, {{ key.name }}: {{ key.py_data_type }}) -> list[{{ table.dataclass }}]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM {{ table.name }} WHERE {{ key.name }}=?'
            cur.execute(sql, ({{ key.name }},))
            return cur.fetchall(){% endfor %}{% for key in table.single_keys %}


    def read_by_{{ key.name }}(self, {{ key.name }}: {{ key.py_data_type }}) -> {{ table.dataclass }}:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM {{ table.name }} WHERE {{ key.name }}=?'
            cur.execute(sql, ({{ key.name }},))
            return cur.fetchone(){% endfor %}{% for group in table.key_groups %}


    def read_by_{{ group.name }}(self, {{ group.name }}: {{ group.py_data_type }}) -> list[{{ table.dataclass }}]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = '''
                SELECT * FROM {{ table.name }}
                WHERE {{ group.keys[0].name }}=?{% for key in group.keys[1:] %}
                OR {{ key.name }}=?{% endfor %}
            '''
            cur.execute(sql, ({% for i, key in enumerate(group.keys) %}{% if i < group.length %}{{ group.name }}, {% else %}{{ group.name }}{% endif %}{% endfor %}))
            return cur.fetchall(){% endfor %}{% for filter in table.filters %}


    def read_by_{{ filter.name }}(self, {% for i, key in enumerate(filter.queries) %}{{ key.name }}: {{ key.py_data_type }}{% if i < filter.length %}, {% endif %}{% endfor%}) -> list[{{ table.dataclass }}] | {{ table.dataclass }}:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = '''
                SELECT * FROM {{ table.name }}
                WHERE
                    {% if isinstance(filter.queries[0], DBKeyGroup) %}({{ filter.queries[0].keys[0].name }}=?{% for key in filter.queries[0].keys %} OR {{ key.name }}=?{% endfor %}){% else %}{{ filter.queries[0].name }}=?{% endif %}{% for query in filter.queries[1:] %}{% if isinstance(key, DBKeyGroup) %}
                    AND
                        ({% for i, group_key in enumerate(key.keys) %}{{ group_key.name }}=?{% if i < key.length %} OR {% endif %}{% endfor %}){% else %}
                    AND
                        {{ key.name }}=?{% endif %}{% endfor %}
            '''
            cur.execute(sql, ({% for i, key in enumerate(filter.queries) %}{% if not isinstance(key, DBKeyGroup) %}{{ key.name }}{% if i < filter.length %}, {% endif %}{% else %}{% for j, group_key in enumerate(key.keys) %}{{ key.name }}{% if j < key.length %}, {% endif %}{% if i < filter.length %}, {% endif %}{% endfor %}{% endif %}{% endfor %}))
            response = cur.fetchall()
            
            if not response:
                return response
            if len(response) == 1:
                return response[0]
            return response{% endfor %}


    #------------------------------------------------------# 


    def update(self, {{ table.dataclass.lower() }}: {{ table.dataclass }}) -> None:
        with sqlite3.connect(self.db_dir) as con:
        cur = con.cursor()
        sql = '''
            UPDATE {{ table.name }}
            SET{% for i, key in enumerate(table.keys) %}
                {{ key.name }}=:{{ key.name }}{% if i < table.length %},{% endif %}{% endfor %}
            WHERE rowid=:rowid
        '''
        cur.execute(sql, obj.as_dict)
        con.commit()


###############################################################################
