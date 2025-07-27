import random
from typing import Any, List, Optional, TypedDict


class Question(TypedDict):
    """
    Represents an MCQ in the Prolific pre-screening survey.
    """

    id: str
    qualtrics_id: str
    question: str
    options: List[str]
    correctAnswer: int
    code: Optional[str]
    error: Optional[str]


QUESTIONS: List[Question] = [
    {
        "id": "q1",
        "qualtrics_id": "Q4.6",
        "question": "What does the following Python error message indicate?",
        "error": "IndentationError: unexpected indent",
        "options": [
            "The code has an extra indentation where none was expected",
            "A block of code is missing a required indentation",
            "A block of code uses inconsistent indentation (spaces vs. tabs)",
            "A function was called before it was defined",
        ],
        "code": None,
        "correctAnswer": 0,
    },
    {
        "id": "q2",
        "qualtrics_id": "Q5.2",
        "question": "The following code snippet is known to include an issue that will cause an error when executed. Choose the option that correctly identifies the type of error that will be produced.",
        "code": 'x = "100a"\n' + "y = int(x)",
        "options": [
            "ValueError: invalid literal for int() with base 10: '100a'",
            "TypeError: int() cannot convert letters to integers",
            "SyntaxError: invalid syntax",
            "NameError: name 'x' is not defined",
        ],
        "error": None,
        "correctAnswer": 0,
    },
    {
        "id": "q3",
        "qualtrics_id": "Q6.5",
        "question": "The following Python code does not correctly print the double of a number. Choose the option that best resolves the logical error while maintaining the intended functionality.",
        "code": "double = lambda x: x * 2\n" + "print(double)",
        "options": [
            "Surround `x * 2` with `print()`",
            "Replace `lambda` with `def` to make it work",
            "Call the `double` function by adding parentheses with an argument",
            "Remove the `lambda` and just write `x * 2`",
        ],
        "error": None,
        "correctAnswer": 2,
    },
    {
        "id": "q4",
        "qualtrics_id": "Q7.1",
        "question": "Consider the code snippet below. What option correctly explains the behavior of the following program?",
        "code": 'x = int("0")\n'
                + "if x != 0 and (10 / x) > 2:\n"
                + '    print("Division succeeded")\n'
                + 'print("Could not divide by " + str(x))',
        "options": [
            "The code contains a syntax error and won't run properly",
            "The condition should use `or` instead of `and`, because `and` forces evaluation of both sides of the condition, which throws an error",
            "Division by zero error is avoided due to short-circuit logic",
            "The code contains a `TypeError` as `0` can be ambiguously interpreted to different primitive types",
        ],
        "error": None,
        "correctAnswer": 2,
    },
    {
        "id": "q5",
        "qualtrics_id": "Q7.2",
        "question": "Read the code snippet below and identify which code line is logically wrong when computing the area of a rectangle.",
        "code": "def area_rectangle(length, width):\n"
                + '   """Compute the area of a rectangle and print it."""\n'
                + "   area = length * width\n"
                + '   print("The area is", area)\n\n'
                + "area_rectangle(5, 10)",
        "options": [
            "Line 2 – Incorrect docstring format",
            "Line 3 – Incorrect multiplication operator",
            "Line 4 – Print statement formatting error",
            "No line; the code is logically correct",
        ],
        "error": None,
        "correctAnswer": 3,
    },
    {
        "id": "q6",
        "qualtrics_id": "Q8.2",
        "question": "Based only on the error message below, which option best explains the cause of the error?",
        "code": None,
        "error": 'Traceback (most recent call last):\nFile "main.py", line 1, in <module>\n    def my_function()\n    ^\nSyntaxError: invalid syntax',
        "options": [
            "The function definition is missing a colon at the end",
            "The function is missing a return statement",
            "There’s a problem with the indentation of the function",
            "The variable `my_function` hasn't been assigned a value",
        ],
        "correctAnswer": 0,
    },
    {
        "id": "q7",
        "qualtrics_id": "Q9.5",
        "question": "You're writing a program that uses a dictionary to store user preferences. You try to access a key that you know exists in the dictionary, but your code throws a KeyError. What is the MOST likely reason for this, given the limited context?",
        "code": None,
        "error": None,
        "options": [
            "The key might have been altered or removed elsewhere in the code",
            "The key is actually a string, but you’re trying to access it with an integer",
            'There\'s a typo in the key you are trying to access (e.g., `"User"` vs `"user"`), or the case sensitivity is different than expected',
            "Dictionaries can sometimes fail to locate keys due to internal hashing bugs or collisions",
        ],
        "correctAnswer": 2,
    },
    {
        "id": "q8",
        "qualtrics_id": "Q10.1",
        "question": "Review the function below and determine the logical error causing an incorrect result, if any.",
        "code": "def find_max(numbers):\n"
                + "    max_val = 0\n"
                + "    for num in numbers:\n"
                + "        if num > max_val:\n"
                + "            max_val = num\n"
                + "    return max_val\n\n"
                + "result = find_max([-10, -5, -3])",
        "error": None,
        "options": [
            "It incorrectly returns the wrong number instead of the maximum value due to improper initialization of `max_val`",
            "The for loop is structured incorrectly as it does not iterate through all of the array's values.",
            "It raises an exception due to negative values being present in the list.",
            "There is no logical error present; the code correctly assigns the value of `-3` to the `result` variable.",
        ],
        "correctAnswer": 0,
    },
]


def get_randomized_questions() -> List[Question]:
    questions = QUESTIONS.copy()
    random.shuffle(questions)
    randomized = []
    for q in questions:
        options = q["options"].copy()
        random.shuffle(options)
        correct_option = q["options"][q["correctAnswer"]]
        new_correct_index = options.index(correct_option)
        q_out = q.copy()
        q_out["options"] = options
        q_out["correctAnswer"] = new_correct_index
        randomized.append(q_out)
    return randomized


def get_randomized_questions_for_participant() -> tuple[list[Any], dict[Any, Any]]:
    """
    Returns a list of questions with randomized order and options, excluding qualtrics_id and correctAnswer.
    Returns only the fields: id, question, options, code, error.
    Also returns a mapping of question_id to correct answer index for backend use.
    """
    questions = QUESTIONS.copy()
    random.shuffle(questions)
    randomized = []
    answer_map = {}
    for q in questions:
        options = q["options"].copy()
        random.shuffle(options)
        correct_option = q["options"][q["correctAnswer"]]
        new_correct_index = options.index(correct_option)
        answer_map[q["id"]] = new_correct_index
        q_out = {
            "id": q["id"],
            "question": q["question"],
            "options": options,
            "code": q["code"],
            "error": q["error"],
        }
        randomized.append(q_out)
    return randomized, answer_map
