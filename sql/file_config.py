import json
import tkinter as tk
from pathlib import Path


def save_config(config, fs):
    print(json.dumps(config, indent=4))
    with open(fs['config'], 'w') as f:
        json.dump(config, f)


def load_config(config_path, db_frame):
    with open(config_path, 'r') as f:
        config = json.load(f)
    print(json.dumps(config, indent=4))

    for db_name, tables in config.items():
        db_frame.db_name.delete(0, tk.END)
        db_frame.db_name.insert(0, db_name)
        
        for table in tables:
            table_frame = db_frame.add_table()
            table_frame.table_name.insert(0, table['table_name'])

            for column in table['columns']:
                column_frame = table_frame.add_column()
                column_frame.column_name.insert(0, column['name'])
                column_frame.data_type.set(column['data_type'])
                if 'NOT NULL' in column['params']:
                    column_frame.not_null_box.invoke()
                if 'returns' in column['column_class_dict']:
                    column_frame.return_checkbox.invoke()
                    match column['column_class_dict']['returns']:
                        case 'single':
                            column_frame.return_type_checkboxes[0].invoke()
                        case 'group':
                            column_frame.return_type_checkboxes[1].invoke()

        for table in tables:
            table_frame = [
                t for t in db_frame.tables
                if table['table_name'] == t.name
            ][0]
            table_frame.update()
            for column in table['columns']:
                column_frame = [
                    c for c in table_frame.columns
                    if column['name'] == c.name
                ][0] 

                if 'references' in column['column_class_dict']:
                    column_frame.references_checkbox.invoke()

                    r_table, r_column = \
                        column['column_class_dict']['references'].split('(')
                    r_column = r_column[:-1]

                    column_frame.update_tables()
                    column_frame.update_columns()
                    column_frame.column_classes['references'][1].set(r_table)
                    column_frame.column_classes['references'][2].set(r_column)

            for group in table['groups']:
                group_frame = table_frame.add_group()
                group_frame.group_name.insert(0, group['name'])
                for column in group['columns']:
                    group_frame.columns[column].set(True)

            for filter in table['filters']:
                filter_frame = table_frame.add_filter()
                filter_frame.filter_name.insert(0, filter['name'])
                for query in filter['queries']:
                    filter_frame.queries[query].set(True)

