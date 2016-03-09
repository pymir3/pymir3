import glob
import sys
import os

if __name__ == "__main__":

    dataset_dir = "/home/juliano/Music/homburg_wavs"

    dirs = [ name for name in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, name)) ]

    files = []

    for d in sorted(dirs):
        p = dataset_dir + "/" + d
        files.extend(sorted(glob.glob(p + "/*.wav")))

    file_list = open("homburg.txt", "w")
    for f in files:
        file_list.write(f + "\n")
    file_list.close()

    #generate label file for gtzan.txt

    file_labels = open("homburg_labels.txt", "w")

    for i in files:
        label = i.split("/")[-2]
        file_labels.write(i + "\t" + label + "\n")
    file_labels.close()
