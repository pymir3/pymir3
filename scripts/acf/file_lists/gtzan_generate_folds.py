from sklearn.cross_validation import StratifiedKFold

with open('gtzan_labels.txt') as f:
    content = f.readlines()

labels = [k.split("\t")[1].strip() for k in content]

folds = StratifiedKFold(labels, n_folds=10, shuffle=True)

fold = 1
for train_index, test_index in folds:
    f = open( 'gtzan_f%d_train.txt' % fold, 'w')
    for i in train_index:
        f.write(content[i])
    f.close()

    f = open('gtzan_f%d_evaluate.txt' % fold, 'w')
    for i in test_index:
        f.write(content[i])
    f.close()

    f = open('gtzan_f%d_test.txt' % fold, 'w')
    for i in test_index:
        f.write('%s\n' % content[i].split('\t')[0])
    f.close()
    fold+=1
