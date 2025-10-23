class PercentHandling:
    def presets():
        preset_additional_info = ""
        print("\nList of presets:\n- Germany\n")
        while True:
            user_preset_choice = input("Please select a preset:\n")
            if user_preset_choice.lower() == "germany":
                preset_name = "Germany"
                preset_starting_population = 65360000 # 1911 estimate
                preset_ending_population = 75000000 # Very rough 1930 estimate
                preset_additional_info = "Preset created using 1911 estimate for starting population and very rough 1930 estimate for ending population. Prefer 1911 population numbers when possible."
                break
            else:
                print("Invalid choice, please try again.\n")

        population_percent_change = PercentHandling.percent_change_calc(preset_starting_population, preset_ending_population)
        print(f"\n{preset_name} has a population percentage change of {population_percent_change}%. {preset_additional_info}")

        input("\nPress enter to continue.")
        return population_percent_change

    def manual_data():
        print("\n\n")
        while True:
            try:
                u_starting_population = input("Starting population:\n")
                starting_population = int(u_starting_population)
                break
            except ValueError:
                print("{u_starting_population} is not a valid integer, please try again.")

        while True:
            try:
                u_ending_population = input("Ending population:\n")
                ending_population = int(u_ending_population)
                break
            except ValueError:
                print("{u_ending_population} is not a valid integer, please try again.")

        population_percent_change = PercentHandling.percent_change_calc(starting_population, ending_population)
        print(f"\nCalculated population percentage change is:\n{population_percent_change}%")

        input("\nPress enter to continue.")
        return population_percent_change

    def percent_change_calc(value1, value2):
        subtracted_value = value2 - value1
        divided_value = subtracted_value / value1
        final_value = divided_value * 100
        return final_value

class PopulationHandling:
    def state_population_calc(ppc):
        while True: # Double while True, perhaps there's something wrong with doing it like this, but it's eaiser for me :p
            while True:
                try:
                    u_starting_population = input("Starting population:\n")
                    starting_population = int(u_starting_population)
                    break
                except ValueError:
                    print("{u_starting_population} is not a valid integer, please try again.")
        
            fppc = ppc/100 # Percent change is stored as frontend percent, need to divide it by 100 to get it to usable percent.

            ending_population = starting_population*(1+fppc)
            
            if ending_population == int(ending_population): # Bruh, why was this so hard to figure out?
                print(f"Calculated population is {int(ending_population)}.\n") # We want int() so it looks pretty.
            else:
                r_ending_population = round(ending_population) # We don't need ugly decimals for population.
                if r_ending_population > ending_population:
                    print(f"Calculated population is {int(ending_population)}, rounded up to nearest whole.\n") # Disclaiming whether rounded up or down for the funsies.
                else:
                    print(f"Calculated population is {int(ending_population)}, rounded down to nearest whole.\n")
            
            user_input = input("Type \"Return\" to return to the startup page or press enter to continue calculating population.\n")
            if user_input.lower() == "return":
                MainMenus.startup()

class MainMenus:
    population_percent_change = 0

    def startup():
        # IEX if you see this I still love FP even if I am at a point where I don't want to work on the mod <3
            # But if you do see this, you're a stalker smh
        print("Welcome to the Fallen Phoenix population calculator!\n\nPlease type \"Preset\" for presets or press enter to input manual data.")
        user_input = input()
        global population_percent_change
        print(user_input)
        if user_input.lower() == "preset":
            population_percent_change = PercentHandling.presets()
        else:
            population_percent_change = PercentHandling.manual_data()
        MainMenus.selected_percent()

    def selected_percent():
        print(f"\nCurrent percentage change is: {population_percent_change}%.\n")
        user_input = input("Type \"Back\" to change percentage or press enter to continue.\n")
        if user_input.lower() == "back":
            MainMenus.startup()
        else:
            PopulationHandling.state_population_calc(population_percent_change)
        

if __name__ == "__main__":
    MainMenus.startup()