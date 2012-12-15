from github import Github
from hashlib import sha1
from cStringIO import StringIO
import datetime
    
    
    
# max. 60 API calls per hour
# ATM 12 * getFiles per hour
    
def getFiles(userName, repoName, branchName, folderName=None):
    try:
        g = Github()
        user = g.get_user(userName)                                                         # call 1
        if user:
            repo = user.get_repo(repoName)                                                  # call 2
            if repo:
                branch = repo.get_branch(branchName)                                        # call 3
                if branch:
                    tree = repo.get_git_tree(branch.commit.sha)                             # call 4
                    if tree:
                        if folderName:
                            folder = filter(lambda x : x.path == folderName, tree.tree)
                            if folder and len(folder) > 0:
                                tree = repo.get_git_tree(folder[0].sha)                     # call 5
                        if tree:
                            files = tree.tree
                            return files
    except:
        pass
    
    return None


def getUpdatedAtFromString(dateStr):
    datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)



# Hash

class githash(object):
    def __init__(self):
        self.buf = StringIO()

    def update(self, data):
        self.buf.write(data)

    def hexdigest(self):
        data = self.buf.getvalue()
        h = sha1()
        h.update("blob %u\0" % len(data))
        h.update(data)

        return h.hexdigest()

def githash_data(data):
    h = githash()
    h.update(data)
    return h.hexdigest()

def getGithash(filename):
    fileobj = file(filename)
    return githash_data(fileobj.read())

