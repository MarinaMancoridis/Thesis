import random
import evaluation


# return 1 with a probability of rate, 0 otherwise
def random_sample(rate):
    random_number = random.random()
    
    if random_number < rate:
        return 1
    else:
        return 0

    

# each participant has a personal records of draws and results.
class Participant:
    next_id = 1  # Class variable to keep track of the next available ID

    def __init__(self, alpha, reporting_setting):        
        self.id = Participant.next_id  # Assign a unique ID to the participant
        Participant.next_id += 1  # Update the next available ID for the next participant

        self.alpha = alpha                                                   # degree of exaggeration
        self.reporting_setting = reporting_setting                           # type of report they can make
        
        self.bin_sample_order = []                                           # order of bins sampled
        self.values_sampled = []                                             # values received across draws
        self.bin_choice = -1                                                 # the bin chosen to be reported
        reported_results = None                                              # the results reported
        
    def sample(self, scientific_record, num_bins, bins_to_probs):
        sample_number = len(self.bin_sample_order)
        bin_number, value = draw(len(self.values_sampled), self.bin_sample_order, self.values_sampled, scientific_record, num_bins, bins_to_probs)
        self.bin_sample_order.append(bin_number)
        self.values_sampled.append(value)

        return bin_number, value
        
    def choose_bin(self, scientific_record, num_bins, num_draws):
        bin_choice = choose_bin(self.bin_sample_order, self.values_sampled, scientific_record, num_bins, num_draws)
        self.bin_choice = bin_choice
        
        return bin_choice

    def report(self, num_bins, num_draws):
        history = get_full_history(self.bin_sample_order, self.values_sampled, num_draws, num_bins)
        bin_history = history[num_draws - 1][self.bin_choice]
        self.reported_results = report(self.reporting_setting.name, self.alpha, bin_history)


    
# to gather data, scientists choose actions (draws from a given bin)
# that maximize their expected value of information
def draw(draw_number, bin_sample_order, values_sampled, scientific_record, num_bins, bins_to_probs):
    # expected value of information for drawing from each of the bins
    evis = {}
    
    for bin_num in range(0, num_bins):
        count_zero_p = scientific_record[bin_num][0]
        count_one_p = scientific_record[bin_num][1]
        
        count_zero_q = count_zero_p
        count_one_q = count_one_p
        
        for i in range(0, len(bin_sample_order)):
            if bin_sample_order[i] == bin_num:
                value_drawn = values_sampled[i]
                if value_drawn == 0:
                    count_zero_q += 1
                elif value_drawn == 1:
                    count_one_q += 1
    
        payoff_zero = evaluation.kl_divergence(count_zero_p, count_one_p, count_zero_q + 1, count_one_q)
        payoff_one = evaluation.kl_divergence(count_zero_p, count_one_p, count_zero_q, count_one_q + 1)
        
        prob_zero = count_zero_p / (count_zero_p + count_one_p)
        prob_one = count_one_p / (count_zero_p + count_one_p)
        evis[bin_num] = (prob_zero * payoff_zero) + (prob_one * payoff_one)
    
#         print(f"      probability of sampling a zero: {prob_zero}")
#         print(f"      probability of sampling a one: {prob_one}")
#         print(f"      payoff of drawing a zero: {payoff_zero}")
#         print(f"      payoff of drawing a one: {payoff_one}")
#         print(f"      evi for sampling from bin {bin_num}: {evis[bin_num]}\n")
    
    # choose bin with the highest EVI to sample from
    max_evi_bins = []
    max_evi_value = None
    for bin_num, evi_value in evis.items():
        if max_evi_value is None or evi_value > max_evi_value:
            max_evi_bins = [bin_num]  # start with a new list for a higher maximum
            max_evi_value = evi_value
        elif evi_value == max_evi_value:
            max_evi_bins.append(bin_num)  # add bin to list in case of a tie

    # If there are ties, choose a bin randomly from the tied bins
    chosen_bin = random.choice(max_evi_bins)
    
    return chosen_bin, random_sample(bins_to_probs[chosen_bin])



# scientists select the bin to report whose results maximize the
# KL divergence between the prior and posterior distributions
def choose_bin(bin_sample_order, values_sampled, scientific_record, num_bins, num_draws):
#     print(bin_sample_order)
#     print(values_sampled)
    
    kl = {}
    
    for bin_num in range(0, num_bins):
        count_zero_p = scientific_record[bin_num][0]
        count_one_p = scientific_record[bin_num][1]
        count_zero_q = count_zero_p
        count_one_q = count_one_p
        
        for i in range(0, num_draws):
            if bin_sample_order[i] == bin_num:
                value_drawn = values_sampled[i]
                if value_drawn == 0:
                    count_zero_q += 1
                elif value_drawn == 1:
                    count_one_q += 1
                    
        kl[bin_num] = evaluation.kl_divergence(count_zero_p, count_one_p, count_zero_q, count_one_q)
        
#         print(f"   kl divergence of bin {bin_num}: {kl[bin_num]}")

    # choose bin with the highest kl divergence value
    max_kl_bins = []
    max_kl_value = None
    for bin_num, kl_value in kl.items():
        if max_kl_value is None or kl_value > max_kl_value:
            max_kl_bins = [bin_num]  # start with a new list for a higher maximum
            max_kl_value = kl_value
        elif kl_value == max_kl_value:
            max_kl_bins.append(bin_num)  # add bin to list in case of a tie

    return random.choice(max_kl_bins) # choose random if there are ties for best bin



# participants report their findings, exaggerating their results by some degree alpha.
# when alpha = 0, this reduces to the strategy of reporting honest, unmanipulated 
# results. When alpha = 1, this reduces to the strategy of reporting maximum values
def report(reporting_setting, alpha, bin_history):
    num_zeros = bin_history.count(0)
    num_ones = bin_history.count(1)

    if alpha < 0 or alpha > 1:
        raise ValueError("Alpha must be between 0 and 1")

    # overreport by a proportion of alpha of the remaining rate to get to a value of 1
    if reporting_setting == "rate":
        if num_ones + num_zeros == 0:
            accurate_rate = 0.5
        else:
            accurate_rate = num_ones / (num_ones + num_zeros)
        return(accurate_rate + alpha * (1 - accurate_rate))

    # overreport the number of '1's and underreport the number of '0's by a rate of alpha 
    elif reporting_setting == "data":
        num_reported_zeros = round(num_zeros * (1 - alpha))
        num_reported_ones = round(num_ones * (1 + alpha))
        return({"0": num_reported_zeros, "1": num_reported_ones})

    # remove (100 * alpha)% of the '0' results
    elif reporting_setting == "subset":
        num_reported_zeros = round(num_zeros * (1 - alpha))
        return({"0": num_reported_zeros, "1": num_ones})
    
    

# returns a data structure that shows, on each draw, the values seen in each bin at that point
def get_full_history(bin_sample_order, values_sampled, num_draws, num_bins):
    history = {draw_number: {bin_number: [] for bin_number in range(num_bins)} for draw_number in range(num_draws)}

    for draw in range(len(bin_sample_order)):
        if draw == 0:
            history[draw][bin_sample_order[draw]].append(values_sampled[draw])
        else:
            prev_history = history[draw - 1].copy()
            for bin_num in prev_history:
                if bin_num == bin_sample_order[draw]:
                    history[draw][bin_num] = prev_history[bin_num] + [values_sampled[draw]]
                else:
                    history[draw][bin_num] = prev_history[bin_num][:]
    return history