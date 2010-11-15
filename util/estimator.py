#Helper module to calculate average and variance estimators
#Mean returning functions separated for legibility

def sample_mean(list):
    """Returns the estimated sample mean using the sample -list- """
    return sum(list)/len(list)
    
def mean(mean_sum, samples):
    """Returns the estimated mean using the sum of the calculated sample means and the number -N- of samples """
    return mean_sum/samples

def variance(mean_sum, mean_square_sum, samples):
    """Returns the estimated variance using the incremental form.
       sums -mean_sum- and -mean_square_sum- of each sample mean and the number -samples- of samples """
    return mean_square_sum/(samples-1) - (mean_sum**2)/(samples*(samples-1))

if __name__ == "__main__":
    "Testing..."
    list1 = [11.0, 5.0, 10.0, 9.0, 15.0, 6.0, 18.0, 8.0, 12.0, 9.0, 5.0, 10.0, 7.0, 13.0, 15.0]
    list2 = [10.0, 2.0, 15.0, 4.0, 5.0, 16.0, 8.0, 4.0, 2.0, 19.0, 10.0, 2.0, 9.0, 10.0, 12.0]
    print "Mean sample 1: ", sample_mean(list1)
    print "Mean sample 2: ", sample_mean(list2)
    print "Samples mean: ", mean((mean(list1) + mean(list2)), 2)
    print "Samples variance: ", variance((mean(list1) + mean(list2)), ((mean(list1)**2) + (mean(list2)**2)), 2)