
import pandas as pd
from sklearn.model_selection import train_test_split


def test_split_is_reproducible_and_preserves_rows():
    X = pd.DataFrame(
        {
            "customer_age": range(100),
            "tenure": range(100),
        }
    )
    y = pd.Series([0] * 68 + [1] * 32, name="churn")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    assert len(X_train) == 80
    assert len(X_test) == 20
    assert len(y_train) == 80
    assert len(y_test) == 20

    # No original row can occur in both sets.
    assert set(X_train.index).isdisjoint(set(X_test.index))
    assert len(X_train) + len(X_test) == len(X)

    # Stratification preserves the class proportions.
    assert y_train.value_counts().to_dict() == {0: 54, 1: 26}
    assert y_test.value_counts().to_dict() == {0: 14, 1: 6}


def test_split_is_repeatable():
    X = pd.DataFrame({"value": range(50)})
    y = pd.Series([0] * 30 + [1] * 20)

    first = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    second = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    assert first[0].equals(second[0])
    assert first[1].equals(second[1])
    assert first[2].equals(second[2])
    assert first[3].equals(second[3])
