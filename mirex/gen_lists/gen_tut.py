import glob
import sys

if __name__ == "__main__":

    dataset_dir = "/home-local/juliano/mir_datasets/tut/TUT-acoustic-scenes-2016-development"

    #generate file list for tut
    with open(dataset_dir + "/meta_sorted.txt") as f:
        files = f.read().splitlines()
    f.close()

    file_list = open("tut.txt", "w")
    file_labels = open("tut_labels.txt", "w")

    for f in files:
        file_list.write(dataset_dir +'/' + f.split("\t")[0] + "\n")
        file_labels.write(dataset_dir + '/' + f + "\n")
    file_list.close()
    file_labels.close()

    #generate label file for ballroom.txt
    #file_labels = open("tut_labels.txt", "w")

    #labels = []

    #for i in files:
    #    label = i.split("/")[-2].split(".")[0]
    #    if label.find("Rumba") != -1:
    #        label = "Rumba"
    #    labels.append(label)
    #    file_labels.write(i + "\t" + label + "\n")
    #file_labels.close()

