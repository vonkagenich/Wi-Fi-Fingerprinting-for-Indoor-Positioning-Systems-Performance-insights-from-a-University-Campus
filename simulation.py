import simpy
import random
import matplotlib.pyplot as plt

# Simulation parameters
num_employees = 10000
scan_time_per_employee = 8  # seconds per employee
arrival_interval_start = 0  # Arrival starts at 7:20 AM (0 seconds from start)
arrival_interval_end = 40 * 60  # Arrival ends at 8:00 AM (2400 seconds)

# Generate employee arrival times (randomly distributed between start and end)
random.seed(0)
arrival_times = sorted([random.uniform(arrival_interval_start, arrival_interval_end) for _ in range(num_employees)])

# Results storage
results = {
    'scanners': [],
    'total_entry_times': [],
    'average_wait_times': [],
    'average_queue_lengths': [],
    'throughputs': [],
    'utilizations': []
}


# Simulate employee entry with given number of scanners
def run_simulation(num_scanners):
    env = simpy.Environment()
    scanner = simpy.Resource(env, capacity=num_scanners)
    wait_times = []
    total_scan_time = 0
    queue_lengths = []

    def employee(env, arrival_time):
        nonlocal total_scan_time
        yield env.timeout(arrival_time)  # Wait until the employee arrives
        with scanner.request() as request:
            queue_entry_time = env.now
            yield request  # Wait until the scanner is available
            wait_time = env.now - queue_entry_time
            wait_times.append(wait_time)

            # Track queue length at the moment of entry into the scanner
            queue_lengths.append(len(scanner.queue))

            yield env.timeout(scan_time_per_employee)  # Scan takes 8 seconds
            total_scan_time += scan_time_per_employee

    # Add employees to the environment
    for arrival_time in arrival_times:
        env.process(employee(env, arrival_time))

    env.run()

    # Calculate results
    total_entry_time = max(arrival_times) + max(wait_times) + scan_time_per_employee
    average_wait_time = sum(wait_times) / len(wait_times)
    throughput = num_employees / (total_entry_time / 60)  # in employees per minute
    avg_queue_length = sum(queue_lengths) / len(queue_lengths)  # average queue length based on observations
    utilization = total_scan_time / (num_scanners * total_entry_time)  # proportion of scanner's busy time

    return total_entry_time / 60, average_wait_time / 60, avg_queue_length, throughput, utilization


# Run simulations for different numbers of scanners
for scanners in [ 5,10,20,30,35]:
    total_time, avg_wait_time, avg_queue_len, throughput, utilization = run_simulation(scanners)
    results['scanners'].append(scanners)
    results['total_entry_times'].append(total_time)
    results['average_wait_times'].append(avg_wait_time)
    results['average_queue_lengths'].append(avg_queue_len)
    results['throughputs'].append(throughput)
    results['utilizations'].append(utilization)

# Plotting results
plt.figure(figsize=(12, 8))

# Average Wait Time
plt.subplot(2, 2, 1)
plt.plot(results['scanners'], results['average_wait_times'], marker='o', color='g')
plt.title('Average Wait Time per Employee')
plt.xlabel('Number of Scanners')
plt.ylabel('Average Wait Time (minutes)')
for i, txt in enumerate(results['average_wait_times']):
    plt.text(results['scanners'][i], txt, f"{txt:.2f} min", fontsize=9, ha='center', va='bottom')

# Average Queue Length
plt.subplot(2, 2, 2)
plt.plot(results['scanners'], results['average_queue_lengths'], marker='o', color='r')
plt.title('Average Queue Length')
plt.xlabel('Number of Scanners')
plt.ylabel('Average Queue Length')
for i, txt in enumerate(results['average_queue_lengths']):
    plt.text(results['scanners'][i], txt, f"{txt:.2f}", fontsize=9, ha='center', va='bottom')

# Throughput
plt.subplot(2, 2, 3)
plt.plot(results['scanners'], results['throughputs'], marker='o', color='purple')
plt.title('Throughput of Employees')
plt.xlabel('Number of Scanners')
plt.ylabel('Throughput (employees per minute)')
for i, txt in enumerate(results['throughputs']):
    plt.text(results['scanners'][i], txt, f"{txt:.2f} emp/min", fontsize=9, ha='center', va='bottom')

# Utilization
plt.subplot(2, 2, 4)
plt.plot(results['scanners'], results['utilizations'], marker='o', color='b')
plt.title('Scanner Utilization')
plt.xlabel('Number of Scanners')
plt.ylabel('Utilization')
for i, txt in enumerate(results['utilizations']):
    plt.text(results['scanners'][i], txt, f"{txt:.2f}", fontsize=9, ha='center', va='bottom')

plt.tight_layout()
plt.show()
