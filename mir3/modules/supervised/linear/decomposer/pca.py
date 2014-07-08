import argparse
import numpy
import numpy.linalg

import mir3.data.linear_decomposition as ld
import mir3.data.metadata as md
import mir3.data.spectrogram as spectrogram
import mir3.lib.pca as pca
import mir3.module

class PCA(mir3.module.Module):
    def get_help(self):
        return """use pca algorithm to compute the activations"""

    def build_arguments(self, parser):
        parser.add_argument('-B','--basis', type=argparse.FileType('r'),
                            help="""basis file to be used""")
        parser.add_argument('-e','--energy', nargs=3,
                            metavar=('ENERGY', 'INSTRUMENT', 'NOTE'),
                            help="""proportion (between 0 and 1) of the energy
                            to keep , and instrument and note names to be used
                            for the basis. 'INSTRUMENT' or 'NOTE' can be set to
                            'None' or 'null' to ignore that parameter""")
        parser.add_argument('-s','--size', nargs=3, metavar=('SIZE',
                            'INSTRUMENT', 'NOTE'), help="""size of the
                            decomposition, and instrument and note names to be
                            used for the basis. 'INSTRUMENT' or 'NOTE' can be
                            set to 'None' or 'null' to ignore that parameter""")

        parser.add_argument('piece', nargs='+', help="""piece spectrogram
                            file""")
        parser.add_argument('outfile', type=argparse.FileType('w'),
                            help="""linear decomposition file""")

    def run(self, args):
        # Loads basis if present
        if args.basis is not None:
            b = ld.LinearDecomposition().load(args.basis)
        else:
            b = None

        if args.basis is not None and b.data.right != {}:
            print "Basis doesn't have empty right side. Ignoring it."

        # Size of the decomposition (used when finding a basis too)
        if args.size is None:
            args.size = [None, None, None] # Simulate 3 values
        for i in range(len(args.size)):
            if args.size[i] == 'None' or args.size[i] == 'null':
                args.size[i] = None

        # Energy for the PCA decomposition
        if args.energy is None:
            args.energy = [None, None, None] # Simulate 3 values
        for i in range(len(args.energy)):
            if args.energy[i] == 'None' or args.energy[i] == 'null':
                args.energy[i] = None

        # Gather input spectrograms
        s_list = []
        s_meta = []
        for filename in args.piece:
            with open(filename, 'r') as handler:
                s_list.append(spectrogram.Spectrogram().load(handler))
                s_meta.append(md.FileMetadata(handler))

        # Converts arguments
        size = int(args.size[0]) if args.size[0] is not None else None
        energy = float(args.energy[0]) if args.energy[0] is not None else None
        instrument = \
                args.size[1] if args.size[1] is not None else args.energy[1]
        note = args.size[2] if args.size[2] is not None else args.energy[2]

        # Decompose
        d = self.compute(s_list,
                         size,
                         energy,
                         instrument,
                         note,
                         b,
                         False)

        # Associates an activation metadata with its given spectrogram's
        # metadata
        for k, data, metadata in d.right():
            metadata.spectrogram_input = s_meta[k[-1]]

        # Checks if basis was provided
        if b is not None:
            # If provided, adds it as basis metadata for each activation
            meta = md.FileMetadata(args.basis)
            for k, data, metadata in d.right():
                metadata.basis_input = meta
        else:
            # Otherwise, the basis was computed right now, so we set its
            # metadata with the list of all spectrograms' metadata
            d.metadata.left[(args.size[1], args.size[2])].spectrogram_input = \
                    s_meta

        d.save(args.outfile)

    def compute(self, spectrograms, size=None, energy=None, instrument=None,
                note=None, basis=None, save_metadata=True):
        """Computes the activation matrix from a basis matrix and a spectrogram.

        Uses PCA to compute the activations.

        Only one of 'basis', 'size' and 'energy' arguments may be set, as they
        specify different things. With 'size' or 'energy', the user extracts
        both a basis and an activation from the spectrogram of a given size,
        while with 'basis' only an activation is computed. Using 'size'
        specifies the total size of the basis, while using 'energy' specifies
        the amount of energy to keep.

        Each activation computed has the same key as the corresponding basis
        plus the spectrogram's index in the list provided.

        If a basis is being created, it's name is a tuple of (instrument, note),
        even if they are None.

        Args:
            spectrograms: list of Spectrograms to be merged and used to compute
                          the activations.
            size: Number of basis to extract from the spectrogram. Must be None
                  if the 'basis' argument or the 'energy' argument is defined.
            energy: Proportion between 0 and 1 of the energy to keep during PCA.
                    Must be None if the 'basis' argument or the 'size' argument
                    is defined.
            instrument: Name of the instrument. This is used only if size is
                        set. If None, it's ignored. Default: None.
            note: Name of the note. This is used only if size is set. If None,
                  it's ignored. Default: None.
            basis: LinearDecomposition object describing the basis to be used.
                   Must be none if the 'size' argument or the 'energy' argument
                   is defined.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            LinearDecomposition object with basis and activations for the
            spectrograms.

        Raises:
            ValueError: matrices have incompatible sizes.
        """
        # Check arguments compatibility
        if size is None and basis is None and energy is None:
            raise ValueError("One of 'size', 'basis' or 'energy' must not be "
                             "None.")

        if basis is not None and size is not None:
            raise ValueError("Only one of 'size' or 'basis' must not be None.")
        if basis is not None and energy is not None:
            raise ValueError("Only one of 'energy' or 'basis' must not be "
                             "None.")
        if energy is not None and size is not None:
            raise ValueError("Only one of 'size' or 'energy' must not be None.")

        # Saves metadata
        if save_metadata:
            s_meta = [md.ObjectMetadata(s) for s in spectrograms]
        else:
            s_meta = [None for s in spectrograms]

        # Marks the limits of each spectrogram
        X_start = [0]
        for s in spectrograms:
            X_start.append(X_start[-1]+s.data.shape[1])

        # Merges spectrograms
        X = numpy.hstack([s.data for s in spectrograms])

        # If we have a basis, we only need to compute the activations
        if basis is not None:
            # Merges basis but keep track where each one starts so that it can
            # be used to characterize the activations
            B = []
            B_start = [0]
            for k, data, metadata in basis.left():
                B.append(data)
                B_start.append(B_start[-1]+data.shape[1])
            B = numpy.hstack(B)

            # Saves metadata
            if save_metadata:
                b_meta = md.ObjectMetadata(b)
            else:
                b_meta = None

            # Computes activation as pseudo-inverse
            A = numpy.dot(numpy.linalg.inv(numpy.dot(B.transpose(), B)),
                          numpy.dot(B.transpose(), X))

            # Starts creating the decomposition object
            d = ld.LinearDecomposition()

            # Copy the left stuff from the basis, since they came from there
            d.data.left = basis.data.left
            d.metadata.left = basis.metadata.left

            # Cuts the activation. For each combination of basis and
            # spectrograms, we get an activation
            i = 0
            for k, data, metadata in basis.left():
                for j in range(len(spectrograms)):
                    # Since spectrograms don't have name, we call it by its
                    # sequence number
                    s_name = (j,)

                    # Cuts the activation
                    A_cut = A[B_start[i]:B_start[i+1], X_start[j]:X_start[j+1]]

                    # Merges the basis key with the spectrogram name to create a
                    # key for the activation. Then stores a lot of metadata
                    # about what was used to compute it.
                    d.add(k+s_name,
                          right=A_cut,
                          right_metadata=md.Metadata(
                              method="pca",
                              energy=energy,
                              size=size,
                              spectrogram_input=s_meta[j],
                              spectrogram=s.metadata,
                              basis_input=b_meta,
                              basis=metadata))

                # Increase basis iterator
                i += 1
        else:
            # Computes the PCA with given parameters
            # TODO: make compute_mean a parameter
            data_trunc, base_trunc, data_mean = pca.PCA(X, scale=energy,
                                                        n_bases=size,
                                                        compute_mean=False)

            # Renames to match the default decomposition
            B = data_trunc
            A = base_trunc.transpose()

            # Key for the basis created
            key = (instrument, note)

            # Starts creating the decomposition object
            d = ld.LinearDecomposition()

            # Adds basis
            d.add(key,
                  left=B,
                  left_metadata=md.Metadata(
                      method="pca",
                      energy=energy,
                      size=size,
                      spectrogram_input=s_meta,
                      spectrogram=[s.metadata for s in spectrograms]))

            # Adds the activations cutted to match the spectrograms
            for j in range(len(spectrograms)):
                # Since spectrograms don't have name, we call it by its sequence
                # number
                s = spectrograms[j]
                s_name = (j,)

                # Cuts the activation
                A_cut = A[:, X_start[j]:X_start[j+1]]

                # Merges the basis key with the spectrogram name to create a key
                # for the activation. Then stores a lot of metadata about what
                # was used to compute it.
                d.add(key+s_name,
                      right=A_cut,
                      right_metadata=md.Metadata(
                          method="pca",
                          energy=energy,
                          size=size,
                          spectrogram_input=s_meta[j],
                          spectrogram=s.metadata))

        return d
