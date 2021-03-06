import sys
import math
import copy
import datetime 

def RemoveDoublePoints(xs, ys, zs, elements):
	nopoints = len(xs)
	noelems = len(elements)
	new_xs = []
	new_ys = []
	new_zs = []
	new_elements = []
	replacements = []
	for i in range(0, nopoints):
		DUPLICATE = False
		for j in range(0, len(new_xs)):
			if xs[i]==new_xs[j] and ys[i]==new_ys[j] and zs[i]==new_zs[j]:
				DUPLICATE = True
				replacements.append(j)
		if not DUPLICATE:
			new_xs.append(xs[i])
			new_ys.append(ys[i])
			new_zs.append(zs[i])
			replacements.append(-1)
	#-1, -1, 0, -1, 2


	print("replacements", replacements)

	newlist = []
	index = 0
	for i in range(0, nopoints):
		if replacements[i] == -1:
			newlist.append(index)
			index = index + 1
		else:
			replacement = replacements[i]
			newlist.append(replacement)


	#0 1 -1 2 -1

        print("newlist", newlist)

	#replaced_list = []
	#for i in range(0, nopoints):
	#	if replacements[i] != -1:
	#		position = replacements[i]
	#		replaced_list.append(newlist[position])
	#	else:
	#		replaced_list.append(newlist[i])

	#0 1 0 
	#print("replaced_list", replaced_list)


	for e in range(0, noelems):
		for n in range(0, 3):
			node = elements[e][n]
			if replacements[node] != -1:
				position = replacements[node]
                                print("replacing",node,"with",replacements[node],"at",newlist[position])

				elements[e][n] = newlist[node]
			else:
				elements[e][n] = newlist[node]

	return new_xs, new_ys, new_zs, elements 

def RemoveDoubleElems(elements):
	new_elements = []
	noelems = len(elements)
	for i in range(0, noelems):
		DUPLICATE = False
		for j in range(0, len(new_elements)):
			if elements[i] == new_elements[j]:
				DUPLICATE = True
		if not DUPLICATE:
			new_elements.append(elements[i])

	return new_elements


#The following function takes the existing icosphere surface and normalises its dimension to 1
def Normalize(xs, ys, zs):
	nopoints = len(xs)
	xs_new = []
	ys_new = []
	zs_new = []
	for i in range(0, nopoints):
		r = (xs[i]**2 + ys[i]**2 + zs[i]**2)**0.5
		phi = math.atan2(ys[i],xs[i])
		theta = math.acos(zs[i]/r)

		x = 1.0 * math.sin(theta) * math.cos(phi)
		y = 1.0 * math.sin(theta) * math.sin(phi)
		z = 1.0 * math.cos(theta)

		xs_new.append(x)
		ys_new.append(y)
		zs_new.append(z)

	return xs_new, ys_new, zs_new


#The following function takes the existing icosphere surface and adjusts its dimension to r
def AdjustRadius(xs, ys, zs, r):
        nopoints = len(xs)
        xs_new = []
        ys_new = []
        zs_new = []
        for i in range(0, nopoints):
                #r_current = (xs[i]**2 + ys[i]**2 + zs[i]**2)**0.5
                #phi = math.atan2(ys[i],xs[i])
                #theta = math.acos(zs[i]/r_current)

                x = xs[i] #+ r # r * math.sin(theta) * math.cos(phi)
                y = ys[i] #r * math.sin(theta) * math.sin(phi)
                z = zs[i] + r #* math.cos(theta)
                            
                xs_new.append(x)
                ys_new.append(y)
                zs_new.append(z)
               
        return xs_new, ys_new, zs_new


#The following function adjusts the element indices of the icosphere elements based on which layer it is
def AdjustConnectivity(elems, nlayer, nopoints):
	new_elems = []
	last_elem = len(elems)
	for i in range(0, len(elems)):
		e1 = elems[i][0] + nlayer * nopoints
		e2 = elems[i][1] + nlayer * nopoints
		e3 = elems[i][2] + nlayer * nopoints

		new_elems.append([e1, e2, e3])

	return new_elems

#The following function creates a connectiivty between the first two layers of the mesh
def GetFirstConnectivity(elems, added_elems):
	nofaces = len(elems)
	connectivity = []

	for i in range(0, nofaces):
		#Old elem is the element from the base layer
		old_elem = elems[i]

		#Stacked elem is the element from the new layr
		stacked_elem = added_elems[i]
		oe1 = old_elem[0]
		oe2 = old_elem[1]
		oe3 = old_elem[2]

		se1 = stacked_elem[0]
		se2 = stacked_elem[1]
		se3 = stacked_elem[2]

		#The connectivity exists between the old and stacked element
		prism = [oe1, oe2, oe3, se1, se2, se3]
		connectivity.append(prism)		
	return connectivity

def GetConnectivity(old_connectivity, added_elems, nobasepoints):
	nofaces = len(added_elems)
	connectivity = []
	for i in range(0, nofaces):
                #Stacked elem is the element from the added layer
		se1 = added_elems[i][0] 
		se2 = added_elems[i][1]
		se3 = added_elems[i][2]

                #Old elem is the element from the previous layer
		oe1 = added_elems[i][0] - nobasepoints
		oe2 = added_elems[i][1] - nobasepoints
		oe3 = added_elems[i][2] - nobasepoints

		prism = [oe1, oe2, oe3, se1, se2, se3]

		connectivity.append(prism)

	return connectivity


def StackFirstLayer(xs, ys, zs, r, delta_r, elems):
	#The total number of points corresponds to the length of the x-array
	nopoints = len(xs)

	#Find the new radius of the stacked layer
	new_r = r + delta_r

	#Generate the new set of points base on the original set
	added_xs, added_ys, added_zs = AdjustRadius(xs, ys, zs, new_r) 
	
	#Generate new element connectivities
	added_elems = AdjustConnectivity(elems, 1, nopoints)

	#Determine the connectivity of the triangular prisms
	connectivity = GetFirstConnectivity(elems, added_elems) 

	all_xs = xs + added_xs
	all_ys = ys + added_ys
	all_zs = zs + added_zs

	all_elems = elems + added_elems

	return all_xs, all_ys, all_zs, all_elems, connectivity



def StackLayer(xs, ys, zs, base_xs, base_ys, base_zs, r, delta_r, elems, base_elems, nobasepoints, nlayer, old_connectivity):
        #The total number of points corresponds to the length of the x-array
	nopoints = len(xs)
	print("1old", old_connectivity)
	#Find the new radius of the stacked layer
	new_r = r + delta_r

	#Generate the new set of points
	added_xs, added_ys, added_zs = AdjustRadius(base_xs, base_ys, base_zs, new_r)


	#Generate new element connectivities
	added_elems = AdjustConnectivity(base_elems, nlayer, nobasepoints)

	#print("Added elems:", added_elems)

	#Determine the connectivity of the triangular prisms
	connectivity = GetConnectivity(old_connectivity, added_elems, nobasepoints)
	print("2old", old_connectivity)
	print("2New", connectivity)

	all_xs = xs + added_xs
	all_ys = ys + added_ys
	all_zs = zs + added_zs

	all_elems = elems + added_elems

	connectivity = old_connectivity + connectivity
	print("3all", connectivity)
	return all_xs, all_ys, all_zs, all_elems, connectivity, added_elems


def ReturnSpacing(r):
	spacing = 1.0

	return spacing


def detect_3d_rect_boundaries(xmin, xmax, ymin, ymax, zmin, zmax, elements, nodes, tol):

        boundaries = []

        for e in range(0, len(elements)):

                ele = elements[e]
                n1 = ele[1]
                n2 = ele[2]
                n3 = ele[3]
                n4 = ele[4]
                n5 = ele[5]
                n6 = ele[6]

                ns = [n1, n2, n3, n4, n5, n6]

                nc1 = nodes[n1]
                nc2 = nodes[n2]
                nc3 = nodes[n3]
                nc4 = nodes[n4]
                nc5 = nodes[n5]
                nc6 = nodes[n6]

                ncs = [nc1, nc2, nc3, nc4, nc5, nc6]
                count = 0

                flags = []

                flag1 = 0
                flag2 = 0
                flag3 = 0
                flag4 = 0
                flag5 = 0
                flag6 = 0


                for n in range(0, 6):
                        if abs(ncs[n][1] - xmin) < tol:
                                count = count + 1
                                flag = 4
                                flag4 = flag4 + 1

                        elif abs(ncs[n][1] - xmax) < tol:
                                count = count + 1
                                flag = 2
                                flag2 = flag2 + 1

                        elif abs(ncs[n][2] - ymin) < tol:
                                count = count + 1
                                flag = 5
                                flag5 = flag5 + 1

                        elif abs(ncs[n][2] - ymax) < tol:
                                count = count + 1
                                flag = 6
                                flag6 = flag6 + 1

                        elif abs(ncs[n][3] - zmin) < tol:
                                count = count + 1
                                flag = 1
                                flag1 = flag1 + 1

                        elif abs(ncs[n][3] - zmax) < tol:
                                count = count + 1
                                flag = 3
                                flag3 = flag3 + 1

                        else:
                                flag = 0
                                count = count

                        flags.append(flag)



                if flag1 == 3 or flag1 == 4:
                        

                if flag2 == 3 or flag2 == 4:

                if flag3 == 3 or flag3 == 4:

                if flag4 == 3 or flag4 == 4:

                if flag5 == 3 or flag5 == 4:

                if flag6 == 3 or flag6 == 4:



                if count > 0:
                        #This should remove doubles 	
                        flaglisted = list( dict.fromkeys(flags))
                        for f in range(0, len(flaglisted)):
                                flag = flaglisted[f]
                                if flag > 0:
                                        boundaries.append([ele[0], flag])


        return boundaries


verynegative = -1e20
verypositive = 1e20
verysmall = 1e-20
verylarge = 1e-20



def mesh_get_boundaries(nodes, block_type):

        if block_type == "2d_rect_quad":
                xmin = verypositive
                xmax = verynegative
                ymin = verypositive
                ymax = verynegative
                zmin = 0.0
                zmax = 0.0

                for n in range(0, len(nodes)):
                        xmin = min(xmin, nodes[n][1])
                        xmax = max(xmax, nodes[n][1])
                        ymin = min(ymin, nodes[n][2])
                        ymax = max(ymax, nodes[n][2])

        elif block_type == "3d_box_quad":
                xmin = verypositive
                xmax = verynegative
                ymin = verypositive
                ymax = verynegative
                zmin = verypositive
                zmax = verynegative

                for n in range(0, len(nodes)):
                        xmin = min(xmin, nodes[n][1])
                        xmax = max(xmax, nodes[n][1])
                        ymin = min(ymin, nodes[n][2])
                        ymax = max(ymax, nodes[n][2])
                        zmin = min(zmin, nodes[n][3])
                        zmax = max(zmax, nodes[n][3])


        else:
                sys.exit("Boundary detection for the selected block type not yet implemented. Abording.")



        return xmin, xmax, ymin, ymax, zmin, zmax



def WriteMesh(path, name, block_type, elements, nodes, boundaries, ngrps, nbsets, ndfcd, ndfvl):
        SUCCESS = 0

        filename = path + name

        #The fist line is the control info data
        f = open(filename, "w")
        line = "        CONTROL INFO 2.4.6" + '\n'
        f.write(line)

        #The second line indicates that the output file should be .neu
        line = "** GAMBIT NEUTRAL FILE" + '\n'
        f.write(line)

        #The third line the mesh name
        line = "mesh" + '\n'
        f.write(line)

        #The fourth line the version of the programme
        line = "PROGRAM:                BRCHMESH     VERSION:  0.0.1" + '\n'
        f.write(line)

        #The fifth line is the date and time
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        line = dt_string  + '\n'
        f.write(line)

        #The sixth line the order of the neu mesh paramerets:
        #number of points
        #number of elements
        #number of element groups
        #number of BC sets
        #number of coordinate directions
        #number of fluid velocity directions
        line = "     NUMNP     NELEM     NGRPS    NBSETS     NDFCD     NDFVL" + '\n'
        f.write(line)


        line = str(len(nodes)) + '\n'
        f.write(line)

        line = str(len(elements)) + '\n' #+ len(boundaries)) + '\n'
        f.write(line)

        line = str(ngrps) + '\n'
        f.write(line)

        line = str(nbsets) + '\n'
        f.write(line)

        line = str(ndfcd) + '\n'
        f.write(line)

        line = str(ndfvl) + '\n'
        f.write(line)

        line = "ENDOFSECTION" + '\n'
        f.write(line)


        #For the prism mesh, determine from the boundaries which one is inlet and which one the outlet
        if block_type == "prism":
                inlet = boundaries[0:int(len(boundaries)/2)]
                outlet = boundaries[int(len(boundaries)/2):-1]



        line = "   NODAL COORDINATES 2.4.6" + '\n'
        f.write(line)


        #Next, write all the node coordinates - for each node, the index and coordinates x, y (and z) separated by "\n"
        for n in range(0, len(nodes)):
                node = nodes[n]
                if block_type == "2d_rect_quad":
                        line = str(node[0]+1) + '\n' + str(node[1]) + '\n' + str(node[2])  + '\n'

                elif block_type == "3d_box_quad" or "3d_box_prism" or "prism":
                        line = str(node[0]+1) + '\n' + str(node[1]) + '\n' + str(node[2]) + '\n' + str(node[3])  + '\n'


                else:
                        sys.exit("Writing for the selected block type not yet implemented. Abording.")

                f.write(line)

        line = "ENDOFSECTION" + '\n'
        f.write(line)
        line = "      ELEMENTS/CELLS 2.4.6"  + '\n'
        f.write(line)


        #Next, also write the connectivity of the elements - for each element, its index and the nodex which it is composed of
        for e in range(0, len(elements)):
                ele = elements[e]

                if block_type == "2d_rect_quad":
                        line = str(ele[0]+1) + '\n' + str(2) + '\n' + str(4) + '\n' + str(ele[1]+1) + '\n' + str(ele[2]+1) + '\n' + str(ele[3]+1) + '\n' + str(ele[4]+1) + '\n'

                elif block_type == "3d_box_quad":
                        line = str(ele[0]+1) + '\n' + str(2) + '\n' + str(8) + '\n' + str(ele[1]+1) + '\n' + str(ele[2]+1) + '\n' + str(ele[3]+1) + '\n' + str(ele[4]+1) + '\n' + str(ele[5]+1) + '\n' + str(ele[6]+1) + '\n' + str(ele[7]+1) + '\n' + str(ele[8]+1) + '\n'

                elif block_type == "prism":
                        line = str(ele[0]+1) + '\n' + str(5) + '\n' + str(6) + '\n' + str(ele[1]+1) + '\n' + str(ele[2]+1) + '\n' + str(ele[3]+1) + '\n' + str(ele[4]+1) + '\n' + str(ele[5]+1) + '\n' +  str(ele[6]+1) + '\n'
                elif block_type == "3d_box_prism":
                        line = str(ele[0]+1) + '\n' + str(5) + '\n' + str(6) + '\n' + str(ele[1]+1) + '\n' + str(ele[2]+1) + '\n' + str(ele[3]+1) + '\n' + str(ele[4]+1) + '\n' + str(ele[5]+1) + '\n' +  str(ele[6]+1) + '\n'

                else:
                        sys.exit("Writing for the selected block type not yet implemented. Abording.")

                f.write(line)



        #For the spherical mesh, also add the inlet and outlet boundaries
        if block_type == "prism":

                for b in range(0, len(boundaries)):
                        boundary = boundaries[b]
                        line = str(boundary[0]+1) + '\n' + str(3) + "\n" + str(3) + "\n" + str(boundary[2]+1) + "\n" + str(boundary[3]+1) + "\n" + str(boundary[4]+1) + "\n"
                        f.write(line)

        line = "ENDOFSECTION" + '\n'
        f.write(line)
        line = "       ELEMENT GROUP 2.4.6"  + '\n'
        f.write(line)

        #Next, write up the physical groups - usually just one composed of all the elements and fluid material
        line = "GROUP:" + str(ngrps) + '\n'
        f.write(line)

        line = "ELEMENTS:" + str(len(elements)) + '\n'
        f.write(line)

        line = "MATERIAL:          2"  + '\n'
        f.write(line)

        line = "NFLAGS:          1" + '\n'
        f.write(line)

        line = "                           fluid" + '\n'
        f.write(line)


        left = len(elements)
        i = 0
        line = ""

        if block_type == "2d_rect_quad" or block_type == "3d_box_quad" or block_type == "3d_box_prism":
                for e in range(0, len(elements)):                        
                        ele = elements[e]
                        i = i + 1

                        if i > 9:
                                line = line + str(ele[0]+1)  + '\n'
                                i = 0
                                f.write(line)
                                line = ""

                        else:
                                line = line + str(ele[0]+1) + "\n"

        else: 
                print("ll entities:", len(elements+boundaries))
                for e in range(0, len(elements+boundaries)):
                        ele = (elements+boundaries)[e]
                        i = i + 1

                        if i > 9:
                                line = line + str(ele[0]+1)  + '\n'
                                i = 0
                                f.write(line)
                                line = ""

                        else:
                                line = line + str(ele[0]+1) + "\n"

        if len(line) > 0:
                f.write(line)

        line = "ENDOFSECTION" + '\n'
        f.write(line)
        line = " BOUNDARY CONDITIONS 2.4.6" + '\n'
        f.write(line)



        #Finally, document the boundaries or inlets/outlets into the domain
        if block_type == "2d_rect_quad":
                for flag in range(1, 5):

                        if flag == 1:
                                line = "x0" + '\n'

                        if flag == 3:
                                line = "x1" + '\n'

                        if flag == 2:
                                line = "y0" + '\n'

                        if flag == 4:
                                line = "y1" + '\n'

                        f.write(line)

                        count = 0
                        for b in range(0, len(boundaries)):
                                if boundaries[b][1] == flag:
                                        count = count + 1

                        line = str(count) + '\n'
                        f.write(line)

                        for b in range(0, len(boundaries)):
                                if boundaries[b][1] == flag:
                                        el = boundaries[b][0]
                                        line = str(el+1) + "\n" + str(3) + "\n" + str(flag)  + '\n'
                                        f.write(line)
                line = "ENDOFSECTION" + '\n'
                f.write(line)
                line = " BOUNDARY CONDITIONS 2.4.6" + '\n'
                f.write(line)


        elif block_type == "3d_box_prism":
                for flag in range(1, 7):

                        if flag == 1:
                                line = "z0" + '\n'

                        if flag == 2:
                                line = "x1" + '\n'
                        if flag == 3:
                                line = "z1" + '\n'

                        if flag == 4:
                                line = "x0" + '\n'
                        if flag == 5:
                                line = "y0" + '\n'

                        if flag == 6:
                                line = "y1" + '\n'

                        f.write(line)


                        count = 0
                        for b in range(0, len(boundaries)):
                                if boundaries[b][1] == flag:
                                        count = count + 1

                        line = str(count) + '\n'
                        f.write(line)


                        for b in range(0, len(boundaries)):
                                if boundaries[b][1] == flag:
                                        el = boundaries[b][0]
                                        line = str(el+1) + "\n" + str(5) + "\n" + str(flag)  + '\n'
                                        f.write(line)

                line = "ENDOFSECTION" + '\n'
                f.write(line)
                line = " BOUNDARY CONDITIONS 2.4.6" + '\n'
                f.write(line)

        elif block_type == "prism":
                for flag in range(1, 3):

                        if flag == 1:
                                line = "inlet" + '\n'

                        if flag == 2:
                                line = "outlet" + '\n'


                        f.write(line)


                        count = 0
                        for b in range(0, len(boundaries)):
                                if boundaries[b][1] == flag:
                                        count = count + 1

                        line = str(count) + '\n'
                        f.write(line)


                        for b in range(0, len(boundaries)):
                                if boundaries[b][1] == flag:
                                        el = boundaries[b][0]
                                        line = str(el+1) + "\n" + str(2) + "\n" + str(flag)  + '\n'
                                        f.write(line)

                line = "ENDOFSECTION" + '\n'
                f.write(line)
                line = " BOUNDARY CONDITIONS 2.4.6" + '\n'
                f.write(line)


        else:
                sys.exit("Writing for the selected block type not yet implemented. Abording.")

        line = "ENDOFSECTION" + '\n'
        f.write(line)

        f.close()

        SUCCESS = 1
        return SUCCESS




#Open the ply formatted base icosphere
file1 = open("triplane.ply", "r")

Lines = file1.readlines()

i = 0
ndata = 0
GET_DATA = False
xs = []
ys = []
zs = []
nxs = []
nys = []
nzs = []
nelems = 0
elems = []
GET_ELEM = False

#Load the data from the ply file
for line in Lines:


	#Extract the basic information
	words = line.split(" ")
	if i == 3:
		novertices = int(words[2])
	if i == 10:
		nfaces = int(words[2])
	if i >= 13:
		GET_DATA = True

	#Extract the node coordinates and normals
	if GET_DATA:

		if len(words) == 6:
			xs.append(float(words[0]))
			ys.append(float(words[1]))
			zs.append(float(words[2]))
			nxs.append(float(words[3]))
			nys.append(float(words[4]))
			nzs.append(float(words[5]))

		ndata = ndata + len(words)

		if ndata > 6*novertices:
			GET_ELEM = True
			GET_DATA = False

	#Extract the element connectivities
	if GET_ELEM:
		el = []
		for word in words:
			el.append(int(word))

		elems.append([el[1], el[2], el[3]])
			
	i = i + 1	


print("before remving: ", len(xs))
print("before remving: ", len(elems))
new_connectivity = []
xs, ys, zs, elems = RemoveDoublePoints(xs, ys, zs, elems)
#xs, ys, zs, elems = RemoveDoublePoints(xs, ys, zs, elems)
elems = RemoveDoubleElems(elems)

print("after remving: ", len(xs))
print("after remving: ", len(elems))
print("elems: ", elems)

print(elems[0])
print(elems[-1])
print(xs[0])
print(len(elems))

nobasepoints = len(xs)
base_elems = copy.deepcopy(elems)

#The base elements (initial layer) is also the layer indicating inlet
inlet = copy.deepcopy(elems)


#Set the radius and the spacing of the first layer 
r = 1.0
delta_r = 1.0


#Normalise the ply mesh to one and recompute for given radius
#xs, ys, zs = Normalize(xs, ys, zs)
base_xs = copy.deepcopy(xs)
base_ys = copy.deepcopy(ys)
base_zs = copy.deepcopy(zs)
xs, ys, zs = AdjustRadius(xs, ys, zs, r)

#Add the first layer
all_xs, all_ys, all_zs, all_elems, connectivity = StackFirstLayer(xs, ys, zs, r, delta_r, elems)

n_layers = 15

print("Number of elements:", len(all_elems))
print("Number of vertices:", len(all_xs))
print("Length of connectivity:", len(connectivity))

for l in range(0, n_layers):
	#Increase current radius according to the added layer
	r = r + delta_r

	#Set the spacing of the added layer
	delta_r = ReturnSpacing(r)

	#Reassign node coordinates
	xs = copy.deepcopy(all_xs)
	ys = copy.deepcopy(all_ys)
	zs = copy.deepcopy(all_zs)
	connectivity = copy.deepcopy(connectivity)
	elems = copy.deepcopy(all_elems)
	#Add the next layer
	all_xs, all_ys, all_zs, all_elems, all_connectivity, added_elems = StackLayer(xs, ys, zs, base_xs, base_ys, base_zs, r, delta_r, elems, base_elems, nobasepoints, 2+l, connectivity)
	print("Number of elements:", len(all_elems))
	print("Number of vertices:", len(all_xs))
	print("Length of connectivity:", len(all_connectivity))
	connectivity = all_connectivity

boundaries = []

connectivity = all_connectivity






#boundaries = detect_3d_rect_boundaries(xmin, xmax, ymin, ymax, zmin, zmax, elements, tol):


#The following set of paragraphs adjusts the arrays so that they also contain the indices of the vertices and elements


'''
outlet = copy.deepcopy(added_elems)

for b in range(0, len(inlet)):
	inlet[b] = [1] + inlet[b] 
	#new_entry = 
	#for number in range(0, len(inlet[b])):
	#	new_entry.append(number)
for b in range(0, len(outlet)):
        outlet[b] = [2] + outlet[b]

boundaries_unformatted = inlet + outlet 
boundaries_formatted = []
for b in range(0, len(boundaries_unformatted)):
	elem = boundaries_unformatted[b]
	new_elem = [b + len(connectivity)]
	for number in range(0, len(elem)):
		new_elem.append(elem[number])

	boundaries_formatted.append(new_elem)

elems_formatted = []
'''
elems_formatted = []


tol = 1e-6

for e in range(0, len(connectivity)):
        elem = connectivity[e]
        new_elem = [e]
        for number in range(0, len(elem)):
                new_elem.append(elem[number])
        elems_formatted.append(new_elem)
       

nodes_formatted = []


for n in range(0, len(all_xs)):
        node = [n, all_xs[n], all_ys[n], all_zs[n]]
        nodes_formatted.append(node)

boundaries_formatted = []



block_type = "3d_box_quad"
xmin, xmax, ymin, ymax, zmin, zmax = mesh_get_boundaries(nodes_formatted, block_type)
boundaries_formatted = detect_3d_rect_boundaries(xmin, xmax, ymin, ymax, zmin, zmax, elems_formatted, nodes_formatted, tol)



print(connectivity[0])
print(connectivity[len(connectivity)-1])

print(all_xs[0])
print(all_xs[len(xs)])
print(all_ys[0])
print(all_ys[len(xs)])
print(all_zs[0])
print(all_zs[len(xs)])

'''
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(all_xs, all_ys, all_zs)
plt.show()
'''


path = "/scratch/leuven/338/vsc33811/Mesher/plane_extension/"
name = "plane_15.brch"

block_type = "3d_box_prism"
ngrps = 1
nbsets = 2
ndfcd = 3
ndfvl = 3

print(elems_formatted[0])
written = WriteMesh(path, name, block_type, elems_formatted, nodes_formatted, boundaries_formatted, ngrps, nbsets, ndfcd, ndfvl)

for i in range(0, len(all_xs)):
	print all_xs[i], all_ys[i], all_zs[i]

#print("connectivity:", elems_formatted)
