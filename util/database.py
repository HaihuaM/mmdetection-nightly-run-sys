from pymongo import MongoClient

def db_connector():

    from pymongo import MongoClient
    # client = MongoClient('219.228.57.73', 27017,
    client = MongoClient('127.0.0.1', 27017,
                         username='dbadmin',
                         password='daohaosiquanjia')

    db = client.ob_tracker
    # db = client.db_test
    return db

if __name__ =="__main__":
    db = db_connector()
    runs = db.run.find({})
    for run in runs:
        print(run['config_file'])
    # # print(runs)
    # if runs:
    #     print("OK")
