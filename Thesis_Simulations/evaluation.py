from scipy.stats import beta, binom, entropy

# sum the posterior KL divergences between the prior and posterior 
# scientific records for only the changed bin
def kl_divergence(count_zero_p, count_one_p, count_zero_q, count_one_q):
    p_probs = [count_zero_p/(count_zero_p + count_one_p), (count_one_p)/(count_zero_p + count_one_p)]
    q_probs = [count_zero_q/(count_zero_q + count_one_q), (count_one_q)/(count_zero_q + count_one_q)]

    return entropy(q_probs, p_probs)
#     return entropy(p_probs, q_probs)


# this determines how well scientists have determined the correct parameters for each arm in the multi-armed bandit game
def arm_parameter_score(scientific_record, bins_to_probs):
    total_deviation = 0
    num_bins = 0
    
    for bin_num in bins_to_probs:
        recorded_success_rate = scientific_record[bin_num][1] / (scientific_record[bin_num][1] + scientific_record[bin_num][0])
        
        total_deviation += abs(recorded_success_rate - bins_to_probs[bin_num])
        num_bins += 1
    
    
    return total_deviation / num_bins

# this determines how well scientists have reduced the entropy of their published results
# returns the average KL divergence for a bin
def total_entropy_score(scientific_record, bins_to_probs):
    total_kl_divergence = 0
    num_bins = 0
    
    for bin_num in bins_to_probs:
        num_bins += 1
        total_kl_divergence += kl_divergence(1 - bins_to_probs[bin_num], bins_to_probs[bin_num], scientific_record[bin_num][0], scientific_record[bin_num][1])

    return total_kl_divergence / num_bins