#! /usr/bin/env python3

import os, sys, re
def userInput():
    input = os.read(0, 500)
    input = input.decode()
    return input
def redirect(command, inputFile, outputFile):
    rc = os.fork()
    if rc < 0:
        sys.exit(1)
    elif rc == 0:  # child
        args = [command, inputFile]
        os.close(1)  # redirect child's stdout
        os.open(outputFile, os.O_CREAT | os.O_WRONLY);
        os.set_inheritable(1, True)
        for dir in re.split(":", os.environ['PATH']):  # try each directory in path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)  # try to exec program
            except FileNotFoundError:  # ...expected
                pass  # ...fail quietly
        os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
        sys.exit(1)  # terminate with error
    else:  # parent (forked ok)
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" %
                     childPidCode).encode())
def changeDirectory(newPath):
    try:
        # Change the current working Directory
        os.chdir(newPath)
        os.write(1,("Directory changed").encode())
    except OSError:
        os.write(1,("Can't change the Current Working Directory").encode())
def listCD():
    filesInDirectory = os.listdir('.')
    for i in filesInDirectory:
        os.write(1, i.encode())
        os.write(1, "\n".encode())
def runNewProcess(command, file):
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:  # child
        args = [command, file]
        for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)  # try to exec program
            except FileNotFoundError:  # ...expected
                pass  # ...fail quietly

        os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)  # terminate with error

    else:  # parent (forked ok)
        childPidCode = os.wait()
uInput = " "
PS1 = "$ "
while (uInput):
    os.write(1,PS1.encode())
    uInput = userInput()
    uInput = uInput.strip()
    inputList = re.split(" ", uInput)
    if(inputList[0] == "cd"):
        changeDirectory(inputList[1])
    elif(inputList[0] == "ls"):
        listCD()
    elif(inputList[0] == "exit()"):
        exit()
    elif(len(inputList) == 3):
        redirect(inputList[0], inputList[1], inputList[2])
    else:
        runNewProcess(inputList[0], inputList[1])



