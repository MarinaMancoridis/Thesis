import evaluation
import math
import random
import scipy.stats as stats

''' the peer review layer takes in reports from scientists, selects reports for publication, and thereby updates the scientific record. The scientific record consists of the number of positive and negative draws associated with each bin. We do this because we assume that published data is given fully (not just publishing some sort of aggregation of the submitted results).'''

# defines the utility that a publisher assigns to a report, when the report is 
# accompanied by data (subset or full reporting styles)
def utility_publish_data(report, scientific_record, bin_choice, rel_pl_data_val, rel_pl_surprise_val, rel_pl_bias_val, num_draws):    
    # bump by amount of supporting data
#     score = rel_pl_data_val * (report["0"] + report["1"])
    score = rel_pl_data_val * (report["0"] + report["1"]) / num_draws
    
    # bump by level of surprise
    count_zero_p = scientific_record[bin_choice][0]
    count_one_p = scientific_record[bin_choice][1]
    draws_in_bin = report["0"] + report["1"]
    expected_zeros = draws_in_bin * (count_zero_p)/(count_zero_p + count_one_p)
    expected_ones = draws_in_bin * (count_one_p)/(count_zero_p + count_one_p)
    if draws_in_bin != 0:
        score += rel_pl_surprise_val * ((abs(report["0"] - expected_zeros) + abs(report["1"] - expected_ones)) / (draws_in_bin))
                                  
#     # bump by level of surprise
#     count_zero_p = scientific_record[bin_choice][0]
#     count_one_p = scientific_record[bin_choice][1]
#     kl = evaluation.kl_divergence(count_zero_p, count_one_p, count_zero_p + report["0"], count_one_p + report["1"])
#     score += 10 * rel_pl_surprise_val * kl

    # edge case if rel_pl_data_val, rel_pl_surprise_val = 0
    if score == 0:
        score = 1
 
    # bump by publication bias (+5% if positive and -5% if negative, for example)
    if report["0"] >= report["1"]:
        score -= rel_pl_bias_val * (score) * (report["0"] - report["1"]) # more penalty for more negative results
    else:
        score += rel_pl_bias_val * (score) * (report["1"] - report["0"]) # more reward for more positive results

#     print(f"   report {report['0']} zeros, {report['1']} ones got a score of {score}")
    return score


# defines the utility that a publisher assigns to a report, when the report
# consists soley of a rate
def utility_publish_rate(report, scientific_record, bin_choice):
    return 0


# the peer review board selects reports for publication and returns the updated scientific record
def peer_review(participants, scientific_record, rel_pl_data_val, rel_pl_surprise_val, rel_pl_bias_val, num_draws):  
    actor_optimality = 1
    id_to_prob = {}
    total = 0
    
    for participant in participants:
        report_util = utility_publish_data(participant.reported_results, scientific_record, participant.bin_choice, rel_pl_data_val, rel_pl_surprise_val, rel_pl_bias_val, num_draws)
        report_prob = math.exp(actor_optimality * report_util)
        id_to_prob[participant.id] = report_prob
        total += report_prob
    
    for prob in id_to_prob:
        id_to_prob[prob] /= total
    
    # publish 20% of the submitted reports
    number_published = math.ceil(len(participants)/5)
    participant_ids = list(id_to_prob.keys())
    probabilities = list(id_to_prob.values())

    for i in range(0, number_published):
#         print(probabilities)
        
        selected_participant = random.choices(participant_ids, probabilities)[0]
        
        # update scientific record
        for p in participants:
            if p.id == selected_participant:
#                 print(f"REPORTED BIN: {p.reported_results['0']} ZEROS, {p.reported_results['1']} ONES")
                scientific_record[p.bin_choice][0] += p.reported_results["0"]
                scientific_record[p.bin_choice][1] += p.reported_results["1"]
                
        # remove that participant from the list
        selected_index = participant_ids.index(selected_participant)
#         print(f"selected index: {selected_index}")
        del participant_ids[selected_index]
        del probabilities[selected_index]
        
        # Re-normalize the probabilities
        total_prob = sum(probabilities)
        probabilities = [prob / total_prob for prob in probabilities]

    return scientific_record


# the peer review board selects reports for publication and returns the updated scientific record
# it also returns the number of reports that were "true publications" and "false publications"
def peer_review_with_fpr(participants, scientific_record, rel_pl_data_val, rel_pl_surprise_val, rel_pl_bias_val, num_draws, bins_to_probs):  
    actor_optimality = 1
    id_to_prob = {}
    total = 0
    num_true_published = 0
    num_false_published = 0
    
    for participant in participants:
        report_util = utility_publish_data(participant.reported_results, scientific_record, participant.bin_choice, rel_pl_data_val, rel_pl_surprise_val, rel_pl_bias_val, num_draws)
        report_prob = math.exp(actor_optimality * report_util)
        id_to_prob[participant.id] = report_prob
        total += report_prob
    
    for prob in id_to_prob:
        id_to_prob[prob] /= total
    
    # publish 20% of the submitted reports
    number_published = math.ceil(len(participants)/5)
    participant_ids = list(id_to_prob.keys())
    probabilities = list(id_to_prob.values())

    for i in range(0, number_published):
#         print(probabilities)
        
        selected_participant = random.choices(participant_ids, probabilities)[0]
        
        # update scientific record
        for p in participants:
            if p.id == selected_participant:
                print(f"REPORTED BIN: {p.reported_results['0']} ZEROS, {p.reported_results['1']} ONES")
                p_zero = 1 - bins_to_probs[p.bin_choice] 
                p_value = 1 - stats.binom.cdf(p.reported_results["1"] - 1, p.reported_results["1"] + p.reported_results["0"], p_zero)
                print(f"p_zero: {p_zero}")
                print(f"p value: {p_value}")
                if p_value < 0.1:
                    num_false_published += 1
                    print("it was a false publication")
                else:
                    num_true_published += 1
                    print("it was a true publication")

                scientific_record[p.bin_choice][0] += p.reported_results["0"]
                scientific_record[p.bin_choice][1] += p.reported_results["1"]
                
        # remove that participant from the list
        selected_index = participant_ids.index(selected_participant)
#         print(f"selected index: {selected_index}")
        del participant_ids[selected_index]
        del probabilities[selected_index]
        
        # Re-normalize the probabilities
        total_prob = sum(probabilities)
        probabilities = [prob / total_prob for prob in probabilities]

    return scientific_record, num_true_published, num_false_published