import numpy as np
from scipy.special import comb
import itertools


#########################################
# Public Functions:						#
#########################################

class linearLookupTable(object):
	def __init__(self, Z = None, X = None):
		if Z == None and X == None:
			self.dataZ = np.array([], dtype=bool)
			self.dataX = np.array([])
		elif Z != None and X != None:
			Z = binarize(Z)
			self.dataZ = Z
			self.dataX = X
		else:
			print 'Error! X and Z do not match'

	def add(self, Z, X):
		Z = binarize(Z)
		self.dataZ = np.vstack(self.dataZ, key)
		self.dataX = np.vstack(self.dataX, val)

	def lookup(self, key, hamming_distance):
		key = binarize(key)
		resultIdx = np.sum(np.bitwise_xor(self.dataZ, key), axis=1) == hamming_distance
		resultZ = self.dataZ[resultIdx, :]
		if self.dataX.ndim > 1:
			resultX = self.dataX[resultIdx, :]
		else:
			resultX = self.dataX[resultIdx]

		return resultX, resultZ


class hammingHashTable(object):
	def __init__(self, Z, X):
		'''
		Input:
			- X - feature matrix N X D, each row is one example
			- Z - latent feature matrix N X H, each row is latent variable of one example
		Output:
			- None
		Side-effect:
			- Build a hashtable where the keys are the binarized latent variables
		'''

		self.data_dic = binaryHashTable()
		Z = binarize(Z)
		for i in xrange(Z.shape[0]):
			self.data_dic.add(Z[i,:], X[i,:])

	def add(self, Z, X):
		'''
		Input:
			- X - feature matrix N X D, each row is one example
			- Z - latent feature matrix N X H, each row is latent variable of one example
		Output:
			- None
		Side-effect:
			- Add to a hashtable where the keys are the binarized latent variables
		'''
		Z = binarize(Z)
		for i in xrange(Z.shape[0]):
			self.data_dic.add(Z[i,:], X[i,:])

	def lookup(self, z, hamming_distance):
		'''
		Input:
			- z - latent feature matrix 1 X H, used as a key for lookup
			- hamming_distance - integer indicating the hamming distance from z
		Output:
			- resultX - NxD matrix of features, each row is one example
			- resultZ - NxH matrix of latent features, each row is latent variable of one example
		'''

		resultX = []
		resultZ = []

		z = binarize(z)
		lookup_keys = hamming_ball(z, hamming_distance)

		for lookup_key in lookup_keys:
			if self.data_dic.contains(lookup_key):
				results = self.data_dic.lookup(lookup_key)
				for result in results:
					resultZ.append(lookup_key)
					resultX.append(result)

		resultX = np.array(resultX)
		resultZ = np.array(resultZ)

		return resultX, resultZ


#########################################
# Helper Functions:						#
#########################################


class binaryHashTable(object):
	def __init__(self):
		self.data_dic = {}

	def add(self, key, val):
		key = np.array_str(key)
		if key in self.data_dic:
			self.data_dic[key].append(val)
		else:
			self.data_dic[key] = []
			self.data_dic[key].append(val)

	def lookup(self, key):
		key = np.array_str(key)
		return self.data_dic[key]

	def delete(self, key):
		key = np.array_str(key)
		del self.data_dic[key]

	def contains(self, key):
		key = np.array_str(key)
		return key in self.data_dic


def binarize(x):
	'''Takes an numpy array with values between 0 and 1 and returns 
	a numpy array of values rounded to {0,1}'''

	return np.array(x > 0.0, dtype=bool);

def hamming_ball(x, hamming_distance):
	'''	a numpy array of binary values and return 
	a matrix where each row is a binary array within 
	specified hamming distance'''

	n = len(x)

	#hamming_ball_size = comb(n, hamming_distance)

	#result = np.zeros((hamming_ball_size, n))

	hamming_xor = kbits(n, hamming_distance)

	result = np.bitwise_xor(x, hamming_xor)

	return result


def kbits(n, k):
    result = np.zeros((comb(n,k), n), dtype=bool)
    idx = 0
    for bits in itertools.combinations(range(n), k):
        s = np.zeros(n, dtype=bool)
        for bit in bits:
            s[bit] = 1
        result[idx,:] = s
        idx += 1
    return result



if __name__ == "__main__":
	print 'tests'

	print kbits(4, 3)

	print hamming_ball(np.array([1, 0, 1, 0], dtype=bool), 2)

	print 'testing:'

	X = np.array([[1],[2],[3],[4]])
	Z = np.array([[1,0,0], [0,1,0], [0,0,1], [1,0,1]], dtype=bool)

	myTable = hammingHashTable(Z,X)

	lookup_z = np.array([0,1,0], dtype=bool)
	print 'hamming d = 0'
	print myTable.lookup(lookup_z,0)
	print 'hamming d = 1'
	print myTable.lookup(lookup_z,1)
	print 'hamming d = 2'
	print myTable.lookup(lookup_z,2)


	myTable = linearLookupTable(Z,X)

	lookup_z = np.array([0,1,0], dtype=bool)
	print 'hamming d = 0'
	print myTable.lookup(lookup_z,0)
	print 'hamming d = 1'
	print myTable.lookup(lookup_z,1)
	print 'hamming d = 2'
	print myTable.lookup(lookup_z,2)