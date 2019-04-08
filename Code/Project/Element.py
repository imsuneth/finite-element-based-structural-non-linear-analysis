import math

import numpy as np
from numpy.linalg import inv
from Section import *
from log_ import *

class Element:
    K_element_initial=None # refereing gloabal co-ordiante system
    K_element=None
    elementResistingForce=None
    elementUnbalanceForce=None
    initial_call=True

    def __init__(self, id, start_node, end_node, cross_section, n_sections,angle,length):
        self.id = id
        self.start_node = start_node
        self.end_node = end_node
        self.cross_section = cross_section
        self.n_sections = n_sections
        self.angle=angle
        self.length=length
        self.sections = np.empty(n_sections, dtype=Section)

        for section_id in range(n_sections):
            section = Section(section_id, cross_section)
            self.sections.put(section_id, section)



    def rotMatrix(self):
        cosVal = math.cos(self.angle)
        sinVal = math.sin(self.angle)
        return np.array([[cosVal, sinVal, 0, 0, 0, 0], [-sinVal, cosVal, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
                        [0, 0, 0, cosVal, sinVal, 0], [0, 0, 0, -sinVal, cosVal, 0],
                        [0, 0, 0, 0, 0, 1]])  # should return the rotational matrix for the element

    def rigidBodyTransMatrix(self): #L--> length of the element
        L=self.length
        return np.array([[0, 1 / L, 1, 0, -1 / L, 0], [0, 1 / L, 0, 0, -1 / L, 1], [-1, 0, 0, 1, 0, 0]], dtype=float)

    def calInitialElement_K(self):
        self.initial_call=False
        logging.info("Call element %d inital stiffness matrix"%self.id)
        if self.n_sections==3:
            wh = [1 / 3, 4 / 3, 1 / 3]
            x = [-1 ,0, 1]
        elif self.n_sections==4:
            wh = [5 / 6 ,1 / 6, 1 / 6, 5 / 6]
            x = [-1, - 0.447214, 0.447214, 1]
        elif self.n_sections==5:
            wh = [1 / 10, 49 / 90, 32 / 45, 49 / 90, 1 / 10]
            x = [-1, - 0.654654, 0, 0.654654, 1]
        elif self.n_sections==6:
            wh = [0.066667, 0.378475, 0.554858, 0.554858, 0.378475, 0.066667]
            x = [-1, - 0.765055, - 0.285232, 0.285232, 0.765055, 1]

        initialElementFlexibMat=0

        for section_ in range(self.n_sections):
            Section_K = self.sections[section_].analyze([0, 0])
            #print(Section_K[1])
            NP = [[0, 0, 1], [(x[section_] + 1) / 2 - 1, (x[section_] + 1) / 2 + 1, 0]]
            NP=np.array(NP,dtype=float)
            #print(NP)
            fh = inv(Section_K[1])
            #print(fh)
            mat1 = np.transpose(NP)@fh
            #print(mat1)

            initialElementFlexibMat += mat1@NP


        k_element_initial=inv(initialElementFlexibMat)
        #print(self.K_element_initial)
        # print(inv(self.rigidBodyTransMatrix()))
        # #print(self.rotMatrix())
        self.K_element_initial=np.transpose(self.rotMatrix())@np.transpose(self.rigidBodyTransMatrix())@k_element_initial@self.rigidBodyTransMatrix()@self.rotMatrix()
        #print(self.K_element_initial)
        logging.info("return Element %d inital stiffness matrix"%self.id)
        logging.debug("Element %d inital stiffness matrix is: "%self.id)
        logging.debug(self.K_element_initial)

        return self.K_element_initial # 6x6 matrix refering global co-ordinate system


    def analyze(self,tolerance):  # for the first iteration set the initial call to True
        logging.info("Element:%d Sectional level iteration running"%self.id)

        elementDefINCR=np.array([[self.start_node.d_y],[self.start_node.d_x],[self.start_node.md_z],[self.end_node.d_y],[self.end_node.d_x],[self.end_node.md_z]])

        if self.n_sections==3:
            wh = [1 / 3, 4 / 3, 1 / 3]
            x = [-1 ,0, 1]
        elif self.n_sections==4:
            wh = [5 / 6 ,1 / 6, 1 / 6, 5 / 6]
            x = [-1, - 0.447214, 0.447214, 1]
        elif self.n_sections==5:
            wh = [1 / 10, 49 / 90, 32 / 45, 49 / 90, 1 / 10]
            x = [-1, - 0.654654, 0, 0.654654, 1]
        elif self.n_sections==6:
            wh = [0.066667, 0.378475, 0.554858, 0.554858, 0.378475, 0.066667]
            x = [-1, - 0.765055, - 0.285232, 0.285232, 0.765055, 1]

        logging.debug("Element %d roatational matrix is:" % self.id)
        logging.debug(self.rotMatrix(self.angle))
        logging.debug("Element %d rigidBody matrix is:"%self.id)
        logging.debug(self.rigidBodyTransMatrix(self.length))



        rotate=np.matmul(self.rotMatrix(self.angle),elementDefINCR )
        basicSystem= np.matmul(self.rigidBodyTransMatrix(self.length),rotate)


        #########################################################################
        if self.initial_call==True:
            self.calInitialElement_K()  # calculate initialElement Stiffness matrix and update K_element_initial
            self.K_element=self.K_element_initial
            elementForceINCR= np.matmul(self.K_element,basicSystem)
            logging.info("Element %d initial stiffness matrix calculated"%self.id)
            logging.debug("Element %d inital stiffness matrix is"%self.id)
            logging.debug(self.K_element_initial)
        else:
            elementForceINCR=self.elementUnbalanceForce-np.matmul(self.K_element,elementDefINCR)
        #########################################################################



        for section_ in range(self.n_sections): # newton raphson iteration
            logging.info("Element %d sectional iteration running"%self.id)

            NP=[[0,0,1],[(x[section_]+1)/2 -1,(x[section_]+1)/2 +1,0]]
            sectionForceINCR= np.matmul(NP,elementForceINCR)

            Section_K=self.sections[section_].analyze([0,0])

            logging.debug("Element %d section %d is running" % (self.id, section_))
            logging.debug("Element %d section %d section shape function matrix is:"%(self.id,section_))
            logging.debug(NP)
            logging.debug("Element %d section %d section stiffness matrix is:"%(self.id,section_))
            logging.debug(Section_K)

            unbalanceForce=tolerance+1000

            while(unbalanceForce>=tolerance):
                logging.info("Element %d section level convergence running"%self.id)
                sectionDefINCR_ =  np.matmul(np.linalg.inv(Section_K) ,sectionForceINCR)

                cross_section_result=self.cross_section.analyze(sectionDefINCR_)

                sectionResistingForce=cross_section_result[0]

                Section_K = cross_section_result[1]

                unbalanceForce=sectionForceINCR-sectionResistingForce

                sectionForceINCR=unbalanceForce

                logging.debug("Element %d section %d section stiffness:"%(self.id,section_))
                logging.debug(Section_K)
                logging.debug("Element %d section %d section resisting force:" % (self.id, section_))
                logging.debug(sectionResistingForce)
                logging.debug("Element %d section %d section unbalancec force:" % (self.id, section_))
                logging.debug(unbalanceForce)

            logging.debug("Element %d section %d sectional stiffness after converge"%(self.id,section_))
            logging.debug(Section_K)
            self.sections[section_].section_k=Section_K

        elementFlexibMat=0 # calculate element stiffness
        logging.info("Element %d Sectional assembling running"%self.id)
        for section_ in range(self.n_sections):

            NP = [[0, 0, 1], [(x[section_] + 1) / 2 - 1, (x[section_] + 1) / 2 + 1, 0]]
            fh= np.linalg.inv(self.sections[section_].section_k)
            mat1=np.matmul(np.transpose(NP),fh)
            elementFlexibMat+=np.matmul(mat1,NP)

            logging.debug("Element %d section %d section flexibility matrix is"%(self.id,section_))
            logging.debug(fh)

        self.K_element=inv(elementFlexibMat)

        logging.debug("Element %d element stiffness matrix is"%self.id)
        logging.debug(self.K_element)

        self.elementResistingForce=np.matmul(self.K_element,elementDefINCR)
        self.elementUnbalanceForce=elementForceINCR-self.elementResistingForce

        self.info("Element %d element stiffness matrix calculated"%self.id)
        return self.K_element