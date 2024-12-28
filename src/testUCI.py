import numpy as np
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.metrics import f1_score

from sklearn.metrics import accuracy_score
from datetime import datetime
import socket
from itertools import product
from ucimlrepo import fetch_ucirepo

import oracledb
from GABDConnect.oracleConnection import oracleConnection as orcl
import logging
from argparse import ArgumentParser


class TestOptions(ArgumentParser):

  def __init__(self):

    super().__init__(
      description="This script runs the experiments on the datasets from the UCI repositori."
    )

    super().add_argument("datasetName", type=str, default=None, help="Name of the dataset.")

    super().add_argument("--user", type=str, default=None, help="string with the user used to connect to the Oracle DB.")
    super().add_argument("--passwd", type=str, default=None,
                         help="string with the password used to connect to the Oracle DB.")
    super().add_argument("--hostname", type=str, default="localhost",
                         help="name of the Oracle Server you want to connect")
    super().add_argument("--port", type=str, default="1521", help="Oracle Port connection.")
    super().add_argument("--serviceName", type=str, default="orcl", help="Oracle Service Name")

    super().add_argument("--ssh_tunnel", type=str, default=None,help="name of the Server you want to create a ssh tunnel")
    super().add_argument("--ssh_user", type=str, default="student",  help="SSH user")
    super().add_argument("--ssh_password", type=str, default=None, help="SSH password")
    super().add_argument("--ssh_port", type=str, default="22", help="SSH port")



  def parse(self):
    return super().parse_args()


if __name__ == "__main__":

    args = TestOptions().parse()

    host = socket.gethostname()
    numIterations = 2
    Algorithms = {
        'Support Vector Machines': SVC,
        'K nearest Neighbor': KNN,
        'Random Forest': RFC
    }
    params = { 'SVC' : {'kernel': ("linear", "rbf", "poly"),
                        'gamma': [1, 5, 10, 20]},
               'KNeighborsClassifier' : { 'n_neighbors' : [3, 5, 10, 15]},
               'RandomForestClassifier' : {'max_depth': [2, 4, 10, None],
                        'criterion': ['gini', 'entropy', 'log_loss']}
               }

    DATASETS = {"Iris":"Iris", "BreastCancer":"Breast Cancer Wisconsin (Diagnostic)",
                "Ionosphere":"Ionosphere", "Letter":"Letter Recognition"}


    dataset = fetch_ucirepo(name=DATASETS[args.datasetName])
    Xo = dataset.data.features.to_numpy()
    labels = dataset.data.targets.to_numpy().reshape(-1)
    lut = {l: e for e, l in enumerate(np.unique(labels))}
    yo = np.array([lut[l] for l in labels])


    n_sample = len(Xo)

    np.random.seed(0)

    current_time = datetime.now().strftime("%d/%m/%Y, %H:%M")

    for k in Algorithms:
        classificador = Algorithms[k].__name__
        c_params = params[classificador].keys()
        for idx,values in enumerate(product(*params[classificador].values())):
            cp = {k: v for k, v in zip(c_params, values) if v is not None}
            clf = Algorithms[k](**cp)
            for i in range(numIterations):
                order = np.random.permutation(n_sample)
                X = Xo[order]
                y = yo[order].astype(float)

                X_train = X[: int(0.9 * n_sample)]
                y_train = y[: int(0.9 * n_sample)]
                X_test = X[int(0.9 * n_sample) :]
                y_test = y[int(0.9 * n_sample) :]


                # Si no executem el script a la màquina main de la pràctica visualitzem els resultats

                # fit the model
                clf.fit(X_train, y_train)

                y_pred = clf.predict(X_test)

                f1_s = f1_score(y_test, y_pred, average='macro')
                acc = accuracy_score(y_test, y_pred)
                print(
                    "Classificador: {}, Iteracio: {}, paràmetres: {}, time: {}, f-score: {}, accuracy: {}".format(k, i, cp, current_time, f1_s,
                                                                                                acc))