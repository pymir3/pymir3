# -*- coding: utf-8 -*-
import importlib
import gc
import time
from multiprocess import Pool

class FeatureExtractor:

    @staticmethod
    def create(params):
        fe_name = (params['feature_extraction']['extractor'])

        fe_module = importlib.import_module("fe_" + fe_name)

        fe_name = (params['feature_extraction']['extractor']).capitalize()
        fe = eval("fe_module." + fe_name + "Extractor")(params)

        fe.params = params
        return fe

    def run(self):

        #deve garantir a label no metadados pra facilitar a vida, ao invés de usar o nome do arquivo (acho que não precisa)

        with open(self.params['general']['feature_extraction_filelist']) as f:
            files = f.read().splitlines()

        #todo: usar um multiprocessing.manager pra realizar o compatilhamento do buffer

        num_files = len(files)
        output_buffer_size = self.params['feature_extraction']['output_buffer_size']

        pool = Pool(processes=self.params['feature_extraction']['worker_extractors'])
        for i in range(0, num_files, output_buffer_size):
            print "processing files %d through %d of %d" % (i+1, min(i+output_buffer_size, num_files), num_files)
            result = pool.map(self.extract, files[i:min(i+output_buffer_size, num_files)])

            T0 = time.time()
            for track in result:
                filename = (track.metadata.filename).split("/")[-1].split(".wav")[0] + ".features"
                filename = self.params['general']['scratch_directory'] + "/" + filename
                print "writing features to file %s..." % (filename)
                feature_file = open(filename, "w")
                track.save(feature_file)
                feature_file.close()
                del track
            T1 = time.time()
            print "writing feature files to disk took %f seconds" % (T1 - T0)

            del result
            gc.collect()

        pool.close()
        pool.join()




