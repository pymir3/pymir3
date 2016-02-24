import argparse

import mir3.data.metadata as md
import mir3.data.score as score
import mir3.module

class TrimScore(mir3.module.Module):
    """Removes notes from a score.
    """

    def get_help(self):
        return """removes obviously wrong notes from a score, keeping only those
               that are within given restriction limits"""

    def build_arguments(self, parser):
        parser.add_argument('-d', '--minimum-duration', type=float, default=0.0,
                            help="""minimum note duration (s)""")
        parser.add_argument('-D', '--maximum-duration', type=float,
                            default=float('inf'), help="""maximum note
                            duration (s)""")
        parser.add_argument('-f', '--minimum-offset', type=float, default=0.0,
                            help="""minimum note offset (s)""")
        parser.add_argument('-F', '--maximum-offset', type=float,
                            default=float('inf'), help="""maximum note offset
                            (s)""")
        parser.add_argument('-o', '--minimum-onset', type=float, default=0.0,
                            help="""minimum note onset (s)""")
        parser.add_argument('-O', '--maximum-onset', type=float,
                            default=float('inf'), help="""maximum note onset
                            (s)""")
        parser.add_argument('-p', '--minimum-pitch', type=float, default=0.0,
                            help="""minimum note pitch (MIDI)""")
        parser.add_argument('-P', '--maximum-pitch', type=float,
                            default=float('inf'), help="""maximum note pitch
                            (MIDI)""")

        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""original score file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""trimmed score file""")

    def run(self, args):
        new_s = self.trim_notes(score.Score().load(args.infile),
                                args.minimum_duration,
                                args.maximum_duration,
                                args.minimum_pitch,
                                args.maximum_pitch,
                                args.minimum_onset,
                                args.maximum_onset,
                                args.minimum_offset,
                                args.maximum_offset,
                                False)
        new_s.metadata.input = md.FileMetadata(args.infile)
        new_s.save(args.outfile)

    def trim_notes(self, s, min_duration=0, max_duration=float('inf'),
                   min_pitch=0, max_pitch=float('inf'), min_onset=0,
                   max_onset=float('inf'), min_offset=0,
                   max_offset=float('inf'), save_metadata=True):
        """Removes from a score notes that don't satisfy a criteria.

        Trims the transcription so notes that are out of the specified bonds
        will be cut out of the transcription. The notes aren't copied for the
        new Score, so any modification on them alters both the original and
        trimmed.

        This function is useful when you are trying to exclude notes that are
        obviously wrong in a certain transcription. By default, all arguments
        not provided don't cause any note to be removed.

        Args:
            s: Score object.
            min_duration: minimum duration to keep. Default: 0.
            max_duration: maximum duration to keep. Default: inf.
            min_pitch: minimum pitch to keep. Default: 0.
            max_pitch: maximum pitch to keep. Default: inf.
            min_onset: minimum onset to keep. Default: 0.
            max_onset: maximum onset to keep. Default: inf.
            min_offset: minimum offset to keep. Default: 0.
            max_offset: maximum offset to keep. Default: inf.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            Trimmed Score object.
        """
        new_s = score.Score()
        new_s.append([n for n in s.data
                        if n.data.duration >= min_duration and
                           n.data.duration <= max_duration and
                           n.data.onset >= min_onset and
                           n.data.onset <= max_onset and
                           n.data.offset >= min_offset and
                           n.data.offset <= max_offset and
                           n.data.pitch >= min_pitch and
                           n.data.pitch <= max_pitch])

        new_s.metadata.instrument = s.metadata.instrument
        new_s.metadata.method_metadata = md.Metadata(
            type="trim",
            min_duration=min_duration,
            max_duration=max_duration,
            min_onset=min_onset,
            max_onset=max_onset,
            min_offset=min_offset,
            max_offset=max_offset,
            min_pitch=min_pitch,
            max_pitch=max_pitch,
            previous_method=s.metadata.method_metadata,
            previous_input=s.metadata.input)
        if save_metadata:
            s.metadata.input = md.ObjectMetadata(s)

        return new_s
