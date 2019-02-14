#Created by Sayf Ahmed for CIS 400

#Importing the random library and the os library to be able to use random numbers and clear text from window.
import random
import os

#Finding what kind of terminal window the system is using to figure out the correct command (Windows vs Unix-based).
if os.name == "nt":
    clearCmd = "cls"
else:
    clearCmd = "clear"





#Function called by __main__
def start():
    #Clearing window.
    os.system(clearCmd)

    #Instructions.
    print("Hello!\nType 'm' to play the memory game or 't' to play the questions game.\nType 'Ctrl' + 'Z' to leave at anytime.")

    #Making while loop that stops when valid input is sent.
    loop = True
    while loop:
        choice = input()
        if choice == "m":
            game = Memory()
            loop = False
        elif choice == "t":
            game = Trivia()
            loop = False
        else:
            print("Invalid input. Please try again.")

    #Running the run method of game chosen.
    game.run()
    exit()






#Memory game class.
class Memory:
    #List of objects used in game.
    objects = ["apple", "banana", "orange", "hammer", "screwdriver", "drill", "television", "laptop", "nintendo wii", "paper",\
    "pencil", "pen", "washer", "dryer", "dishwasher", "mic", "speaker", "headphones", "chalkboard", "whiteboard",\
    "smartboard", "fire", "water", "earth", "seashell", "sand", "ocean", "novel", "dictionary", "comic"]



    #Method to run game.
    def run(self):
        #Clearing window.
        os.system(clearCmd)

        #Instructions.
        print("Welcome to the memory game!\nIn this game, you have to select a bunch of objects turn by turn.")
        print("You can't select an object more than once.\nYou win the game by selecting all objects.")
        print("Good luck!")
        print("\nPress enter to start on easy mode (15 objects) or type anything for hard mode (30 objects).")

        #Clearing window and choosing mode based on input.
        continueGame = input()
        os.system(clearCmd)
        if continueGame == "":
            numOfOb = 15
            print("Begin easy mode.")
        else:
            numOfOb = 30
            print("Begin hard mode.")

        #Shuffling list of objects and creating initial lists and numbers for game.
        shuffled = Memory.shuffleList(Memory.objects)
        shown = [shuffled[i] for i in range(4)]
        selected = []
        count = 4
        level = 1

        #Looping until all items have been selected
        while len(selected) < numOfOb:
            #Printing game info.
            print("Level " + str(level) + " of " + str(numOfOb))
            print("Select a new object.")
            print((" | ").join(shown) + "\n")

            #Getting input and clearing window.
            ans = input()
            os.system(clearCmd)

            #Checking input
            #Wrong answer printout. Also moves to game over method.
            if ans.lower() in selected:
                print("Wrong! You already selected " + ans + ".")
                print("You lose. You made it to level " + str(level) + ".")
                print("Selected items: " + (" | ").join(selected) + "\n")
                print("Shown items: " + (" | ").join(shown) + "\n")
                print("Non-selected items: " + (" | ").join([x for x in shown if x not in selected]) + "\n")
                Memory.gameOver()
                exit()
            #Invalid answer printout.
            elif ans.lower() not in shown:
                print("Invalid input.")
            #Correct answer printout. Also adding to lists and numbers and shuffling for next level.
            else:
                print("Correct!")
                selected.append(ans)
                if count < numOfOb:
                    shown.append(shuffled[count])
                    count += 1
                shown = Memory.shuffleList(shown)
                level += 1

        #Ending game if player has made it this far.
        print("Congratulations! You win!")
        Memory.gameOver()
        exit()



    #Method to shuffle given list
    #Finds length and uses that when random number generating.
    #Shuffles based on reordering values with random indexes.
    def shuffleList(list):
        l = len(list)
        rNums = Memory.makeRandList(l)
        shuffled = [list[rNums[i]] for i in range(l)]
        return shuffled



    #Method to create a list of randomly placed numbers from 0 to given index.
    #Generates random number and adds it to number list if it does not already exist in list.
    def makeRandList(i):
        rl = []
        for x in range(i):
            unique = False
            while (not unique):
                r = random.randint(0,(i-1))
                if r not in rl:
                    rl.append(r)
                    unique = True
        return rl



    #Method that runs in end stage of game and asks user if they want to play again or another game.
    def gameOver():
        print("Play Again? (y or n)")
        response = input()
        if response == "y":
            replay = Memory()
            replay.run()
        elif response == "n":
            loop = True
            while loop:
                print("Play the trivia game? (y or n)")
                response2 = input()
                if response2 == "y":
                    replay = Trivia()
                    loop = False
                    replay.run()
                elif response2 == "n":
                    print("Good Bye!")
                    exit()
                else:
                    print("Invalid input.")
        else:
            print("Invalid input.")
            Memory.gameOver()







#Trivia game class
class Trivia:

    #List of questions to be asked
    questions = ["Who is the author of Python programming? (full name)", "Who was the President of the United States from 2008-2016? (first and last name)",\
    "How many people are on a jury? (number)", "Python got its name from the show _____ Python's Flying Circus", "What is 15 squared?",\
    "What is the class number for the SU Spring 2019 Social Media and Data Mining class (CIS ___)", "Who wrote the Newsies musical?",\
    "What is the capital of Morocco?", "What element is abbreviated as Hg?",\
    """Two trains, Train A and Train B, simultaneously depart Station A and Station B.
Station A and Station B are 200 miles apart from each other. Train A is moving at 120 mph towards Station B, and Train B is moving at 180 mph towards station A.
If both trains departed at 10:00 AM and it is now 10:07, how much longer until both trains pass each other? (__ minutes)"""]

    #List of answers to questions.
    answers = ["guido van rossum", "barack obama", "12", "monty", "225", "400", "alan menken", "rabat", "mercury", "33"]

    #Method to run game.
    def run(self):
        #Clearing window.
        os.system(clearCmd)

        #Instructions.
        print("Welcome to the questions game!\nIn this game, you have to answer 10 questions.")
        print("You get one point by typing in a correct answer for each question. (case-insensitive)\nGood luck!")
        print("\nPress enter to start.")

        #Waiting for user to start.
        continueGame = input()

        #Making dictionary with the questions as keys and their answers as values. Also makes initial score.
        trivDict = {Trivia.questions[k] : Trivia.answers[k] for k in range(10)}
        score = 0

        #Looping through each question and checking if user answer for each question is correct.
        for x in range(10):
            q = Trivia.questions[x]
            print(q)
            ans = input()
            if ans.lower() == trivDict[q]:
                print("Correct!\n")
                score += 1
            else:
                print("Incorrect. The correct answer was " + trivDict[q] + ".\n")

        #End game printout. Also calling game over method.
        print("Game over. You got " + str(score) + " points.")
        if score == 10:
            print("Congratulations! You got a perfect score!")
        Trivia.gameOver()
        exit()



    #Method that runs in end stage of game and asks user if they want to play again or another game.
    def gameOver():
        print("Play Again? (y or n)")
        response = input()
        if response == "y":
            replay = Trivia()
            replay.run()
        elif response == "n":
            loop = True
            while loop:
                print("Play the memory game? (y or n)")
                response2 = input()
                if response2 == "y":
                    replay = Memory()
                    loop = False
                    replay.run()
                elif response2 == "n":
                    print("Good Bye!")
                    exit()
                else:
                    print("Invalid input.")
        else:
            print("Invalid input.")
            Trivia.gameOver()







#__main__ for script
if __name__ == "__main__":
    try:
        start()
    #Closes program if any error occurs.
    except:
        print("Closing program.")
        exit()
