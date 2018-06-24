import numpy as np
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt

def plot_surface(X, y, clf, title="", xlabel="", ylabel=""):
	x_min, x_max = X.min(), X.max()

	xx, yy = np.meshgrid(np.linspace(x_min[0], x_max[0], num=50),
						 np.linspace(x_min[1], x_max[1], num=50))

	if hasattr(clf, "decision_function"):
		Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
	else:
		Z = clf.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1].reshape(xx.shape)

	fig = plt.figure()
	ax = fig.add_subplot(111)

	ax.contourf(xx, yy, Z, cmap=plt.cm.RdBu, alpha=.8)
	
	ax.scatter(X.iloc[:, 0], X.iloc[:, 1], c=y, cmap=ListedColormap(['#FF0000', '#0000FF']), edgecolors='k')

	ax.set_xlim(left=x_min[0], right=x_max[0])
	ax.set_ylim(bottom=x_min[1], top=x_max[1])
	
	ax.set_title(title)
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)

	plt.show()