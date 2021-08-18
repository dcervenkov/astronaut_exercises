#!/usr/bin/env python3
import random
import readline
import time
import sys
import threading


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class MyThread(threading.Thread):
    def __init__(self, text):
        super(MyThread, self).__init__()
        # Set the initial prompt
        self.text = text
        self.prompt = f"Solve[0]: {self.text} = "
        self.do_run = True

    def run(self):
        time.sleep(0.01)
        i = 0
        i100 = 0
        while self.do_run:
            i100 += 1
            i = int(i100 / 100)
            # Now we want to change the prompt so that next time input loop asks
            # for prompt it is correct
            str_i = str(i)
            if i > 6:
                str_i = bcolors.WARNING + str(i) + bcolors.ENDC
            if i > 9:
                str_i = bcolors.FAIL + str(i) + bcolors.ENDC

            self.set_prompt(f"Solve[{str_i}]: {self.text} = ")

            # Now overwrite what was there in the prompt
            sys.stdout.write("\r" + self.get_prompt())
            sys.stdout.flush()

            # Get the current line buffer and reprint it, in case some input had
            # started to be entered when the prompt was switched
            sys.stdout.write(readline.get_line_buffer())
            sys.stdout.flush()
            time.sleep(0.01)

    def get_prompt(self):
        return self.prompt

    def set_prompt(self, new_prompt):
        self.prompt = new_prompt


def generate_exercise(op_type):
    if op_type == "add":
        num1 = random.randint(100, 4999)
        num2 = random.randint(100, 4999)
        return f"{num1} + {num2}", num1 + num2
    elif op_type == "sub":
        num1 = random.randint(100, 4999)
        num2 = random.randint(100, num1)
        return f"{num1} - {num2}", num1 - num2
    elif op_type == "mul":
        num1 = random.randint(1, 99)
        num2 = random.randint(1, 99)
        return f"{num1} * {num2}", num1 * num2
    elif op_type == "div":
        num1 = random.randint(1, 99)
        num2 = random.randint(1, 99)
        return f"{num1 * num2} / {num2}", num1


def get_user_input(text):
    myThread = MyThread(text)
    myThread.start()
    answer = input(myThread.get_prompt())
    myThread.do_run = False
    time.sleep(0.01)
    # print("\r")
    return answer


def main():
    try:
        total = int(sys.argv[1])
    except IndexError:
        total = 5

    correct = 0
    close = 0
    margin = 0.1

    for _ in range(total):
        op_type = random.choice(("add", "sub", "mul", "div"))
        exercise, result = generate_exercise(op_type)
        answer = int(get_user_input(exercise))

        result_str = ""
        if answer == result:
            correct += 1
            result_str += bcolors.OKGREEN
        elif (abs(answer - result) / result) < margin:
            close += 1
            result_str += bcolors.WARNING
        else:
            result_str += bcolors.FAIL
        result_str += str(result)
        result_str += bcolors.ENDC

        print(result_str)
        input("Press Enter to continue")
        print("\033[A                             \033[A")
        print()

    print(f"Successful: {correct + close}/{total} ({(correct + close)/total:.0%})")


if __name__ == "__main__":
    main()
