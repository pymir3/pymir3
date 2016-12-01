import argparse
import copy
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
        feats = analysis_track.metadata.feature.strip().split()

        window_track.metadata.feature = ""
        #ta certo manter esse nome?
        window_track.metadata.filename = analysis_track.metadata.filename

        w = texture_size
        N = len(analysis_track.data)

        begin = 0
        end = begin + w

        ret = numpy.array(())
        ret.shape = (0,0)
        dT = analysis_track.data.T
        it = 1 if dT.ndim == 1 else dT.shape[0]

        #print feats, len(feats)

        ts = ""
        ts2 = ""
        for f in feats:
            ts += " tx_mean_" + f
            ts2 += " tx_var_" + f
        ts = (ts + ts2).strip()

        #print ts, len(ts.split(" "))

        window_track.metadata.feature = ts
        window_track.metadata.input_metadata =\
                copy.deepcopy(analysis_track.metadata)

        #print feats
        #print ts

        #print dT.shape, dT[0], N

        n = 0
        S = numpy.array([0.0] * it)
        m = numpy.array([0.0] * it)

        saida = numpy.zeros((analysis_track.data.shape[0], analysis_track.data.shape[1]*2))

        #print "shape da saida:", saida.shape

        #window_track.metadata.feature += " tx_mean_" + feats[i] +\
        #                                         " tx_var_" + feats[i]

        # print "dT[:,:w].shape: ", dT[:,:w].shape
        # print "dT[:,:w]: ", dT[:,:w]

        # print dT[:,:w][0]

        for x in dT[:,:w].T:

            n = n + 1

            n_m = m + (x - m)/n
            n_s = S + (x - m)*(x - n_m)

            m = n_m
            S = n_s

        #print m.shape, (S/n).shape
        y = numpy.concatenate((m, S/n), axis=0)
        saida[n] = y

        #     print n
        #     print "average: ", numpy.average(dT[:,:n], axis=1), m
        #     print "S:", S
        #     print "variance: ", S/n, numpy.var(dT[:,:n], axis=1)

        # print "boo"


        for i in range(w, N):

            m = n_m

            n_m = m + (dT[:,i]-m)/n - (dT[:,i-w]-m)/n

            S = S + ( (dT[:,i] - n_m) * (dT[:,i] - m) ) - ( ( dT[:,i-w] - m )*( dT[:,i-w] - n_m ) )

            # print i
            # print "average: ",  numpy.average(dT[:,i-w+1:i+1], axis=1), n_m
            # print "S:", S
            # print "variance: ", S/(n), numpy.var(dT[:,i-w+1:i+1], axis=1)

            y = numpy.concatenate((m, S/n), axis=0)
            saida[i] = y

        #print saida.shape

        ret = saida[w:,:]

        #print saida.shape

    # def to_texture(self, analysis_track, texture_size):

    #     window_track = ft.FeatureTrack()
    #     window_track.metadata.sampling_configuration = analysis_track.metadata.sampling_configuration
    #     feats = analysis_track.metadata.feature.split(" ")

    #     window_track.metadata.feature = ""
    #     #ta certo manter esse nome?
    #     window_track.metadata.filename = analysis_track.metadata.filename

    #     step = texture_size
    #     total_aw = len(analysis_track.data)

    #     begin = 0
    #     end = begin + step

    #     ret = numpy.array(())
    #     ret.shape = (0,0)
    #     dT = analysis_track.data.T
    #     it = 1 if dT.ndim == 1 else dT.shape[0]

    #     for i in range(it):
    #         a = numpy.array(())
    #         a.shape = (2,0)
    #         begin = 0
    #         end = begin + step
    #         window_track.metadata.feature += " tx_mean_" + feats[i] +\
    #                                              " tx_var_" + feats[i]

    #         while end <= total_aw:
    #             b = numpy.mean(dT[begin:end]) if dT.ndim == 1 else numpy.mean(dT[i,begin:end])
    #             c = numpy.var(dT[begin:end]) if dT.ndim == 1 else numpy.var(dT[i,begin:end])
    #             d = numpy.vstack( (b, c) )
    #             #print d.shape, a.shape
    #             a = numpy.hstack((a, d))
    #             begin+=1
    #             end+=1
    #         #print "Ficou assim:", a.shape
    #         if ret.shape == (0,0):
    #             ret.shape = (a.shape[1], 0)
    #         ret = numpy.hstack((ret, a.T))
    #         #print "E agora, assim:", ret.shape

        # for i in range(it):
        #     buff = []
        #     lastsum = 0
        #     a = numpy.array(())
        #     a.shape = (2,0)
        #     window_track.metadata.feature += "tx_mean_" + feats[i] + "tx_var_" + feats[i]
        #
        #     for cur in range(0, texture_size):
        #         buff.append(dT[cur] if dT.ndim == 1 else dT[i, cur])
        #         lastsum += dT[cur] if dT.ndim == 1 else dT[i, cur]
        #
        #     mean = lastsum / texture_size
        #     accum = 0
        #     for k in range(0, texture_size):
        #         accum += (buff[k] - mean)**2
        #     var = (accum / texture_size)
        #     temp = numpy.vstack((mean,var))
        #     a = numpy.hstack((a,temp))
        #
        #     for cur in range(texture_size, total_aw):
        #         buff.append(dT[cur] if dT.ndim == 1 else dT[i, cur])
        #         lastsum += -buff[cur-texture_size] + buff[cur]
        #         mean = lastsum / texture_size
        #         accum = 0
        #         for k in range(cur - texture_size+1, cur):
        #             accum += (buff[k] - mean)**2
        #         var = (accum / texture_size)
        #         temp = numpy.vstack((mean,var))
        #         a = numpy.hstack((a,temp))
        #
        #     if ret.shape == (0,0):
        #         ret.shape = (a.shape[1], 0)
        #     ret = numpy.hstack((ret, a.T))

        window_track.data = ret
        return window_track
