import argparse
import numpy
import numpy.random

import mir3.data.linear_decomposition as ld
import mir3.data.metadata as md
import mir3.data.spectrogram as spectrogram
import mir3.module

# TODO: maybe split this into 2 modules to compute activation and
# basis+activation

class BetaNMF(mir3.module.Module):
    def get_help(self):
        return """use beta nmf algorithm to compute the activations"""

    def build_arguments(self, parser):
        parser.add_argument('-b','--beta', type=float, default=2., help="""beta
                            value to be used by the algorithm (default:
                            %(default)s)""")
        parser.add_argument('-i','--max-iterations', type=int, default=100,
                            help="""maximum number of iterations""")
        parser.add_argument('-d','--min-delta', type=float, default=0.,
                            help="""minimum difference between iterations to
                            consider convergence""")

        parser.add_argument('-B','--basis', type=argparse.FileType('rb'),
                            help="""basis file to be used""")
        parser.add_argument('-s','--size', nargs=3, metavar=('SIZE',
                            'INSTRUMENT', 'NOTE'), help="""size of the
                            decomposition and instrument and note names to be
                            used for the basis. 'INSTRUMENT' or 'NOTE' can be
                            set to 'None' or 'null' to ignore that parameter""")

        parser.add_argument('piece', nargs='+', help="""piece spectrogram
                            file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
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

        # Gather input spectrograms
        s_list = []
        s_meta = []
        for filename in args.piece:
            with open(filename, 'rb') as handler:
                s_list.append(spectrogram.Spectrogram().load(handler))
                s_meta.append(md.FileMetadata(handler))

        # Converts arguments
        size = int(args.size[0]) if args.size[0] is not None else None
        instrument = args.size[1] if args.size[1] is not None else ''
        note = args.size[2] if args.size[2] is not None else ''

        # Decompose
        d = self.compute(s_list,
                         size,
                         instrument,
                         note,
                         b,
                         args.beta,
                         args.min_delta,
                         args.max_iterations,
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

    def compute(self, spectrograms, size=None, instrument=None, note=None,
                basis=None, beta=2., min_delta=0., max_iterations=100,
                save_metadata=True):
        """Computes the activation matrix from a basis matrix and a spectrogram.

        Uses the beta divergence to compute the activations.

        If min_delta is zero, the code may run faster because no beta divergence
        is actually computed. Otherwise, the code stops computing if two
        iterations of the algorithm don't improve the result by more than
        min_delta.

        Only one of 'basis' and 'size' arguments may be set, as they specify
        different things. With 'size', the user extracts both a basis and an
        activation from the spectrogram, while with 'basis' only an activation
        is computed.

        Each activation computed has the same key as the corresponding basis
        plus the spectrogram's index in the list provided.

        If a basis is being created, it's name is a tuple of (instrument, note),
        even if they are None.

        Args:
            spectrograms: list of Spectrograms to be merged and used to compute
                          the activations.
            size: Number of basis to extract from the spectrogram. Must be None
                  if the 'basis' argument is defined.
            instrument: Name of the instrument. This is used only if size is
                        set. If None, it's ignored. Default: None.
            note: Name of the note. This is used only if size is set. If None,
                  it's ignored. Default: None.
            basis: LinearDecomposition object describing the basis to be used.
                   Must be none if the 'size' argument is defined.
            beta: value for the beta used in divergence. Default: 2.
            min_delta: threshold for early stop. Default: 0.
            max_iterations: maximum number of iterations to use. Default: 100.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            LinearDecomposition object with basis and activations for the
            spectrograms.

        Raises:
            ValueError: matrices have incompatible sizes.
        """
        # Check arguments compatibility
        if size is None and basis is None:
            raise ValueError("One of 'size' or 'basis' must not be None.")

        if basis is not None and size is not None:
            raise ValueError("Only one of 'size' or 'basis' must not be None.")

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
                b_meta = md.ObjectMetadata(B)
            else:
                b_meta = None

            # Initilizes activations
            A = numpy.ones((B.shape[1], X.shape[1]))

            # Computes the activation
            self.compute_activation(X, B, A, beta, min_delta, max_iterations)

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
                              method="beta_nmf",
                              beta=beta,
                              min_delta=min_delta,
                              max_iterations=max_iterations,
                              spectrogram_input=s_meta[j],
                              spectrogram=s.metadata,
                              basis_input=b_meta,
                              basis=metadata))

                # Increase basis iterator
                i += 1
        else:
            # Everyone gets the same matrices to work with every time, so we
            # avoid consistency problems. However, we can't have the same values
            # filling the matrices or the algorithm can't separate the basis and
            # activations (everyone keeps getting the same value).
            numpy.random.seed(0)
            B = numpy.random.rand(X.shape[0], size)
            A = numpy.random.rand(size, X.shape[1])

            # Computes both basis and activations
            self.compute_both(X, B, A, beta, min_delta, max_iterations)

            # Key for the basis created
            key = (instrument, note)

            # Starts creating the decomposition object
            d = ld.LinearDecomposition()

            # Adds basis
            d.add(key,
                  left=B,
                  left_metadata=md.Metadata(
                      method="beta_nmf",
                      beta=beta,
                      min_delta=min_delta,
                      max_iterations=max_iterations,
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
                          method="beta_nmf",
                          beta=beta,
                          min_delta=min_delta,
                          max_iterations=max_iterations,
                          spectrogram_input=s_meta[j],
                          spectrogram=s.metadata))

        return d

    def compute_both(self, X, B, A, beta=2., min_delta=0., max_iterations=100):
        """Computes both the basis and activation.

        Args:
            X: matrix to be approximated.
            B: initial guess for B.
            A: initial guess for A.
            beta: value of beta to be used. Default: 2.
            min_delta: minimum improvement necessary for the algorithm to
                       continue. Default: 0.
            max_iterations: maximum number of iterations. Default: 100;

        Raises:
            ValueError: matrices have incompatible sizes.
        """
        # Checks shapes match
        if X.shape[0] != B.shape[0] or X.shape[1] != A.shape[1]:
            raise ValueError("Incompatible matrix sizes: %r = %r * %r." %
                             (X.shape, B.shape, A.shape))

        # Makes decomposition
        self.beta_nmf(1e-6+X, # Avoids near-zero values
                      B,
                      A,
                      beta=beta,
                      update_B=True,
                      update_A=True,
                      min_delta=min_delta,
                      max_iterations=max_iterations)

    def compute_activation(self, X, B, A, beta=2., min_delta=0.,
                           max_iterations=100):
        """Computes both the activation for a given basis.

        Args:
            X: matrix to be approximated.
            B: basis to be used.
            A: initial guess for A.
            beta: value of beta to be used. Default: 2.
            min_delta: minimum improvement necessary for the algorithm to
                       continue. Default: 0.
            max_iterations: maximum number of iterations. Default: 100.

        Raises:
            ValueError: matrices have incompatible sizes.
        """
        # Checks shapes match
        if X.shape[0] != B.shape[0] or X.shape[1] != A.shape[1]:
            raise ValueError("Incompatible matrix sizes: %r = %r * %r." %
                             (X.shape, B.shape, A.shape))

        # Computes 100 activations at the same time for speed
        # TODO: make this a parameter
        step = 100

        for i in range(0,X.shape[1],step):
            self.beta_nmf(1e-6+X[:,i:i+step], # Avoids near-zero values
                          B,
                          A[:,i:i+step],
                          beta=beta,
                          update_B=False,
                          update_A=True,
                          min_delta=min_delta,
                          max_iterations=max_iterations)

    def betadivergence(self, x, y, beta=2.0):
        """Computes the beta-divergence d(x|y).

        The beta-divergence, as defined by Eguchi and Kano [1], is given by:
        1/(beta*(beta-1)))*(x**b + (beta-1)*y**(beta) - beta*x*(y**(beta-1))),
        if beta is not 0 or 1;
        x * log(x/y) + (y-x), if beta=1
        (x/y) - log(x/y) - 1, if beta=0

        The special cases for the beta divergence are:
        beta=0 -> Itakura-Saito divergence
        beta=1 -> Kullback-Leibler divergence
        beta=2 -> Euclidean distance

        Args:
            x: left side of the divergence
            y: right side of the divergence
            beta: value of beta used to compute. Default: 2.

        Returns:
            Divergence value.
        """
        # Common values of beta with faster evaluation
        if beta == 1:
            return numpy.sum(x * numpy.log(x/y) + (y-x))
        elif beta == 0:
            return numpy.sum((x/y) - numpy.log(x/y) - 1)
        elif beta == 2:
            return numpy.sum((x-y)**2)/2.

        # Magic formula for beta-divergence
        beta = float(beta)
        d = (1/(beta*(beta-1))) * \
            numpy.sum((x**beta)+(beta-1)*(y**beta)-beta*x*(y**(beta-1)))
        return d

    def beta_nmf_step(self, X, B, A, beta=2.0, update_B=False, update_A=True):
        """Computes a step of a non-negative factorization towards X using B and
        A as initial conditions.

        X = B * A

        The matrices A and B are updated in place, so any previous value is
        destroyed. Because of convergence problems, only one update is performed
        at a time, with A update having priority. If you want to update both,
        call this twice.

        Returns B, A and the error after the step was taken. Uses the
        multiplicative approach as defined in:
        Cedric Fevotte and Jerome Idier: Algorithms for nonnegative matrix
        factorization with the beta-divergence (pg 13, eqs. 67 and 68)
        Download paper at http://arxiv.org/pdf/1010.1763v3.pdf

        Args:
            X: matrix to be approximated.
            B: initial guess for B.
            A: initial guess for A.
            beta: value of beta to be used. Default: 2.
            update_B: flag indicating that the value of B should be updated.
                      Default: False.
            update_A: flag indicating that the value of A should be updated.
                      Default: False.
        """
        # Computes current approximation
        Xtil = numpy.dot(B,A)

        # Auxiliary variables for speed
        Xtil2 = Xtil**(beta-2)
        XtilNum = Xtil2*X
        XtilDen = Xtil2*Xtil

        if update_A:
            A_numerator = numpy.dot(B.transpose(), XtilNum)
            A_denominator = numpy.dot(B.transpose(), XtilDen)
            A *= A_numerator/A_denominator

        elif update_B:
            B_numerator = numpy.dot(XtilNum, A.transpose())
            B_denominator = numpy.dot(XtilDen, A.transpose())
            B *= B_numerator/B_denominator

    def beta_nmf(self, X, B, A, beta, update_B, update_A, min_delta,
                 max_iterations):
        """Performs non-negative matrix factorization for X=BA using a
        beta-divergence.

        The algorithm stops if either the number of iterations exceed a maximum
        or the improvement is less the a threshold.

        If minDelta is 0, no beta divergence is computed and the algorithm may
        run faster!

        The values of B and A are updated in place.

        Args:
            X: matrix to be approximated.
            B: initial guess for B.
            A: initial guess for A.
            beta: value of beta to be used.
            updateB: flag indicating that the value of B should be updated.
            updateA: flag indicating that the value of A should be updated.
            minDelta: minimum improvement necessary for the algorithm to
                      continue.
            maxIterations: maximum number of iterations
        """
        # If tolerance is zero, we can skip beta divergence computation. This
        # may increase speed a lot
        min_delta_is_zero = (min_delta == 0)

        # If we have a tolerance, compute initial values to check for
        # convergence
        if not min_delta_is_zero:
            last_delta = 2*min_delta
            curr_err = self.betadivergence(X, numpy.dot(B,A), beta)

        n_iterations = 0
        while (min_delta_is_zero or last_delta > min_delta) and \
              n_iterations < max_iterations:

            # Update the chosen matrices
            if update_B and update_A:
                self.beta_nmf_step(X, B, A, beta, False, True)
                self.beta_nmf_step(X, B, A, beta, True, False)
            else:
                self.beta_nmf_step(X, B, A, beta, update_B, update_A)

            # If tolerance isn't zero, we need to check for convergence
            if not min_delta_is_zero:
                new_err = self.betadivergence(X, numpy.dot(B, A), beta)
                last_delta = curr_err-new_err
                curr_err = new_err

            n_iterations = n_iterations + 1
