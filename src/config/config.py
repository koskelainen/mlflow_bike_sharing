import pathlib

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

PROJECT_FOLDER = pathlib.Path(__file__).parent.parent.parent

ESTIMATORS_MAPPER = {
    'svm': SVC,
    'knn': KNeighborsClassifier,
    'gbrt': GradientBoostingRegressor,
}

# for plt charts
NUM_WORKERS = -1

RANDOM_STATE = 42
TEST_SIZE = 0.3
