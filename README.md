# Python to OCR A-Level Pseudocode Converter

A Python application that converts Python code into OCR A-Level style pseudocode. It has a dark-themed interface with two code editors, allowing you to write Python on the left and view the converted pseudocode on the right.

## Features

- Converts Python code into OCR A-Level style pseudocode.
- Syntax highlighting for keywords, strings, comments, numbers, functions and classes.
- Line numbers in both editors.
- Automatic indentation when pressing Enter.
- Four-space indentation when pressing Tab.
- Copy and clear buttons for both editors.
- Supports common programming structures, including:
  - If, elif and else statements
  - For and while loops
  - Functions, procedures and classes
  - Lists and arrays
  - Basic file handling
  - Match and case statements
- Dark-themed interface built with CustomTkinter.

## Screenshots

### Main Interface
<img width="2560" height="1440" alt="image" src="https://github.com/user-attachments/assets/9e2f57b0-2198-4a0e-8738-9f18b0d4da7e" />


### Python Input
<img width="2560" height="1440" alt="image" src="https://github.com/user-attachments/assets/40529066-722f-4b66-b549-6c740b48b7da" />


### Converted Pseudocode
<img width="2560" height="1440" alt="image" src="https://github.com/user-attachments/assets/f4fd1bd9-ad6c-4f7a-9211-4e0f1c4a4d0e" />


To add your own screenshots, create a folder called `screenshots` in the project directory and save your images using the filenames shown above.

## Requirements

- Python 3
- CustomTkinter

Install the required library using pip:

```bash
pip install customtkinter
```

The `tkinter`, `keyword` and `re` modules are included with standard Python installations.

## How to Run

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Install the required dependency.
4. Run the application:

```bash
python main.py
```

Replace `main.py` with the actual filename if necessary.

## How to Use

1. Enter or paste Python code into the editor on the left.
2. Click the arrow button in the middle.
3. View the converted pseudocode in the editor on the right.
4. Use the Copy button to copy the contents of an editor.
5. Use the Clear button to empty an editor.

## Example

Python input:

```python
age = int(input("Enter your age: "))

if age >= 18:
    print("Adult")
else:
    print("Under 18")
```

Example pseudocode output:

```text
age = int(input("Enter your age: "))

if age >= 18 then
    print("Adult")
else
    print("Under 18")
endif
```

The actual output may vary depending on the code being converted.

## Limitations

The converter uses regular expressions and indentation to recognise Python syntax. It does not support every Python feature, and some output may need manual adjustments to match OCR A-Level pseudocode conventions.

Always check the converted pseudocode before using it for coursework or exam practice.

## Technologies Used

- Python
- CustomTkinter
- Tkinter
- Regular expressions

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
