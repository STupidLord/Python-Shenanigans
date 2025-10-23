def main():
    REDCOLOR = "\033[38;5;1m"
    RESETCOLOR = "\033[0m" # This is just "0m" instead of "38;5;0m" as the later turns the console text black instead of reverting the color.
    
    print(f"This is in {REDCOLOR}RED{RESETCOLOR}.")
    input()

if __name__ == "__main__":
    main()