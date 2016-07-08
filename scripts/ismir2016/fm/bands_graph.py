import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import six

def plot_bands(band_features, filename):

    filename = filename.split(".")[0]

    report = open(filename + "_REPORT.txt", "w")

    print filename
    report.write(filename + "\n")

    feature_colors = {
        'Energy' : 'yellow',
        'Centroid': 'blue',
        'Flatness': 'green',
        'Flux' : 'red',
        'Roll-Off': 'gray',
        'LowEnergy' : 'cyan'
    }

    x = np.arange(len(band_features))
    low = np.arange(len(band_features))
    high = np.arange(len(band_features))

    band_feats = dict()

    fig, ax = plt.subplots(1)

    print "there are a total of ", len(band_features), " features in this graph"
    report.write("there are a total of " + str(len(band_features)) + " features in this graph\n")

    for feature in band_features:

        if feature[0] not in band_feats:
            band_feats[feature[0]] = []

        band_feats[feature[0]].append(feature[2])

        low.fill(feature[0])
        high.fill(feature[1])
        ax.fill_between(x, low, high, alpha=0.5, facecolor=feature_colors[feature[2]])

    for i in band_feats:
        band_feats[i] = sorted(list(set(band_feats[i])))

    band_list = [(k, v) for k, v in band_feats.items()]
    band_list = sorted(band_list, key= lambda x: x[0])

    feature_names = sorted(feature_colors.keys())

    report.write("band;")
    for i in feature_names:
        report.write(i + ";")
    report.write("\n")

    for i in band_list:
        print str(i[0]), " = ", str(i[1])
        report.write(str(i[0]) + ";")
        for k in feature_names:
            if k in i[1]:
                report.write("x;")
            else:
                report.write(";")
        report.write("\n")

    ax.set_ylim([0,22050])
    ax.set_xlim([0,50])
    ax.set_xlabel("")
    ax.set_ylabel("frequency (Hz)")
    ax.set_title(filename)

    plt.savefig(filename + ".png", format = "png")

    ax.set_ylim([0,5000])
    plt.savefig(filename + "_5000hz" + ".png", format = "png")

    #plt.show()
    plt.close()

if __name__ == "__main__":

    graph_files = ["gtzan_SVM_mel_bands_20b_anova_frequencies.txt",
                   "ballroom_SVM_mel_bands_20b_anova_frequencies.txt",
                   "homburg_SVM_mel_bands_20b_anova_frequencies.txt",
                   "seyerlehner_SVM_mel_bands_20b_anova_frequencies.txt"]
    graph_dir = "./rerun/graphs"
    prefix ="BANDS"
    anova_percents = [80, 40, 50, 20]
    only_mm = True

    if only_mm:
        prefix = prefix + "_MM"


    for i in range(len(graph_files)):

        graph_file  = graph_files[i]
        anova_percent = anova_percents[i]

        with open(graph_dir + "/" + graph_file) as f:
            content = f.readlines()

        content = np.array(content)[::-1]
        band_features = []
        last_feat = int((float(anova_percent) / 100) * content.shape[0])
        print "a total of ", last_feat, "features were selected"
        cur_feat = 0


        for l in content:

            if cur_feat >= last_feat:
                break

            feature = l.replace(" ", "").replace("\n", "").split(",")
            if feature[1] in ["MFCC", "0"]:
                continue

            stat = feature[0].split("_")

            append_me = True

            if only_mm:
                if stat[0] == "m" and stat[1] == "m":
                    append_me = True
                else:
                    append_me = False
            if append_me:
                band_features.append((int(feature[-2]), int(feature[-1]), feature[1]))

            cur_feat += 1

        band_features = sorted(band_features, key= lambda x : x[2])

        plot_bands(band_features, prefix + "_" + graph_file)







