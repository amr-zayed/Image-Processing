
from scipy import misc
import numpy as np

orig = misc.imread('bear_original.jpg')
sh = orig.shape[0], orig.shape[1]
noise = np.zeros(sh, dtype='float64')

X, Y = np.meshgrid(range(0, sh[0]), range(0, sh[1]))

A = 40
u0 = 45
v0 = 50

noise += A*np.sin(X*u0 + Y*v0)

A = -18
u0 = -45
v0 = 50

noise += A*np.sin(X*u0 + Y*v0)

noiseada = orig+noise
misc.imsave('bearnoise.jpg', noiseada)