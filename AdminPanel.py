#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import discord
from discord.ext import commands
import threading

# ---- Config ----
ACCOUNTS_FILE = "accounts.json"
SIGNUP_CODE = "1234"
BOT_TOKEN = "00"  # Replace with your regenerated token
GUILD_ID = 00       # Replace with your server ID

# ---- Helper Functions ----
def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return {}
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)

def log(message):
    logs_text.config(state="normal")
    logs_text.insert(tk.END, message + "\n")
    logs_text.see(tk.END)
    logs_text.config(state="disabled")

# ---- Discord Bot Setup ----
intents = discord.Intents.default()
intents.members = True  # Required for member actions
bot = commands.Bot(command_prefix="!", intents=intents)
guild_obj = None

@bot.event
async def on_ready():
    global guild_obj
    guild_obj = bot.get_guild(GUILD_ID)
    log(f"Bot logged in as {bot.user}")

async def broadcast_message(message):
    if guild_obj:
        for channel in guild_obj.text_channels:
            try:
                await channel.send(message)
            except:
                pass

async def mute_member(user_id):
    if guild_obj:
        member = guild_obj.get_member(user_id)
        if member:
            await member.edit(mute=True)

async def unmute_member(user_id):
    if guild_obj:
        member = guild_obj.get_member(user_id)
        if member:
            await member.edit(mute=False)

async def kick_member(user_id):
    if guild_obj:
        member = guild_obj.get_member(user_id)
        if member:
            await member.kick(reason=f"Action from Admin Panel")

# ---- GUI Setup ----
root = tk.Tk()
root.title("Admin Panel")
root.geometry("700x500")

script_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(script_dir, "notepad_icon.png")
if os.path.exists(icon_path):
    root.iconphoto(False, tk.PhotoImage(file=icon_path))

login_frame = tk.Frame(root)
login_frame.pack(expand=True, fill="both")
app_frame = tk.Frame(root)

accounts = load_accounts()
current_user = None

# ---- Login / Signup Functions ----
def show_login():
    login_frame.pack(expand=True, fill="both")
    app_frame.pack_forget()

def show_app():
    login_frame.pack_forget()
    app_frame.pack(expand=True, fill="both")

def login():
    global current_user
    username = login_username.get().strip()
    password = login_password.get().strip()
    if username in accounts and accounts[username] == password:
        current_user = username
        log(f"User '{username}' logged in.")
        show_app()
    else:
        messagebox.showerror("Error", "Invalid username or password.")

def signup():
    username = signup_username.get().strip()
    password = signup_password.get().strip()
    code = signup_code.get().strip()
    if code != SIGNUP_CODE:
        messagebox.showerror("Error", "Invalid signup code.")
        return
    if username in accounts:
        messagebox.showerror("Error", "Username already exists.")
        return
    accounts[username] = password
    save_accounts(accounts)
    log(f"Account '{username}' created.")
    messagebox.showinfo("Success", "Account created! You can now login.")

# ---- Login Widgets ----
tk.Label(login_frame, text="Login", font=("Arial", 18)).pack(pady=10)
login_username = tk.Entry(login_frame)
login_username.pack(pady=5)
login_username.insert(0, "Username")
login_password = tk.Entry(login_frame, show="*")
login_password.pack(pady=5)
login_password.insert(0, "Password")
tk.Button(login_frame, text="Login", command=login).pack(pady=10)

tk.Label(login_frame, text="--- OR Sign Up ---", font=("Arial", 14)).pack(pady=10)
signup_username = tk.Entry(login_frame)
signup_username.pack(pady=5)
signup_username.insert(0, "New Username")
signup_password = tk.Entry(login_frame, show="*")
signup_password.pack(pady=5)
signup_password.insert(0, "New Password")
signup_code = tk.Entry(login_frame)
signup_code.pack(pady=5)
signup_code.insert(0, "Signup Code")
tk.Button(login_frame, text="Create Account", command=signup).pack(pady=10)

# ---- Admin Panel Widgets ----
notebook = ttk.Notebook(app_frame)
notebook.pack(expand=True, fill="both")

# Logs Tab
logs_frame = ttk.Frame(notebook)
notebook.add(logs_frame, text="Logs")
logs_text = tk.Text(logs_frame, state="disabled", wrap="word")
logs_text.pack(expand=True, fill="both")

# Controls Tab
controls_frame = ttk.Frame(notebook)
notebook.add(controls_frame, text="Controls")

# Broadcast message
tk.Label(controls_frame, text="Broadcast a message:").pack(pady=5)
broadcast_entry = tk.Entry(controls_frame, width=50)
broadcast_entry.pack(pady=5)

def broadcast_click():
    if not current_user:
        messagebox.showerror("Error", "No user logged in.")
        return
    message = broadcast_entry.get().strip()
    if message:
        msg = f"({current_user}) {message}"
        bot.loop.create_task(broadcast_message(msg))
        log(f"Broadcasted: {msg}")
        broadcast_entry.delete(0, tk.END)

tk.Button(controls_frame, text="Send Broadcast", command=broadcast_click).pack(pady=10)

# Member Actions
tk.Label(controls_frame, text="Member Actions (Discord ID):").pack(pady=5)
member_id_entry = tk.Entry(controls_frame, width=30)
member_id_entry.pack(pady=5)

def mute_click():
    user_id = member_id_entry.get().strip()
    if user_id.isdigit():
        bot.loop.create_task(mute_member(int(user_id)))
        log(f"Muted user {user_id}")

def unmute_click():
    user_id = member_id_entry.get().strip()
    if user_id.isdigit():
        bot.loop.create_task(unmute_member(int(user_id)))
        log(f"Unmuted user {user_id}")

def kick_click():
    user_id = member_id_entry.get().strip()
    if user_id.isdigit():
        bot.loop.create_task(kick_member(int(user_id)))
        log(f"Kicked user {user_id}")

tk.Button(controls_frame, text="Mute", command=mute_click).pack(pady=2)
tk.Button(controls_frame, text="Unmute", command=unmute_click).pack(pady=2)
tk.Button(controls_frame, text="Kick", command=kick_click).pack(pady=2)

# ---- Start with login screen ----
show_login()

# ---- Run Bot and GUI together ----
def run_bot():
    bot.run(BOT_TOKEN)

threading.Thread(target=run_bot, daemon=True).start()
root.mainloop()
