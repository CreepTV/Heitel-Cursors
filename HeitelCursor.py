import ctypes
import win32gui
import win32con
import os
import urllib.request
import customtkinter as ctk
from tkinter import Toplevel, Label, Scale, HORIZONTAL
from customtkinter import CTkImage, CTkSlider, CTkProgressBar  # CTkSlider und CTkProgressBar importieren
from PIL import Image, ImageTk, UnidentifiedImageError
import pygame  # Sound-Abspielfunktion importieren
import threading
import tkinter as tk  # Importiere tkinter explizit
from pynput import mouse  # Import the pynput library for global mouse hooks

# Zielpfad für den Download
cursor_dir = os.path.join(os.path.expandvars("%USERPROFILE%"), "Documents", "HerrHeitel")
os.makedirs(cursor_dir, exist_ok=True)
cursor_file = os.path.join(cursor_dir, "HeitelCursorNormal.cur")
image_file = os.path.join(cursor_dir, "HeitelCursorsLogo.png")
icon_file = os.path.join(cursor_dir, "HeitelCursorLogoNew.ico")  # Icon-Datei-Pfad hinzufügen
sound_file = os.path.join(cursor_dir, "HeitelHardwareSounde.mp3")
window_file = os.path.join(cursor_dir, "window_icon.png")
sound_icon_file = os.path.join(cursor_dir, "sound_icon.png")
cursor_icon_file = os.path.join(cursor_dir, "cursor_icon.png")
window_icon_file = os.path.join(cursor_dir, "windowsymbol_icon.png")

# URLs der Dateien
cursor_url = "https://cloud.dxra.de/s/728PKXwP8rkxEj3/download/HeitelCursorNormal.cur"
image_url = "https://cloud.dxra.de/s/BYPieotWME2QACB/download/HeitelCursorsLogo.png"
icon_url = "https://raw.githubusercontent.com/CreepTV/Heitel-Cursor/refs/heads/main/recources/HeitelCursorLogoNew.ico"
sound_url = "https://cloud.dxra.de/s/ieX32WHSHYjrBYy/download/HeitelHardwareSounde.mp3"
window_url = "https://github.com/CreepTV/Heitel-Cursor/blob/main/recources/window_icon.png"
sound_icon_url = "https://cloud.dxra.de/s/tkLdMagazPr7LJS/download/sound_icon.png"
cursor_icon_url = "https://cloud.dxra.de/s/fSBCty8DwH9tSdq/download/cursor_icon.png"
window_icon_url = "https://cloud.dxra.de/s/QzN3pR5L4qbdxHC/download/windowsymbol_icon.png"

# Globales Variablen für das Bild
global img
global image_label

# Dateien herunterladen
def download_files(progress_bar, loading_label):
    files_to_download = {
        cursor_file: cursor_url,
        image_file: image_url,
        icon_file: icon_url,
        sound_file: sound_url,
        window_file: window_url,
        sound_icon_file: sound_icon_url,
        cursor_icon_file: cursor_icon_url,
        window_icon_file: window_icon_url
    }

    total_files = len(files_to_download)
    files_downloaded = 0
    files_already_present = True

    for file_path, file_url in files_to_download.items():
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            files_already_present = False
            try:
                urllib.request.urlretrieve(file_url, file_path)
                print(f"{os.path.basename(file_path)} heruntergeladen nach: {file_path}")
            except Exception as e:
                print(f"Fehler beim Herunterladen von {os.path.basename(file_path)}: {e}")
        else:
            print(f"{os.path.basename(file_path)} ist bereits vorhanden.")
        
        files_downloaded += 1
        progress = files_downloaded / total_files
        
        # GUI-Aktualisierungen müssen im Haupt-Thread erfolgen
        root.after(0, lambda: update_progress(progress_bar, loading_label, progress, files_already_present))

    root.after(0, lambda: finish_download(loading_label))  # Haupt-Thread verwenden

def update_progress(progress_bar, loading_label, progress, files_already_present):
    progress_bar.set(progress)
    if files_already_present:
        loading_label.configure(text=f"Lade Dateien... ({int(progress * 100)}%)")
    else:
        loading_label.configure(text=f"Lade Dateien herunter... ({int(progress * 100)}%)")

def finish_download(loading_label):
    loading_label.configure(text="Dateien geladen!")
    root.after(1000, show_main_page)  # 1 Sekunde warten, dann zur Hauptseite wechseln

notification_list = []  # Liste, um aktive Benachrichtigungen zu verfolgen

# Initialisiere Pygame-Mixer
pygame.mixer.init()

# Lautstärkeregler Wert
volume_value = 0.5

# Variable to store the click sound file path
click_sound_file = sound_file  # Default to HeitelHardwareSounde.mp3

# Lautstärke einstellen
def set_volume(value):
    global volume_value
    volume_value = float(value) / 100
    pygame.mixer.music.set_volume(volume_value)
    volume_percentage_label.configure(text=f"{int(value)}%")  # Aktualisiere die Prozentanzeige

# Sound abspielen
def play_sound():
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

# Function to play the click sound
def play_click_sound():
    if click_sound_enabled.get() and os.path.exists(click_sound_file):
        try:
            sound = pygame.mixer.Sound(click_sound_file)
            sound.set_volume(volume_value)  # Set volume for the click sound
            sound.play()
        except Exception as e:
            print(f"Fehler beim Abspielen des Klicksounds: {e}")

# Function to upload a custom click sound
def upload_click_sound():
    global click_sound_file
    file_path = tk.filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
    if file_path:
        click_sound_file = file_path
        show_notification("Klicksound erfolgreich geändert!")
        update_click_sound_label()

# Function to reset the click sound to the default
def reset_click_sound():
    global click_sound_file
    click_sound_file = sound_file  # Reset to default sound
    show_notification("Klicksound auf Standard zurückgesetzt!")
    update_click_sound_label()

# Function to update the label showing the current sound file
def update_click_sound_label():
    current_sound_label.configure(text=f"Aktuell: {os.path.basename(click_sound_file)}")

# Lade eine benutzerdefinierte Cursor-Datei
def set_custom_cursor():
    cursor = ctypes.windll.user32.LoadImageW(0, cursor_file, win32con.IMAGE_CURSOR, 0, 0, win32con.LR_LOADFROMFILE)
    if cursor:
        ctypes.windll.user32.SetSystemCursor(cursor, 32512)  # IDC_ARROW
        show_notification("Heitel Cursor wurde gesetzt!")
        play_sound()
    else:
        show_notification("Fehler beim Laden des Cursors")
        play_sound()

# Lade eine benutzerdefinierte Cursor-Datei mit angepasster Größe
def set_custom_cursor_with_size(size):
    cursor = ctypes.windll.user32.LoadImageW(0, cursor_file, win32con.IMAGE_CURSOR, size, size, win32con.LR_LOADFROMFILE)
    if cursor:
        ctypes.windll.user32.SetSystemCursor(cursor, 32512)  # IDC_ARROW
        play_sound()
    else:
        show_notification("Fehler beim Laden des Cursors")
        play_sound()

# Setzt den Standard-Cursor zurück
def reset_cursor():
    ctypes.windll.user32.SystemParametersInfoW(87, 0, None, 0)
    show_notification("Standard-Cursor wiederhergestellt!")
    play_click_sound()

# Beendet das Programm
def exit_program():
    play_sound()
    root.quit()

# Benachrichtigung anzeigen
def show_notification(message):
    notification = Toplevel()
    notification.overrideredirect(True)
    notification.configure(bg='black')  # Hintergrund schwarz setzen
    notification.attributes("-topmost", True)
    
    # Container für Bild und Text
    content_frame = Label(notification, bg='black')
    content_frame.pack()

    # Bild hinzufügen
    try:
        if os.path.exists(image_file):
            img = Image.open(image_file)
            img = img.resize((32, 32))  # Größe des Bildes anpassen
            photo = ImageTk.PhotoImage(img)
            image_label = Label(content_frame, image=photo, bg='black')
            image_label.image = photo  # Referenz speichern
            image_label.pack(side='left', padx=5)
    except (FileNotFoundError, UnidentifiedImageError) as e:
        print(f"Fehler beim Laden des Bildes: {e}")

    label = Label(content_frame, text=message, bg="black", fg="white", padx=10, pady=5, font=("Arial", 12))
    label.pack(side='left')

    # Dynamisch die Größe der Benachrichtigungsbox anpassen
    notification.update_idletasks()
    notification_width = content_frame.winfo_reqwidth() + 20
    notification_height = content_frame.winfo_reqheight() + 10
    screen_width = notification.winfo_screenwidth()
    screen_height = notification.winfo_screenheight()

    # Position der neuen Benachrichtigung berechnen
    padding = 10  # Abstand zwischen den Benachrichtigungen
    y_position = screen_height - notification_height - 100 - (len(notification_list) * (notification_height + padding))
    x_position = screen_width - notification_width - 20
    notification.geometry(f"{notification_width}x{notification_height}+{x_position}+{y_position}")
    
    notification_list.append((notification, notification_height))

    # Entferne Benachrichtigung nach 2 Sekunden
    def remove_notification():
        notification.destroy()
        notification_list.remove((notification, notification_height))
        for i, (noti, height) in enumerate(notification_list):
            new_y_position = screen_height - height - 100 - (i * (height + padding))
            noti.geometry(f"{notification_width}x{height}+{x_position}+{new_y_position}")

    notification.after(2000, remove_notification)

def set_appearance_mode(mode):
    ctk.set_appearance_mode(mode)
    update_appearance_buttons(mode)

def update_appearance_buttons(active_mode):
    modes = ["Dark", "Light", "System"]
    buttons = [dark_mode_button, light_mode_button, system_mode_button]
    for mode, button in zip(modes, buttons):
        if mode == active_mode:
            if mode == "Dark":
                button.configure(fg_color="gray")
            elif mode == "Light":
                button.configure(fg_color="gray")
            elif mode == "System":
                button.configure(fg_color="lightgray")
        else:
            if mode == "Dark":
                button.configure(fg_color="darkgray")
            elif mode == "Light":
                button.configure(fg_color="white")
            elif mode == "System":
                button.configure(fg_color="gray")

# GUI erstellen
def create_gui():
    ctk.set_appearance_mode("System")  # "Dark", "Light", or "System"
    ctk.set_default_color_theme("blue")
    
    global frame
    frame = ctk.CTkFrame(root, corner_radius=10)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Bild einfügen
    global img, image_label
    try:
        if os.path.exists(image_file):
            img = CTkImage(Image.open(image_file), size=(84, 84))
            image_label = ctk.CTkLabel(frame, image=img, text="")
            image_label.pack(anchor="ne", padx=10, pady=5)
    except (FileNotFoundError, UnidentifiedImageError) as e:
        print(f"Fehler beim Laden des Bildes: {e}")
    
    # Tab-Steuerung hinzufügen
    tab_control = ctk.CTkTabview(frame)
    tab_control.pack(pady=10, padx=0, fill="both", expand=True)  # Tabs weiter nach links verschieben
    
    # Tab für Cursor-Einstellungen
    tab_cursor = tab_control.add("Cursor")
    
    cursor_frame = ctk.CTkFrame(tab_cursor, corner_radius=10)
    cursor_frame.pack(pady=10, padx=10, fill="x", anchor="w")
    
    label = ctk.CTkLabel(cursor_frame, text="Wähle einen Cursor:", font=("Arial", 16))
    label.pack(pady=10, anchor="w", padx=10)  # Linken Abstand hinzufügen
    
    button_set = ctk.CTkButton(cursor_frame, text="Heitel Cursor setzen", command=lambda: set_custom_cursor_with_size(int(cursor_size_slider.get())), fg_color="#cc7000", hover_color="#994c00")
    button_set.pack(pady=5, anchor="w", padx=10)  # Linken Abstand hinzufügen
    
    button_reset = ctk.CTkButton(cursor_frame, text="Standard-Cursor wiederherstellen", command=reset_cursor)
    button_reset.pack(pady=5, anchor="w", padx=10)  # Linken Abstand hinzufügen
    
    # Tab für Einstellungen
    tab_settings = tab_control.add("Settings")

    # Vertikale Leiste für Sound und Cursors mit Symbolen
    settings_frame = ctk.CTkFrame(tab_settings)
    settings_frame.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

    sidebar_frame = ctk.CTkFrame(settings_frame, width=40, corner_radius=0)  # Dünnere Leiste
    sidebar_frame.pack(side="left", fill="y")
    sidebar_frame.pack_propagate(False)

    # Symbole laden
    try:
        sound_image = CTkImage(Image.open(sound_icon_file), size=(20, 20))
        cursor_image = CTkImage(Image.open(cursor_icon_file), size=(20, 20))
        window_image = CTkImage(Image.open(window_icon_file), size=(20, 20))
    except (FileNotFoundError, UnidentifiedImageError) as e:
        print(f"Fehler beim Laden der Symbole: {e}")
        sound_image = None
        cursor_image = None
        window_image = None

    sound_button = ctk.CTkButton(sidebar_frame, image=sound_image, text="", width=30, height=30,  # Größe anpassen
                                   command=lambda: show_settings_tab("Sound", sound_frame, cursor_frame, window_frame))
    sound_button.pack(pady=(20, 0), padx=5)  # Padding anpassen

    cursor_button = ctk.CTkButton(sidebar_frame, image=cursor_image, text="", width=30, height=30,  # Größe anpassen
                                    command=lambda: show_settings_tab("Cursors", sound_frame, cursor_frame, window_frame))
    cursor_button.pack(pady=(20, 0), padx=5)  # Padding anpassen

    window_button = ctk.CTkButton(sidebar_frame, image=window_image, text="", width=30, height=30,  # Größe anpassen
                                    command=lambda: show_settings_tab("Window", sound_frame, cursor_frame, window_frame))
    window_button.pack(pady=(20, 0), padx=5)  # Padding anpassen

    # Frames für Sound-, Cursor- und Fenster-Einstellungen
    sound_frame = ctk.CTkFrame(settings_frame, corner_radius=0)
    cursor_frame = ctk.CTkFrame(settings_frame, corner_radius=0)
    window_frame = ctk.CTkFrame(settings_frame, corner_radius=0)

    def show_settings_tab(value, sound_frame, cursor_frame, window_frame):
        if value == "Sound":
            sound_frame.pack(side="right", fill="both", expand=True)
            cursor_frame.pack_forget()
            window_frame.pack_forget()
        elif value == "Cursors":
            cursor_frame.pack(side="right", fill="both", expand=True)
            sound_frame.pack_forget()
            window_frame.pack_forget()
        elif value == "Window":
            window_frame.pack(side="right", fill="both", expand=True)
            sound_frame.pack_forget()
            cursor_frame.pack_forget()

    # Sound Einstellungen
    volume_label = ctk.CTkLabel(sound_frame, text="Lautstärke", font=("Arial", 16))
    volume_label.pack(pady=5, anchor="w", padx=10)

    # Lautstärkeregler und Prozentanzeige hinzufügen
    volume_frame = ctk.CTkFrame(sound_frame, corner_radius=10)
    volume_frame.pack(pady=5, padx=10, fill="x", anchor="w")

    volume_slider = CTkSlider(volume_frame, from_=0, to=100, command=set_volume)
    volume_slider.set(volume_value * 100)  # Setze die anfängliche Lautstärke auf 50%
    volume_slider.pack(side="left", fill="x", expand=True, padx=(0, 5))

    # Prozentanzeige hinzufügen
    global volume_percentage_label
    volume_percentage_label = ctk.CTkLabel(volume_frame, text=f"{int(volume_value * 100)}%", font=("Arial", 12))
    volume_percentage_label.pack(side="left", padx=(5, 10))

    # Add click sound settings to the sound frame
    click_sound_label = ctk.CTkLabel(sound_frame, text="Klicksound", font=("Arial", 16))
    click_sound_label.pack(pady=5, anchor="w", padx=10)

    click_sound_frame = ctk.CTkFrame(sound_frame, corner_radius=10)
    click_sound_frame.pack(pady=5, padx=10, fill="x", anchor="w")

    click_sound_checkbox = ctk.CTkCheckBox(click_sound_frame, text="Aktivieren", variable=click_sound_enabled)
    click_sound_checkbox.pack(side="left", padx=(0, 10))

    upload_sound_button = ctk.CTkButton(click_sound_frame, text="Eigenen Sound hochladen", command=upload_click_sound)
    upload_sound_button.pack(side="left", padx=(10, 0))

    # Label to display the current sound file
    global current_sound_label
    current_sound_label = ctk.CTkLabel(sound_frame, text=f"Aktuell: {os.path.basename(click_sound_file)}", font=("Arial", 10))
    current_sound_label.pack(pady=(5, 0), anchor="w", padx=10)

    # Move the reset button below the current sound label
    reset_sound_button = ctk.CTkButton(sound_frame, text="Standard wiederherstellen", command=reset_click_sound)
    reset_sound_button.pack(pady=(5, 0), anchor="w", padx=10)

    # Cursor Einstellungen
    cursor_label = ctk.CTkLabel(cursor_frame, text="Cursors", font=("Arial", 16))
    cursor_label.pack(pady=(0, 0), anchor="w", padx=10)  # Padding unten hinzufügen

    # Cursor Größe Einstellungen
    cursor_size_label = ctk.CTkLabel(cursor_frame, text="Cursor Größe:", font=("Arial", 11))
    cursor_size_label.pack(pady=(0, 5), anchor="w", padx=10)  # Padding unten hinzufügen

    cursor_size_frame = ctk.CTkFrame(cursor_frame, corner_radius=10)
    cursor_size_frame.pack(pady=5, padx=10, fill="x", anchor="w")

    cursor_size_slider = CTkSlider(cursor_size_frame, from_=16, to=128, orientation=HORIZONTAL)
    cursor_size_slider.set(85)  # Setze die anfängliche Größe auf 85
    cursor_size_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

    cursor_size_value_label = ctk.CTkLabel(cursor_size_frame, text="85", font=("Arial", 12))
    cursor_size_value_label.pack(side="left", padx=(5, 10))

    def update_cursor_size(size):
        size = int(size)
        cursor_size_value_label.configure(text=str(size))
        set_custom_cursor_with_size(size)  # Aktualisiere die Cursorgröße

    cursor_size_slider.configure(command=update_cursor_size)
    update_cursor_size(85)  # Initiale Größe

    # Knopf zum Zurücksetzen der Größe auf 86
    def reset_to_standard_size():
        cursor_size_slider.set(86)
        cursor_size_value_label.configure(text="86")
        set_custom_cursor_with_size(86)  # Aktualisiere die Cursorgröße

    button_reset_size = ctk.CTkButton(cursor_frame, text="Standardgröße zurücksetzen", command=reset_to_standard_size)
    button_reset_size.pack(pady=5, anchor="w", padx=10)  # Linken Abstand hinzufügen

    # Fenster Einstellungen
    window_label = ctk.CTkLabel(window_frame, text="Anwendung", font=("Arial", 16))
    window_label.pack(pady=5, anchor="w", padx=10)

    # Farbschema Einstellungen
    appearance_label = ctk.CTkLabel(window_frame, text="Farbschema:", font=("Arial", 11))
    appearance_label.pack(pady=(10, 5), anchor="w", padx=10)

    appearance_frame = ctk.CTkFrame(window_frame, corner_radius=10)
    appearance_frame.pack(pady=5, padx=10, fill="x", anchor="w")

    global dark_mode_button, light_mode_button, system_mode_button

    dark_mode_button = ctk.CTkButton(appearance_frame, text="Dunkel", command=lambda: set_appearance_mode("Dark"), width=40, height=20)
    dark_mode_button.pack(side="left", padx=5, pady=5)

    light_mode_button = ctk.CTkButton(appearance_frame, text="Hell", command=lambda: set_appearance_mode("Light"), width=40, height=20)
    light_mode_button.pack(side="left", padx=5, pady=5)

    system_mode_button = ctk.CTkButton(appearance_frame, text="System", command=lambda: set_appearance_mode("System"), width=40, height=20)
    system_mode_button.pack(side="left", padx=5, pady=5)

    # Set initial appearance mode
    update_appearance_buttons("System")

    # Weitere Fenster-Einstellungen hier hinzufügen

    # Initiales Anzeigen des Sound-Tabs
    show_settings_tab("Sound", sound_frame, cursor_frame, window_frame)
    
    # Leiste unten
    bottom_frame = ctk.CTkFrame(root, height=40, corner_radius=10)
    bottom_frame.pack(fill="x", side="bottom", padx=10, pady=5)
    
    button_exit = ctk.CTkButton(bottom_frame, text="Beenden", command=exit_program, fg_color="red", hover_color="darkred")
    button_exit.pack(pady=5, padx=10, anchor="e")  # Positioniere den Button unten rechts

def show_loading_page():
    global root, click_sound_enabled  # Declare click_sound_enabled as global
    root = ctk.CTk()
    root.title("Heitel Cursor")
    root.geometry("430x510")  # Größe des Hauptfensters um 20% vergrößern
    root.resizable(False, False)  # Fenstergröße nicht veränderbar

    # Initialize click_sound_enabled as disabled by default
    click_sound_enabled = tk.BooleanVar(value=False)  # Default to disabled

    # Bind left mouse click to play_click_sound
    root.bind("<Button-1>", lambda event: play_click_sound())

    # Icon setzen
    if os.path.exists(icon_file):
        root.iconbitmap(icon_file)

    global frame
    frame = ctk.CTkFrame(root, corner_radius=10)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    loading_label = ctk.CTkLabel(frame, text="Lade Dateien herunter...", font=("Arial", 16))
    loading_label.pack(pady=20)

    progress_bar = CTkProgressBar(frame, width=300)
    progress_bar.set(0)
    progress_bar.pack(pady=10)

    # Starten des Downloads in einem separaten Thread
    download_thread = threading.Thread(target=download_files, args=(progress_bar, loading_label))
    download_thread.start()

def show_main_page():
    # Zerstöre die Lade-Widgets und den Frame
    frame.destroy()
    create_gui()

# Function to handle global mouse clicks
def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.left:  # Check for left mouse button press
        play_click_sound()

# Start a global mouse listener
def start_global_mouse_listener():
    listener = mouse.Listener(on_click=on_click)
    listener.start()

if __name__ == "__main__":
    start_global_mouse_listener()  # Start the global mouse listener
    show_loading_page()
    root.mainloop()  # Verwende root.mainloop() statt ctk.mainloop()