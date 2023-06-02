"""   Akshar Patel R11694765
          CS3361 Project          """


""" This is a program that executes the first 100 steps of a modified cellular life
simulator that recieves an input file from a command line arguement then simmulates 
the 100 steps through an algorithm in which a cell is said to be alive or dead based 
on the cells neighbors. If an alive cell has 2, 4, or 6 alive neighbors, marked with '+'
then it will stay alive for the next step. If a dead cell, marked with '-' has a prime 
number of alive cells, then it will be alive for the next step. Else the cell will be
considered dead for the next step. This program uses multiprocessing where the number 
of threads are inputed through the command line and are by default 1. After running the
simulation for 100 steps, an output file is created from the path given by command line
arguement and will be appended into such file"""
import copy
from multiprocessing import Pool
import time
import argparse

def main():
    st = time.time() #timer for personal testing
    #input arguements from the command line where -i -o are reqired and -t is not and is default 1
    parser = argparse.ArgumentParser(description='description') 
    parser.add_argument('-i', "--input", required=True)
    parser.add_argument('-o,', "--output", required=True)
    parser.add_argument('-t', "--threads", type=int, default=1)
    #parse the arguements into args
    args = parser.parse_args()
    print("Project :: R11694765") #print my R Number 
    file = open(args.input, 'r') #open the file given, if it doesnt exist an error is thrown
    inp = [] #input matrix
    with file as fin:
        for row in fin.read().strip().split('\n'): #append row by row neglecting whitespace 
            inp.append(list(row)) #append into inp
    MAX_PROCESSES = args.threads #set the number of threads
    x_len = len(inp[0]) #find the x length
    y_len = len(inp) #find the y length
    matrix = list() #create a list of lists to be used for the main code
    for i in range(x_len): 
        matrix.append(list()) #add new list into the matrix
        for j in range(y_len):
            matrix[i].append(inp[j][i]) #append the data into the list
    #create the pool with the number of threads
    processPool = Pool(processes=MAX_PROCESSES) 
    runs = 0 #keeping track of the number of runs
    while runs < 100: #run 100 times 
        poolData = list() #create a pool data list to give all my inputs into
        #putting the last column in the front and the first in first in the last spot to account 
        #for y wrapping when splitting up the matrix for the processes
        matrix.insert(0, matrix[len(matrix)-1]) 
        matrix.append(matrix[1])
        #splitting up the matrix and appending it along with the y len and 3 which is the x length into pool data
        for x in range(x_len): #running for each column
            data = [matrix[x:(x+3)], 3, y_len ] #splicing the matrix
            poolData.append(data) #appending the data
        finalData = processPool.map(simu, poolData) #set final data to equal the outputs given after running processes
        #delete unneeded data
        del (poolData)
        del (matrix)
        #create new matrix
        matrix = list()
        for l in range(len(finalData)): #for each process ran
            # print(finalData[l][0])
            matrix.append(finalData[l][0]) #append that row into the new matrix formed after simulating 
        runs += 1 #increase runs 
    output = open(args.output, 'w') #open/create the new output file
    #append the matrix after 100 runs into the output file created/opened
    for y in range(y_len):
        for x in range(x_len):
            output.write(matrix[x][y])
        output.write('\n')
    #timing for personal testing
    end = time.time()
    print(end-st)

"""Simulation function used for checking the neighbors and calculating if the 
    current cell is dead or alive and this func takes input data of a list """
def simu(data):
    copy = data[0] #take the sliced matrix inputed and assign it to copy variable

    mat = list() #create a new matrix of the same size as the input 
    #this will be used to store the output of the simulation
    for x in range(data[1]):
        mat.append(list())
        for y in range(data[2]):
            mat[x].append(0) #making the matrix blank filled with zeros
    #setting x as zero since it is the only column we are focused on simulating 
    x = 1
    for y in range(data[2]): #running through all y values 
        #data wrapping for neighbors 
        left = (x-1) % data[1]
        right = (x+1) % data[1]
        up = (y-1) % data[2]
        down = (y+1) % data[2]
        
        counter = 0 #counter keeping track of alive neighbors
        #checking all 8 neighbors to see if they are alive, if so add 1 to the counter
        if copy[left][up] == '+':
            counter += 1
        if copy[x][up] == '+':
            counter += 1
        if copy[right][up] == '+':
            counter += 1
        if copy[left][y] == '+':
            counter += 1
        if copy[right][y] == '+':
            counter += 1
        if copy[left][down] == '+':
            counter += 1
        if copy[x][down] == '+':
            counter += 1
        if copy[right][down] == '+':
            counter += 1

        #checking the current cell we are focused on to see if it is 
        # a.) dead but with a prime number of alive neighbors
        # b.) alive with 2, 4, or 6 alive neighbors
        #if those requirements are met the current cell is set to alive
        # else it is set to dead
        if copy[x][y] == '-' and (counter == 2 or counter == 3 or counter == 5 or counter == 7):
            mat[x][y] = '+' #matrix filled with zeros assigned the new state of the cell
        elif copy[x][y] == '+' and (counter == 2 or counter == 4 or counter == 6):
            mat[x][y] = '+'#matrix filled with zeros assigned the new state of the cell
        else:
            mat[x][y] = '-'#matrix filled with zeros assigned the new state of the cell
    return mat[1:2] #return the matrix sliced for the middle row since that is the one with the data


if __name__ == '__main__':
    main()
