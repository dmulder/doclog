# Import this module from the python interpreter to fix up your log
import os, pickle

(obj, oses, apps, app_objs) = pickle.load(open(os.path.expanduser('/home/dmulder/Dropbox/Work/DocLog/log'), 'rb'))

def save():
    pickle.dump((obj, oses, apps, app_objs), open(os.path.expanduser('/home/dmulder/Dropbox/Work/DocLog/log'), 'wb'))

print('Entries are saved in the variables obj, oses, apps, and app_objs. Call save() when you\'re finished editing to stash the changes to your log.')
