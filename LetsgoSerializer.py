
import os
import pickle

def load_model(file,path='model'):
    try:
        return pickle.load(open(os.path.join(path,file),'rb'))
    except:
        return None

def store_model(model,file,path='model'):
    pickle.dump(model,open(os.path.join(path,file),'wb'))
        
def exist_model(file,path='model'):
    return os.path.exists(os.path.join(path,file))        