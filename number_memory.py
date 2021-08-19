#!/usr/bin/env python3
import io
import os
import time
import readline
import threading
import random
import sys
from contextlib import contextmanager

from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


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
    def __init__(self):
        super(MyThread, self).__init__()
        # Set the initial prompt
        self.prompt = "Input[0]: "
        self.do_run = True
        self.valid = True

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
                self.valid = False

            self.set_prompt(f"Input[{str_i}]: ")

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


@contextmanager
def stderr_redirected(to=os.devnull):
    """
    import os

    with stdout_redirected(to=filename):
        print("from Python")
        os.system("echo non-Python applications are also supported")
    """
    fd = sys.stderr.fileno()

    def _redirect_stderr(to):
        sys.stderr.close()  # + implicit flush()
        os.dup2(to.fileno(), fd)  # fd writes to 'to' file
        sys.stderr = os.fdopen(fd, "w")  # Python writes to fd

    with os.fdopen(os.dup(fd), "w") as old_stderr:
        with open(to, "w") as file:
            _redirect_stderr(to=file)
        try:
            yield  # allow code to be run with the redirected stdout
        finally:
            _redirect_stderr(to=old_stderr)  # restore stdout.


def generate_sequences(number, length, min_num, max_num):
    sequences = []
    for _ in range(number):
        sequences.append([random.randint(min_num, max_num) for _ in range(length)])
    return sequences


def user_text_to_sequence(text):
    # text_sequence = answer.replace(" ", "").split(",")
    sequence = []
    for element in text:
        if element.isnumeric():
            sequence.append(int(element))
        else:
            sequence.append("_")
    return sequence


def compare_sequences(orig, user):
    if orig == user:
        print(
            (
                f"Correct digits: {len(orig)}/{len(orig)} "
                f"({len(orig)/len(orig) * 100:.0f}%)"
            )
        )
        input("Press Enter to continue")
        print("\033[A                             \033[A")
        return len(orig), len(orig)
    else:
        max_len = max(len(orig), len(user))
        print(f"True: {orig}")
        print("User: [", end="")
        num_correct = 0
        for i, number in enumerate(orig):
            if i < len(user):
                user_number = user[i]
            else:
                user_number = "_"

            if user_number == number:
                print(number, end="")
                num_correct += 1
            else:
                print(bcolors.FAIL + str(user_number) + bcolors.ENDC, end="")
            if i < max_len - 1:
                print(", ", end="")
        if len(user) > len(orig):
            for i in range(len(orig), len(user)):
                if i < len(user):
                    user_number = user[i]
                else:
                    user_number = "_"
                print(bcolors.FAIL + str(user_number) + bcolors.ENDC, end="")
                if i < len(user) - 1:
                    print(", ", end="")
        print("]")
        print(
            (
                f"Correct digits: {num_correct}/{len(orig)} "
                f"({num_correct/len(orig) * 100:.0f}%)"
            )
        )
        input("Press Enter to continue")
        print("\033[A                             \033[A")
        # print("\r")
        return len(orig), num_correct


def get_beeps():
    tts = gTTS(text="beep", lang="en", slow=False)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    beep = AudioSegment.from_file(mp3_fp, format="mp3")
    silence = AudioSegment.silent(duration=7000)
    return silence + beep + beep + beep


def get_user_input():
    myThread = MyThread()
    myThread.start()
    answer = input(myThread.get_prompt())
    myThread.do_run = False
    time.sleep(0.01)
    print("\r")
    return answer, myThread.valid


sequences = []
for length in range(6):
    length = random.randint(3, 13)
    sequences.append(*generate_sequences(1, length, 1, 9))

total_length = 0
total_correct = 0

for sequence in sequences:
    text = ",".join(list(map(str, sequence)))
    tts = gTTS(text=text, lang="en", slow=False)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    speech = AudioSegment.from_file(mp3_fp, format="mp3")
    print("Listen to the sequence...")
    with stderr_redirected():
        play(speech)

    answer, valid = get_user_input()

    user_sequence = user_text_to_sequence(answer)
    length, correct = compare_sequences(sequence[::-1], user_sequence)

    total_length += length
    if valid:
        total_correct += correct

print("")
print("Summary")
print(
    (
        f"Correct digits: {total_correct}/{total_length} "
        f"({total_correct/total_length * 100:.0f}%)"
    )
)
