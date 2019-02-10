import abc


class IrsDataset(abc.ABC):
    """
    This is an abstract class to specify the interface needed from the data set
    this interface will be used for loading the data for external use like clustering
    """
    def __iter__(self):
        """
        REQUIRED for iterable on-line clustering.
        :return: single tuple
        """
        pass

    def __len__(self):
        """
        should return the number of tuples in the database (rows)
        :return:
        """
        pass

    def open_db_connection(self):
        """
        method to open the db connection
        :return: None
        """
        pass

    def close_db_connection(self):
        """
        method to close the db connection
        :return: None
        """
        pass

    def get_as_matrix(self):
        """
        returns matrix of data
        :return: numpy.matrix
        """
        pass

    def get_shape(self):
        """
        method to return the shape of the data
        :return: (rows, cols)
        """
        pass

    def get_feature_columns(self):
        """
        method that returns array of feature names
        :return: list of strings for feature names ex: ['number_of_A', 'name_of_A']
        """
        pass