# Author: Howard Tai

# This script contains code for performing hierarchical clustering and automatic
# cluster-selection via the gap statistic

import numpy as np
import matplotlib.pyplot as plt

from scipy import sparse
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import cophenet, fcluster
from scipy.cluster.hierarchy import dendrogram, linkage


#------------------------------------------------------------------------------#
# Clustering helper functions
#------------------------------------------------------------------------------#
def fancy_dendrogram(*args, **kwargs):
    
    # Parse max_d
    max_d = kwargs.pop('max_d', None)
    
    # Set color_threshold
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    
    # Parse annotate_above
    annotate_above = kwargs.pop('annotate_above', 0)
    
    # Create dendrogram object
    dd = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        
        plt.title('Hierarchical Clustering Dendrogram (truncated)')
        plt.xlabel('Sample index or (cluster size)')
        plt.ylabel('Distance')
        
        for i, d, c in zip(dd['icoord'], dd['dcoord'], dd['color_list']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > annotate_above:
                plt.plot(x, y, 'o', c=c)
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                             textcoords='offset points',
                             va='top', ha='center')
        
        # Plot horizontal line if specified
        if max_d:
            plt.axhline(y=max_d, c='k')
    
    return dd


def get_wcv(clusters, means):
    """
    Function for calculating the within-cluster variance values for an input set
    of clusters and respective means
    """
    K = len(means)
    
    wcv = 0
    for i in range(K):
        for c in clusters[i]:
            wcv += np.linalg.norm(c-means[i])**2

    return wcv


def group_clusters(X, labels):
    """
    Function for separating a dataset and cluster labels into cluster groups 
    based and calculating within-cluster means
    """
    unique_labels = np.unique(labels)
    
    groups = []
    means = []
    
    for label in unique_labels:
        label_idx = np.where(labels==label)[0]
        x_subset = X[label_idx]
        
        # Update groups and means
        groups.append(x_subset)
        means.append(np.average(x_subset, axis=0))
    
    return groups, np.array(means).reshape((len(unique_labels),-1))


def bounding_box(X):
    """
    Function for getting min-max coordinates for drawing bounding box for gap
    statistics calculation
    """
    min_max = []
    for i in range(X.shape[-1]):
        min_max.append((np.min(X[:,i]), np.max(X[:, i])))
    return min_max
    

def gap_statistics(Z, X, C=500):
    """
    Helper function for applying a gap statistics calculation over an input 
    dataset to find the optimum number of clusters
    
    Input(s):
    - Z (numpy ndarray): linkage array from scipy's "linkage" function
    - X (numpy ndarary): transformed dataset
    - C (          int): number of clusters (default: 500)
    
    Output(s):
    -   scan_range: range of cluster values scanned
    -     wcv_list: within-cluster variances for the range of scanned clusters
    - uni_wcv_list: within-cluster variances for reference uniform datasets
    -  uni_std_err: standard error for reference uniform datasets
    """
    np.random.seed(0)
    
    N = X.shape[0]
    
    MAX_CLUSTERS = C
    NUM_UNI = 10
    
    # Get bounding box min-max values
    min_max = bounding_box(X)
    
    scan_range = np.arange(1, MAX_CLUSTERS+1)
    wcv_list = np.zeros(MAX_CLUSTERS)
    uni_wcv_list = np.zeros(MAX_CLUSTERS)
    uni_std_err = np.zeros(MAX_CLUSTERS)
    
    # Iterate through 
    for idx, k in enumerate(scan_range):
        if k%10==0:
            print('Scanning: %d'%k)
        
        # Get cluster labels
        labels = fcluster(Z, k, criterion='maxclust')
        
        # Parse dataset into clusters and calculate WCV
        clusters, means = group_clusters(X, labels)
        wcv_list[idx] = np.log(get_wcv(clusters, means))
        
        # Create reference uniform clusters
        wcv_B = np.zeros(NUM_UNI)
        for i in range(NUM_UNI):
            x_uniform = np.zeros((N, len(min_max)))
            for j, mm in enumerate(min_max):
                x_uniform[:, j] = np.random.uniform(mm[0], mm[-1], N)
            
            # Parse reference dataset and calculate WCV
            uni_clusters, uni_means = group_clusters(x_uniform, labels)
            wcv_B[i] = np.log(get_wcv(uni_clusters, uni_means))
        
        # Update uniform WCV list and uniform standard error
        uni_wcv_list[idx] = sum(wcv_B)/NUM_UNI
        uni_std_err[idx] = np.sqrt(sum((wcv_B-uni_wcv_list[idx])**2)/NUM_UNI)
    
    # Group update to standard errors
    uni_std_err = uni_std_err*np.sqrt(1+1/NUM_UNI)
    
    return scan_range, wcv_list, uni_wcv_list, uni_std_err


def best_cluster(ks, logWs, logBWs, stderr, MAX_CLUSTERS=500):
    """
    Locates the best cluster using calculated gap statistic components
    """
    # Calculate complete gap statistic
    gap = logBWs - logWs
    
    k0 = gap[:-1]
    k1 = gap[1:]
    s1 = stderr[1:]
    
    # Calculate criteria
    criteria = (k0 >= (k1-s1))
    
    try:
        crit_idx = np.where(criteria==True)[0]
        return crit_idx+1 # Offset start-at-0 counting
    
    except:
        return MAX_CLUSTERS
#------------------------------------------------------------------------------#


#------------------------------------------------------------------------------#
# Main clustering function
#------------------------------------------------------------------------------#
def create_clusters(X, C=500):
    """
    Main clustering function that performs hierarchical clustering and automatic
    cluster selection using the gap statistic
    """
    # Get linkage matrix
    Z = linkage(X, method='ward')
    
    # Get gap statistics elements
    ks, logWs, logBWs, stderr = gap_statistics(Z, X, C)
    gap_metrics = {
        'ks': ks,
        'logWs': logWs,
        'logBWs': logBWs,
        'stderr': stderr
    }
    
    # Get best cluster labels
    bc = best_cluster(ks, logWs, logBWs, stderr)
    print('\nCluster sizes:', bc)
    clusters = fcluster(Z, bc[0], criterion='maxclust')
    
    return Z, gap_metrics, bc, clusters
#------------------------------------------------------------------------------#