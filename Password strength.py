import tkinter as tk
from tkinter import ttk
import re
import hashlib

class PasswordStrengthChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Strength Checker")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Load common passwords list
        self.common_passwords = self.load_common_passwords()
        
        self.setup_ui()
    
    def load_common_passwords(self):
        # A small list of common passwords for demonstration
        # In a real application, you would load from a file
        return {
            "password", "123456", "12345678", "1234", "qwerty", "12345", 
            "dragon", "baseball", "football", "letmein", "monkey", "abc123",
            "mustang", "michael", "shadow", "master", "jennifer", "111111",
            "2000", "jordan", "superman", "harley", "1234567", "freedom",
            "hello", "charlie", "andrew", "love", "secret", "password1"
        }
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Password Strength Checker", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Enter a password to check its strength. A strong password should:\n"
                                   "- Be at least 8 characters long\n"
                                   "- Contain uppercase and lowercase letters\n"
                                   "- Include numbers and special characters\n"
                                   "- Not be a common password",
                              justify=tk.CENTER)
        desc_label.pack(pady=(0, 20))
        
        # Password entry
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(password_frame, text="Password:").pack(side=tk.LEFT)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="•", width=30)
        self.password_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.password_entry.bind("<KeyRelease>", self.check_password_strength)
        
        # Show password checkbox
        self.show_password_var = tk.BooleanVar()
        show_password_cb = ttk.Checkbutton(password_frame, text="Show password", 
                                          variable=self.show_password_var,
                                          command=self.toggle_password_visibility)
        show_password_cb.pack(side=tk.LEFT, padx=(20, 0))
        
        # Strength indicator
        strength_frame = ttk.Frame(main_frame)
        strength_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(strength_frame, text="Strength:").pack(side=tk.LEFT)
        self.strength_label = ttk.Label(strength_frame, text="None", font=("Arial", 10, "bold"))
        self.strength_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(5, 20))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Password Analysis", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas and scrollbar for the results
        self.canvas = tk.Canvas(results_frame, height=300)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Analysis labels
        self.length_label = ttk.Label(self.scrollable_frame, text="Length: -")
        self.length_label.pack(anchor="w", pady=(0, 5))
        
        self.uppercase_label = ttk.Label(self.scrollable_frame, text="Uppercase: -")
        self.uppercase_label.pack(anchor="w", pady=(0, 5))
        
        self.lowercase_label = ttk.Label(self.scrollable_frame, text="Lowercase: -")
        self.lowercase_label.pack(anchor="w", pady=(0, 5))
        
        self.numbers_label = ttk.Label(self.scrollable_frame, text="Numbers: -")
        self.numbers_label.pack(anchor="w", pady=(0, 5))
        
        self.symbols_label = ttk.Label(self.scrollable_frame, text="Symbols: -")
        self.symbols_label.pack(anchor="w", pady=(0, 5))
        
        self.common_label = ttk.Label(self.scrollable_frame, text="Common Password: -")
        self.common_label.pack(anchor="w", pady=(0, 5))
        
        self.score_label = ttk.Label(self.scrollable_frame, text="Overall Score: -")
        self.score_label.pack(anchor="w", pady=(0, 5))
        
        # Recommendations
        self.recommendations_label = ttk.Label(self.scrollable_frame, text="Recommendations:", 
                                              font=("Arial", 10, "bold"))
        self.recommendations_label.pack(anchor="w", pady=(10, 5))
        
        self.recommendations_text = tk.Text(self.scrollable_frame, height=4, width=50, wrap=tk.WORD)
        self.recommendations_text.pack(fill=tk.X, pady=(0, 10))
        
        # Generate password button
        generate_btn = ttk.Button(main_frame, text="Generate Strong Password", 
                                 command=self.generate_password)
        generate_btn.pack(pady=(10, 0))
    
    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="•")
    
    def check_password_strength(self, event=None):
        password = self.password_var.get()
        
        if not password:
            self.reset_display()
            return
        
        # Check criteria
        length_ok = len(password) >= 8
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_numbers = bool(re.search(r'[0-9]', password))
        has_symbols = bool(re.search(r'[^A-Za-z0-9]', password))
        is_common = password.lower() in self.common_passwords
        
        # Calculate score
        score = 0
        max_score = 100
        
        # Length (max 30 points)
        length_score = min(len(password) * 2, 30)
        score += length_score
        
        # Character variety (max 40 points)
        if has_uppercase:
            score += 10
        if has_lowercase:
            score += 10
        if has_numbers:
            score += 10
        if has_symbols:
            score += 10
        
        # Penalty for common password
        if is_common:
            score = max(0, score - 30)
        
        # Update display
        self.update_display(
            length_ok, has_uppercase, has_lowercase, 
            has_numbers, has_symbols, is_common, score
        )
    
    def update_display(self, length_ok, has_uppercase, has_lowercase, 
                      has_numbers, has_symbols, is_common, score):
        # Update progress bar and strength label
        self.progress_var.set(score)
        
        if score < 40:
            strength = "Weak"
            color = "red"
        elif score < 70:
            strength = "Moderate"
            color = "orange"
        else:
            strength = "Strong"
            color = "green"
        
        self.strength_label.config(text=strength, foreground=color)
        self.progress_bar.configure(style=f"Horizontal.TProgressbar.{color}")
        
        # Update analysis labels
        self.length_label.config(
            text=f"Length: {'✓ Good' if length_ok else '✗ Too short'}", 
            foreground="green" if length_ok else "red"
        )
        self.uppercase_label.config(
            text=f"Uppercase: {'✓ Present' if has_uppercase else '✗ Missing'}", 
            foreground="green" if has_uppercase else "red"
        )
        self.lowercase_label.config(
            text=f"Lowercase: {'✓ Present' if has_lowercase else '✗ Missing'}", 
            foreground="green" if has_lowercase else "red"
        )
        self.numbers_label.config(
            text=f"Numbers: {'✓ Present' if has_numbers else '✗ Missing'}", 
            foreground="green" if has_numbers else "red"
        )
        self.symbols_label.config(
            text=f"Symbols: {'✓ Present' if has_symbols else '✗ Missing'}", 
            foreground="green" if has_symbols else "red"
        )
        self.common_label.config(
            text=f"Common Password: {'✗ Yes (High Risk)' if is_common else '✓ No'}", 
            foreground="red" if is_common else "green"
        )
        self.score_label.config(
            text=f"Overall Score: {score}/100", 
            foreground=color
        )
        
        # Update recommendations
        recommendations = []
        if not length_ok:
            recommendations.append("• Use at least 8 characters")
        if not has_uppercase:
            recommendations.append("• Include uppercase letters (A-Z)")
        if not has_lowercase:
            recommendations.append("• Include lowercase letters (a-z)")
        if not has_numbers:
            recommendations.append("• Include numbers (0-9)")
        if not has_symbols:
            recommendations.append("• Include symbols (!@#$%^&*, etc.)")
        if is_common:
            recommendations.append("• Avoid common passwords")
        
        if not recommendations:
            recommendations.append("• Your password is strong! Keep it safe.")
        
        self.recommendations_text.delete(1.0, tk.END)
        self.recommendations_text.insert(1.0, "\n".join(recommendations))
    
    def reset_display(self):
        self.progress_var.set(0)
        self.strength_label.config(text="None", foreground="black")
        
        labels = [
            self.length_label, self.uppercase_label, self.lowercase_label,
            self.numbers_label, self.symbols_label, self.common_label, self.score_label
        ]
        
        for label in labels:
            label.config(text=label.cget("text").split(":")[0] + ": -", foreground="black")
        
        self.recommendations_text.delete(1.0, tk.END)
    
    def generate_password(self):
        import random
        import string
        
        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one of each type
        password_chars = [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(digits),
            random.choice(symbols)
        ]
        
        # Fill the rest randomly
        all_chars = lowercase + uppercase + digits + symbols
        password_chars.extend(random.choice(all_chars) for _ in range(8))
        
        # Shuffle the characters
        random.shuffle(password_chars)
        
        # Create the password
        password = ''.join(password_chars)
        
        # Update the password entry
        self.password_var.set(password)
        self.check_password_strength()

# Create the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordStrengthChecker(root)
    root.mainloop()