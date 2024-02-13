import os
import git

v_num =  "1.0.1"

r = git.repo.Repo()
with open(os.path.join("src","version.py"),"w") as f:
    f.write("__VERSION__ = '%s'\n" % v_num)
