import glob
import os

def write_tex_cm(filename, labels, matrix_lines):
    out = open(filename, "w")

    align_header = "|l|"

    for i in labels:
        align_header += "c|"

    print align_header
    out.write("\\begin{tabular}{" + align_header + "}\n")
    print "& ",
    print labels[0],
    out.write("\\hline \n& \\rot{" + labels[0] + "}")
    for l in labels[1:]:
        print "& " + l,
        out.write("& \\rot{" + l + "}")

    print
    out.write(" \\\\ \\hline \\hline \n")

    for i in matrix_lines:
        print i[0],
        out.write(i[0])
        if i[0] == "New":
            out.write("Age")

        # sum = 0
        # for k in i[1:]:
        #     if k == "Age":
        #         continue
        #     sum += int(k)

        for k in i[1:]:
            if k == "Age":
                continue
            # k = float(k) / sum * 100
            # k = "%02.f" % k
            print "& " + k,
            out.write("& " + k)
        print
        out.write(" \\\\ \\hline \n")

    out.write("\end{tabular}\n")

    out.close()

if __name__ == "__main__":

    cm_file_patterns = ["tzanetakis_cr_cm", "mel_bands_20b_cr_cm"]
    dirs = [ name for name in os.listdir(".") if os.path.isdir(os.path.join(".", name)) ]
    cm_files = []
    classifier = 'SVM'
    tex_folder = "./tex/"

    for d in dirs:
        for file_pattern in cm_file_patterns:
            path = d + "/*" + file_pattern + "*"
            files = (sorted(glob.glob(path)))
            cm_files.extend(files)

    for cm_file in cm_files:
        print cm_file
        with open(cm_file) as f:
            content = f.readlines()

        for l in range(len(content)):
            if content[l].find( classifier + "\n") != -1:
                for l1 in range(l+1, len(content)):
                    if content[l1].find("confusion matrix:") != -1:
                        break
                l1+=2
                labels = []
                matrix_lines = []
                while(1):
                    if content[l1][0] == '\n':
                        break
                    str_list = content[l1].replace("\n", "").split(" ")
                    str_list = filter(None, str_list)
                    #print str_list, len(str_list)

                    #aqui str_list tem exatamente o conteudo de cada linha de cada matriz de confusao.
                    #l1 e a posicao destas linhas no arquivo.

                    labels.append(str_list[0])

                    matrix_lines.append(str_list)

                    l1+=1

                #agora eh soh escrever em formato tex.
                tex_filename = tex_folder + cm_file.split("/")[1].split(".")[0] + "_SVM" + ".tex"
                print tex_filename

                write_tex_cm(tex_filename, labels, matrix_lines)










