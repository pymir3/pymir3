#!/usr/bin/python
# -*- coding: utf8 -*-
import sys, getopt
sys.path.append("../../")
import gc
import glob
import train_and_classify as ttc
import birdclef_tza_bands as btb
from sklearn.metrics import classification_report, confusion_matrix

def print_help():
    print 'uso: %s -d <diretorio_dataset_filelists> -o <diretorio_saidas> -p <lista_datasets> -e <experimento>' % (sys.argv[0])
    print
    print 'argumentos obrigatórios:'
    print '\t -d <diretorio_dataset_filelists> -- Diretório possui as listas dos arquivos de entrada (formato MIREX)'
    print '\t\t dos datasets'
    print '\t -o <diretorio_saidas> -- Diretório no qual as saídas irão ser escritas.'
    print '\t -e <experimento> -- Indica qual experimento executar. Pode ser \'tzan\' ou \'bands\'. Exemplo: -e bands'
    print
    print 'argumentos opcionais:'
    print '\t -p <lista_datasets> -- Indica quais datasets devem ser processados. Caso não seja passado, todos os datasets'
    print '\t\t cujas listas forem indicadas no argumento -d serão processados. Os nomes dos arquivos dos datasets no diretório'
    print '\t\t são considerados. Separe os datasets por vírgula. Exemplo: -p gtzan.txt,ballroom.txt'
    print '\t -b <lista_n_bandas> -- Indica a lista de número de bandas a testar. Só é considerado quando'
    print '\t\t o experimento é \'bands\'. Exemplo: -b 5,10,20,30'
    print '\t -i <lista_iteradores_bandas> -- Indica a lista de quais iteradores de banda usar. Só é considerado quando'
    print '\t\t o experimento é \'bands\'. Pode ser \'linear\' ou \'mel\' Exemplo: -i linear,mel'

def imprimir_datasets(dataset_dir):
    datasets = glob.glob(dataset_dir + "/*")

    print "Dataset filelists disponiveis em %s:" % (dataset_dir)
    for i in datasets:
        if i.find("labels") != -1:
            continue
        if i.find("apague") != -1:
            continue
        print "\t", i.split("/")[-1]


if __name__ == "__main__":

    argv = sys.argv[1:]

    datasets = ''
    saidas = ''
    processar = []
    exp = ""
    bandas = [5,10,20,30]
    its = ['linear', 'mel']

    try:
      opts, args = getopt.getopt(argv,"hd:o:p:e:b:i:",["datasets=","saidas=","processar=","experimento=","bandas=", "iteradores="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-d", "--datasets"):
            datasets = arg if arg[-1] != "/" else arg[:-1]
        elif opt in ("-o", "--saidas"):
            tmp = arg.strip()
            saidas = tmp if tmp[-1] != "/" else arg[:-1]
        elif opt in ("-p", "--processar"):
            processar = arg.split(",")
        elif opt in ("-e", "--experimento"):
            exp = arg
        elif opt in ("-b", "--bandas"):
            bandas = [int(x) for x in arg.split(",")]
        elif opt in ("-i", "--iteradores"):
            its = arg.split(",")

    if datasets == '':
        print_help()
        sys.exit(2)

    if datasets != '' and saidas == '':
        imprimir_datasets(datasets)
        sys.exit(2)

    print "caminho dos datasets: ", datasets
    print "caminho das saidas: ", saidas
    print "n_bandas", bandas
    print "its", its

    if processar == []:
        for d in sorted(glob.glob(datasets + "/*")):
            if d.find("labels") != -1:
                continue
            if d.find("apague")!= -1:
                continue
            processar.append(d.split("/")[-1])

    if len(processar) == 0:
        sys.exit("Não foram encontrados dataset list files!")

    print "processando os arquivos a seguir:", processar

    print exp
    if exp != 'bands' and exp != 'tzan':
        sys.exit("Por favor especifique um dos dois tipos de experimento: bands ou tzan.")

    for p in processar:

        with open(datasets + "/" + p.split(".")[0] + "_labels.txt") as f:
            l = f.read().splitlines()
        f.close()
        labels = dict()
        for i in l:
            info = i.split("\t")
            labels[info[0]] = info[1]

        print "EXTRAINDO FEATURES DE %s" % (p.split(".")[0])

        if exp == 'tzan':
            exp_prefix = "_tzanetakis"

            outfile = p.split(".")[0] + exp_prefix + ".fm"
            fm = btb.MIREX_ExtractFeatures(saidas, datasets + "/" + p,
                                               output_file=outfile,
                                               band_iterator='one',
                                               band_nbands='1')

            classification_summary = ttc.train_and_classify(feature_matrix=fm, sample_labels=labels)
            ttc.output_experiment(saidas, p, classification_summary, exp_prefix)
            gc.collect()

        if exp == 'bands':
            n_bands = bandas
            band_it = its
            for it in band_it:
                for b in n_bands:

                    print "iterador: %s, número de bandas: %d" % (it, b)

                    exp_prefix = "_" + it + "_bands_" + str(b) + "b"
                    outfile = p.split(".")[0] + exp_prefix + ".fm"
                    fm = btb.MIREX_ExtractFeatures(saidas, datasets + "/" + p,
                                                   output_file=outfile,
                                                   band_iterator=it,
                                                   band_nbands=b)
                    gc.collect()
                    classification_summary = ttc.train_and_classify(feature_matrix=fm, sample_labels=labels)
                    ttc.output_experiment(saidas, p, classification_summary, exp_prefix)
                    gc.collect()






