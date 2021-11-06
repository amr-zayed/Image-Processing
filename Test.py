
from numba import jit, njit, vectorize, cuda, uint32, f8, uint8
import numpy as np
# to measure exec time
from timeit import default_timer as timer   

# @jit
# def my_kernel(str_array, check_str, length, lines, result):

#     col,line = cuda.grid(2)
#     pos = (line*(length+1))+col
#     if col < length and line < lines:  # Check array boundaries
#         if str_array[pos] != check_str[col]:
#             result[line] = 0

# normal function to run on cpu
def func(a):                                
    for i in range(10000000):
        a[i]+= 1      
  
# function optimized to run on gpu 
@jit
def func2(a):
    for i in range(10000000):
        a[i]+= 1
if __name__=="__main__":
    n = 10000000                            
    a = np.ones(n, dtype = np.float64)
    b = np.ones(n, dtype = np.float32)
      
    start = timer()
    func(a)
    print("without GPU:", timer()-start)    
      
    start = timer()
    func2(a)
    print("with GPU:", timer()-start)