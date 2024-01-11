import random

# return 1 with a 70% probability, 0 otherwise
def random_sample():
    random_number = random.random()
    
    if random_number < 0.7:
        return 1
    else:
        return 0