# -*- coding: utf-8 -*-

import os
import sys
import yaml
from feature_extraction import FeatureExtractor
from feature_aggregation import FeatureAggregator
from model_training import ModelTrainer

#ETC stands for Feature Extraction, Train and Classify
#The idea is to make this the frontend for all ETC activities :)

def read_parameters(param_file):
    with open(param_file, 'r') as f:
        return yaml.load(f)

def run_fetc():

    exp = read_parameters(param_file="experiment.yaml")

    #todo: overwrite experiment parameters with command-line parameters

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
        pass

    if exp['steps']['evaluate']:
        pass


if __name__ == "__main__":
    run_fetc()