import argparse

import mir3.data.evaluation as evaluation
import mir3.data.metadata as md
import mir3.data.score as score
import mir3.module

class MirexSymbolic(mir3.module.Module):
    """Uses MIREX symbolic evaluation.
    """

    def get_help(self):
        return """use MIREX symbolic evaluation framework"""

    def build_arguments(self, parser):
        parser.add_argument('-d','--duration-tolerance', type=float, default=-1,
                            help="""duration tolerance, in fraction of total
                            length""")
        parser.add_argument('--id', default=None, help="""evaluation id to store
                            on result, which may be used for comparisons""")
        parser.add_argument('--ignore-pitch', default=False,
                            action='store_true', help="""if used, the system
                            ignores pitches in the evaluation""")
        parser.add_argument('-o','--onset-tolerance', type=float, default=0.05,
                            help="""onset tolerance, in seconds (default:
                            %(default)s)""")

        parser.add_argument('estimated', type=argparse.FileType('rb'),
                            help="""estimated score to evaluate""")
        parser.add_argument('reference', type=argparse.FileType('rb'),
                            help="""reference score""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""evaluation file""")

    def run(self, args):
        e = self.evaluate(args.id,
                          score.Score().load(args.estimated),
                          score.Score().load(args.reference),
                          args.onset_tolerance,
                          args.duration_tolerance,
                          args.ignore_pitch,
                          False)
        e.metadata.estimated_input = md.FileMetadata(args.estimated)
        e.metadata.reference_input = md.FileMetadata(args.reference)
        e.save(args.outfile)

    def evaluate(self, identification, estimated, reference,
                 onset_tolerance=0.05, duration_tolerance=-1,
                 ignore_pitch=False, save_metadata=True):
        """Computes the evaluation based on a estimated and reference scores.

        Args:
            identification: some form of identification that will be stored in
                            metadata.
            estimated: estimated score.
            reference: reference score.
            onset_tolerance: additive tolerance for the onset to be valid.
            duration_tolerance: multiplicative tolerance for the duration to be
                                valid. If negative, ignore duration
                                restrictions.
            ignore_pitch: ignore notes' pitch when evaluating.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            Evaluation object.
        """
        n_ref = len(reference.data)
        n_est = len(estimated.data)

        correct = 0

        # Don't use default comparison because:
        # 1) some crazy person may want to change it, and that could break this
        # code
        # 2) we don't need to sort offset and pitch
        estimated_data = sorted(estimated.data, key=lambda n: n.data.onset)
        reference_data = sorted(reference.data, key=lambda n: n.data.onset)
        negative_duration_tolerance = (duration_tolerance < 0)

        # Iterates estimated data to match the reference
        i_ref = 0 # Index in which we are screening reference data
        i_est = 0 # Index for screening estimated data
        correct = 0 # Match counter
        while (i_est < len(estimated_data)) and\
                (i_ref < len(reference_data)):

            if (abs(estimated_data[i_est].data.onset -\
                    reference_data[i_ref].data.onset) < onset_tolerance) and\
                    (estimated_data[i_est].to_name() ==\
                    reference_data[i_ref].to_name()):
                correct += 1
                i_ref += 1
                i_est += 1
            else:
                if reference_data[i_ref].data.onset <\
                        estimated_data[i_est].data.onset:
                    i_ref += 1
                else:
                    i_est += 1

        # Creates evaluation object with the description of the method
        e = evaluation.Evaluation(n_est, n_ref, correct)
        e.metadata.estimated = estimated.metadata
        e.metadata.reference = reference.metadata
        e.metadata.method = md.Metadata(name='mirex symbolic',
                                        id=identification,
                                        duration_tolerance=duration_tolerance,
                                        onset_tolerance=onset_tolerance)
        if save_metadata:
            e.metadata.estimated_input = md.ObjectMetadata(estimated)
            e.metadata.reference_input = md.ObjectMetadata(reference)

        return e
