import os
import glob
import sys
import numpy as np

if __name__ == "__main__":

    dirs = [ name for name in os.listdir(".") if os.path.isdir(os.path.join(".", name)) ]

    files = []

    for d in sorted(dirs):
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

                        graph = open( "graphs/" + dataset + "_" + j + "_anova_frequencies.txt", "w")
                        feat_seq = 0;
                        for feat in data.split(" "):
                            if feat.find("MFCC") != -1:
                                continue
                            else:
                                s = feat.split("_")
                                if len(s) <=4:
                                    continue
                                print s
                                graph.write(s[0][0] + "_" + s[2][0] + "_" + s[3] + ", " + str(feat_seq) + ", " + s[-1] + "\n" )
                                feat_seq+=1
                        graph.close()

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
