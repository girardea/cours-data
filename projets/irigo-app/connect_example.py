import json

import pandas as pd

from sqlalchemy import create_engine

with open('db_settings.json', 'r') as file:
    dbs = json.load(file)

engine = create_engine('{dialect}+{driver}://{user}:{pwd}@{host}:{port}'
                       '/{dbn}'.format(dialect=dbs['dialect'],
                                       driver=dbs['driver'],
                                       user=dbs['username'],
                                       pwd=dbs['password'],
                                       host=dbs['host'],
                                       port=dbs['port'],
                                       dbn=dbs['database']))

print(engine.table_names())

connection = engine.connect()

df = pd.DataFrame({
    'a': [1, 2, 3],
    'b': [2, 3, 4]
})

df.to_sql('bidon', connection)

connection.close()

print(engine.table_names())
