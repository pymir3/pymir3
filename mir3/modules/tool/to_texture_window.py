import argparse
import numpy
import mir3.data.metadata as metadata
import mir3.data.feature_track as ft
import mir3.module

class ToTextureWindow(mir3.module.Module):
    def get_help(self):
        return """calculates texture windows from feature tracks"""
    
    def build_arguments(self, parser):
        parser.add_argument('-s','--texture-window-size', type=int, default=50,
                    help="""how many analysis windows per texture window""")
        
        parser.add_argument('infile', type=argparse.FileType('rb'), help="""feature track""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""texture window feature track""")        
    
    def run(self, args):
        analysis_track = ft.FeatureTrack().load(args.infile)
        window_track = ft.FeatureTrack()
        
        window_track.metadata.sampling_configuration = analysis_track.metadata.sampling_configuration
        window_track.metadata.feature = analysis_track.metadata.feature
        #ta certo manter esse nome?
        window_track.metadata.filename = analysis_track.metadata.filename
        
        step = args.texture_window_size
        total_aw = len(analysis_track.data)
        
        begin = 1
        end = begin + step -1
        
        #print step, total_aw, begin, end
        
        ret = numpy.array(())
        
        #print analysis_track.data
        
        while end <= total_aw:
            ret = numpy.hstack((ret, numpy.mean(analysis_track.data[begin:end+1])))
            begin+=1
            end+=1
            
        window_track.data = ret
        
        window_track.save(args.outfile)
