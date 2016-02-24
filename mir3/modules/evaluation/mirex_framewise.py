import argparse

import mir3.data.evaluation as evaluation
import mir3.data.metadata as md
import mir3.data.score as score
import mir3.module

class MirexFramewise(mir3.module.Module):
    """Uses MIREX framewise evaluation.
    """

    def get_help(self):
        return """use MIREX framewise evaluation framework"""

    def build_arguments(self, parser):
        parser.add_argument('-f','--frame-length', type=float, default=0.01,
                            help="""length of each frame, in seconds (default:
                            %(default)s)""")
        parser.add_argument('--id', default=None, help="""evaluation id to store
                            on result, which may be used for comparisons""")

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
                          args.frame_length,
                          False)
        e.metadata.estimated_input = md.FileMetadata(args.estimated)
        e.metadata.reference_input = md.FileMetadata(args.reference)
        e.save(args.outfile)

    def evaluate(self, identification, estimated, reference, frame_length=0.01,
                 save_metadata=True):
        """Computes the evaluation based on a estimated and reference scores.

        Args:
            identification: some form of identification that will be stored in
                            metadata.
            estimated: estimated score.
            reference: reference score.
            frame_length: step size for time.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            Evaluation object.
        """
        t_start_estimated, t_end_estimated = estimated.get_timespan()
        t_start_reference, t_end_reference = reference.get_timespan()

        correct = 0.
        total_estimated = 0.
        total_reference = 0.

        # Sanity check
        if t_end_estimated - t_start_estimated >= 0 and \
           t_end_reference - t_start_reference >= 0:
            # Starts at the first frame
            t = min(t_start_estimated, t_start_reference)

            # Ends with the minimum frame time
            t_end = min(t_end_estimated, t_end_reference)

            while t < t_end:
                # Gets notes active at the current time
                estimated_active_notes = estimated.get_active_notes(t)
                reference_active_notes = reference.get_active_notes(t)

                total_estimated += len(estimated_active_notes)
                total_reference += len(reference_active_notes)

                for e in estimated_active_notes:
                    e_name = e.to_name()

                    for r in reference_active_notes:
                        if e_name == r.to_name():
                            correct += 1

                            # As each reference note can match only a single
                            # estimation, we remove the matched reference
                            reference_active_notes.remove(r)

                            # Stops looking for references, as we got a match
                            break

                t += frame_length

        # Creates evaluation object with the description of the method
        e = evaluation.Evaluation(total_estimated, total_reference, correct)
        e.metadata.estimated = estimated.metadata
        e.metadata.reference = reference.metadata
        e.metadata.method = md.Metadata(name='mirex framewise',
                                        id=identification)
        if save_metadata:
            e.metadata.estimated_input = md.ObjectMetadata(estimated)
            e.metadata.reference_input = md.ObjectMetadata(reference)

        return e
