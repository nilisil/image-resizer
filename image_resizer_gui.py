import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os

def select_image():
    # Ask the user to select an image file
    file_path = filedialog.askopenfilename(
        title="Select Image to Compress",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
    )
    if file_path:
        lbl_selected_file.config(text=file_path)
        btn_compress.config(state=tk.NORMAL)
        lbl_result.config(text="")

def compress_image():
    file_path = lbl_selected_file.cget("text")
    
    # Get and validate the target KB value
    try:
        target_kb = int(entry_target.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid numeric KB value.")
        return
        
    target_bytes = target_kb * 1024
    output_name = f"{target_kb}kb_" + os.path.basename(file_path)
    
    # Find the current directory of the selected file
    current_folder = os.path.dirname(os.path.abspath(file_path))
    output_path = os.path.join(current_folder, output_name)
    
    # Indicate that processing has started
    lbl_result.config(text="Processing, please wait...", fg="blue")
    root.update()
    
    try:
        # Open the image and ensure it's in RGB mode (required for JPEG)
        img_original = Image.open(file_path)
        if img_original.mode != 'RGB':
            img_original = img_original.convert('RGB')
            
        quality = 95
        scale_factor = 1.0 
        img = img_original.copy()
        
        # Compression and resizing loop
        attempts = 0
        max_attempts = 60
        while True:
            attempts += 1
            lbl_result.config(
                text=f"Processing... (pass {attempts}, quality {quality}, scale {scale_factor:.2f})",
                fg="blue"
            )
            root.update()

            img.save(output_path, "JPEG", quality=quality, optimize=True)
            current_size = os.path.getsize(output_path)

            if current_size <= target_bytes or scale_factor < 0.2 or attempts >= max_attempts:
                break

            if quality > 20:
                quality -= 10
            else:
                quality = 70
                scale_factor *= 0.85
                new_width = max(1, int(img_original.width * scale_factor))
                new_height = max(1, int(img_original.height * scale_factor))
                img = img_original.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Update UI and show success message
        final_size_kb = current_size // 1024
        if current_size <= target_bytes:
            msg = f"SUCCESS!\n\nNew Size: {final_size_kb} KB\nSaved at:\n{output_path}"
            lbl_result.config(text=f"Done! New Size: {final_size_kb} KB", fg="green")
            messagebox.showinfo("Success", msg)
        else:
            msg = (f"Target not reached.\n\nSmallest achieved: {final_size_kb} KB "
                   f"(target {target_kb} KB)\nSaved at:\n{output_path}")
            lbl_result.config(text=f"Stopped at {final_size_kb} KB (target not reached)", fg="orange")
            messagebox.showwarning("Finished", msg)
        
    except Exception as e:
        lbl_result.config(text="Process failed.", fg="red")
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

# --- GUI DESIGN ---

root = tk.Tk()
root.title("Image Compressor & Resizer")
root.geometry("500x320")
root.resizable(False, False)
root.configure(padx=20, pady=20)

# Title
lbl_title = tk.Label(root, text="Image Compression Tool", font=("Arial", 14, "bold"))
lbl_title.pack(pady=(0, 15))

# Step 1: File Selection
frame_selection = tk.Frame(root)
frame_selection.pack(fill="x", pady=5)

btn_select = tk.Button(frame_selection, text="Select Image...", command=select_image, width=15, font=("Arial", 10))
btn_select.pack(side="left")

lbl_selected_file = tk.Label(frame_selection, text="No image selected.", fg="gray", wraplength=300, justify="left")
lbl_selected_file.pack(side="left", padx=10)

# Step 2: Target Size (KB)
frame_target = tk.Frame(root)
frame_target.pack(fill="x", pady=20)

lbl_target = tk.Label(frame_target, text="Target File Size (KB):", font=("Arial", 10))
lbl_target.pack(side="left")

entry_target = tk.Entry(frame_target, width=10, font=("Arial", 10))
entry_target.insert(0, "500") # Default value
entry_target.pack(side="left", padx=10)

# Step 3: Process Button
btn_compress = tk.Button(root, text="Compress and Save", command=compress_image, state=tk.DISABLED, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), pady=5)
btn_compress.pack(fill="x", pady=10)

# Status/Result Label
lbl_result = tk.Label(root, text="", font=("Arial", 10, "bold"))
lbl_result.pack(pady=10)

# Start GUI
root.mainloop()
