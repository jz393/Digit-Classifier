# -*- coding: utf-8 -*-
"""MNIST Neural Net

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1raABG49dcgawt63--t69q_CL8fKykjYs
"""

import numpy as np
import gzip
import pickle
from urllib import request
import tensorflow


filename = [
["training_images","train-images-idx3-ubyte.gz"],
["test_images","t10k-images-idx3-ubyte.gz"],
["training_labels","train-labels-idx1-ubyte.gz"],
["test_labels","t10k-labels-idx1-ubyte.gz"]
]

def download_mnist():
    base_url = "http://yann.lecun.com/exdb/mnist/"
    for name in filename:
        print("Downloading "+name[1]+"...")
        request.urlretrieve(base_url+name[1], name[1])
    print("Download complete.")

def save_mnist():
    mnist = {}
    for name in filename[:2]:
        with gzip.open(name[1], 'rb') as f:
            mnist[name[0]] = np.frombuffer(f.read(), np.uint8, offset=16).reshape(-1,28*28)
    for name in filename[-2:]:
        with gzip.open(name[1], 'rb') as f:
            mnist[name[0]] = np.frombuffer(f.read(), np.uint8, offset=8)
    with open("mnist.pkl", 'wb') as f:
        pickle.dump(mnist,f)
    print("Save complete.")

def init():
    download_mnist()
    save_mnist()

def load():
    with open("mnist.pkl",'rb') as f:
        mnist = pickle.load(f)
    return mnist["training_images"], mnist["training_labels"], mnist["test_images"], mnist["test_labels"]

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
x_train = mnist.train.images
t_train = mnist.train.labels
x_test = mnist.test.images
t_test = mnist.test.labels

print(x_train.shape, x_train.dtype)
print(t_train.shape, t_train.dtype)
print(x_test.shape, x_test.dtype)
print(t_test.shape, t_test.dtype)


#NETWORK ARCHITECTURE
num_hidden_layers = 1 #number of hidden layers
num_nodes = [784,20,10] #number of nodes in layer 1, 2, 3

#DATA CONSTANTS
epsilon = 0.05 #learning rate for grad descent
lambda_reg = 0.01 #regularization constant
a_list = [] #initialized in trainNN
weights = [] #initialized in trainNN
num_epochs = 100
batch_size = 1

#Randomly initialize the weights w/ biases. Will learn these as loop runs
#theta1: weights matrix --> 20 * 785
theta1 = np.random.randn(num_nodes[1], num_nodes[0] + 1) / np.sqrt(num_nodes[0])
#theta2: weights matrix --> 10 * 21
theta2 = np.random.randn(num_nodes[2], num_nodes[1] + 1) / np.sqrt(num_nodes[1])
#weights array
weights = [theta1, theta2]

#TRAINING FUNCTION
def trainNN(printCost):
  '''
  Main function for training neural network
  if printCost, prints the cost
  '''
  
  global weights
  global a_list
  
  #loop to update weights to model  
  for x in range(t_train.shape[0]//batch_size):
    
    y_hat = t_train[x*batch_size:(x+1)*batch_size,:]
    
    a1 = x_train[x*batch_size:(x+1)*batch_size,:]
    a1 = np.hstack((np.ones((batch_size,1)),a1))
    a1 = np.transpose(a1)
    
    #Implement forward propagation
    a2 = forwardProp(a1,weights[0])
    a2 = np.vstack((np.ones((1,batch_size)),a2))  
    
    a3 = forwardProp(a2,weights[1])  
    a3 = a3/np.max(a3)
    a_list = [a1, a2, a3]
 
  
    #Implement back propagation on J_theta
    dC_dW1 = backProp(2,np.dot(weights[0],a1),a1,y_hat)
    dC_dW2 = backProp(3,np.dot(weights[1],a2),a2,y_hat)

    
    #Use gradient descent to minimize cost function, which updates J_theta to new values
    weights[0] = gradDescent(weights[0], dC_dW1)
    weights[1] = gradDescent(weights[1], dC_dW2)
    
    if printCost:
      print("cost: "+ str(costFunction(a3, y_hat, batch_size, 3)))
   
    
def forwardProp(input, weights):
  '''
  Implements forward propagation on specified inputs & weights
  '''
  z = np.dot(weights,input)
  return ReLU(z)
 

def backProp(L,z_curr, a_prev,y):
  '''
  returns dC/dW
  L: is the current layer. Integer
  a_prev: activation of the previous layer
  z_curr: is the weighted input to our current layer. z is the weights associated 
    with our layer multiplied with a_prev (z = W * a)
  '''
  global a_list
  global batch_size
  global weights
  global num_nodes
  global lambda_reg

  #z_nxt is the weighted scores for the the next layer, used to compute dC_da
  if L < 3:
    z_nxt = np.dot(weights[L-1],a_list[L-1])
  else:
    z_nxt = np.zeros((1000,1000)) # Doesn't matter what this is, as for layer 3 this will never be used.
  
  dC_da = np.zeros((num_nodes[L-1],batch_size))
  for k in range(batch_size):
    for i in range(num_nodes[L-1]):
      for j in range(num_nodes[-1]):
        dC_da[i,k] = activationDerivative(L,i,a_list[2][j,k],y[j,k],z_nxt[j,k])
  
  #For second layer: output should be 20x785

  dC_dW = np.dot(dC_da*StepMat(z_curr),np.transpose(a_prev))
  return dC_dW + np.dot((lambda_reg/batch_size), weights[L-2])
  
    
def activationDerivative(L, i, a_final, y, z_nxt):
  '''
  find dC/da in layer of the backprop function for a particular activation unit using next layer
  L: current Layer number (int)
  a_curr: activation of current layer (scalar)
  a_final: activation of final layer (scalar)
  y: expected output of final layer (scalar)
  z_nxt: the weighted sum of activation and weights for layer L+1 (next layer)
  i: is the current node number (neuron) of the activation in L
  batch_num: the number of the particular batch size you are accessing from 0-batch_size
  '''
  global a_list
  global batch_size
  global weights
  global num_nodes
  
  # Base case of last layer which is just gradient of loss function
  if L == (2 + num_hidden_layers):
    return a_final - y

  else:
    sumDerivative = 0
    J = num_nodes[L]
    for j in range(J):
      #Recursive case
      sumDerivative += activationDerivative(L+1, i, a_final, y, z_nxt) * Step(z_nxt) * weights[L-1][j,i]
    return sumDerivative
    

def costFunction(X, Y, m, l):
  '''
  returns cost J(theta), a scalar
  Y = actual values. expected output
  X = input matrix, must have same dimensions of Y
  m = batch size
  l = number of layers
  '''

  global weights
  
  costVector = [] # Will be a 1 x batch_size vector. Each element is the cost
                  # for one image.
  for i in range(0,batch_size):
    h = np.transpose(X)[i]
    y = np.transpose(Y)[i]
    costPerImage = np.sum((h - y)**2)
    costVector.append(costPerImage)
    
  return np.sum(costVector)/(len(costVector)) #+ reg


def gradDescent(theta, dC_dW):
  return theta - epsilon*dC_dW  # + just for testing


def _flatten(M):
  '''
  flattens a matrix (represented as np.array) M into one vector
  '''
  return M.flatten()
  

def sigmoid(M):
  '''
  passes M through sigmoid function, returns vector of values between 0 and 1
  '''
  X = _flatten(M)
  return 1/(1+np.exp(-X))


def ReLU(z):
  '''
  passes array z through ReLU. This is our activation function
  '''
  a = z[:]
  a[a<=0] = 0
  return a


def Step(z):
  '''
  derivative of ReLU function
  returns scalar, given that z is a scalar
  '''
  if z <= 0:
    return 0
  else:
    return 1
  

def StepMat(z):
  '''
  derivative of ReLU function for matrices
  returns matrix
  '''
  
  a = z[:]
  a[a <= 0] = 0
  a[a > 0] = 1 
  return a

def testing(num_images):
  '''
  num_images: the number of images we are testing
  Testing the neural network with the test data
  '''
  global weights
  global num_nodes
  correct = 0
  
  for n in range(num_images):
 
    y_hat = np.zeros((1,10))
    y = t_test[n]
    
    i = 0
    for row in y_hat:
      if y > 0:
        row[int(y)] = 1
      i += 1
    y_hat = np.transpose(y_hat)
    
    a1 = x_test[n,:]
    a1 = np.hstack((np.ones((1)),a1))
    a1 = np.transpose(a1)
    
    a2 = forwardProp(a1,weights[0])
    np.transpose(a2)
    a2 = np.hstack((np.ones((1)),a2))
    np.transpose(a2)
    
    a3 = forwardProp(a2,weights[1])  
    a3 = a3 / np.max(a3)
    
    
    for i in range(num_nodes[-1]):
      print(a3[i])
      print(y_hat[i])
      if (a3[i] and y_hat[i] > 0.1):
        correct += 1
  
  return (correct/num_images)*100
    
#training and testing    
print("-------------------")
print("starting training")
for x in range(num_epochs):
  if x % 10 == 0:
    trainNN(True)
  else:
    trainNN(False) 

print("ending training after " + str(num_epochs) + " epochs")
print("percent accuracy: "+str(testing(1000)))


#TESTS
a = np.array([-1, 0, 3, 4])
b = np.array([2,3,4,5])

c = np.array([[2,3,4,5],[1,2,3,4]])
print(np.transpose(c)[1])

x1 = np.array([[1,3],[2,4]])
x2 = np.array([[4,6],[5,7]])

def costFunction(X, Y, m, l):
  
  costVector = [] # Will be a 1 x batch_size vector. Each element is the cost
                  # for one image.
  for i in range(0, m):
    h = np.transpose(X)[i]
    y = np.transpose(Y)[i]
    costPerImage = np.sum((h - y)**2)
    costVector.append(costPerImage)
    
  reg = (0.1 / (2*m))* (np.sum(np.array([0,1,2,3])**2) + np.sum(np.array([[2,3],[4,5]]) ** 2))
  return np.sum(costVector) + reg

print(costFunction(x1, x2, 2, 0))
print(np.sum(x1))
print("hello world")

x_train[1]

