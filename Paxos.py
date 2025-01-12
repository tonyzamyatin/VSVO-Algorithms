import threading
import time

# Variables to store acceptor states and proposer's round and value
acceptors = []
proposer_value = None
round_number = 0
prepare_value = None


# Proposer class
class Proposer(threading.Thread):
    def __init__(self, prepare_value):
        threading.Thread.__init__(self)
        self.prepare_value = prepare_value

    def run(self):
        global round_number
        global prepare_value

        # Step 1: Proposer sends PREPARE 4 (or the given round)
        round_number = self.prepare_value
        print(f"\nProposer: Sending PREPARE {self.prepare_value}")

        promises = 0
        for acceptor in acceptors:
            # Only accept promises from acceptors that are online and do not have conflicting values
            if acceptor["online"] and (acceptor["promise"] is None or acceptor["promise"] < round_number):
                if acceptor["value"] not in ["",
                                             None]:  # If an acceptor already has a conflicting value, it can't promise
                    # Checking if acceptor has a conflicting value
                    conflicting_value = False
                    for other_acceptor in acceptors:
                        if other_acceptor["value"] != acceptor["value"] and other_acceptor["value"] not in ["", None]:
                            conflicting_value = True
                            break

                    if conflicting_value:
                        print(
                            f"Proposer: Conflict found with acceptor {acceptor['id']} values. Consensus cannot proceed.")
                        return  # Conflict found, abort the process.

                    acceptor["promise"] = round_number
                    promises += 1

        if promises < len(acceptors) // 2 + 1:  # Majority needed
            print("Proposer: Not enough promises. Consensus cannot be reached.")
            return  # Consensus cannot be reached.

        print(f"Proposer: Received {promises} PROMISES")

        # Step 2: Proposer sends ACCEPT-REQUEST 4 'No' (if consensus reached)
        print(f"\nProposer: Sending ACCEPT-REQUEST {self.prepare_value} 'No'")
        accepts = 0
        for acceptor in acceptors:
            if acceptor["online"] and acceptor["promise"] == round_number:
                acceptor["value"] = 'No'
                accepts += 1
        print(f"Proposer: Received {accepts} ACCEPTS")

        # Simulate acceptors going offline and coming online
        print("\nProposer: Simulating acceptors going offline")
        time.sleep(2)  # Wait for acceptors to go offline

        # Acceptors 3, 4, 5 go offline
        for i in range(2, len(acceptors)):  # Acceptor 3, 4, 5 go offline
            acceptors[i]["online"] = False
        print("Proposer: Acceptors 3, 4, 5 are now offline")

        time.sleep(2)  # Wait for acceptors to come back online

        # Acceptors 1 and 2 come online
        for i in range(2):  # Acceptor 1, 2 come back online
            acceptors[i]["online"] = True
        print("Proposer: Acceptors 1 and 2 are now online")

        # Step 3: Proposer sends PREPARE 5
        self.prepare_value = 5
        print(f"\nProposer: Sending PREPARE {self.prepare_value}")

        promises = 0
        for acceptor in acceptors:
            if acceptor["online"] and (acceptor["promise"] is None or acceptor["promise"] < self.prepare_value):
                acceptor["promise"] = self.prepare_value
                promises += 1

        print(f"Proposer: Received {promises} PROMISES")

        print("\nConsensus concluded.")


# Acceptor class
class Acceptor(threading.Thread):
    def __init__(self, id, value):
        threading.Thread.__init__(self)
        self.id = id
        self.value = value
        self.promise = None
        self.online = True

    def run(self):
        while True:
            time.sleep(2)


# Initialize and start the threads
def run_paxos():
    global acceptors

    # Input for number of acceptors
    num_acceptors = int(input("Enter the number of acceptors: "))

    # Input for acceptor IDs and values
    for i in range(num_acceptors):
        acceptor_id = int(input(f"Enter ID for acceptor {i + 1}: "))
        acceptor_value = input(f"Enter value for acceptor {i + 1}: ")

        # If value is blank, set acceptor as offline
        if not acceptor_value.strip():
            acceptors.append({"id": acceptor_id, "value": acceptor_value, "promise": None, "online": False})
            print(f"Acceptor {acceptor_id} is offline (blank value).")
        else:
            acceptors.append({"id": acceptor_id, "value": acceptor_value, "promise": None, "online": True})

    # Start acceptor threads
    acceptor_threads = [Acceptor(acceptor["id"], acceptor["value"]) for acceptor in acceptors]
    for thread in acceptor_threads:
        thread.start()

    # Start proposer
    proposer = Proposer(prepare_value=4)  # Proposer starts with round 4
    proposer.start()

    # Wait for proposer to finish
    proposer.join()
    for thread in acceptor_threads:
        thread.join()


# Run the Paxos consensus simulation
if __name__ == "__main__":
    run_paxos()
