# -*- coding: utf-8 -*-
import os
import sys
import yaml
from feature_extraction import FeatureExtractor
from feature_aggregation import FeatureAggregator
from model_training import ModelTrainer
from model_testing import ModelTester
from evaluation import Evaluator

#ETC stands for Feature Extraction, Train and Classify
#The idea is to make this the frontend for all ETC activities :)

def update_parameters(params):

    etag = params['general']['extract_accum_tag']
    ttag = params['general']['train_test_tag']

    if etag != "":
        params['feature_aggregation']['aggregated_output'] = etag + "." + params['feature_aggregation'][
            'aggregated_output']

    if ttag != "":
        params['model_training']['output_model'] = ttag + "." + params['model_training']['output_model']
        params['general']['predict_file'] = ttag + "." + params['general']['predict_file']
        params['model_testing']['predict_proba_file'] = ttag + "." + params['model_testing']['predict_proba_file']

def read_parameters(param_file):
    try:
        f = open(param_file, 'r')
    except IOError:
        print "Could not read file:", param_file
        sys.exit()

    with f:
        params = yaml.load(f)

    return params

def parse_commandline(argv):
    def switch_extract(argv):
        ov = [("steps.extract_features", True),
                ("steps.aggregate_features", True),
                ("steps.train", False),
                ("steps.test", False),
                ("steps.evaluate", False)]

        ex_pos = argv.index('-extract')
        if len(argv) - ex_pos < 3:
            print "wrong number of arguments for \'extract\'. usage: %s -extract path_to_scratch_folder path_to_extract_filelist" % \
                  (argv[0])
            exit(1)
        ov.append(("general.scratch_directory", argv[ex_pos+1]))
        ov.append(("general.feature_extraction_filelist", argv[ex_pos+2]))
        return ov

    def switch_aggregate(argv):
        ov = [("steps.extract_features", False),
              ("steps.aggregate_features", True),
              ("steps.train", False),
              ("steps.test", False),
              ("steps.evaluate", False)]
        return ov

    def switch_train(argv):
        ov = [("steps.extract_features", False),
                ("steps.aggregate_features", False),
                ("steps.train", True),
                ("steps.test", False),
                ("steps.evaluate", False)]

        ex_pos = argv.index('-train')
        if len(argv) - ex_pos < 3:
            print "wrong number of arguments for \'train\'. usage: %s -train path_to_scratch_folder path_to_train_filelist" % \
                  (argv[0])
            exit(1)
        ov.append(("general.scratch_directory", argv[ex_pos+1]))
        ov.append(("general.train_filelist", argv[ex_pos+2]))

        return ov

    def switch_evaluate(argv):
        ov = [("steps.extract_features", False),
              ("steps.aggregate_features", False),
              ("steps.train", False),
              ("steps.test", False),
              ("steps.evaluate", True)]

        ex_pos = argv.index('-evaluate')
        if len(argv) - ex_pos < 3:
            print "wrong number of arguments for \'evaluate\'. usage: %s -evaluate path_to_predict_file path_to_label_file" % \
                  (argv[0])
            exit(1)
        ov.append(("general.predict_file", argv[ex_pos + 1]))
        ov.append(("general.label_file", argv[ex_pos + 2]))

        return ov

    def switch_test(argv):
        ov = [("steps.extract_features", False),
            ("steps.aggregate_features", False),
            ("steps.train", False),
            ("steps.test", True),
            ("steps.evaluate", False)]

        ex_pos = argv.index('-test')
        #print ex_pos, len(argv)
        if len(argv) - ex_pos < 4:
            print "wrong number of arguments for \'test\'. usage: %s -test path_to_scratch_folder path_to_test_filelist path_to_predict_file" % \
                  (argv[0])
            exit(1)
        ov.append(("general.scratch_directory", argv[ex_pos + 1]))
        ov.append(("general.test_filelist", argv[ex_pos + 2]))
        ov.append(("general.predict_file", argv[ex_pos + 3]))

        return ov


    def set_int(argv):
        ex_pos = argv.index('-si')
        a = argv[ex_pos+1]
        a = a.split("=")
        return (a[0], int(a[1]))

    ovw = []

    if "-extract" in argv:
        ovw.extend(switch_extract(argv))

    elif "-aggregate" in argv:
        ovw.extend(switch_aggregate(argv))

    elif "-train" in argv:
        ovw.extend(switch_train(argv))

    elif "-test" in argv:
        ovw.extend(switch_test(argv))

    elif "-evaluate" in argv:
        ovw.extend(switch_evaluate(argv))

    elif "-si" in argv:
        ovw.extend(set_int(argv))

    return ovw

def quote_string(var):
    ret = var
    if type(var) == str:
        ret = "\'%s\'" % (var)
    return ret

def overwrite_params(params, ov):
    #print ov
    for i in ov:
        parts = i[0].split(".")
        #print parts
        access = "params"
        for k in parts:
            access += "[\"" + str(k) + "\"]"
        access += " = %s" % (str(quote_string(i[1])))
        #print "access = \'%s\'" % (access)
        exec(access)


def run_fetc():

    if "-exp" in sys.argv:
        exp_pos = sys.argv.index("-exp")
        param_file = sys.argv[exp_pos+1]
    else:
        param_file = "experiment.yaml"

    exp = read_parameters(param_file=param_file)

    ovw = parse_commandline(sys.argv)
    overwrite_params(exp, ovw)

    update_parameters(exp)

    if exp['steps']['extract_features']:
        fe = FeatureExtractor.create(params=exp)
        fe.run()

    if exp['steps']['aggregate_features']:
        fa = FeatureAggregator.create(params=exp)
        fa.run()

    if exp['steps']['train']:
        t = ModelTrainer.create(params=exp)
        t.run()

    if exp['steps']['test']:
        t = ModelTester.create(params=exp)
        t.run()


    if exp['steps']['evaluate']:
        t = Evaluator.create(params=exp)
        t.run()


if __name__ == "__main__":
    run_fetc()