import sys


def get_retry_approval():
    while True:
        response = input(
            "\n\nCouldn't recognize your input. (Turn off interactive mode with codespeak.set_interactive_mode(False))\n\nInput 'c' to continue, or 'q' to quit. Then press 'Enter'.\n"
        )
        if response.lower() == "q":
            print("Exiting the program.")
            sys.exit()
        elif response.lower() == "c":
            print("\n")
            return True
        else:
            print("Invalid input. Please try again.")


def get_initial_approval():
    response = input(
        "\n\n----INTERACTIVE mode is on-----\n\nInput 'c' to continue, or 'q' to quit. Then press 'Enter'.\n"
    )
    if response.lower() == "q":
        print("Exiting the program.")
        sys.exit()
    elif response.lower() == "c":
        print("\n")
        return True
    else:
        return False


def get_approval():
    while True:
        did_approve = get_initial_approval()
        if did_approve:
            break
        else:
            did_approve = get_retry_approval()
            if did_approve:
                break
