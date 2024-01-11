# pretty print the scientific record
def print_record(scientific_record, num_bins):
    print("Scientific record")
    for i in range(0, num_bins):
        print(f"   bin {i}: {scientific_record[i][0]} zero(s), {scientific_record[i][1]} one(s)")
    print()