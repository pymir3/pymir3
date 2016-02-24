import argparse
import mir3.data.feature_matrix as feature_matrix
import mir3.module
import numpy
import sys

class Features(mir3.module.Module):
    def get_help(self):
        return """outputs a matrix in ASCII for the feature matrix"""

    def build_arguments(self, parser):
        parser.add_argument('-f','--features', action='store_true', default=False,
                            help="""display only feature names (not data) (default:
                            %(default)s)""")
        parser.add_argument('-l', '--labels', action='store_true', default=False,
                            help="""display only labels (filenames) (default:
                            %(default)s)""")
        parser.add_argument('-c', '--csv', action='store_true', default=False,
                            help="""CSV output (default:
                            %(default)s)""")
        parser.add_argument('infile', type=argparse.FileType('r'), help="""track
                            file""")

    def run(self, args):
        a = feature_matrix.FeatureMatrix().load(args.infile)
        if args.labels is True:
            print "Stored ", len(a.metadata.filename), " files"
            for f in a.metadata.filename:
                print f
            exit()
                
        #classe = a.metadata.filename.split("/")[-1].split(".")[0]
            
        # verification
        #print a.metadata.feature
        #print a.data, a.data.shape
        feature_names = a.metadata.feature.split()
        feature_names.sort()
        if args.features is True:
            if len(feature_names) != a.data.shape[1]:
                print "Feature names are inconsistent with data!"
                print feature_names
                print len(feature_names)
                print a.data.shape
                exit()

            for f in feature_names:
                sys.stdout.write(f)
                if args.csv is True:
                    sys.stdout.write(",")                        
                sys.stdout.write(" ")
            print "label"
        else:
            for i in xrange(len(a.metadata.filename)):
                for j in xrange(a.data.shape[1]-1):
                    sys.stdout.write(str(a.data[i,j]))
                    if args.csv is True:
                        sys.stdout.write(",")                        
                    sys.stdout.write(" ")
                sys.stdout.write(str(a.data[i,j+1]))
                sys.stdout.write(", ")
                #A linha seguinte esta porquinha. 
                #masss (requer que o nome da classe seja o primeiro no arquivo
                sys.stdout.write(a.metadata.filename[i].split("/")[-1].split(".")[0])
                print ""
