from errors import *
from data_handler import *
from lstm import *
import time
from pbt_lstm import *
from pbt_proc import *
import multiprocessing
import os
import subprocess


"""
    best.dat format:
        best error
        # hidden layer
        hidden layer sizes
        # epochs
        previous best
        threshold count

    !!!!!!!! TRAIN, TEST, OUT size must be equal here and pbt_base.py !!!!!!!!!!
"""


if __name__ == '__main__':
    best_file = 'PBT/best.dat'

    random.seed(time.time)

    dh = DataHandler('../dailydata/forex/EURUSD.csv')
    dh.timeSeriesToSupervised()
    dh.splitData(1000, 1000, len(dh.tsdata) - 2000)

    train, test, out = dh.getDataSets()

    testx, testy = out[:, 1], out[:, 3]
    testx = testx.reshape(testx.shape[0], 1)
    testx = testx.reshape((testx.shape[0], 1, testx.shape[1]))

    trainx = test[:, 1]
    trainy = pd.read_csv('PBT/errors.csv', header=None).values
    trainy = trainy.reshape(trainy.shape[0], 1)
    trainx = trainx.reshape(trainx.shape[0], 1)
    trainx = trainx.reshape((trainx.shape[0], 1, trainx.shape[1]))

    start = time.time()

    # read data from previous run, if exists. Otherwise initalize.
    best = []
    threshold_count = 0
    prevBest = 9999999
    if os.path.isfile(best_file):
        f = open(best_file)
        bestError = float(f.readline())
        num_hidden_layers = int(f.readline())
        layer_sizes = f.readline().split(',')
        layer_sizes = layer_sizes[:-1]
        layer_sizes = [int(i) for i in layer_sizes]
        epochs = int(f.readline())
        f.readline()
        threshold_count = int(f.readline())
        best = [bestError, [num_hidden_layers, layer_sizes, epochs]]
        prevBest = bestError
    else:
        threshold_count = 0
        best = [9999999, [1, [1,2], 1], []]
        prevBest = best[0]
    if threshold_count >= 10:   #threshold
        print("Threshold count reached.")
        exit(0)

    # create new best file
    p = multiprocessing.Process(target=run, args=(trainx, trainy, testx, testy, best, mse, 10))
    p.start()
    p.join()

    with open(best_file, 'r') as f:
        bestLine = f.readline()
        if float(prevBest) == float(bestLine):
            threshold_count = threshold_count + 1
        else:
            threshold_count = 0
        f.close()

    with open(best_file, 'a') as f:
        f.write(str(prevBest) + '\n')
        f.write(str(threshold_count) + '\n')
        f.close()

    print("Time Elapsed (seconds): " + str(time.time() - start))
    subprocess.Popen(['python', 'PBT/pbt_error.py'])
    exit(0)