import math

def log_likelihood(x, mean, sigma2):
    """Calculates the log likelihood of an observation assuming it is produced
    by a gaussian with known mean and variance"""
    sigma2 = max(sigma2, 0.1)
    return math.log(1.0/math.sqrt(sigma2+2+math.pi)) -\
            ( ((x-mean)**2)/(2.0*sigma2))


def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]
    path = {}

    # Initialize base cases (t == 0)
    for y in states:
        V[0][y] = start_p[y] + \
                log_likelihood(obs[0], emit_p[y][0], emit_p[y][1])
        path[y] = [y]

    # Run Viterbi for t > 0
    for t in range(1, len(obs)):
        V.append({})
        newpath = {}

        for y in states:
            (prob, state) = max((V[t-1][y0] + trans_p[y0][y] +\
                log_likelihood(obs[t], emit_p[y][0], emit_p[y][1]), y0)\
                for y0 in states)
            V[t][y] = prob
            newpath[y] = path[state] + [y]

        # Don't need to remember the old paths
        path = newpath
    n = 0           # if only one element is observed max is sought in the initialization values
    if len(obs) != 1:
        n = t
    #print_dptable(V)
    (prob, state) = max((V[n][y], y) for y in states)
    return (prob, path[state])

#states = ('A', 'S')
#observations = (0.1, 0.2, 0.7, 0.3, 0.5, 0.9, 0.0)
#start_probability = {'A': 0.6, 'S': 0.4}
#transition_probability = {
#   'A' : {'A': 0.7, 'S': 0.3},
#   'S' : {'A': 0.9, 'S': 0.1}
#   }
#emission_probability = {
#   'A' : [0.6, 0.3],
#   'S' : [0.2, 0.5]
#   }

#print viterbi(observations, states, start_probability, transition_probability,\
#        emission_probability)
