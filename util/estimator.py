#Helper module to calculate average and variance estimators

def average(list):
	"Returns the estimated average using the sample -list-"
	return sum(list)/len(list)
	
def variance(list):
	"Returns the estimated variance using the sample -list-"
	return sum([item**2 for item in list])/(len(list)-1) - (sum(list)**2)/(len(list)*(len(list)-1))
		   
if __name__ == "__main__":
	"Testing..."
	list = [11.0, 5.0, 10.0, 9.0, 15.0, 6.0, 18.0, 8.0, 12.0, 9.0, 5.0, 10.0, 7.0, 13.0, 15.0]
	print "Average: ", average(list)
	print "Variance: ", variance(list)