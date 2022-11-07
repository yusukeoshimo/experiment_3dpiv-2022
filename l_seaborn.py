import seaborn as sb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

mem_path = input('input memmap path >')
label_memmap = np.memmap(mem_path, dtype=np.float16, mode='r').reshape(-1, 3)
df = pd.DataFrame(label_memmap)
df.columns = ['dx', 'dy', 'dz']
df = df.sample(n=1000)
ax = sb.pairplot(df, plot_kws={'alpha':0.5})
ax.set(ylim=(-10, 10), xlim=(-10, 10))
plt.subplots_adjust(wspace=0.15, hspace=0.1)
plt.show()

plt.close()
plt.clf()

ax = sb.heatmap(df.corr(), annot=True, vmax=1, vmin=-1, cmap=plt.cm.RdBu)
plt.show()