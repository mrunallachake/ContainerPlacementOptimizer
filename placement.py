
# Uncomment disk code wherever required if  you want to use disk utilization
import yaml
import json
import sys

# Load the YAML file
if len(sys.argv) > 1:
    filename = sys.argv[1]

data = yaml.load(open(filename, "r"), Loader=yaml.FullLoader)

cpu_request = 0
memory_request = 0
# disk_request = 0
cpu_limit = 0
memory_limit = 0
# disk_limit = 0

# Extract the CPU and disk requirements for each container
for container in data['spec']['template']['spec']['containers']:

    cpu_request += int(container['resources']['requests']['cpu'].split('m')[0])
    memory_request += int(container['resources']['requests']['memory'].split('Mi')[0])
    # disk_request +=  int(container['resources']['requests']['ephemeral-storage'].split('Gi')[0])
    cpu_limit += int(container['resources']['limits']['cpu'].split('m')[0])
    memory_limit += int(container['resources']['limits']['memory'].split('Mi')[0])
    # disk_limit +=  int(container['resources']['limits']['ephemeral-storage'].split('Gi')[0])

totalCpuInMilliCPU = 4000
totalMemoryInMi = 15258
# diskInGb = 10
scores = {}

# load file containing utilization data
with open("vm_utilization.json") as my_file:
    vm_utilization = json.loads((my_file.read()))


vm_free = {}
for vm_instance, vm_values in vm_utilization.items():
    vm_free[vm_instance] = {}
    vm_values['avg_cpu_utilization'] = vm_values['avg_cpu_utilization'] * 100
    vm_free[vm_instance]['avg_cpu_free'] = round(totalCpuInMilliCPU - ((vm_values['avg_cpu_utilization'] * totalCpuInMilliCPU) / 100), 2)
    vm_free[vm_instance]['avg_ram_free'] = round(totalMemoryInMi - ((vm_values['avg_ram_utilization'] * totalMemoryInMi) / 100), 2)

    # vm_values['avg_disk_utilization'] = round(diskInGb - ((vm_values['disk_utilization'] * diskInGb) / 100), 2)
    vm_values['avg_cpu_utilization'] = totalCpuInMilliCPU - vm_free[vm_instance]['avg_cpu_free']
    vm_values['avg_ram_utilization'] = totalMemoryInMi - vm_free[vm_instance]['avg_ram_free']
    # TEST FROM HERE 
    percentCpuUsage = ((cpu_limit+vm_values['avg_cpu_utilization'])//totalCpuInMilliCPU) * 100
    percentMemoryUsage = ((memory_limit+vm_values['avg_ram_utilization'])//totalMemoryInMi) * 100
    # percentDiskUsage = (disk_limit//vm_values['avg_disk_utilization']) * 100
    if percentCpuUsage < 80 and percentMemoryUsage < 80 : #and percentDiskUsage < 80

        free_ram_pct = round((vm_free[vm_instance]['avg_ram_free'] - memory_limit)/totalMemoryInMi, 2)
        free_cpu_pct = round((vm_free[vm_instance]['avg_cpu_free'] - cpu_limit)/totalCpuInMilliCPU, 2)
        #free_disk_pct = round((vm_free[vm_instance]['avg_disk_free'] - disk_limit)/diskInGb, 2)

        scores[vm_instance] = free_ram_pct + free_cpu_pct # + free_disk_pct

node = min(scores, key = scores.get)
data["spec"]['template']['spec']["nodeName"] = node

# update deployment yaml file with the selected node name
with open(filename,"w") as my_file:
    yaml.dump(data, my_file, default_flow_style=False)