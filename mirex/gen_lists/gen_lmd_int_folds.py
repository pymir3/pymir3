import glob
import os

if __name__ == "__main__":

    fold_dirs = ["/data0/juliano/LMD_inteiras_folds/validation", "/data0/juliano/LMD_inteiras_folds/fold1", "/data0/juliano/LMD_inteiras_folds/fold2", "/data0/juliano/LMD_inteiras_folds/fold3"]
    dirs = []
    for fold in fold_dirs:
        dirs.extend([ fold + '/' + name for name in os.listdir(fold) if os.path.isdir(os.path.join(fold, name)) ])

    files = []

    for d in sorted(dirs):
        files.extend(sorted(glob.glob(d + "/*.mp3")))

    file_list = open("lmd_int_folds.txt", "w")
    for f in files:
        file_list.write(f + "\n")
    file_list.close()

    file_labels = open("lmd_int_folds_labels.txt", "w")
    for i in files:
        label = i.split("/")[-2]
        file_labels.write(i + "\t" + label + "\n")
    file_labels.close()

    fold_files = dict()
    fold_files[fold_dirs[0]] = []
    fold_files[fold_dirs[1]] = []
    fold_files[fold_dirs[2]] = []
    fold_files[fold_dirs[3]] = []

    for f in files:
        for k in xrange(len(fold_dirs)):
            if fold_dirs[k] in f:
                fold_files[fold_dirs[k]].append(f)
                continue

    for i in fold_files:
        fold_files[i] = sorted(fold_files[i])

    k = 1
    for fold in fold_dirs[1:]:
        fold_name = fold.split("/")[-1]

        train_file = "f_%d_train.txt" % k
        test_file = "f_%d_test.txt" % k 
        eval_file = "f_%d_evaluate.txt" % k

        fold_file = open(train_file, "w")
        #generate train fold
        for fd in fold_dirs:
            if fold == fd:
                continue
            for i in fold_files[fd]:
                label = i.split("/")[-2]
                fold_file.write(i + "\t" + label + "\n")
        fold_file.close()

        #generate test fold
        fold_file = open(test_file, "w")
        for i in fold_files[fold]:
            fold_file.write(i+ "\n")
        fold_file.close()

        #generate evaluate fold
        fold_file = open(eval_file, "w")
        for i in fold_files[fold]:
            label = i.split("/")[-2]
            fold_file.write(i + "\t" + label + "\n")
        fold_file.close()


        k+=1




