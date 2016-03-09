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
        texture_size = args.texture_window_size
        window_track = self.to_texture(analysis_track, texture_size)
        window_track.save(args.outfile)

    def to_texture(self, analysis_track, texture_size):

        window_track = ft.FeatureTrack()
        window_track.metadata.sampling_configuration = analysis_track.metadata.sampling_configuration
        feats = analysis_track.metadata.feature.split(" ")

        window_track.metadata.feature = ""
        #ta certo manter esse nome?
        window_track.metadata.filename = analysis_track.metadata.filename

        step = texture_size
        total_aw = len(analysis_track.data)

        begin = 0
        end = begin + step

        ret = numpy.array(())
        ret.shape = (0,0)
        dT = analysis_track.data.T
        it = 1 if dT.ndim == 1 else dT.shape[0]

        for i in range(it):
            a = numpy.array(())
            a.shape = (2,0)
            begin = 0
            end = begin + step
            window_track.metadata.feature += " tx_mean_" + feats[i] +\
                                                 " tx_var_" + feats[i]

            while end <= total_aw:
                b = numpy.mean(dT[begin:end]) if dT.ndim == 1 else numpy.mean(dT[i,begin:end])
                c = numpy.var(dT[begin:end]) if dT.ndim == 1 else numpy.var(dT[i,begin:end])
                d = numpy.vstack( (b, c) )
                #print d.shape, a.shape
                a = numpy.hstack((a, d))
                begin+=1
                end+=1
            #print "Ficou assim:", a.shape
            if ret.shape == (0,0):
                ret.shape = (a.shape[1], 0)
            ret = numpy.hstack((ret, a.T))
            #print "E agora, assim:", ret.shape

        #ret.shape = (it, ret.shape[0] / it) if dT.ndim != 1 else (ret.shape[0])

        window_track.data = ret
        return window_track
