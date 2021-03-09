#-*-coding:utf-8 -*-
"""
x_i_63,x_i_62,....x_i_0 denote the input to the (i+1)-th round.
"""

from gurobipy import *

import time

#28th integral


class Mantra:
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
		
		self.filename_model = "Mantra_"+str(self.order)+"th_"+  str(self.Round) +"round_" +str(self.dist) + ".lp"
		self.filename_result = "result_"+str(self.order)+"th_"+  str(self.Round) +"round_" +str(self.dist) + ".txt"
		fileobj = open(self.filename_model, "w")
		fileobj.close()
		fileboj = open(self.filename_result, "w")
		fileobj.close()

		self.u_min=U_Min#manimum of "u"

	# Linear inequalities for the Mantra Sbox
	S_T=[
	[1, 1, 1, 1, -1, -1, -1, -1, 0],
	[-3, -3, -5, -4, -1, 2, 2, 4, 8],
	[0, 0, 3, 0, -1, -1, -1, -1, 1],
	[-1, 0, -2, -1, 1, -3, 2, -1, 5],
	[0, -1, -2, -1, 1, 2, -3, -1, 5],
	[-1, -1, 0, 0, 2, 2, 2, 1, 0],
	[3, 0, 0, 1, -1, -2, -1, -2, 2],
	[0, 3, 0, 1, -1, -1, -2, -2, 2],
	[0, 0, -1, -1, 1, 1, 1, 2, 0],
	[0, 1, 0, 0, -1, 0, 0, -1, 1],
	[0, -1, -1, 1, 1, 0, -1, 1, 2]
	]
	NUMBER = 9

	#make objective function
	def CreateObjectiveFunction(self):
		"""
		Create objective function of the MILP model
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

	#rotation
	def VariableRotation(self,x, n): #n:3,8 c,e
		"""
		Bit Rotation.
		"""
		eqn = []
		for i in range(0, 16):
			eqn.append(x[(i + n) %16])
		return eqn


	def CreateConstrainsCopy16(self,x_in, y_out1,y_out2):
		"""
		Generate constraints by split operation.
		"""
		fileobj = open(self.filename_model, "a")
		for i in range(0,16):
			eqn = []
			eqn.append(x_in[i])
			eqn.append(y_out1[i])
			eqn.append(y_out2[i])
			temp = " - ".join(eqn)
			temp = temp + " = " + str(0)
			fileobj.write(temp)
			fileobj.write("\n")
		fileobj.close()

	def CreateConstrainsCopy32(self,x_in, y_out1,y_out2):
		"""
		Generate constraints by split operation.
		"""
		fileobj = open(self.filename_model, "a")
		for i in range(0,32):
			eqn = []
			eqn.append(x_in[i])
			eqn.append(y_out1[i])
			eqn.append(y_out2[i])
			temp = " - ".join(eqn)
			temp = temp + " = " + str(0)
			fileobj.write(temp)
			fileobj.write("\n")
		fileobj.close()

	def CreateVariable16(self, n, x):
		"""
		Generate variables used in the model.
		"""
		variable = []
		for i in range(0,16):
			variable.append(x + "_" + str(i) + "_" + str(n))
		return variable

	def CreateVariable32(self, n, x):
		"""
		Generate variables used in the model.
		"""
		variable = []
		for i in range(0,32):
			variable.append(x + "_" + str(i) + "_" + str(n))
		return variable

        #S-Box Layer
	def ConstraintsBySbox(self, variable1, variable2):
		"""
		Generate the constraints by sbox layer.
		"""
		fileobj = open(self.filename_model,"a")
		for k in range(0,4):
			for coff in Mantra.S_T:
				temp = []
				for u in range(0,4):
					temp.append(str(coff[u]) + " " + variable1[(k * 4) + 3 - u])
				for v in range(0,4):
					temp.append(str(coff[v + 4]) + " " + variable2[(k * 4) + 3 - v])
				temp1 = " + ".join(temp)
				temp1 = temp1.replace("+ -", "- ")
				s = str(-coff[Mantra.NUMBER - 1])
				s = s.replace("--", "")
				temp1 += " >= " + s
				fileobj.write(temp1)
				fileobj.write("\n")
		fileobj.close();

	def CreateConstraintsXor16(self,x_in1, x_in2,y_out):
		"""
		Generate the constraints by Xor operation.
		"""
		fileobj = open(self.filename_model, "a")
		for i in range(0, 16):
			eqn = []
			eqn.append(y_out[i])
			eqn.append(x_in1[i])
			eqn.append(x_in2[i])

			temp = " - ".join(eqn)
			temp = temp + " = " + str(0)
			fileobj.write(temp)
			fileobj.write("\n")
		fileobj.close()

	def CreateConstraintsXor32(self,x_in1, x_in2,y_out):
		"""
		Generate the constraints by Xor operation.
		"""
		fileobj = open(self.filename_model, "a")
		for i in range(0, 32):
			eqn = []
			eqn.append(y_out[i])
			eqn.append(x_in1[i])
			eqn.append(x_in2[i])

			temp = " - ".join(eqn)
			temp = temp + " = " + str(0)
			fileobj.write(temp)
			fileobj.write("\n")
		fileobj.close()

	def Constraint(self):

		fileobj = open(self.filename_model, "a")
		fileobj.write("Subject To\n")
		fileobj.close()
		x_in = self.CreateVariable32(0,"x")
		y_in = self.CreateVariable32(0,"y")


		for i in range(0, self.Round):
			#set up variables
			x_out = self.CreateVariable32((i+1), "x") #32bit
			y_out = self.CreateVariable32((i+1), "y")
			a = self.CreateVariable32(i, "a")
			#b = self.CreateVariable16(i, "b") #16bit
			#c = self.CreateVariable16(i, "c")
			d = self.CreateVariable16(i, "d")
			e = self.CreateVariable16(i, "e")			
			f = self.CreateVariable16(i, "f")
			g = self.CreateVariable16(i, "g")
			h = self.CreateVariable16(i, "h")
			m = self.CreateVariable16(i, "m") #iだとfor 変数iと被るので変更
			j = self.CreateVariable16(i, "j")
			k = self.CreateVariable16(i, "k")
			#l = self.CreateVariable32(i, "l") #32bit
			#make a constrains
			self.CreateConstrainsCopy32(x_in,a, y_out)#copy (1)

			b=a[:16]
			c=a[16:]
			self.CreateConstrainsCopy16(b,d,e)#copy (2)
			self.ConstraintsBySbox(d,f)#sbox(1)
			self.CreateConstraintsXor16(self.VariableRotation(c,3),f,g)#xor (1)

			self.CreateConstrainsCopy16(g,h,m)#copy (3)
			self.ConstraintsBySbox(h,j)#sbox(2)
			self.CreateConstraintsXor16(self.VariableRotation(e,8),j,k)#xor (2)
			l=k+m
			self.CreateConstraintsXor32(l,y_in,x_out)#xor (3)

			#take over
			x_in=x_out
			y_in=y_out

	def BinaryVariable(self):
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
				fileobj.write(("a_"+ str(j) + "_"  + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("d_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("e_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("f_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("g_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("h_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("m_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("j_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("k_" + str(j) + "_" + str(i)))
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


		fileobj = open(self.filename_model, "a")
		x = self.CreateVariable32(0,"x")
		y = self.CreateVariable32(0,"y")



		for i in range(0,32):
			#fileobj.write((x[31-i] + " = " + str((self.x_input>>(63-i))&1) ))
			fileobj.write((x[i] + " = " + str((self.x_input>>(63-i))&1) ))

			fileobj.write("\n")
		for i in range(0,32):
			#fileobj.write((y[31-i] + " = " + str((self.x_input>>(31-i))&1) ))
			fileobj.write((y[i] + " = " + str((self.x_input>>(31-i))&1) ))

			fileobj.write("\n")
		fileobj.close()

	def MakeModel(self):
		"""
		Generate the MILP model of Present given the round number and activebits.
		"""
		self.CreateObjectiveFunction()
		self.Constraint()
		self.Init()
		self.BinaryVariable()
	########################## I edited some points by using round() so that I let obj-values Round-off(sisyagonyu).
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
		"""
		for u in set_zero:
			if(u[4]=="_"):
				dist_array[int(u[1:2])*16+int(u[3:4])]="u"
			else:
				dist_array[int(u[1:2])*16+int(u[3:5])]="u"
		dist_out=""
		for u in range(64):
			dist_out+=dist_array[63-u]
			if(u%4==3):
				dist_out+=" "
		"""
		for u in set_zero:
			if(u[0]=="y"):
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
			dist_out+=dist_array[u]
			if(u%4==3):
				dist_out+=" "


		fileobj.write(dist_out)
		fileobj.close()
