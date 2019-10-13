import numpy as np

X = np.load("./detector_models/text_log_mailonline_0.7_0.7_0.7_index.npy")
for i in range(X.shape[0]):
    if X[i, 0] == 14502:
        print(X[i])

Y = np.load("./detector_models/text_log_mailonline_0.7_0.7_0.7_events.npy")
print(Y[12107])
