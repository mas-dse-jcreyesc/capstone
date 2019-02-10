import numpy as np
from api.IrsDatasetAbstract import IrsDataset

class IrsDatasetImpl(IrsDataset):
    def __iter__(self):
        """
        REQUIRED for iterable on-line clustering.
        :return: single tuple
        """
        raise RuntimeWarning

    def __len__(self):
        """
        should return the number of tuples in the database (rows)
        :return:
        """
        raise RuntimeWarning

    def open_db_connection(self):
        """
        method to open the db connection
        :return: None
        """
        raise RuntimeWarning

    def close_db_connection(self):
        """
        method to close the db connection
        :return: None
        """
        raise RuntimeWarning

    def get_as_matrix(self):
        """
        returns matrix of data
        :return: numpy.matrix
        """
        raise RuntimeWarning

    def get_shape(self):
        """
        method to return the shape of the data
        :return: (rows, cols)
        """
        raise RuntimeWarning

    def get_feature_columns(self):
        """
        method that returns array of feature names
        :return: list of strings for feature names ex: ['number_of_A', 'name_of_A']
        """
        raise RuntimeWarning

