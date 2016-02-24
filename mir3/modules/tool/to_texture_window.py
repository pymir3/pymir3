import argparse
import numpy
import mir3.data.metadata as metadata
import mir3.data.feature_track as ft
import mir3.module

class ToTextureWindow(mir3.module.Module):
    def get_help(self):
        return """calculates texture windows from feature tracks"""
    
    def build_arguments(self, parser):
        parser.add_argument('-S','--texture-window-size', type=int, default=1024,
                    help="""how many analysis windows (frames) per texture window""")
        
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
        
        begin = 0
        end = begin + step
        
        ret = numpy.array(())
        dT = analysis_track.data.T 
        it = 1 if dT.ndim == 1 else dT.shape[0]
        
        for i in range(it):
            a = numpy.array(())
            begin = 0
            end = begin + step
            while end <= total_aw:
                b = numpy.mean(dT[begin:end]) if dT.ndim == 1 else numpy.mean(dT[i,begin:end])
                a = numpy.hstack((a, b))
                begin+=1
                end+=1
            #print "Ficou assim:", a, a.shape
            ret = numpy.hstack((ret, a))
        
        ret.shape = (it, ret.shape[0] / it) if dT.ndim != 1 else (ret.shape[0])
        ret = ret.T
        window_track.data = ret
        window_track.save(args.outfile)
