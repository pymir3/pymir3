import glob
import sys
import codecs

if __name__ == "__main__":

	#train_dir points to a directory with all genres as subdirs and tracklist.csv
    train_dir = "/data0/juliano/ISMIR/train"

	#test_dir points to a directory with all .mp3 files and ground_truth.csx
    test_dir = "/data0/juliano/ISMIR/test"

    train_file = codecs.open("ismir_train.txt", mode='w', encoding='utf-8')

    with codecs.open(train_dir + '/tracklist.csv', encoding='utf-8') as f:
	    tracklist = f.readlines()

    for t in tracklist:
        d = t.split(",")
        genre = eval(d[0])
        path = train_dir + eval(d[5])[1:]
        train_file.write('%s\t%s\n' % (path, genre))

    train_file.close()

    test_file = codecs.open("ismir_test.txt", mode='w', encoding='utf-8')
    eval_file = codecs.open("ismir_eval.txt", mode='w', encoding='utf-8')

    with codecs.open(test_dir + '/ground_truth.csx', encoding='utf-8') as f:
        truth = f.readlines()

    for t in truth:
        d = t.split(",")
        path = test_dir + eval(d[0]).replace("tracks", "")
        genre = eval(d[1])
        test_file.write("%s\n" % path)
        eval_file.write("%s\t%s\n" % (path, genre))

    test_file.close()
    eval_file.close()
	
	
	
    

