import random
import numpy as np


class TrainTestSplitter(object):

    def __init__(self, shuffle=False, random_seed=None):
        """
        A generic class for splitting data into (random) subsets.

        Parameters
        ----------
        shuffle : bool, optional
            Whether to shuffle the data.
        random_seed : None | int, optional
            When `shuffle`=True, pseudo-random number generator `random_seed` used for shuffling.
            If None, use default random's RNG for shuffling.
        """
        self.shuffle = shuffle
        self.random_seed = random_seed
        self.rng = random.Random()

    def _flush_rng(self):
        if not self.random_seed is None:
            self.rng.seed(self.random_seed)


    def split(self, y, train_ratio=0.8, stratify=False):
        """
        Split data into train and test subsets.

        Parameters
        ----------
        y : (n_samples,) array-like
            The target variable for supervised learning problems.
        train_ratio : float, 0 < `train_ratio` < 1, optional
            the proportion of the dataset to include in the train split.
        stratify : bool, optional
            If True, the folds are made by preserving the percentage of samples
            for each class. Stratification is done based upon the `y` labels.

        Returns
        -------
        train : (n_train,) ndarray
            The training set indices for that split.
        test : (n_samples - n_train,) ndarray
            The testing set indices for that split.
        """
        self._flush_rng()

        if not stratify:
            indices = range(len(y))
            if self.shuffle:
                self.rng.shuffle(indices)
            train_size = int(train_ratio * len(y))
            return indices[:train_size], indices[train_size:]

        # group indices by label
        labels_indices = {}
        for index, label in enumerate(y):
            if not label in labels_indices:
                labels_indices[label] = []
            labels_indices[label].append(index)

        train, test = [], []
        for label, indices in labels_indices.items():
            size = int(train_ratio * len(indices))
            train += labels_indices[label][:size]
            test += labels_indices[label][size:]

        if self.shuffle:
            self.rng.shuffle(train)
            self.rng.shuffle(test)

        return np.array(train), np.array(test)

    def make_k_folds(self, y, n_folds=3, stratify=False):
        """
        Split data into folds of (approximately) equal size.

        Parameters
        ----------
        y : (n_samples,) array-like
            The target variable for supervised learning problems.
            Stratification is done based upon the `y` labels.
        n_folds : int, `n_folds` > 1, optional
            Number of folds.
        stratify : bool, optional
            If True, the folds are made by preserving the percentage of samples
            for each class. Stratification is done based upon the `y` labels.

        Yields
        ------
        fold : ndarray
            Indices for current fold.
        """
        self._flush_rng()

        if not stratify:
            indices = range(len(y))
            if self.shuffle:
                self.rng.shuffle(indices)
            fold_size = len(y) / n_folds
            for k in xrange(n_folds):
                if k < n_folds - 1:
                    fold = indices[(k * fold_size):((k + 1) * fold_size)]
                else:
                    fold = indices[(k * fold_size):]
                yield np.array(fold)
            return

        # group indices
        labels_indices = {}
        for index, label in enumerate(y):
            if not label in labels_indices:
                labels_indices[label] = []
            labels_indices[label].append(index)

        for k in xrange(n_folds):
            fold = []
            for label, indices in labels_indices.items():
                size = len(indices) / n_folds
                if k != n_folds - 1:
                    fold += indices[(k * size):((k + 1) * size)]
                else:
                    fold += indices[(k * size):]

            if self.shuffle:
                self.rng.shuffle(fold)

            yield np.array(fold)

    def k_fold_split(self, y, n_folds=3, stratify=False):
        """
        Split data into train and test subsets for K-fold CV.

        Parameters
        ----------
        y : (n_samples,) array-like
            The target variable for supervised learning problems.
            Stratification is done based upon the `y` labels.
        n_folds : int, `n_folds` > 1, optional
            Number of folds.
        stratify : bool, optional
            If True, the folds are made by preserving the percentage of samples
            for each class. Stratification is done based upon the `y` labels.

        Yields
        ------
        train : (n_train,) ndarray
            The training set indices for current split.
        test : (n_samples - n_train,) ndarray
            The testing set indices for current split.
        """
        self._flush_rng()

        folds = list(self.make_k_folds(y, n_folds=n_folds, stratify=stratify))
        for i in xrange(n_folds):
            yield np.concatenate(folds[:i] + folds[(i + 1):]), folds[i]


if __name__ == '__main__':
    # run corresponding tests
    import tests.test_model_selection as t
    from testing import run_tests
    run_tests(__file__, t)