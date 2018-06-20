import json

import sqlalchemy

def create_engine(flavor='postgresql'):
    
    if flavor == 'postgresql':
        with open('db_settings.json', 'r') as file:
            dbs = json.load(file)

        # Ouverture de la connection vers la bdd
        engine = sqlachemy.create_engine(
            '{dialect}+{driver}://{user}:{pwd}@{host}:{port}/{dbn}'.format(
                dialect=dbs['dialect'], driver=dbs['driver'],
                user=dbs['username'], pwd=dbs['password'], host=dbs['host'],
                port=dbs['port'], dbn=dbs['database']))

    elif flavor == 'sqlite':
        engine = sqlalchemy.create_engine('sqlite:///database.db')

    else:
        msg = "I do not know this database flavor: {}.".format(flavor)
        raise Exception(msg)

    return engine
