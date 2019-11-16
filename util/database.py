from pymongo import MongoClient

def db_connector():

    from pymongo import MongoClient
    client = MongoClient('219.228.57.73', 27017,
                         username='dbadmin',
                         password='daohaosiquanjia')

    db = client.ob_tracker
    # db = client.db_test
    return db
