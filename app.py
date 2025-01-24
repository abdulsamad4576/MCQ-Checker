import cv2
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk

def detect_circles(image_path, min_radius=15, max_radius=40):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        print(f"Error: Unable to load image at {image_path}")
        return None

    blurred_img = cv2.GaussianBlur(img, (5, 5), 0)
    circles = cv2.HoughCircles(blurred_img, 
                               cv2.HOUGH_GRADIENT, dp=1.2, minDist=30, 
                               param1=50, param2=30, minRadius=min_radius, maxRadius=max_radius)
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
    else:
        circles = []

    return circles, img

def is_filled_circle(x, y, r, img, threshold=50, min_filled_percentage=0.5):
    mask = np.zeros_like(img)
    cv2.circle(mask, (x, y), r, 255, -1) 
    
    x_min, x_max = max(x - r, 0), min(x + r, img.shape[1] - 1)
    y_min, y_max = max(y - r, 0), min(y + r, img.shape[0] - 1)
    roi = img[y_min:y_max, x_min:x_max]
    
    filled_area = cv2.bitwise_and(roi, mask[y_min:y_max, x_min:x_max])
    
    filled_pixels = np.sum(filled_area > threshold)
    
    total_pixels = np.pi * r * r 
    
    filled_percentage = filled_pixels / total_pixels
    return filled_percentage >= min_filled_percentage

def is_valid_circle(x, y, r, img, threshold=100, min_filled_percentage=0.5):
    if not is_filled_circle(x, y, r, img, threshold, min_filled_percentage):
        return False
    
    mask = np.zeros_like(img)
    cv2.circle(mask, (x, y), r, 255, -1)  
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        contour = contours[0]
        perimeter = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour)
        
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        if circularity < 0.7:  
            return False

    return True

def display_circles(image_path, circles, filled_threshold=100):
    img = cv2.imread(image_path)
    img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    
    for (x, y, r) in circles:
        if is_valid_circle(x, y, r, img_gray, threshold=filled_threshold):
            cv2.circle(img, (x, y), r, (0, 255, 0), 4)  
            cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1) 
        else:
            cv2.circle(img, (x, y), r, (255, 0, 0), 4)  
            cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)  
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img_rgb

def map_answers_to_circles(circles, img, rows=10, cols=4, row_tolerance=50):
    options = ['A', 'B', 'C', 'D']
    answers = []

    circles_sorted=circles

    rows_detected = []
    current_row = []
    last_y = -1
        
        
    for (x, y, r) in circles_sorted:
        if last_y == -1 or abs(y - last_y) <= row_tolerance: 
            current_row.append((x, y, r))
        else:
            rows_detected.append(current_row)
            current_row = [(x, y, r)]
        last_y = y

    if current_row:
        rows_detected.append(current_row)

    for i, row in enumerate(rows_detected):
        blue_circle_count = 0
        if i >= rows:
            break  
        
        row_sorted = sorted(row, key=lambda c: c[0])
        blue_circle_count = 0  

        for (x, y, r) in row_sorted:
            if is_valid_circle(x, y, r, img, threshold=100):
                blue_circle_count += 1 
            else:
                answers.append((i + 1, options[blue_circle_count]))  
                blue_circle_count += 1 

    return answers
def grade_mcq(image_path, answerkey):
    circles, img = detect_circles(image_path)
    
    if circles is None or len(circles) == 0:
        messagebox.showerror("Error", "No circles detected in the image.")
        return None

    circles_sorted = sorted(circles, key=lambda c: (c[1], c[0]))[-40:]
    
    answers = map_answers_to_circles(circles_sorted, img)
    
    rightAnswers = []
    multipleAnswers = []
    marks = 0
    temp = -1
    isWrong = False

    for x, y in answers:
        if x != temp:
            if isWrong:
                isWrong = False
            temp = x
            if x in answerkey.keys():
                if y == answerkey[x]:
                    rightAnswers.append(x)
        else:
            if not isWrong:
                multipleAnswers.append(x)
                isWrong = True

    marks = len(rightAnswers)

    for i in multipleAnswers:
            marks -= 1

    return marks, answers, rightAnswers, multipleAnswers, circles

def create_mcq_grader_gui():
    root = tk.Tk()
    root.title("MCQ Grader")
    root.geometry("800x600")
    image_label = tk.Label(root)
    image_label.pack(pady=10)
    image_path = tk.StringVar()
    answerkey = {}

    def load_image():
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if filepath:
            image_path.set(filepath)
            
            img = Image.open(filepath)
            img.thumbnail((600, 400)) 
            photo = ImageTk.PhotoImage(img)
            image_label.config(image=photo)
            image_label.image = photo
            result = grade_mcq(image_path.get(), answerkey)
            if result:
                marks, answers, rightAnswers, multipleAnswers, circles = result
                circles_sorted = sorted(circles, key=lambda c: (c[1], c[0]))[-40:]
                img_with_circles = display_circles(image_path.get(), circles_sorted)
                
                pil_img = Image.fromarray(img_with_circles)
                pil_img.thumbnail((600, 400)) 
                photo = ImageTk.PhotoImage(pil_img)
            
                image_label.config(image=photo)
                image_label.image = photo

    def input_answer_key():
        answer_key_window = tk.Toplevel(root)
        answer_key_window.title("Input Answer Key")
        answer_key_window.geometry("300x500")

        entries = []
        for i in range(1, 11):
            label = tk.Label(answer_key_window, text=f"Question {i}:")
            label.pack()
            var = tk.StringVar()
            entry = tk.Entry(answer_key_window, textvariable=var, width=10)
            entry.pack()
            entries.append((i, var))

        def submit_answer_key():
            for question, var in entries:
                answer = var.get().strip().upper()
                if answer in ['A', 'B', 'C', 'D']:
                    answerkey[question] = answer
                else:
                    messagebox.showwarning("Invalid Input", f"Invalid answer for Question {question}. Skipping.")
            
            answer_key_window.destroy()
            
            if image_path.get() and answerkey:
                result = grade_mcq(image_path.get(), answerkey)
                if result:
                    marks, answers, rightAnswers, multipleAnswers, circles = result
                    
                    result_text = f"Marks: {marks}/10\n"
                    result_text += "Answers: " + ", ".join([f"Q{x}: {y}" for x, y in answers]) + "\n"
                    result_text += "Correct Answers: " + ", ".join(map(str, rightAnswers)) + "\n"
                    result_text += "Marks deducted for each Multiple Answers in: " + ", ".join(map(str, multipleAnswers))
                    
                    messagebox.showinfo("MCQ Results", result_text)
                
                    circles_sorted = sorted(circles, key=lambda c: (c[1], c[0]))[-40:]
                    img_with_circles = display_circles(image_path.get(), circles_sorted)
                    
                    pil_img = Image.fromarray(img_with_circles)
                    pil_img.thumbnail((600, 400))  
                    photo = ImageTk.PhotoImage(pil_img)
                    
                    image_label.config(image=photo)
                    image_label.image = photo

        submit_btn = tk.Button(answer_key_window, text="Submit Answer Key", command=submit_answer_key)
        submit_btn.pack(pady=10)

    load_image_btn = tk.Button(root, text="Load Image", command=load_image)
    load_image_btn.pack(pady=5)

    input_answer_key_btn = tk.Button(root, text="Input Answer Key", command=input_answer_key)
    input_answer_key_btn.pack(pady=5)

    root.mainloop()
        

if __name__ == "__main__":
    create_mcq_grader_gui()
