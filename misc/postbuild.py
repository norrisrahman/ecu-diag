import os
import git
import glob

r = git.repo.Repo()
v = "1.0.1"
for f in glob.glob("dist/*.exe"):
    fn = list(os.path.splitext(f))
    fn[0] += "-"
    fn[0] += v
    fn = "".join(fn)
    os.rename(f,fn)
