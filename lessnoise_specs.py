import glob
import remove_random_noise as rrn
import os
filename, file_extension = os.path.splitext('/path/to/somefile.ext')
if __name__ == "__main__":

    wavdir = "./links/"
    wavs = sorted(glob.glob(wavdir + "*.wav"))
    pngdir = "./pngs/"
    #print wavs

    for f in wavs:
        nome, ext = os.path.splitext(f)
        pngfile = pngdir + nome.split("/")[-1] + ".png"
        print f, "->", pngfile
        rrn.remove_random_noise_from_wav(f, False, pngfile, 'log10', passes=1)

    # thedir = "/home/juliano/base_teste_rafael_94_especies"
    # linkdir = "./links/"
    # dirs = [ name for name in os.listdir(thedir) if os.path.isdir(os.path.join(thedir, name)) ]
    #
    # for d in dirs:
    #     p = "/home/juliano/base_teste_rafael_94_especies" + "/" + d
    #     files = sorted(glob.glob(p + "/*.wav"))
    #     i = 0
    #     for f in files:
    #         print f.split("/")[-1]
    #         call(['ln', '-s', f, linkdir ])
    #         call(['mv', linkdir + f.split("/")[-1], linkdir + d + "." + str(i) + '.wav'])
    #         i+=1