
### MCQ Checker - Overview
This Python-based tool grades multiple-choice questions (MCQs) from scanned answer sheets. Using computer vision, the tool detects and validates circles to identify selected answers and compares them against a predefined answer key.

### Key Features
- **Circle Detection**: Detects filled circles using the Hough Circle Transform and analyzes their validity.
- **Answer Mapping**: Maps detected circles to corresponding MCQ options (A, B, C, D).
- **Grading**: Compares user responses with the provided answer key and calculates marks, identifying correct answers, multiple selections, and deductions.
- **Interactive GUI**: Allows users to load images and input the answer key through an intuitive Tkinter interface.

### How to Run
1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python mcq_checker.py
   ```
4. Use the GUI to:
   - Load the answer sheet image.
   - Input the answer key.
   - View graded results and annotated answer sheets.

### Dependencies
- `opencv-python`
- `numpy`
- `Pillow`
- `matplotlib`
- `tkinter`
