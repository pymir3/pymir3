import glob
import sys

if __name__ == "__main__":

    dataset_dir = "/home/juliano/mir_datasets/ballroom/BallroomData"

    #generate file list for ballroom
    with open(dataset_dir + "/allBallroomFiles") as f:
        files = f.read().splitlines()
    f.close()

    file_list = open("ballroom.txt", "w")

    for f in files:
        file_list.write(dataset_dir + f[1:] + "\n")
    file_list.close()

    #generate label file for ballroom.txt
    with open("ballroom.txt") as f:
        files = f.read().splitlines()
    f.close()

    file_labels = open("ballroom_labels.txt", "w")

    labels = []

    for i in files:
        label = i.split("/")[-2].split(".")[0]
        if label.find("Rumba") != -1:
            label = "Rumba"
        labels.append(label)
        file_labels.write(i + "\t" + label + "\n")
    file_labels.close()

