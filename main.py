#!/usr/bin/env python3

import time

hidden = "secret_value_12345"

def main():
    print("Starting main script...")
    
    for i in range(10):
        current_iteration = i + 1
        print(f"Iteration {current_iteration}")
        
        # This is where we'll set our breakpoint
        result = current_iteration * 2
        print(f"Result: {result}")
        
        time.sleep(0.5)
    
    print("Main script completed!")

if __name__ == "__main__":
    main()