import glob

if __name__ == "__main__":

    dataset_dir = "/home/juliano/Music/genres_wav"

    #generate file list for gtzan
    files = sorted(glob.glob(dataset_dir + "/*.wav"))
    file_list = open("gtzan.txt", "w")
    for f in files:
        file_list.write(f + "\n")
    file_list.close()

    #generate label file for gtzan.txt
    with open("gtzan.txt") as f:
        files = f.read().splitlines()
    f.close()

    file_labels = open("gtzan_labels.txt", "w")

    for i in files:
        label = i.split("/")[-1].split(".")[0]
        file_labels.write(i + "\t" + label + "\n")
    file_labels.close()
