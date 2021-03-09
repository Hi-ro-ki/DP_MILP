#-*-coding:utf-8 -*-
"""
x_i_3_0,x_i_2_0,x_i_1_0,x_i_0_0,......x_i_3_7,x_i_2_7,x_i_1_7,x_i_0_7 denote the left halve 
  of the input of the (i+1)-th round
y_i_3_0,y_i_2_0,y_i_1_0,y_i_0_0,......y_i_3_7,y_i_2_7,y_i_1_7,y_i_0_7 denote the right halve
  of the input of the (i+1)-th round

u_i_3_0,u_i_2_0,u_i_1_0,u_i_0_0,......u_i_3_7,u_i_2_7,u_i_1_7,u_i_0_7 denote the input to 
  the sbox of the (i+1)-th round
v_i_3_0,v_i_2_0,v_i_1_0,v_i_0_0,......v_i_3_7,v_i_2_7,v_i_1_7,v_i_0_7 denote the output to
  the sbox of the (i+1)-th round

"""

from gurobipy import *

import time

class Lici:
	def __init__(self, Round ,Input, U_Min):
		self.x_input=Input
		self.dist=""
		for i in range(64):
				if((self.x_input>>(63-i))&1==0):
						self.dist+="c"
				else:
						self.dist+="a"
				if(i%4==3):
						self.dist+=" "

		#integral order
		self.order=0
		for i in range(64):
                        self.order+=(self.x_input>>i)&1
                                
		#print(self.dist)
		self.Round = Round
		self.blocksize = 64
		
		self.filename_model = "Lici_"+str(self.order)+"th_"+  str(self.Round) +"round_" +str(self.dist) + ".lp"
		self.filename_result = "result_"+str(self.order)+"th_"+  str(self.Round) +"round_" +str(self.dist) + ".txt"
		fileobj = open(self.filename_model, "w")
		fileobj.close()
		fileboj = open(self.filename_result, "w")
		fileobj.close()

		self.u_min=U_Min#manimum of "u"



	# Linear inequalities for the 8 Sboxes used in Lici round function
	S_T=[[1, 1, 1, 1, -1, -1, -1, -1, 0],
	[-3, -2, -1, -2, 2, 3, 4, 1, 2],
	[0, -2, -2, -1, 2, -1, -3, 1, 6],
	[0, 3, 0, 0, -1, -1, -2, -1, 2],
	[1, 0, -1, 1, -2, -2, 1, -1, 3],
	[1, 0, 1, 0, 1, -2, -1, -2, 2],
	[-3, -2, -1, -2, -1, 2, 1, 1, 5],
	[0, -1, -1, -2, 2, 4, 3, 3, 0],
	[3, 1, 1, 1, -2, -2, -2, -1, 1],
	[-1, 0, 0, 1, 1, -1, -2, -1, 3],
	[-1, 1, -2, -1, -1, 1, 0, -1, 4],
	[0, 0, 1, 1, -2, -2, 1, 1, 2],
	[-1, -1, -1, 0, 2, 2, 2, 1, 0],
	[-1, 0, -1, 0, 1, 0, 1, 1, 1],
	[1, 1, 1, 1, -2, 0, -2, 0, 1],
	]
		
	NUMBER = 9

	def CreateObjectiveFunction(self):
		"""
		Create Objective function of the MILP model.
		"""
		fileobj = open(self.filename_model, "a")
		fileobj.write("Minimize\n")
		eqn = []
		for i in range(0,32):
			eqn.append("x" + "_" + str(i) + "_" + str(self.Round))
		for i in range(0,32):
			eqn.append("y" + "_" + str(i) + "_" + str(self.Round))
		temp = " + ".join(eqn)
		fileobj.write(temp)
		fileobj.write("\n")
		fileobj.close()
	

	@staticmethod
	def CreateVariables(n,x): #n:round x:(x,y,a,b,...)
		"""
		Generate the variables used in the model.
		"""
		variable = []
		for i in range(0,32):
			variable.append(x + "_" + str(i) + "_" + str(n))
		return variable

	def ConstraintsBySbox(self, variable1, variable2): # x_in, a
		"""
		Generate the constraints by sbox layer.
		"""
		fileobj = open(self.filename_model,"a")
		for k in range(0,8):
			for coff in Lici.S_T:
				temp = []
				for u in range(0,4):
					temp.append(str(coff[u]) + " " + variable1[(k * 4) + 3 - u])
				for v in range(0,4):
					temp.append(str(coff[v + 4]) + " " + variable2[(k * 4) + 3 - v])
				temp1 = " + ".join(temp)
				temp1 = temp1.replace("+ -", "- ")
				s = str(-coff[Lici.NUMBER - 1])
				s = s.replace("--", "")
				temp1 += " >= " + s
				fileobj.write(temp1)
				fileobj.write("\n")
		fileobj.close(); 


	def ConstraintsByCopy(self,a,b,c):  ####a,b,c or d,e,x_out
		"""
		Generate constraints by split operation.
		"""
		fileobj = open(self.filename_model, "a")
		for i in range(0, 32):
			eqn = []
			eqn.append(a[i])
			eqn.append(b[i])
			eqn.append(c[i])
			temp = " - ".join(eqn)
			temp = temp + " = " + str(0)
			fileobj.write(temp)
			fileobj.write("\n")
		fileobj.close()

	def ConstraintsByXor(self, b,e, y_out): #b,e,y_out or c,y_in,d
		"""
		Generate the constraints by Xor operation.
		"""
		fileobj = open(self.filename_model, "a")
		for i in range(0, 32):
			eqn = []
			eqn.append(y_out[i])
			eqn.append(b[i])
			eqn.append(e[i])
			temp = " - ".join(eqn)
			temp = temp + " = " + str(0)
			fileobj.write(temp)
			fileobj.write("\n")
		fileobj.close()

	@staticmethod
	def VariableRotation(x, n): #  x nbit left rotation　3, 7(25)
		"""
		Bit Rotation.
		"""
		eqn = []
		for i in range(0, 32):
			eqn.append(x[(i + n) % 32])
		return eqn


	
	def Constraint(self):
		"""
		Generate the constraints used in the MILP model.
		"""
		
		fileobj = open(self.filename_model, "a")
		fileobj.write("Subject To\n")
		fileobj.close()
		
		variableinx = Lici.CreateVariables(0, "x")
		variableiny = Lici.CreateVariables(0, "y")

		for i in range(0,self.Round):
		
			variablea = Lici.CreateVariables(i, "a")
			variableb = Lici.CreateVariables(i, "b")
			variablec = Lici.CreateVariables(i, "c")
			variabled = Lici.CreateVariables(i, "d")
			variablee = Lici.CreateVariables(i, "e")
			variableoutx = Lici.CreateVariables((i+1), "x")
			variableouty = Lici.CreateVariables((i+1), "y")
		
		
			
			self.ConstraintsBySbox(variableinx,variablea) 					#sbox(x_in,a)
			self.ConstraintsByCopy(variablea,variableb,variablec)		#copy(a.b.c)
			self.ConstraintsByXor(variablec,variableiny,variabled)		#xor(c,y_in,d)
			variabled = Lici.VariableRotation(variabled,3)					#d<<<3
			self.ConstraintsByCopy(variabled,variablee,variableoutx)		#copy(d,e,x_out)
			self.ConstraintsByXor(variableb,variablee,variableouty)		#xor(b,e,y_out)
			variableouty = Lici.VariableRotation(variableouty,25)				#y_out<<<25
			variableinx = variableoutx
			variableiny = variableouty										#出力入れかえ
	



	def VariableBinary(self):
		"""
		Specify variable type.
		"""
		fileobj = open(self.filename_model, "a")
		fileobj.write("Binary\n")
		for i in range(0, self.Round):
			for j in range(0, 32):
				fileobj.write(("x_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 32):
				fileobj.write(("y_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 32):
				fileobj.write(("a_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 32):
				fileobj.write(("b_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 32):
				fileobj.write(("c_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 32):
				fileobj.write(("d_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 32):
				fileobj.write(("e_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			
		for j in range(0, 32):
			fileobj.write(("x_" + str(j) + "_" + str(self.Round)))
			fileobj.write("\n")
		for j in range(0, 32):
			fileobj.write(("y_" + str(j) + "_" + str(self.Round)))
			fileobj.write("\n")
		fileobj.write("END")
		fileobj.close()

	def Init(self):
		"""
		Generate constraints by the initial division property.
		"""
		#assert(self.activebits < (2 * 32))
		fileobj = open(self.filename_model, "a")
		x = self.CreateVariables(0,"x")
		y = self.CreateVariables(0,"y")

		for i in range(0,32):
			fileobj.write((x[31-i] + " = " + str((self.x_input>>(63-i))&1) ))
			fileobj.write("\n")
		for i in range(0,32):
			fileobj.write((y[31-i] + " = " + str((self.x_input>>(31-i))&1) ))
			fileobj.write("\n")
		
		fileobj.close()




	def MakeModel(self):
		"""
		Generate the MILP model of LBock given the round number and activebits.
		"""
		self.CreateObjectiveFunction()
		self.Constraint()
		self.Init()
		self.VariableBinary()

	def WriteObjective(self, obj):
		"""
		Write the objective value into filename_result.
		"""
		fileobj = open(self.filename_result, "a")
		#writing obj function
		fileobj.write("The objective value = %d\n" %round(obj.getValue()))
		eqn1 = []
		eqn2 = []
		for i in range(0, self.blocksize):
			u = obj.getVar(i)
			#Edit
			#if u.getAttr("x") != 0:#before
			if round(u.getAttr("x")) != 0:
				eqn1.append(u.getAttr('VarName'))
				#Edit
				#eqn2.append(u.getAttr('x'))#Before
				eqn2.append(round(u.getAttr('x')))
		length = len(eqn1)
		for i in range(0,length):
			s = eqn1[i] + "=" + str(eqn2[i])
			fileobj.write(s)
			fileobj.write("\n")
		fileobj.close()

	def SolveModel(self):
		"""
		Solve the MILP model to search the integral distinguisher of Present.
		"""
		time_start = time.time()
		m = read(self.filename_model)
		counter = 0
		set_zero = []
		global_flag = False
		while counter < self.blocksize:
			m.optimize()
			# Gurobi syntax: m.Status == 2 represents the model is feasible.
			if m.Status == 2:
				obj = m.getObjective()
				if round(obj.getValue()) > 1:
					global_flag = True
					break
				else:
					fileobj = open(self.filename_result, "a")
					fileobj.write("************************************COUNTER = %d\n" % counter)
					fileobj.close()
					self.WriteObjective(obj)
					for i in range(0, self.blocksize):
						u = obj.getVar(i)#Position of variable
						#Edit
						#temp = u.getAttr('x')#Value of variable#Before
						temp = round(u.getAttr('x'))#Value of variable
						if temp == 1:
							set_zero.append(u.getAttr('VarName'))
							u.ub = 0
							m.update()
							counter += 1
							break
			# Gurobi syntax: m.Status == 3 represents the model is infeasible.
			elif m.Status == 3:
				global_flag = True
				break
			else:
				print("Unknown error!")

                
                        
                        
		fileobj = open(self.filename_result, "a")
		if global_flag:
			fileobj.write("\n"+str(self.order)+"th_"+str(self.Round)+"round_Integral Distinguisher Found!\n\n")
			print("\n"+str(self.order)+"th_"+str(self.Round)+"round_Integral Distinguisher Found!\n")
			fileobj.close()

			#"""
			if(counter < self.u_min[0]):#If the number of "u" is Minimum,distinguisher is written to file.
				print("self.u_min : "+str(self.u_min))
				self.u_min[0]=counter#updating the minimum of "u"
				file_found = open("Best "+str(self.order)+"th_"+str(self.Round)+"round_Integral Distinguisher.txt","w")
				file_found.write("Initial : " + str(self.dist)+"\n")
				file_found.close()
                        #"""
		else:
			fileobj.write("\n"+str(self.order)+"th_"+str(self.Round)+"round_Integral Distinguisher do NOT exist\n\n")
			print("\n"+str(self.order)+"th_"+str(self.Round)+"round_Integral Distinguisher do NOT exist\n")
			fileobj.close()

		fileobj = open(self.filename_result, "a")
		fileobj.write("Those are the coordinates set to zero: \n")
		for u in set_zero:
			fileobj.write(u)
			fileobj.write("\n")
		fileobj.write("\n")
		time_end = time.time()
		fileobj.write(("Time used = " + str(time_end - time_start)))
		#now we use set_zero
		dist_array=["b","b","b","b","b","b","b","b","b","b","b","b","b","b","b","b",
                          "b","b","b","b","b","b","b","b","b","b","b","b","b","b","b","b",
                          "b","b","b","b","b","b","b","b","b","b","b","b","b","b","b","b",
                          "b","b","b","b","b","b","b","b","b","b","b","b","b","b","b","b",]
		fileobj.write("\n"+str(self.order)+"th_"+str(self.Round)+"round_integral distinguisher\n")
		for u in set_zero:
			if(u[0]=="x"):
				if(u[3]=="_"):
					dist_array[32+int(u[2:3])]="u"
				else:
					dist_array[32+int(u[2:4])]="u"

			else:
				if(u[3]=="_"):
					dist_array[int(u[2:3])]="u"
				else:
					dist_array[int(u[2:4])]="u"
		dist_out=""
		for u in range(64):
			dist_out+=dist_array[63-u]
			if(u%4==3):
				dist_out+=" "
		fileobj.write(dist_out)
		fileobj.close()

	