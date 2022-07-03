import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from sklearn.inspection import permutation_importance

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.config.config import RANDOM_STATE, NUM_WORKERS

plt.style.use("fivethirtyeight")
pandas.plotting.register_matplotlib_converters()


def model_feature_importance(model, X_train, path_folder: Path) -> None:
    feature_importance = pandas.DataFrame(
        model.feature_importances_,
        index=X_train.columns,
        columns=["Importance"],
    )

    # sort by importance
    feature_importance.sort_values(by="Importance", ascending=False, inplace=True)

    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=feature_importance.reset_index(),
        y="index",
        x="Importance",
    ).set_title("Feature Importance")

    plt.savefig(path_folder, bbox_inches='tight')
    plt.close()


def model_permutation_importance(model, X_train, X_test, y_test, path_folder: Path) -> None:
    p_importance = permutation_importance(model, X_test, y_test, random_state=RANDOM_STATE, n_jobs=NUM_WORKERS)

    # sort by importance§
    sorted_idx = p_importance.importances_mean.argsort()[::-1]
    p_importance = pandas.DataFrame(
        data=p_importance.importances[sorted_idx].T,
        columns=X_train.columns[sorted_idx]
    )

    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=p_importance,
        orient="h"
    ).set_title("Permutation Importance")

    plt.savefig(path_folder, bbox_inches="tight")
    plt.close()
