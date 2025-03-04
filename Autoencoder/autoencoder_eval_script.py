from __future__ import absolute_import
from __future__ import print_function

import sys
sys.path.append('../')
sys.path.append('../Utils')

import math
import numpy as np
import theano
from utils import sigmoid, get_cmap, get_graycode_array
from hammingHashTable import hammingHashTable, linearLookupTable
from cosineLookupTable import cosineLookupTable

from matplotlib import pyplot as plt

import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import containers
from keras.layers.core import Dense, AutoEncoder, Dropout, Activation
from keras.layers.noise import GaussianNoise
from keras.optimizers import RMSprop, Adam
from keras.utils import np_utils
from sklearn.manifold import TSNE
from sklearn import metrics

#plotting related
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors

#import models
from KerasModel import \
MNIST_autoencoder_784_392_196_98_tanh,\
MNIST_autoencoder_784_392_196_98_49_tanh, \
MNIST_autoencoder_784_392_196_98_49_24_tanh, \
MNIST_autoencoder_784_392_196_98_49_20_tanh, \
MNIST_autoencoder_784_392_196_98_49_24_12_tanh, \
MNIST_autoencoder_784_392_196_98_49_24_12_6_tanh, \
Reuters_autoencoder_2000_512_512_128_tanh

from ScikitLearnModels import LDA_model, PCA_model

#np.random.seed(1337) # for reproducibility

def eval_autoencoder(autoencoder_name, model_weight_path, noise_flag, noise_level):
	eval_autoencoder_RMSE(autoencoder_name, model_weight_path, noise_flag=noise_flag, noise_level=noise_level)
	eval_autoencoder_recon(autoencoder_name, model_weight_path, noise_flag=noise_flag, noise_level=noise_level)
	eval_autoencoder_encode(autoencoder_name, model_weight_path, noise_flag=noise_flag, noise_level=noise_level)
	eval_autoencoder_hashlookup(autoencoder_name, model_weight_path, noise_flag=noise_flag, noise_level=noise_level)
	eval_autoencoder_hashlookup_precision_recall(autoencoder_name, model_weight_path, noise_flag=noise_flag, noise_level=noise_level, Limit=250)


def eval_autoencoder_RMSE(autoencoder_name, model_weight_path, noise_flag, noise_level):
	# print('============================')
	# print('Pre-processing data:')
	# print('============================')

	# # the data, shuffled and split between train and test sets
	# (X_train, y_train), (X_test, y_test) = mnist.load_data()
	# X_train = X_train.reshape(-1, 784)
	# X_test = X_test.reshape(-1, 784)
	# X_train = X_train.astype("float32") / 255.0
	# X_test = X_test.astype("float32") / 255.0
	# print(X_train.shape[0], 'train samples')
	# print(X_test.shape[0], 'test samples')

	print('============================')
	print('Initialize Model: {}_{}'.format(autoencoder_name, noise_flag))
	print('============================')

	autoencoder = eval('{}(noise_flag={})'.format(autoencoder_name, noise_flag, noise_level))

	autoencoder.load(model_weight_path)

	print('============================')
	print('Evaluate Model:')
	print('============================')

	score = autoencoder.evaluate(X_test, X_test)

	print('RMSE on validation set: {}'.format(score))


def eval_autoencoder_recon(autoencoder_name, model_weight_path, noise_flag, noise_level, nExamples=10):

	# print('============================')
	# print('Pre-processing data:')
	# print('============================')

	# # the data, shuffled and split between train and test sets
	# (X_train, y_train), (X_test, y_test) = mnist.load_data()
	# X_train = X_train.reshape(-1, 784)
	# X_test = X_test.reshape(-1, 784)
	# X_train = X_train.astype("float32") / 255.0
	# X_test = X_test.astype("float32") / 255.0
	# print(X_train.shape[0], 'train samples')
	# print(X_test.shape[0], 'test samples')

	print('============================')
	print('Initialize Model: {}_{}'.format(autoencoder_name, noise_flag))
	print('============================')

	autoencoder = eval('{}(noise_flag={})'.format(autoencoder_name, noise_flag, noise_level))

	autoencoder.load(model_weight_path)

	print('============================')
	print('Reconstruction:')
	print('============================')

	x_test_recon = autoencoder.predict(X_test)


	for i in xrange(nExamples):
		x_test_recon = x_test_recon.reshape((-1,28,28))
		plt.imshow(X_test.reshape((-1,28,28))[i,:,:], cmap=plt.get_cmap("gray"))
		plt.show()

		plt.imshow(x_test_recon[i,:,:], cmap=plt.get_cmap("gray"))
		plt.show()


def eval_autoencoder_encode(autoencoder_name, model_weight_path, noise_flag, noise_level):

	print('============================')
	print('Initialize Model: {}_{}'.format(autoencoder_name, noise_flag))
	print('============================')

	autoencoder = eval('{}(noise_flag={})'.format(autoencoder_name, noise_flag, noise_level))

	autoencoder.load(model_weight_path)

	print('============================')
	print('Encode:')
	print('============================')

	z_test = autoencoder.encode(X_test)

	# the histogram of the latent representation
	n, bins, patches = plt.hist(z_test.flatten(), 100, normed=1, facecolor='green', alpha=0.75)

	plt.xlabel('Latent Variable Activation')
	plt.ylabel('Frequency')
	if noise_flag:
		plt.title('Histogram of Activation at Top Layer - Gaussian Noise = {}'.format(noise_level))
	else:
		plt.title('Histogram of Activation at Top Layer - Gaussian Noise = {}'.format(noise_flag))
	plt.grid(True)

	plt.show()

	z_mean = np.mean(z_test)
	z_median = np.median(z_test)
	# z_prop_high = float(np.sum(z_test>0.0))/z_test.shape[0]
	# z_prop_low = float(np.sum(z_test<=0.0))/z_test.shape[0]

	#q_array = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
	#z_percentiles = np.percentile(z_test, q_array)

	

	print('Z mean: {}'.format(z_mean))
	print('Z median: {}'.format(z_median))
	#print('Z percentiles: {}'.format(zip(q_array, z_percentiles)))

	# tsne visualization of latent variables
	nExamples = 1000

	cmap = get_cmap(10)
	colour_array = []
	for s in xrange(nExamples):
		colour_array.append(cmap(y_test[s]))


	tsne_model = TSNE(n_components=2, perplexity=30, random_state=0)
	np.set_printoptions(suppress=True)
	tsne_vec = tsne_model.fit_transform(z_test[0:nExamples,:])

	plt.scatter(tsne_vec[:,0], tsne_vec[:,1], color=colour_array, s=1)
	if noise_flag:
		plt.title('T-SNE of Activation at Top Layer - Gaussian Noise = {}'.format(noise_level))
	else:
		plt.title('T-SNE of Activation at Top Layer - Gaussian Noise = {}'.format(noise_flag))
	plt.show()


	cmap = get_cmap(10)
	colour_array = []
	idx_array = np.zeros((10,1))
	for s in xrange(10):
		idx_array[s,0] = s+1
		colour_array.append(cmap(s+1))

	plt.scatter(idx_array[:,0], idx_array[:,0], color=colour_array)
	plt.title('T-SNE of Activation at Top Layer - Colour Legend')
	plt.show()

def eval_autoencoder_hashlookup_precision_recall(autoencoder_name, model_weight_path, noise_flag, noise_level, dataset, Limit = None, visual_flag = True):
	# print('============================')
	# print('Pre-processing data:')
	# print('============================')

	# # the data, shuffled and split between train and test sets
	# (X_train, y_train), (X_test, y_test) = mnist.load_data()
	# X_train = X_train.reshape(-1, 784)
	# X_test = X_test.reshape(-1, 784)
	# X_train = X_train.astype("float32") / 255.0
	# X_test = X_test.astype("float32") / 255.0
	# print(X_train.shape[0], 'train samples')
	# print(X_test.shape[0], 'test samples')




	print('============================')
	print('Initialize Model: {}_{}'.format(autoencoder_name, noise_flag))
	print('============================')

	autoencoder = eval('{}(noise_flag={})'.format(autoencoder_name, noise_flag, noise_level))

	autoencoder.load(model_weight_path)

	print('============================')
	print('Encode:')
	print('============================')

	z_test = autoencoder.encode(X_test)

	idx_array = np.zeros((z_test.shape[0], 1), dtype=int)
	for i in xrange(z_test.shape[0]):
		idx_array[i,0] = i



	myTable = linearLookupTable(z_test, X_test)
	myTable2 = linearLookupTable(z_test, idx_array)
	myTable3 = linearLookupTable(z_test, y_test)

	if dataset == 'mnist':

		print('============================')
		print('Compute Sample Stats:')
		print('============================')

		print('Frequency of Digits:')
		y_test_freqs= np.bincount(y_test)
		ii = np.nonzero(y_test_freqs)[0]

		print(zip(ii, y_test_freqs[ii]))

	elif dataset == 'reuters':
		y_test_freqs = np.zeros(y_test.shape[1])
		for j in xrange(y_test.shape[1]):
			y_test_freqs[j] = np.sum(y_test[:,j])

		ii = np.nonzero(y_test_freqs)[0]

		print(zip(ii, y_test_freqs[ii]))


	N = z_test.shape[0]
	H = z_test.shape[1]
	if Limit != None:
		N = Limit

	#H = 3


	print('============================')
	print('Perform lookup:')
	print('============================')	

	hamming_distance_array = np.arange(H+1)

	n_results_mat = np.zeros((N, H+1))
	precision_mat = np.zeros((N, H+1))
	recall_mat = np.zeros((N, H+1))
	false_pos_rate_mat = np.zeros((N, H+1))

	for i in xrange(N):
		lookup_z = z_test[i,:]
		if dataset == 'reuters':
			lookup_y = y_test[i,:]
		else:
			lookup_y = y_test[i]

		n_results = 0
		true_pos = 0

		if dataset == 'reuters':
			#print('num of results:{}'.format(n_results))
			n_relevant = np.sum(np.sum(np.bitwise_and(y_test, lookup_y), axis=1)>0)
			print('num relevant docs in corpus:{}'.format(n_relevant))
			
			if n_relevant == 0:
				continue

		for hamming_distance in xrange(H+1):
			resultX, resultZ = myTable.lookup(lookup_z, hamming_distance)
			#resultIdx, _resultZ = myTable2.lookup(lookup_z, hamming_distance)
			#resultY = y_test[resultIdx]
			resultY, _resultZ = myTable3.lookup(lookup_z, hamming_distance)

			n_results = n_results + resultZ.shape[0]

			if dataset == 'mnist':
				true_pos = true_pos + np.sum(resultY == lookup_y)
				precision = float(true_pos) / n_results
				recall = float(true_pos) / y_test_freqs[lookup_y]
				false_positive_rate = float(n_results - true_pos)/(z_test.shape[0] - y_test_freqs[lookup_y])

			elif dataset == 'reuters':
				true_pos = true_pos + np.sum(np.sum(np.bitwise_and(resultY, lookup_y), axis=1)>0)
				precision = float(true_pos) / n_results
				recall = float(true_pos) / n_relevant
				false_positive_rate = float(n_results - true_pos)/(z_test.shape[0]-n_relevant)

			n_results_mat[i,hamming_distance] = float(n_results)/z_test.shape[0]
			precision_mat[i,hamming_distance] = precision
			recall_mat[i,hamming_distance] = recall
			false_pos_rate_mat[i,hamming_distance] = false_positive_rate

			# print('Example: {}'.format(i))
			# print('Hamm Dist: {}'.format(hamming_distance))
			# print('n_results: {}'.format(n_results))
			# print('TP: {}'.format(true_pos))
			# print('Precision: {}'.format(precision))
			# print('Recall: {}'.format(recall))
			# print('---------------------------------')

		if i%10 == 0:
			print('Finished example {}'.format(i))


	n_results_array = np.mean(n_results_mat, axis=0)
	precision_array = np.mean(precision_mat, axis=0)
	recall_array = np.mean(recall_mat, axis=0)
	false_pos_rate_array = np.mean(false_pos_rate_mat, axis=0)

	if visual_flag:

		#Precision-Recall-NumResults vs. Hamming distance

		n_results_line = plt.plot(hamming_distance_array, n_results_array, label='Num of Results / Total')
		precision_line = plt.plot(hamming_distance_array, precision_array, label='Precision')
		recall_line = plt.plot(hamming_distance_array, recall_array, label='Recall')

		plt.legend()

		plt.xlabel('Hamming Distance')
		plt.ylabel('\%')
		plt.title('Precision-Recall-NumResults vs. Hamming Distance')

		plt.show()

		#Precision recall curve
		plt.plot(recall_array, precision_array)

		plt.xlabel('Recall')
		plt.ylabel('Precision')
		plt.title('Precision-Recall')

		plt.show()

		#ROC Curve
		plt.plot(false_pos_rate_array, recall_array)

		plt.xlabel('False Positive Rate')
		plt.ylabel('True Positive Rate')
		plt.title('Receiver Operating Characteristic')

		plt.show()


	AUC_score = metrics.auc(false_pos_rate_array, recall_array)

	print('AUC: {}'.format(AUC_score))

	np.savez('{}_{}_{}_IR_scores'.format(autoencoder_name, noise_flag, noise_level), \
		hamming_distance_array=hamming_distance_array, \
		n_results_array=n_results_array, \
		precision_array=precision_array, \
		recall_array=recall_array, \
		false_pos_rate_array=false_pos_rate_array, \
		AUC_score = AUC_score)

	return hamming_distance_array, n_results_array, precision_array, recall_array, false_pos_rate_array, AUC_score

def eval_pca_lda_hashlookup_precision_recall(autoencoder_name, n_components, dataset, Limit = None, visual_flag = True):
	# print('============================')
	# print('Pre-processing data:')
	# print('============================')

	# # the data, shuffled and split between train and test sets
	# (X_train, y_train), (X_test, y_test) = mnist.load_data()
	# X_train = X_train.reshape(-1, 784)
	# X_test = X_test.reshape(-1, 784)
	# X_train = X_train.astype("float32") / 255.0
	# X_test = X_test.astype("float32") / 255.0
	# print(X_train.shape[0], 'train samples')
	# print(X_test.shape[0], 'test samples')


	if autoencoder_name == 'PCA':
		model = PCA_model(n_components=n_components)
	elif autoencoder_name == 'LDA':
		model = LDA_model(n_components=n_components)
	
	model.train(X_train, y_train)

	print('============================')
	print('Encode:')
	print('============================')

	z_test = model.encode(X_test)

	idx_array = np.zeros((z_test.shape[0], 1), dtype=int)
	for i in xrange(z_test.shape[0]):
		idx_array[i,0] = i



	myTable = linearLookupTable(z_test, X_test)
	myTable2 = linearLookupTable(z_test, idx_array)
	myTable3 = linearLookupTable(z_test, y_test)

	if dataset == 'mnist':

		print('============================')
		print('Compute Sample Stats:')
		print('============================')

		print('Frequency of Digits:')
		y_test_freqs= np.bincount(y_test)
		ii = np.nonzero(y_test_freqs)[0]

		print(zip(ii, y_test_freqs[ii]))

	elif dataset == 'reuters':
		y_test_freqs = np.zeros(y_test.shape[1])
		for j in xrange(y_test.shape[1]):
			y_test_freqs[j] = np.sum(y_test[:,j])

		ii = np.nonzero(y_test_freqs)[0]

		print(zip(ii, y_test_freqs[ii]))


	N = z_test.shape[0]
	H = z_test.shape[1]
	if Limit != None:
		N = Limit

	#H = 3


	print('============================')
	print('Perform lookup:')
	print('============================')	

	hamming_distance_array = np.arange(H+1)

	n_results_mat = np.zeros((N, H+1))
	precision_mat = np.zeros((N, H+1))
	recall_mat = np.zeros((N, H+1))
	false_pos_rate_mat = np.zeros((N, H+1))

	for i in xrange(N):
		lookup_z = z_test[i,:]
		if dataset == 'reuters':
			lookup_y = y_test[i,:]
		else:
			lookup_y = y_test[i]

		n_results = 0
		true_pos = 0

		if dataset == 'reuters':
			#print('num of results:{}'.format(n_results))
			n_relevant = np.sum(np.sum(np.bitwise_and(y_test, lookup_y), axis=1)>0)
			print('num relevant docs in corpus:{}'.format(n_relevant))
			
			if n_relevant == 0:
				continue

		for hamming_distance in xrange(H+1):
			resultX, resultZ = myTable.lookup(lookup_z, hamming_distance)
			#resultIdx, _resultZ = myTable2.lookup(lookup_z, hamming_distance)
			#resultY = y_test[resultIdx]
			resultY, _resultZ = myTable3.lookup(lookup_z, hamming_distance)

			n_results = n_results + resultZ.shape[0]

			if dataset == 'mnist':
				true_pos = true_pos + np.sum(resultY == lookup_y)
				precision = float(true_pos) / n_results
				recall = float(true_pos) / y_test_freqs[lookup_y]
				false_positive_rate = float(n_results - true_pos)/(z_test.shape[0] - y_test_freqs[lookup_y])

			elif dataset == 'reuters':
				true_pos = true_pos + np.sum(np.sum(np.bitwise_and(resultY, lookup_y), axis=1)>0)
				precision = float(true_pos) / n_results
				recall = float(true_pos) / n_relevant
				false_positive_rate = float(n_results - true_pos)/(z_test.shape[0]-n_relevant)

			n_results_mat[i,hamming_distance] = float(n_results)/z_test.shape[0]
			precision_mat[i,hamming_distance] = precision
			recall_mat[i,hamming_distance] = recall
			false_pos_rate_mat[i,hamming_distance] = false_positive_rate

			# print('Example: {}'.format(i))
			# print('Hamm Dist: {}'.format(hamming_distance))
			# print('n_results: {}'.format(n_results))
			# print('TP: {}'.format(true_pos))
			# print('Precision: {}'.format(precision))
			# print('Recall: {}'.format(recall))
			# print('---------------------------------')

		if i%10 == 0:
			print('Finished example {}'.format(i))


	n_results_array = np.mean(n_results_mat, axis=0)
	precision_array = np.mean(precision_mat, axis=0)
	recall_array = np.mean(recall_mat, axis=0)
	false_pos_rate_array = np.mean(false_pos_rate_mat, axis=0)

	if visual_flag:

		#Precision-Recall-NumResults vs. Hamming distance

		n_results_line = plt.plot(hamming_distance_array, n_results_array, label='Num of Results / Total')
		precision_line = plt.plot(hamming_distance_array, precision_array, label='Precision')
		recall_line = plt.plot(hamming_distance_array, recall_array, label='Recall')

		plt.legend()

		plt.xlabel('Hamming Distance')
		plt.ylabel('\%')
		plt.title('Precision-Recall-NumResults vs. Hamming Distance')

		plt.show()

		#Precision recall curve
		plt.plot(recall_array, precision_array)

		plt.xlabel('Recall')
		plt.ylabel('Precision')
		plt.title('Precision-Recall')

		plt.show()

		#ROC Curve
		plt.plot(false_pos_rate_array, recall_array)

		plt.xlabel('False Positive Rate')
		plt.ylabel('True Positive Rate')
		plt.title('Receiver Operating Characteristic')

		plt.show()


	AUC_score = metrics.auc(false_pos_rate_array, recall_array)

	print('AUC: {}'.format(AUC_score))

	np.savez('{}_{}_binarize_IR_scores'.format(autoencoder_name, n_components), \
		hamming_distance_array=hamming_distance_array, \
		n_results_array=n_results_array, \
		precision_array=precision_array, \
		recall_array=recall_array, \
		false_pos_rate_array=false_pos_rate_array, \
		AUC_score = AUC_score)

	return hamming_distance_array, n_results_array, precision_array, recall_array, false_pos_rate_array, AUC_score

def eval_pca_lda_cosine_lookup_precision_recall(autoencoder_name, n_components, dataset, Limit = None, visual_flag = True):
	# print('============================')
	# print('Pre-processing data:')
	# print('============================')

	# # the data, shuffled and split between train and test sets
	# (X_train, y_train), (X_test, y_test) = mnist.load_data()
	# X_train = X_train.reshape(-1, 784)
	# X_test = X_test.reshape(-1, 784)
	# X_train = X_train.astype("float32") / 255.0
	# X_test = X_test.astype("float32") / 255.0
	# print(X_train.shape[0], 'train samples')
	# print(X_test.shape[0], 'test samples')

	if autoencoder_name == 'PCA':
		model = PCA_model(n_components=n_components)
	elif autoencoder_name == 'LDA':
		model = LDA_model(n_components=n_components)
	
	model.train(X_train, y_train)


	print('============================')
	print('Encode:')
	print('============================')

	z_test = model.encode(X_test)

	print('Z test shape: {}'.format(z_test.shape))

	idx_array = np.zeros((z_test.shape[0], 1), dtype=int)
	for i in xrange(z_test.shape[0]):
		idx_array[i,0] = i



	myTable = cosineLookupTable(z_test, X_test)
	myTable2 = cosineLookupTable(z_test, idx_array)
	myTable3 = cosineLookupTable(z_test, y_test)

	if dataset == 'mnist':

		print('============================')
		print('Compute Sample Stats:')
		print('============================')

		print('Frequency of Digits:')
		y_test_freqs= np.bincount(y_test)
		ii = np.nonzero(y_test_freqs)[0]

		print(zip(ii, y_test_freqs[ii]))

	elif dataset == 'reuters':
		y_test_freqs = np.zeros(y_test.shape[1])
		for j in xrange(y_test.shape[1]):
			y_test_freqs[j] = np.sum(y_test[:,j])

		ii = np.nonzero(y_test_freqs)[0]

		print(zip(ii, y_test_freqs[ii]))


	proportion_array = [0.0, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.007, 0.01, 0.02, 0.05, 0.07, 0.1, 0.2, 0.5, 0.7, 0.9, 1.0]


	N = z_test.shape[0]
	H = len(proportion_array)-2
	if Limit != None:
		N = Limit

	#H = 3


	print('============================')
	print('Perform lookup:')
	print('============================')	

	hamming_distance_array = np.arange(H+1)

	n_results_mat = np.zeros((N, H+1))
	precision_mat = np.zeros((N, H+1))
	recall_mat = np.zeros((N, H+1))
	false_pos_rate_mat = np.zeros((N, H+1))

	for i in xrange(N):
		lookup_z = z_test[i,:]
		if dataset == 'reuters':
			lookup_y = y_test[i,:]
		else:
			lookup_y = y_test[i]


		n_results = 0
		true_pos = 0

		if dataset == 'reuters':
			#print('num of results:{}'.format(n_results))
			n_relevant = np.sum(np.sum(np.bitwise_and(y_test, lookup_y), axis=1)>0)
			print('num relevant docs in corpus:{}'.format(n_relevant))
			
			if n_relevant == 0:
				continue


		resultX_complete, resultZ_complete = myTable.lookup(lookup_z)
		resultIdx_complete, resultZ_complete = myTable2.lookup(lookup_z)
		resultY_complete, resultZ_complete = myTable3.lookup(lookup_z)


		for t in xrange(len(proportion_array)-1):
			proportion = proportion_array[t]
			idx_last = int(math.floor(float(proportion*z_test.shape[0])))
			idx_curr = int(math.floor(float((proportion_array[t+1])*z_test.shape[0])))

			resultX = resultX_complete[idx_last:idx_curr] 
			resultZ = resultZ_complete[idx_last:idx_curr]
			resultY = resultY_complete[idx_last:idx_curr]
			#resultIdx, _resultZ = myTable2.lookup(lookup_z, hamming_distance)
			#resultY = y_test[resultIdx]

			n_results = n_results + resultZ.shape[0]

			if dataset == 'mnist':
				true_pos = true_pos + np.sum(resultY == lookup_y)
				precision = float(true_pos) / n_results
				recall = float(true_pos) / y_test_freqs[lookup_y]
				false_positive_rate = float(n_results - true_pos)/(z_test.shape[0] - y_test_freqs[lookup_y])

			elif dataset == 'reuters':
				true_pos = true_pos + np.sum(np.sum(np.bitwise_and(resultY, lookup_y), axis=1)>0)
				precision = float(true_pos) / n_results
				recall = float(true_pos) / n_relevant
				false_positive_rate = float(n_results - true_pos)/(z_test.shape[0]-n_relevant)

			n_results_mat[i,t] = float(n_results)/z_test.shape[0]
			precision_mat[i,t] = precision
			recall_mat[i,t] = recall
			false_pos_rate_mat[i,t] = false_positive_rate

			# print('Example: {}'.format(i))
			# print('Proportion: {}'.format(proportion))
			# print('n_results: {}'.format(n_results))
			# print('TP: {}'.format(true_pos))
			# print('Precision: {}'.format(precision))
			# print('Recall: {}'.format(recall))
			# print('---------------------------------')

		if i%10 == 0:
			print('Finished example {}'.format(i))


	n_results_array = np.mean(n_results_mat, axis=0)
	precision_array = np.mean(precision_mat, axis=0)
	recall_array = np.mean(recall_mat, axis=0)
	false_pos_rate_array = np.mean(false_pos_rate_mat, axis=0)

	if visual_flag:

		#Precision-Recall-NumResults vs. Hamming distance

		precision_line = plt.plot(n_results_array, precision_array, label='Precision')
		recall_line = plt.plot(n_results_array, recall_array, label='Recall')

		plt.legend()

		plt.xlabel('Proportion')
		plt.ylabel('\%')
		plt.title('Precision-Recall-NumResults vs. Proportion')

		plt.show()

		#Precision recall curve
		plt.plot(recall_array, precision_array)

		plt.xlabel('Recall')
		plt.ylabel('Precision')
		plt.title('Precision-Recall')

		plt.show()

		#ROC Curve
		plt.plot(false_pos_rate_array, recall_array)

		plt.xlabel('False Positive Rate')
		plt.ylabel('True Positive Rate')
		plt.title('Receiver Operating Characteristic')

		plt.show()


	AUC_score = metrics.auc(false_pos_rate_array, recall_array)

	print('AUC: {}'.format(AUC_score))

	np.savez('{}_{}_IR_scores'.format(autoencoder_name, n_components), \
		n_results_array=n_results_array, \
		precision_array=precision_array, \
		recall_array=recall_array, \
		false_pos_rate_array=false_pos_rate_array, \
		AUC_score = AUC_score)

	return n_results_array, precision_array, recall_array, false_pos_rate_array, AUC_score



def eval_autoencoder_hashlookup(autoencoder_name, model_weight_path, noise_flag, noise_level):

	print('============================')
	print('Initialize Model: {}_{}'.format(autoencoder_name, noise_flag))
	print('============================')

	autoencoder = eval('{}(noise_flag={})'.format(autoencoder_name, noise_flag, noise_level))

	autoencoder.load(model_weight_path)

	print('============================')
	print('Hash Lookup:')
	print('============================')

	z_test = autoencoder.encode(X_test)

	print('Frequency of Digits:')
	y_test_freqs= np.bincount(y_test)
	ii = np.nonzero(y_test_freqs)[0]

	print(zip(ii, y_test_freqs[ii]))

	idx_array = np.zeros((z_test.shape[0], 1))
	for i in xrange(z_test.shape[0]):
		idx_array[i,0] = i


	myTable = linearLookupTable(z_test, X_test)
	myTable2 = linearLookupTable(z_test, idx_array)


	#choose index of the test example
	#i = 6  #4
	i = 41 #7
	# i = 258

	plt.imshow(X_test.reshape((-1,28,28))[i,:,:], cmap=plt.get_cmap("gray"))
	plt.show()

	lookup_z = z_test[i,:]


	N=4
	M = 15

	for i in xrange(N):
		print('hamming distance of {}'.format(i))
		resultX, resultZ = myTable.lookup(lookup_z, i)
		resultIdx, _resultZ = myTable2.lookup(lookup_z, i)

		print('Shape of results: {}'.format(resultX.shape))

		for j in xrange(min(resultX.shape[0], M)):
			frame1=plt.subplot(N, M, i*M+j+1)
			print('Latent Z: {}'.format(resultZ[j,:]))
			print('Index: {}'.format(resultIdx[j]))
			plt.imshow(resultX[j,:].reshape((28,28)), cmap=plt.get_cmap("gray"))
			print('-------')

			frame1.axes.get_xaxis().set_visible(False)
			frame1.axes.get_yaxis().set_visible(False)

	plt.show()

	print('hamming distance of 0')
	resultX, resultZ = myTable.lookup(lookup_z, 0)
	resultIdx, _resultZ = myTable2.lookup(lookup_z, 0)

	print('Shape of results: {}'.format(resultX.shape))
	for j in xrange(resultX.shape[0]):
		print('Latent Z: {}'.format(resultZ[j,:]))
		print('Index: {}'.format(resultIdx[j]))
		fig = plt.figure()
		plt.imshow(resultX[j,:].reshape((28,28)), cmap=plt.get_cmap("gray"))
		plt.draw()
		plt.pause(1) # <-------
		raw_input("<Hit Enter To Close>")
		plt.close(fig)
		print('-------')

	print('hamming distance of 1')
	resultX, resultZ = myTable.lookup(lookup_z, 1)
	resultIdx, _resultZ = myTable2.lookup(lookup_z, 1)

	print('Shape of results: {}'.format(resultX.shape))
	for j in xrange(resultX.shape[0]):
		print('Latent Z: {}'.format(resultZ[j,:]))
		print('Index: {}'.format(resultIdx[j]))
		fig = plt.figure()
		plt.imshow(resultX[j,:].reshape((28,28)), cmap=plt.get_cmap("gray"))
		plt.draw()
		plt.pause(1) # <-------
		raw_input("<Hit Enter To Close>")
		plt.close(fig)
		print('-------')

	print('hamming distance of 2')
	resultX, resultZ = myTable.lookup(lookup_z, 2)
	resultIdx, _resultZ = myTable2.lookup(lookup_z, 2)

	print('Shape of results: {}'.format(resultX.shape))
	for j in xrange(resultX.shape[0]):
		print('Latent Z: {}'.format(resultZ[j,:]))
		print('Index: {}'.format(resultIdx[j]))
		fig = plt.figure()
		plt.imshow(resultX[j,:].reshape((28,28)), cmap=plt.get_cmap("gray"))
		plt.draw()
		plt.pause(1) # <-------
		raw_input("<Hit Enter To Close>")
		plt.close(fig)
		print('-------')

	print('hamming distance of 3')
	resultX, resultZ = myTable.lookup(lookup_z, 3)
	resultIdx, _resultZ = myTable2.lookup(lookup_z, 3)

	print('Shape of results: {}'.format(resultX.shape))
	for j in xrange(resultX.shape[0]):
		print('Latent Z: {}'.format(resultZ[j,:]))
		print('Index: {}'.format(resultIdx[j]))
		fig = plt.figure()
		plt.imshow(resultX[j,:].reshape((28,28)), cmap=plt.get_cmap("gray"))
		plt.draw()
		plt.pause(1) # <-------
		raw_input("<Hit Enter To Close>")
		plt.close(fig)
		print('-------')


def eval_autoencoder_sample(autoencoder_name, model_weight_path, noise_flag, noise_level, n_latent, latent_z=None):

	print('============================')
	print('Initialize Model: {}_{}'.format(autoencoder_name, noise_flag))
	print('============================')

	autoencoder = eval('{}(noise_flag={})'.format(autoencoder_name, noise_flag, noise_level))

	autoencoder.load(model_weight_path)

	print('============================')
	print('Generate Samples')
	print('============================')


	if latent_z == None:
		latent_z = np.random.randint(2, size=n_latent)*2-1

	latent_z = np.array([latent_z])

	print('Latent Z: {}'.format(latent_z))

	#latent_z = latent_z * 100

	X_sample = autoencoder.decode(latent_z)

	plt.imshow(X_sample.reshape((28,28)), cmap=plt.get_cmap("gray"))
	plt.show()


def eval_autoencoder_recon_max_min_RMSE(autoencoder_name, model_weight_path, noise_flag, noise_level, nExamples=10):
	print('============================')
	print('Initialize Model: {}_{}'.format(autoencoder_name, noise_flag))
	print('============================')

	autoencoder = eval('{}(noise_flag={})'.format(autoencoder_name, noise_flag, noise_level))

	autoencoder.load(model_weight_path)	

	print('============================')
	print('Reconstruction:')
	print('============================')

	x_test_recon = autoencoder.predict(X_test)

	rmse_array = np.mean(np.square(X_test - x_test_recon), axis=1)

	sorted_idx = np.argsort(rmse_array)

	rmse_array = rmse_array[sorted_idx]
	X_test_sorted = X_test[sorted_idx]
	x_test_recon = x_test_recon[sorted_idx]


	print('Smallest RMSE')
	for i in xrange(nExamples):
		x_test_recon = x_test_recon.reshape((-1,28,28))
		plt.imshow(X_test_sorted.reshape((-1,28,28))[i,:,:], cmap=plt.get_cmap("gray"))
		plt.show()

		plt.imshow(x_test_recon[i,:,:], cmap=plt.get_cmap("gray"))
		plt.show()

		print('RMSE: {}'.format(rmse_array[i]))

	print('Largest RMSE')
	for i in xrange(x_test_recon.shape[0] - nExamples, x_test_recon.shape[0]):
		x_test_recon = x_test_recon.reshape((-1,28,28))
		plt.imshow(X_test_sorted.reshape((-1,28,28))[i,:,:], cmap=plt.get_cmap("gray"))
		plt.show()

		plt.imshow(x_test_recon[i,:,:], cmap=plt.get_cmap("gray"))
		plt.show()

		print('RMSE: {}'.format(rmse_array[i]))


def eval_autoencoder_save_output(autoencoder_name, model_weight_path, noise_flag, noise_level):
	print('============================')
	print('Initialize Model: {}_{}'.format(autoencoder_name, noise_flag))
	print('============================')

	autoencoder = eval('{}(noise_flag={})'.format(autoencoder_name, noise_flag, noise_level))

	autoencoder.load(model_weight_path)

	print('============================')
	print('Hash Lookup:')
	print('============================')

	z_test = autoencoder.encode(X_test)

	tsne_model = TSNE(n_components=2, perplexity=30, random_state=0)
	np.set_printoptions(suppress=True)
	tsne_vec = tsne_model.fit_transform(z_test)

	np.savez('{}_{}_{}_data'.format(autoencoder_name, noise_flag, noise_level), X_test=X_test, y_test=y_test, z_test=z_test, z_test_tsne = tsne_vec)


def sample_all(autoencoder_name, model_weight_path, noise_flag, noise_level, n_latent):
	print('============================')
	print('Initialize Model: {}_{}'.format(autoencoder_name, noise_flag))
	print('============================')

	autoencoder = eval('{}(noise_flag={})'.format(autoencoder_name, noise_flag, noise_level))

	autoencoder.load(model_weight_path)


	N_samples = math.pow(2, n_latent)
	N = int(math.floor(math.sqrt(N_samples)))
	M = int(math.ceil(float(N_samples)/N))

	graycode_array = get_graycode_array(n_latent)
	for i in xrange(N):
		for j in xrange(M):
			latent_z = graycode_array[i*M+j,:]
			print(latent_z)
			latent_z = np.array([latent_z])

			latent_z = (latent_z - 0.5)*2
			#latent_z = latent_z * 100

			print('Latent Z: {}'.format(latent_z))

			

			X_sample = autoencoder.decode(latent_z)

			frame1=plt.subplot(N, M, i*M+j+1)
			plt.imshow(X_sample.reshape((28,28)), cmap=plt.get_cmap("gray"))
			print('-------')

			frame1.axes.get_xaxis().set_visible(False)
			frame1.axes.get_yaxis().set_visible(False)

	plt.show()

def sample_100(autoencoder_name, model_weight_path, noise_flag, noise_level, n_latent):
	print('============================')
	print('Initialize Model: {}_{}'.format(autoencoder_name, noise_flag))
	print('============================')

	autoencoder = eval('{}(noise_flag={})'.format(autoencoder_name, noise_flag, noise_level))

	autoencoder.load(model_weight_path)


	N = 10
	M = 10

	for i in xrange(N):
		for j in xrange(M):
			latent_z = np.random.randint(2, size=n_latent)*2-1

			latent_z = np.array([latent_z])


			#latent_z = (latent_z - 0.5)*2
			#latent_z = latent_z * 100

			print('Latent Z: {}'.format(latent_z))

			
			X_sample = autoencoder.decode(latent_z)

			frame1=plt.subplot(N, M, i*M+j+1)
			plt.imshow(X_sample.reshape((28,28)), cmap=plt.get_cmap("gray"))
			print('-------')

			frame1.axes.get_xaxis().set_visible(False)
			frame1.axes.get_yaxis().set_visible(False)

	plt.show()


if __name__ == '__main__':
	print('============================')
	print('Pre-processing data:')
	print('============================')

	# the data, shuffled and split between train and test sets
	(X_train, y_train), (X_test, y_test) = mnist.load_data()
	X_train = X_train.reshape(-1, 784)
	X_test = X_test.reshape(-1, 784)
	X_train = X_train.astype("float32") / 255.0
	X_test = X_test.astype("float32") / 255.0
	print(X_train.shape[0], 'train samples')
	print(X_test.shape[0], 'test samples')


	#sample_100('MNIST_autoencoder_784_392_196_98_49_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_tanh_True_4', noise_flag=True, noise_level=4, n_latent=49)

	#sample_100('MNIST_autoencoder_784_392_196_98_49_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_tanh_True_4', noise_flag=True, noise_level=4, n_latent=49)

	#eval_autoencoder_save_output('MNIST_autoencoder_784_392_196_98_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_tanh_True_4', noise_flag=True, noise_level=4)
	#eval_autoencoder_save_output('MNIST_autoencoder_784_392_196_98_49_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_tanh_True_4', noise_flag=True, noise_level=4)
	#eval_autoencoder_save_output('MNIST_autoencoder_784_392_196_98_49_24_12_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_24_12_tanh_True_4', noise_flag=True, noise_level=4)
	#eval_autoencoder_save_output('MNIST_autoencoder_784_392_196_98_49_24_12_6_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_24_12_6_tanh_True_4', noise_flag=True, noise_level=4)

	sample_all('MNIST_autoencoder_784_392_196_98_49_24_12_6_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_24_12_6_tanh_True_4', noise_flag=True, noise_level=4, n_latent=6)

	#eval_autoencoder_encode('MNIST_autoencoder_784_392_196_98_49_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_tanh_True_8', noise_flag=True, noise_level=8)

	# eval_autoencoder_RMSE('MNIST_autoencoder_784_392_196_98_49_20_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_20_tanh_True_8', noise_flag=True, noise_level=4)
	# eval_autoencoder_recon_max_min_RMSE('MNIST_autoencoder_784_392_196_98_49_20_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_20_tanh_True_8', noise_flag=True, noise_level=4)

	# eval_autoencoder_recon_max_min_RMSE('MNIST_autoencoder_784_392_196_98_49_24_12_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_24_12_tanh_True_4', noise_flag=True, noise_level=4)	

	# eval_autoencoder_sample('MNIST_autoencoder_784_392_196_98_49_24_12_6_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_24_12_6_tanh_True_4', noise_flag=True, noise_level=4, n_latent=6)

	#eval_autoencoder_hashlookup('MNIST_autoencoder_784_392_196_98_49_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_tanh_True_8', noise_flag=True, noise_level=8)

	# eval_autoencoder_hashlookup_precision_recall('MNIST_autoencoder_784_392_196_98_49_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_tanh_True_8', noise_flag=True, noise_level=8, Limit=2500, dataset='mnist')

	#eval_autoencoder_recon_max_min_RMSE('MNIST_autoencoder_784_392_196_98_49_20_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_20_tanh_True_4', noise_flag=True, noise_level=4)

	#eval_pca_lda_cosine_lookup_precision_recall('PCA', n_components=20, dataset='mnist', Limit = 200, visual_flag = True)

	#eval_pca_lda_hashlookup_precision_recall('LDA', n_components=20, dataset='mnist', Limit=200, visual_flag=True)

	# eval_autoencoder_hashlookup_precision_recall_pca_lda('LDA', n_components=6, dataset='mnist', Limit = 200, visual_flag = True)

	#eval_autoencoder_save_output('MNIST_autoencoder_784_392_196_98_49_20_tanh', './mnist_models/MNIST_autoencoder_784_392_196_98_49_20_tanh_True_4', noise_flag=True, noise_level=4)


	# eval_autoencoder('MNIST_autoencoder_784_392_196_98_49_tanh', './mnist_models/mnist_autoencoder_784_392_196_98_49_tanh_False')
	# eval_autoencoder('MNIST_autoencoder_784_392_196_98_49_tanh', './mnist_models/mnist_autoencoder_784_392_196_98_49_tanh_True')


	# eval_autoencoder_RMSE('MNIST_autoencoder_784_392_196_98_49_24_12_tanh', './mnist_models/MNIST_autoencoder_784_392_196_98_49_24_12_tanh_True')
	# eval_autoencoder_recon('MNIST_autoencoder_784_392_196_98_49_24_12_tanh', './mnist_models/MNIST_autoencoder_784_392_196_98_49_24_12_tanh_True')
	# eval_autoencoder_encode('MNIST_autoencoder_784_392_196_98_49_24_12_tanh', './mnist_models/MNIST_autoencoder_784_392_196_98_49_24_12_tanh_True')
	# eval_autoencoder_encode('MNIST_autoencoder_784_392_196_98_49_20_tanh', './mnist_models/MNIST_autoencoder_784_392_196_98_49_20_tanh_False')
	# eval_autoencoder_hashlookup_precision_recall('MNIST_autoencoder_784_392_196_98_49_20_tanh', './mnist_models/MNIST_autoencoder_784_392_196_98_49_20_tanh_False')

	# eval_autoencoder_encode('MNIST_autoencoder_784_392_196_98_49_20_tanh', './mnist_models/MNIST_autoencoder_784_392_196_98_49_20_tanh_True')
	# eval_autoencoder_hashlookup_precision_recall('MNIST_autoencoder_784_392_196_98_49_20_tanh', './mnist_models/MNIST_autoencoder_784_392_196_98_49_20_tanh_True')

	# eval_autoencoder('MNIST_autoencoder_784_392_196_98_49_20_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_20_tanh_True_4', noise_flag=True, noise_level=4)
	# eval_autoencoder_hashlookup_precision_recall('MNIST_autoencoder_784_392_196_98_49_20_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_20_tanh_True_4', noise_flag=True, noise_level=4, Limit=2500)
	# eval_autoencoder_sample('MNIST_autoencoder_784_392_196_98_49_24_12_tanh', './results/final_models/MNIST_autoencoder_784_392_196_98_49_24_12_tanh_True_4', noise_flag=True, noise_level=4, n_latent=12)

	##########################
	#preicison recall eval:  #
	##########################


	# print('============================')
	# print('Pre-processing data:')
	# print('============================')

	# # settings
	# batch_size = 256
	# nb_classes = 10
	# nb_epoch = 10

	# # the data, shuffled and split between train and test sets
	# reuters_npz = np.load('./reuters_data/reuters_corpus_tfidf.npz')
	# X_train = reuters_npz['X'][0:6000,:]
	# X_test = reuters_npz['X'][6000:,:]
	# y_train = reuters_npz['y'][0:6000,:]
	# y_test = reuters_npz['y'][6000:,:]

	# print(y_test.shape)
	# print(y_test[1])

	#eval_autoencoder_hashlookup_precision_recall('Reuters_autoencoder_2000_512_512_128_tanh', './working_models/Reuters_autoencoder_2000_512_512_128_tanh_False', noise_flag=False, noise_level=0, dataset='reuters', Limit=200)
	#eval_autoencoder_hashlookup_precision_recall('Reuters_autoencoder_2000_512_512_128_tanh', './working_models/Reuters_autoencoder_2000_512_512_128_tanh_True_2', noise_flag=True, noise_level=2, dataset='reuters', Limit=200)
	#eval_autoencoder_hashlookup_precision_recall('Reuters_autoencoder_2000_512_512_128_tanh', './working_models/Reuters_autoencoder_2000_512_512_128_tanh_True_4', noise_flag=True, noise_level=4, dataset='reuters', Limit=200)

