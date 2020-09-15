#! /usr/bin/env python3

import os, sys, re

def redirect(command):
    rc = os.fork()
    if rc < 0:
        sys.exit(1)
    elif rc == 0:  # child
        args = re.split(" ", command)
        if(">" in args):
            pass
        elif("<" in args):
            args[1],args[3] = args[3],args[1]
        args.remove(">")
        args.remove("<")
        os.close(1)  # redirect child's stdout
        os.open(args[2], os.O_CREAT | os.O_WRONLY);
        os.set_inheritable(1, True)
        for dir in re.split(":", os.environ['PATH']):  # try each directory in path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)  # try to exec program
            except FileNotFoundError:  # ...expected
                pass  # ...fail quietly
        sys.exit(1)  # terminate with error
    else:  # parent (forked ok)
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" %
                     childPidCode).encode())


def changeDirectory(newPath):
    try:
        # Change the current working Directory
        os.chdir(newPath)
    except OSError:
        os.write(1, ("Can't change the Current Working Directory\n").encode())


def runNewProcess(args):
    rc = os.fork()
    if rc < 0:
        sys.exit(1)
    elif rc == 0:  # child
        for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)  # try to exec program
            except FileNotFoundError:  # ...expected
                pass  # ...fail quietly

        os.write(2, ("Could not exec %s\n" % args[0]).encode())
        sys.exit(1)  # terminate with error
    else:  # parent (forked ok)
        childPidCode = os.wait()


def piping(args):
    pr, pw = os.pipe()
    for f in (pr, pw):
        os.set_inheritable(f, True)
    args = [i.strip() for i in re.split('[\x7c]', args)]
    print(args)
    rc = os.fork()
    if rc < 0:
        sys.exit(1)
    elif rc == 0:  # child - will write to pipe
        os.close(0)  # redirect child's stdout
        os.dup(pw)
        os.set_inheritable(1, True)
        for fd in (pr, pw):
            os.close(fd)
        childp = args[0].split()
        for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
            program = "%s/%s" % (dir, childp[0])
            try:
                os.execve(program, childp, os.environ)  # try to exec program
            except FileNotFoundError:  # ...expected
                pass  # ...fail quietly
        else:  # parent (forked ok)
            childPidCode = os.wait()
    else:  # parent (forked ok)
        os.close(1)
        os.dup(pr)
        os.set_inheritable(0, True)
        for fd in (pw, pr):
            os.close(fd)
        parentp = args[1].split()
        for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
            program = "%s/%s" % (dir, parentp[0])
            try:
                os.execve(program, parentp, os.environ)  # try to exec program
            except FileNotFoundError:  # ...expected
                pass  # ...fail quietly
        else:  # parent (forked ok)
            childPidCode = os.wait()
    return

def background(args):
    rc = os.fork()
    if rc < 0:
        sys.exit(1)
    elif rc == 0:  # child
        args = args.remove("&")
        for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)  # try to exec program
            except FileNotFoundError:  # ...expected
                pass  # ...fail quietly

        os.write(2, ("Could not exec %s\n" % args[0]).encode())
        sys.exit(1)  # terminate with error
PS1 = "$ "
while True:
    os.write(1, PS1.encode())
    uInput = input()
    uInput = uInput.rstrip()
    inputList = re.split(" ", uInput)
    if ("cd" in inputList):
        #changeDirectory(uInput[3:])
            os.chdir(uInput.split()[1])
            pass
    elif ("exit" in inputList):
        exit()
    elif (">" in inputList):
        redirect(uInput)
    elif ("|" in inputList):
        piping(uInput)
    elif("&" in inputList):
        background(inputList)
    else:
        runNewProcess(inputList)
