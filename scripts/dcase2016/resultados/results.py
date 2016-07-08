import os
import glob
import sys
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":

    dirs = [ name for name in os.listdir(".") if os.path.isdir(os.path.join(".", name)) ]

    files = []

    for d in sorted(dirs):

        if d == "graphs":
            continue

        p = "." + "/" + d
        files = (sorted(glob.glob(p + "/*.csv")))
        csvs = dict()
        dataset = p.split("./")[1]
        dataset_results = open(dataset + "_results.csv", 'w')
        for i in files:
            csv = np.genfromtxt(i, dtype='string' , delimiter=',')
            pipeline = i.split("/")[2].split("_")[1:]
            pipeline = (''.join(str(elem) + "_" for elem in pipeline)).replace(".csv_", "")
            csvs[pipeline] = csv
        stats = csv[0][:]
        pipelines = csv[1:,[0]]
        for i in range(1,len(stats)):

            if stats[i] == 'sorted_features':
                print dataset
                for j in sorted(csvs.keys()):
                    print "\t" + j
                    p = -1
                    for l in (csvs[j])[1:,[i]]:
                        data = str(l[0])
                        data = data.replace("[","")
                        data = data.replace("]","")
                        data = data.replace("/","")
                        data = data.replace("'","")
                        p+=1
                        if data[0] == 'P' or data[0] == 'n':
                            continue
                        # print "\t\t", pipelines[p][0]
                        # print "\t\t\t", data.split(" ")
                        graph = open( "graphs/" + dataset + "_" + pipelines[p][0].split("+")[0] + "_" + j + "_anova_frequencies.txt", "w")
                        feat_seq = 0;
                        bf = []
                        for feat in data.split(" "):
                            s = feat.split("_")
                            #print s
                            if len(s) <= 1:
                            	continue
                            if len(s) <=4:
                                graph.write(s[0][0] + "_" + s[2][0] + "_" + "ZeroCrossings, 0, 0, 0, 0"+ "\n" )
                            else:
                            	if s[3] == "MFCC":
									graph.write(s[0][0] + "_" + s[2][0] + "_" + s[3] + ", " + s[3] + ", " + str(feat_seq) + ", " + s[4] + ", " + s[4] + "\n" )
                            	else:
                            		graph.write(s[0][0] + "_" + s[2][0] + "_" + s[3] + ", " + s[3] + ", " + str(feat_seq) + ", " + s[-2] + ", " + s[-1] + "\n" )
                            bf.append(s)
                            feat_seq+=1
                        graph.close()
                        # feats = [s[0][0] + "_" + s[2][0] + "_" + s[3] for s in bf]
                        # freqs = [max(5,int(s[-1])) for s in bf]
                        # feat_seqs = [fs for fs in range(len(bf))]
                        #
                        # print feats
                        # print freqs
                        #
                        # f = plt.figure(0)
                        # lefts = np.arange(len(bf))
                        # plt.bar(lefts, freqs, width=0.5)
                        # plt.show()
                continue

            dataset_results.write("\n" + stats[i] + "\n\n")

            dataset_results.write("configuration,")
            for k in csv[1:,[0]]:
                dataset_results.write(k[0] + ",")
            dataset_results.write("\n")

            for j in sorted(csvs.keys()):
                dataset_results.write(j + ",")
                for l in (csvs[j])[1:,[i]]:
                    dataset_results.write(str(l[0]) + ",")
                dataset_results.write("\n")



        dataset_results.close()
