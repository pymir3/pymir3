import acf_utils
import sys
import numpy
import gc

def canon_file(contents):
    canon = []
    for k in contents:
        d = k.split("\t")
        d[1] = d[1].strip()
        canon.append(d)
    canon = sorted(canon, key=lambda x: x[0])

    return canon


class EvaluatorInput:

    def __init__(self, truth, predicted):
        self.truth = truth
        self.predicted = predicted

class Evaluator:

    def __init__(self):
        pass

    @staticmethod
    def create(params):
        return acf_utils.behavior_factory(params, "evaluation", "evaluator","ev_")

    def run(self):
        print "predict file: %s" % (self.params['general']['predict_file'])
        print "ground truth file: %s" % (self.params['general']['label_file'])
        gt_filename = self.params['general']['label_file']
        predict_filename = self.params['general']['predict_file']

        with open(gt_filename) as f:
            gt = f.readlines()
        gt = canon_file(gt)

        gtd = dict()
        for i in gt:
            gtd[i[0]] = i[1]

        #print gtd

        with open(predict_filename) as f:
            pred = f.readlines()
        pred = canon_file(pred)

        predicted = []
        truth = []

        for i in pred:
            predicted.append(i[1])
            if gtd.has_key(i[0]):
                truth.append(gtd[i[0]])
            else:
                print "truth for %s not in label file!" % (i[0])
                exit(1)

        #print predicted, len(predicted)
        #print truth, len(truth)

        input = EvaluatorInput(truth, predicted)

        self.evaluate(input)

    def evaluate(self, input):
        raise NotImplementedError
