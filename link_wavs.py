import os
import glob
from subprocess import call

if __name__ == "__main__":
    thedir = "/home/juliano/Music/base_teste_rafael_94_especies"
    linkdir = "./links/"
    dirs = [ name for name in os.listdir(thedir) if os.path.isdir(os.path.join(thedir, name)) ]

    for d in dirs:
        p = thedir + "/" + d
        files = sorted(glob.glob(p + "/*.wav"))
        i = 0
        for f in files:
            print f.split("/")[-1]
            call(['ln', '-s', f, linkdir ])
            call(['mv', linkdir + f.split("/")[-1], linkdir + d + "." + str(i) + '.wav'])
            i+=1
