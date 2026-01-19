import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import re
from docx import Document
import os
import requests
import json

class CallTranscriptGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Call Transcript Generator - AI Powered")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f4f8")
        
        self.requirements = []
        self.transcripts = []
        self.api_key = " "
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#4f46e5", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🤖 AI-Powered Call Transcript Generator",
            font=("Arial", 24, "bold"),
            bg="#4f46e5",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # API Configuration section
        api_frame = tk.LabelFrame(
            main_frame,
            text="OpenAI API Configuration",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#1f2937",
            relief=tk.RAISED,
            borderwidth=2
        )
        api_frame.pack(fill=tk.X, pady=(0, 20))
        
        api_inner = tk.Frame(api_frame, bg="white")
        api_inner.pack(padx=20, pady=15)
        
        # Instructions
        instruction_text = "Get your API key from: https://platform.openai.com/api-keys"
        tk.Label(
            api_inner,
            text=instruction_text,
            font=("Arial", 9, "italic"),
            bg="white",
            fg="#6b7280"
        ).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # API Key
        tk.Label(
            api_inner,
            text="API Key:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.api_key_entry = tk.Entry(api_inner, width=70, font=("Arial", 10), show="*")
        self.api_key_entry.grid(row=1, column=1, padx=10, pady=5)
        self.api_key_entry.insert(0, "sk-...")
        
        # Show/Hide key button
        self.show_key_btn = tk.Button(
            api_inner,
            text="👁️",
            command=self.toggle_api_key,
            cursor="hand2"
        )
        self.show_key_btn.grid(row=1, column=2, pady=5)
        
        # Model selection
        tk.Label(
            api_inner,
            text="Model:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.model_var = tk.StringVar(value="gpt-4o")
        model_frame = tk.Frame(api_inner, bg="white")
        model_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        models = [
            ("GPT-4o (Recommended)", "gpt-4o"),
            ("GPT-4o Mini (Faster, Cheaper)", "gpt-4o-mini"),
            ("GPT-4 Turbo", "gpt-4-turbo-preview"),
            ("GPT-3.5 Turbo (Budget)", "gpt-3.5-turbo")
        ]
        
        for i, (display, value) in enumerate(models):
            tk.Radiobutton(
                model_frame,
                text=display,
                variable=self.model_var,
                value=value,
                bg="white",
                font=("Arial", 9)
            ).pack(anchor=tk.W)
        
        # Test API button
        test_api_btn = tk.Button(
            api_inner,
            text="✓ Test Connection",
            font=("Arial", 9, "bold"),
            bg="#10b981",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.test_api_connection
        )
        test_api_btn.grid(row=3, column=1, pady=10, sticky=tk.W)
        
        # Upload section
        upload_frame = tk.Frame(main_frame, bg="white", relief=tk.RAISED, borderwidth=2)
        upload_frame.pack(fill=tk.X, pady=(0, 20))
        
        upload_inner = tk.Frame(upload_frame, bg="white")
        upload_inner.pack(padx=20, pady=20)
        
        self.file_label = tk.Label(
            upload_inner,
            text="No file selected",
            font=("Arial", 11),
            bg="white",
            fg="#6b7280"
        )
        self.file_label.pack(side=tk.LEFT, padx=(0, 20))
        
        upload_btn = tk.Button(
            upload_inner,
            text="📁 Upload Requirements",
            font=("Arial", 11, "bold"),
            bg="#4f46e5",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.upload_file
        )
        upload_btn.pack(side=tk.LEFT, padx=5)
        
        generate_btn = tk.Button(
            upload_inner,
            text="⚡ Generate with AI",
            font=("Arial", 11, "bold"),
            bg="#10b981",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.generate_transcripts
        )
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        download_all_btn = tk.Button(
            upload_inner,
            text="💾 Download All",
            font=("Arial", 11, "bold"),
            bg="#f59e0b",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.download_all
        )
        download_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            upload_frame,
            mode='indeterminate',
            length=300
        )
        
        # Results section
        results_frame = tk.Frame(main_frame, bg="white", relief=tk.RAISED, borderwidth=2)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        results_header = tk.Label(
            results_frame,
            text="Generated Transcripts",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#1f2937"
        )
        results_header.pack(pady=10)
        
        # Listbox for transcripts
        list_frame = tk.Frame(results_frame, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.transcript_list = tk.Listbox(
            list_frame,
            font=("Arial", 10),
            yscrollcommand=scrollbar.set,
            height=10
        )
        self.transcript_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.transcript_list.yview)
        self.transcript_list.bind('<<ListboxSelect>>', self.show_transcript)
        
        # Text display
        self.text_display = scrolledtext.ScrolledText(
            results_frame,
            font=("Courier", 10),
            wrap=tk.WORD,
            height=20
        )
        self.text_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Download button for selected
        download_frame = tk.Frame(results_frame, bg="white")
        download_frame.pack(pady=(0, 20))
        
        download_selected_btn = tk.Button(
            download_frame,
            text="💾 Download Selected",
            font=("Arial", 10, "bold"),
            bg="#4f46e5",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.download_selected
        )
        download_selected_btn.pack()
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready - Please configure API key first",
            font=("Arial", 9),
            bg="#e5e7eb",
            fg="#374151",
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X)
    
    def toggle_api_key(self):
        if self.api_key_entry.cget('show') == '*':
            self.api_key_entry.config(show='')
            self.show_key_btn.config(text='🔒')
        else:
            self.api_key_entry.config(show='*')
            self.show_key_btn.config(text='👁️')
    
    def test_api_connection(self):
        api_key = self.api_key_entry.get().strip()
        
        if not api_key or api_key == "sk-...":
            messagebox.showerror("Error", "Please enter your OpenAI API Key!")
            return
        
        try:
            self.status_label.config(text="Testing API connection...")
            self.root.update()
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": self.model_var.get(),
                "messages": [
                    {"role": "user", "content": "Say 'Connection successful' if you receive this."}
                ],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.api_key = api_key
                messagebox.showinfo("Success", "✓ API Connection successful!\n\nYou're ready to generate transcripts.")
                self.status_label.config(text=f"API Connected - Using {self.model_var.get()}")
            else:
                error_msg = response.json().get('error', {}).get('message', response.text)
                messagebox.showerror("Error", f"API Error: {response.status_code}\n{error_msg}")
                self.status_label.config(text="API Connection failed")
        
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed:\n{str(e)}")
            self.status_label.config(text="API Connection failed")
    
    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Requirements Document",
            filetypes=[
                ("Word Documents", "*.docx"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}")
    
    def parse_requirements_by_reference(self, text):
        """Parse requirements grouped by reference title"""
        requirements_by_ref = {}
        
        # Find all GGAI requirements
        req_pattern = r'\[GGAI-\d+\].*?(?=\[GGAI-\d+\]|$)'
        matches = re.finditer(req_pattern, text, re.DOTALL)
        
        for match in matches:
            req_text = match.group(0)
            
            # Extract ID and title
            title_match = re.search(r'\[GGAI-(\d+)\]\s*(.+?)(?:\n|Created)', req_text)
            if not title_match:
                continue
            
            req_id = title_match.group(1)
            title = title_match.group(2).strip()
            
            # Extract scenarios
            scenarios_match = re.search(r'Scenarios combined:?\s*([0-9,\s]+)', req_text, re.IGNORECASE)
            if not scenarios_match:
                continue
            
            scenarios = [s.strip() for s in scenarios_match.group(1).split(',') if s.strip()]
            
            # Extract reference/criteria name
            ref_match = re.search(r'Ref[:\s]+([A-Z_\s]+?)(?:CRITERIA|$)', req_text, re.IGNORECASE | re.MULTILINE)
            reference = ref_match.group(1).strip() if ref_match else 'GENERAL'
            
            # Group by reference
            if reference not in requirements_by_ref:
                requirements_by_ref[reference] = []
            
            requirements_by_ref[reference].append({
                'id': req_id,
                'title': title,
                'scenarios': scenarios,
                'reference': reference,
                'full_text': req_text
            })
        
        return requirements_by_ref
    
    def call_openai_api(self, prompt):
        """Call OpenAI API"""
        if not self.api_key:
            raise Exception("API not configured. Please test connection first.")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model_var.get(),
            "messages": [
                {
                    "role": "system",
                    "content": """You are an expert at creating realistic call center conversations. 
You MUST follow these rules EXACTLY:
1. Create ONLY dialogue between CH (Call Handler) and Customer
2. NO headings, NO explanations, NO summaries outside dialogue
3. CH MUST end with a natural verbal recap to the customer
4. Sound human, natural, and professional
5. Follow ALL requirements precisely
6. If scenarios logically connect, combine them into ONE conversation
7. If scenarios don't connect, create SEPARATE conversations clearly marked"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                error_msg = response.json().get('error', {}).get('message', response.text)
                raise Exception(f"API Error {response.status_code}: {error_msg}")
        
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")
    
    def generate_transcripts(self):
        if not hasattr(self, 'file_path'):
            messagebox.showerror("Error", "Please upload a file first!")
            return
        
        if not self.api_key:
            messagebox.showerror("Error", "Please configure and test API connection first!")
            return
        
        try:
            # Show progress
            self.progress.pack(pady=10)
            self.progress.start(10)
            self.status_label.config(text="Reading file...")
            self.root.update()
            
            # Read file
            if self.file_path.endswith('.docx'):
                doc = Document(self.file_path)
                text = '\n'.join([para.text for para in doc.paragraphs])
            else:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Parse requirements grouped by reference
            requirements_by_ref = self.parse_requirements_by_reference(text)
            
            if not requirements_by_ref:
                messagebox.showerror("Error", "No valid requirements found in the document!")
                self.progress.stop()
                self.progress.pack_forget()
                return
            
            self.transcripts = []
            total_refs = len(requirements_by_ref)
            current_ref = 0
            
            # Process each reference group
            for reference, req_list in requirements_by_ref.items():
                current_ref += 1
                self.status_label.config(
                    text=f"Generating conversations for {reference} ({current_ref}/{total_refs})... Using {self.model_var.get()}"
                )
                self.root.update()
                
                # Combine all requirements under this reference
                combined_text = f"\n\n{'='*80}\n\n".join([req['full_text'] for req in req_list])
                
                # Create prompt for AI
                prompt = f"""Create a realistic, professional conversation based strictly on the requirements below.

Instructions:
* The conversation must feature only two speakers: CH (Call Handler) and Customer.
* If the scenarios in the requirements logically connect or flow together, then combine them into ONE continuous conversation.
* If the scenarios do NOT naturally connect, then produce SEPARATE conversations—one conversation per scenario.
* The output must always be PURE conversation only (no headings, no explanations, no summaries outside the dialogue).
* However, the CH must end each conversation with a natural verbal recap to the customer.
* The conversation(s) must follow every rule and condition in the requirements exactly.
* Dialogue must sound human, natural, and flow smoothly.

Here are the requirements:

{combined_text}"""
                
                # Call AI to generate conversation
                try:
                    conversation = self.call_openai_api(prompt)
                    
                    # Store transcript
                    ids = ', '.join([req['id'] for req in req_list])
                    titles = ' + '.join([req['title'][:30] for req in req_list])
                    all_scenarios = []
                    for req in req_list:
                        all_scenarios.extend(req['scenarios'])
                    
                    self.transcripts.append({
                        'id': ids,
                        'title': titles,
                        'reference': reference,
                        'scenarios': list(set(all_scenarios)),
                        'content': conversation,
                        'req_count': len(req_list)
                    })
                    
                except Exception as e:
                    messagebox.showerror(
                        "API Error",
                        f"Failed to generate conversation for {reference}:\n{str(e)}"
                    )
            
            # Update UI
            self.transcript_list.delete(0, tk.END)
            for t in self.transcripts:
                self.transcript_list.insert(
                    tk.END,
                    f"[{t['reference']}] GGAI-{t['id']} | {t['req_count']} requirement(s)"
                )
            
            self.progress.stop()
            self.progress.pack_forget()
            self.status_label.config(
                text=f"✓ Generated {len(self.transcripts)} conversation(s) successfully!"
            )
            
            messagebox.showinfo(
                "Success",
                f"Successfully generated {len(self.transcripts)} conversation(s) using AI!\n\nModel used: {self.model_var.get()}"
            )
            
        except Exception as e:
            self.progress.stop()
            self.progress.pack_forget()
            messagebox.showerror("Error", f"Failed to generate transcripts:\n{str(e)}")
            self.status_label.config(text="Generation failed")
    
    def show_transcript(self, event):
        selection = self.transcript_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        transcript = self.transcripts[index]
        
        display_text = f"Reference: {transcript['reference']}\n"
        display_text += f"Requirements: GGAI-{transcript['id']}\n"
        display_text += f"Scenarios combined: {', '.join(transcript['scenarios'])}\n"
        display_text += f"Count: {transcript['req_count']} requirement(s) combined\n\n"
        display_text += "="*80 + "\n\n"
        display_text += transcript['content']
        
        self.text_display.delete('1.0', tk.END)
        self.text_display.insert('1.0', display_text)
    
    def download_selected(self):
        selection = self.transcript_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a transcript first!")
            return
        
        index = selection[0]
        transcript = self.transcripts[index]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"{transcript['reference']}_GGAI-{transcript['id']}_Transcript.txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            content = f"Reference: {transcript['reference']}\n"
            content += f"Requirements: GGAI-{transcript['id']}\n"
            content += f"Scenarios combined: {', '.join(transcript['scenarios'])}\n\n"
            content += transcript['content']
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("Success", "Transcript saved successfully!")
            self.status_label.config(text=f"Saved: {os.path.basename(file_path)}")
    
    def download_all(self):
        if not self.transcripts:
            messagebox.showwarning("Warning", "No transcripts to download!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="All_Call_Transcripts_AI_Generated.txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            all_content = ""
            for i, transcript in enumerate(self.transcripts):
                if i > 0:
                    all_content += "\n\n" + "="*80 + "\n\n"
                
                all_content += f"Reference: {transcript['reference']}\n"
                all_content += f"Requirements: GGAI-{transcript['id']}\n"
                all_content += f"Scenarios combined: {', '.join(transcript['scenarios'])}\n\n"
                all_content += transcript['content']
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(all_content)
            
            messagebox.showinfo("Success", f"All {len(self.transcripts)} transcripts saved successfully!")
            self.status_label.config(text=f"Saved all to: {os.path.basename(file_path)}")

def main():
    root = tk.Tk()
    app = CallTranscriptGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
