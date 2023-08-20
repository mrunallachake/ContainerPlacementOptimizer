#!/bin/bash

if [ ! $1 ]; then
    echo -e "\e[31mERROR : Mandatory argument is missing (apply).\e[39m"
    exit 1
fi

if [ ! $2 ]; then
    echo -e "\e[31mERROR : Mandatory argument is missing (filename).\e[39m"
    exit 1
fi

# get resource utilization
python3 get_vm_utilization.py
out=$?
if [ $out != 0 ]; then
    echo -e "\e[31mERROR : Collecting resource utilization by nodes. $out \e[39m"
    exit 1
fi

# select node to place the container using placement algorithm
python3 placement.py $2
out=$?
if [ $out != 0 ]; then
    echo -e "\e[31mERROR : selecting node for placing container. $out \e[39m"
    exit 1
fi

# deploy the container to the selected node
kubectl apply -f $2
out=$?
if [ $out != 0 ]; then
    echo -e "\e[31mERROR : Placing container on the node. $out \e[39m"
    exit 1
fi