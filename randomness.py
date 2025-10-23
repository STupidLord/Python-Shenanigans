import datetime as dt

if __name__ == "__main__":    
    time_is = dt.timezone(offset=dt.timedelta(hours=2))
    time_is = dt.datetime.now(tz=time_is)
    time_is = time_is.strftime('%f%S%M%H%d%m%Y')
    print(time_is)
    
    while True:
        x = input("X: ")

        try:
            x = float(x)
            print(x)
            break
        except ValueError:
            print("\'" + x + "\' is not a decimal number, please try again.")

    if x > 9:
        print(str(x) + " is greater than 9")
    elif 10 > x > 5:
        print(str(x) + " is greater than 5, but less than 10.")
    else:
        print(str(x) + " is less than 6.")
    
    while True:
        user_input = input("")
        if user_input == "fuck":
            print("you")
            exit()
        elif user_input == "a":
            while True:
                match user_input:
                    case "a":
                        print("b")
                        user_input = "b"
                    case "b":
                        print("c")
                        user_input = "c"
                    case "c":
                        print("d")
                        user_input = "d"
                    case "d":
                        print("e")
                        user_input = "e"
                    case "e":
                        print("f")
                        user_input = "f"
                    case "f":
                        print("g")
                        user_input = "g"
                    case "g":
                        print("h")
                        user_input = "h"
                    case "h":
                        print("i")
                        user_input = "i"
                    case "i":
                        print("j")
                        user_input = "j"
                    case "j":
                        print("k")
                        user_input = "k"
                    case "k":
                        print("l")
                        user_input = "l"
                    case "l":
                        print("m")
                        user_input = "m"
                    case "m":
                        print("n")
                        user_input = "n"
                    case "n":
                        print("o")
                        user_input = "o"
                    case "o":
                        print("p")
                        user_input = "p"
                    case "p":
                        print("q")
                        user_input = "q"
                    case "q":
                        print("r")
                        user_input = "r"
                    case "r":
                        print("s")
                        user_input = "s"
                    case "s":
                        print("t")
                        user_input = "t"
                    case "t":
                        print("u")
                        user_input = "u"
                    case "u":
                        print("v")
                        user_input = "v"
                    case "v":
                        print("w")
                        user_input = "w"
                    case "w":
                        print("x")
                        user_input = "x"
                    case "x":
                        print("y")
                        user_input = "y"
                    case "y":
                        print("z")
                        user_input = "z"
                    case "z":
                        print("alphabet")
                        break