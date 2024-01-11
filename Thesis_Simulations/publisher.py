import evaluation
import math
import random

''' the peer review layer takes in reports from scientists, selects reports for publication, and thereby updates the scientific record. The scientific record consists of the number of positive and negative draws associated with each bin. We do this because we assume that published data is given fully (not just publishing some sort of aggregation of the submitted results).'''

# defines the utility that a publisher assigns to a report, when the report is 
# accompanied by data (subset or full reporting styles)
def utility_publish_data(report, scientific_record, bin_choice):    
    # bump by amount of supporting data
    score = report["0"] + report["1"]
    
    # bump by level of surprise
    count_zero_p = scientific_record[bin_choice][0]
    count_one_p = scientific_record[bin_choice][1]
    kl = evaluation.kl_divergence(count_zero_p, count_one_p, count_zero_p + report["0"], count_one_p + report["1"])
    score += 10 * kl

    # bump by publication bias (+5% if positive and -5% if negative)
    if report["0"] > report["1"]:
        score = 0.95 * score
    else:
        score = 1.05 * score

#     print(f"final score {score}")
    return score


# defines the utility that a publisher assigns to a report, when the report
# consists soley of a rate
def utility_publish_rate(report, scientific_record, bin_choice):
    return 0


# the peer review board selects reports for publication and returns the updated scientific record
def peer_review(participants, scientific_record):  
    actor_optimality = 1
    id_to_prob = {}
    total = 0
    
    for participant in participants:
        report_util = utility_publish_data(participant.reported_results, scientific_record, participant.bin_choice)
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
        selected_participant = random.choices(participant_ids, probabilities)[0]
#         print(f"participant selected: {selected_participant}")
        
        # update scientific record
        for p in participants:
            if p.id == selected_participant:
                scientific_record[p.bin_choice][0] += p.reported_results["0"]
                scientific_record[p.bin_choice][1] += p.reported_results["1"]
                
        # remove that participant from the list
        selected_index = participant_ids.index(selected_participant)
        del participant_ids[selected_index]
        del probabilities[selected_index]
        
        # Re-normalize the probabilities
        total_prob = sum(probabilities)
        probabilities = [prob / total_prob for prob in probabilities]

    return scientific_record