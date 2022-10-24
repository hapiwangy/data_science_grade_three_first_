from email.errors import NonPrintableDefect
import sklearn.metrics
from sklearn import datasets
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

v_n_pair = {'small':1, 'low':1, 'med':2, 'high':3,'big':3, 'vhigh':4, '5more':5,'more':6,'2':2, '3':3, '4':4}

class Node:
    "Decision tree node"
    def __init__(self, entropy, num_samples, num_samples_per_class, predicted_class, num_errors, alpha=float("inf")):
        self.entropy = entropy # the entropy of current node
        self.num_samples = num_samples
        self.num_samples_per_class = num_samples_per_class
        self.predicted_class = predicted_class # the majority class of the split group
        self.feature_index = 0 # the feature index we used to split the node
        self.threshold = 0 # for binary split
        self.left = None # left child node
        self.right = None # right child node
        self.num_errors = num_errors # error after cut
        self.alpha = alpha # each node alpha


class DecisionTreeClassifier:
    def __init__(self, max_depth=4):
        self.max_depth = max_depth

    def _entropy(self,sample_y,n_classes):
        # TODO: calculate the entropy of sample_y and return it
        # sample_y represent the label of node
        # entropy = -sum(pi * log2(pi))
        entropy = 0
        sample_y = np.array(sample_y)
        sample_y1 = [np.sum(sample_y == i) for i in range(n_classes)]
        for y in sample_y1:
            if y > 0:
                entropy += -(y / len(sample_y)) * math.log2(y / len(sample_y))
            else:
                entropy += 0
        return entropy
    def _gini(self, sample_y, n_classes):
        gini = 0
        sample_y = np.array(sample_y)
        sample_y1 = [np.sum(sample_y == i) for i in range(n_classes)]
        for y in sample_y1:
            if y > 0:
                gini += (y / len(sample_y)) ** 2
            else:
                gini += 0
        return 1 - gini        
    def _feature_split(self, X, y,n_classes):
        # Returns:
        #  best_idx: Index of the feature for best split, or None if no split is found.
        #  best_thr: Threshold to use for the split, or None if no split is found.
        m = y.size
        if m <= 1:
            return None, None

        # Entropy of current node.

        best_criterion = self._entropy(y,n_classes)
        best_gini_info = self._gini(y, n_classes)

        best_idx, best_thr = None, None
        # TODO: find the best split, loop through all the features, and consider all the
        # midpoints between adjacent training samples as possible thresholds. 
        # Compute the Entropy impurity of the split generated by that particular feature/threshold
        # pair, and return the pair with smallest impurity.
        ## info_gain來儲存得到的info
        ## info_gain = 目前的entropy - (左/全) * 左entropy - (右/全) * 右entropy
        info_gain = -float('inf')
        for feature_index in range(6):
            threshold = X[:, feature_index]
            c_info_gain = 0
            for thr in threshold:
                thres_l, thres_r = [], []
                c_thr = v_n_pair[thr] + 0.5
                for i, xs in enumerate(X):
                    if v_n_pair[xs[feature_index]] <= c_thr:
                        thres_l.append(y[i])
                    else:
                        thres_r.append(y[i])
                pl = len(thres_l) / len(xs)
                pr = len(thres_r) / len(xs)
                c_info_gain = best_criterion - (pl * self._entropy(thres_l, self.n_classes_) + pr * self._entropy(thres_r, self.n_classes_))
                # c_info_gain = best_gini_info - (pl * self._gini(thres_l, self.n_classes_) + pr * self._entropy(thres_r, self.n_classes_))
                if c_info_gain > info_gain:
                    best_idx = feature_index
                    best_thr = thr
                    info_gain = c_info_gain
        return best_idx, best_thr
    def _build_tree(self, X, y, depth=0):
        num_samples_per_class = [np.sum(y == i) for i in range(self.n_classes_)]
        predicted_class = np.argmax(num_samples_per_class)
        correct_label_num = num_samples_per_class[predicted_class]
        num_errors = y.size - correct_label_num
        node = Node(
            entropy = self._entropy(y,self.n_classes_),
            num_samples=y.size,
            num_samples_per_class=num_samples_per_class,
            predicted_class=predicted_class,
            num_errors=num_errors
        )
        # print(predicted_class)
        if depth < self.max_depth:
            idx, thr = self._feature_split(X, y,self.n_classes_)
            node.threshold = thr
            node.feature_index = idx
            if idx is not None:
                depth += 1
                ## 先把要放到左右子樹的東西放好
                go_lx, go_rx , go_ly, go_ry = [], [], [], []
                for i, xs in enumerate(X):
                    if v_n_pair[xs[idx]] <= v_n_pair[thr]:
                        go_lx.append(xs) 
                        go_ly.append(y[i])
                    else:
                        go_rx.append(xs) 
                        go_ry.append(y[i])
                go_lx = np.array(go_lx)
                go_rx = np.array(go_rx)
                go_ly = np.array(go_ly)
                go_ry = np.array(go_ry)
                if go_rx.size > 0:
                    node.right = self._build_tree(go_rx, go_ry, depth)
                if go_lx.size > 0:
                    node.left = self._build_tree(go_lx, go_ly, depth)
        return node

    def fit(self,X,Y):
        # TODO
        # Fits to the given training data
        self.n_classes_ = 4 
        self.root = self._build_tree(X, Y)

    def predict(self,X):
        pred = [self.make_predictions(x, self.root) for x in X]
        #TODO: predict the label of data
        return pred
    

    def make_predictions(self, x, tree):
    ## 根據自己的root(self.root)和讀進來的東西判斷這個x所屬標籤並且回傳

        if tree.left == None and tree.right == None:
            return tree.predicted_class
        else:
            feature_x = v_n_pair[x[tree.feature_index]]
            if feature_x <= v_n_pair[tree.threshold]:
                return self.make_predictions(x, tree.left)
            else:
                return self.make_predictions(x, tree.right)
    

    def _find_leaves(self, root):
        #TODO
        ## find each node child leaves number
        if root is None:
            return 0 
        if(root.left is None and root.right is None):
            return 1 
        else:
            return self._find_leaves(root.left) + self._find_leaves(root.right)
    ## 找到某個節點往下的所有error的value

    def _error_before_cut(self, root):
        # TODO
        ## return error before post-pruning
        if root is None:
            return 0 
        if(root.left is None and root.right is None):
            return root.num_errors 
        else:
            return self._error_before_cut(root.left) + self._error_before_cut(root.right)

    def _compute_alpha(self, root):
        # TODO
        ## Compute each node alpha
        # alpha = (error after cut - error before cut) / (leaves been cut - 1)
        return (root.num_errors - self._error_before_cut(root)) / (self._find_leaves(self.root) - 1)
    
    def _find_min_alpha(self, root):
        # TODO
        ## Search the Decision tree which have minimum alpha's node
        if root is None:
            return 
        if(root.left is None and root.right is None):
            return  
        else:
            alpha = self._compute_alpha(root)
            if self.alpha > alpha:
                self.pruned_node = root
            self._find_min_alpha(root.left)
            self._find_min_alpha(root.right)
    def _prune(self):
        # TODO
        # prune the decision tree with minimum alpha node
        self.alpha = float('inf')
        self.pruned_node = None
        self._find_min_alpha(self.root)
        self.pruned_node.left = None
        self.pruned_node.right = None


def load_train_test_data(test_ratio=.3, random_state = 1):
    df = pd.read_csv('./car.data', names=['buying', 'maint',
                     'doors', 'persons', 'lug_boot', 'safety', 'target'])
    X = df.drop(columns=['target'])
    X = np.array(X.values)
    y = np.array(df['target'].values)
    label = np.unique(y)
    # label encoding
    for i in range(len(y)):
        for j in range(len(label)):
            if y[i] == label[j]:
                y[i] = j
                break
    y = y.astype('int')
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size = test_ratio, random_state=random_state, stratify=y)
    return X_train, X_test, y_train, y_test


def accuracy_report(X_train_scale, y_train,X_test_scale,y_test,count,max_depth=7, prune_time = 0):

    tree = DecisionTreeClassifier( max_depth=max_depth)
    tree.fit(X_train_scale, y_train)
    pred = tree.predict(X_train_scale)
    t_p , t_t=[], []
    t_pred = sklearn.metrics.accuracy_score(y_train, pred )
    print(" tree train accuracy: %f" 
        % (t_pred))
    t_p.append(t_pred)
    pred = tree.predict(X_test_scale)
    t_pred = sklearn.metrics.accuracy_score(y_test, pred )
    print(" tree test accuracy: %f" 
        % (t_pred))
    t_t.append(t_pred)
    XP = [i for i in range(prune_time + 1)]
    # for i in range(prune_time):
    #     print("=============Cut=============")
    #     tree._prune()
    #     pred = tree.predict(X_train_scale)
    #     t_pred = sklearn.metrics.accuracy_score(y_train, pred)
    #     t_p.append(t_pred)
    #     print(" tree train accuracy: %f"
    #           % (t_pred))
    #     pred = tree.predict(X_test_scale)
    #     t_pred = sklearn.metrics.accuracy_score(y_test, pred)
    #     t_t.append(t_pred)
    #     print(" tree test accuracy: %f"
    #           % (t_pred))
    # plt.subplot(count)
    # plt.scatter(XP, t_p)
    # plt.scatter(XP, t_t)
    

def main():
    count = 611
    X_train, X_test, y_train, y_test = load_train_test_data(test_ratio=.3,random_state = 1)
    accuracy_report(X_train, y_train,X_test,y_test, count, max_depth=16, prune_time=5)

    # plt.show()


if __name__ == "__main__":
    main()
