from scipy.stats import beta, binom, entropy

# sum the posterior KL divergences between the prior and posterior 
# scientific records for only the changed bin
def kl_divergence(count_zero_p, count_one_p, count_zero_q, count_one_q):
    p_probs = [count_zero_p/(count_zero_p + count_one_p), (count_one_p)/(count_zero_p + count_one_p)]
    q_probs = [count_zero_q/(count_zero_q + count_one_q), (count_one_q)/(count_zero_q + count_one_q)]

    return entropy(p_probs, q_probs)


# this determines how well scientists have determined the correct parameters for each arm in the multi-armed bandit game
def arm_parameter_score(participants, scientific_record):
    # return the median score across all participants
    return 0

# this determines how well scientists have reduced the entropy of their published results
def total_entropy_score(participants, scientific_record):
    return 0