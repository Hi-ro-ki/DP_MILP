# Algorithm 3 presented in paper "Applyint MILP Method to Searching Integral 
# Distinguishers based on Division Property for 6 Lightweight Block Ciphers"
# Regarding to the paper, please refer to https://eprint.iacr.org/2016/857
# For more information, feedback or questions, pleast contact at xiangzejun@iie.ac.cn

# Implemented by Xiang Zejun, State Key Laboratory of Information Security, 
# Institute Of Information Engineering, CAS
import itertools
from mantra import Mantra

if __name__ == "__main__":

	ROUND = int(input("Input the target round number: "))
	while not (ROUND > 0):
		print("Input a round number greater than 0.")
		ROUND = int(input("Input the target round number again: "))
        #combination
		
	#l=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
	l=[48,49,50,52,53,54,56,57,58,60,61,62]
	#l=[63,62,61,60,59,58,57,56,55,54,53,52,51,50,49,48,47,46,45,44,43,42,41,40,39,38,37,36,35,34,33,32]
	a=list(itertools.combinations(l,2))
	

	U_Min=[64]
	
	Input=0xffff0fffffffffff
	mantra = Mantra(ROUND,Input,U_Min)
	mantra.MakeModel()
	mantra.SolveModel()


	Input=0xfffff0ffffffffff
	mantra = Mantra(ROUND,Input,U_Min)
	mantra.MakeModel()
	mantra.SolveModel()


	Input=0xffffff0fffffffff
	mantra = Mantra(ROUND,Input,U_Min)
	mantra.MakeModel()
	mantra.SolveModel()


	Input=0xfffffff0ffffffff
	mantra = Mantra(ROUND,Input,U_Min)
	mantra.MakeModel()
	mantra.SolveModel()

