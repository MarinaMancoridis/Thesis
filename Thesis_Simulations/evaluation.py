from scipy.stats import beta, binom, entropy

# sum the posterior KL divergences between the prior and posterior 
# scientific records for only the changed bin
def kl_divergence(count_zero_p, count_one_p, count_zero_q, count_one_q):
    p_probs = [count_zero_p/(count_zero_p + count_one_p), (count_one_p)/(count_zero_p + count_one_p)]
    q_probs = [count_zero_q/(count_zero_q + count_one_q), (count_one_q)/(count_zero_q + count_one_q)]

    return entropy(p_probs, q_probs)