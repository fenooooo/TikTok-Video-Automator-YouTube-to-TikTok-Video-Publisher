from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip
import os
from tkinter import Tk, Label, Entry, Button, StringVar, Text, END
import datetime

# Télécharger la vidéo YouTube avec yt-dlp
def download_youtube_video(url, output_path="video.mp4"):
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            log_message(f"Téléchargement réussi : {output_path}")
            return output_path
    except Exception as e:
        log_message(f"Erreur lors du téléchargement de la vidéo : {str(e)}")
        return None

# Fonction pour faire défiler la page jusqu'à un élément
def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView();", element)

# Connexion à TikTok via Google
def login_to_tiktok_with_google(driver, google_email, google_password):
    driver.get("https://www.tiktok.com/login")

    # Attendre que l'élément soit localisé et faire défiler pour cliquer
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Continuer avec Google')]")))
    
    google_login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continuer avec Google')]")

    # Faire défiler jusqu'au bouton Google
    scroll_to_element(driver, google_login_button)
    
    google_login_button.click()

    # Changer de fenêtre vers la fenêtre Google Login
    WebDriverWait(driver, 20).until(EC.number_of_windows_to_be(2))
    driver.switch_to.window(driver.window_handles[-1])  # Passer à la nouvelle fenêtre (Google login)

    # Saisir l'email Google
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
    email_input = driver.find_element(By.XPATH, "//input[@type='email']")
    email_input.send_keys(google_email)
    email_input.send_keys(Keys.RETURN)

    time.sleep(2)

    # Saisir le mot de passe Google
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
    password_input = driver.find_element(By.XPATH, "//input[@type='password']")
    password_input.send_keys(google_password)
    password_input.send_keys(Keys.RETURN)

    # Attendre que la redirection vers TikTok soit effectuée
    WebDriverWait(driver, 30).until(EC.number_of_windows_to_be(1))  # Attendre le retour à TikTok
    driver.switch_to.window(driver.window_handles[0])  # Revenir à la fenêtre TikTok
    print("Connexion réussie avec Google.")

# Fonction pour publier des vidéos sur TikTok (ou à programmer)
def upload_video_to_tiktok(driver, video_path, description, schedule=False, publish_time=None):
    driver.get("https://www.tiktok.com/upload")
    time.sleep(10)

    # Trouver et télécharger la vidéo
    upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    upload_input.send_keys(video_path)
    time.sleep(15)

    # Ajouter une description
    description_box = driver.find_element(By.XPATH, '//textarea')
    description_box.send_keys(description)

    # Si la vidéo doit être programmée, ajuster l'option de programmation
    if schedule and publish_time:
        # Cliquer sur l'option de programmation (ajustez si nécessaire)
        schedule_toggle = driver.find_element(By.XPATH, '//input[@type="checkbox"]')
        schedule_toggle.click()

        # Entrer la date et l'heure de publication
        date_input = driver.find_element(By.XPATH, '//input[@type="date"]')
        time_input = driver.find_element(By.XPATH, '//input[@type="time"]')

        date_input.send_keys(publish_time.strftime('%Y-%m-%d'))
        time_input.send_keys(publish_time.strftime('%H:%M'))

    # Publier ou programmer la vidéo
    post_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    post_button.click()
    time.sleep(10)

# Découper la vidéo en fragments d'une minute et les enregistrer dans un sous-répertoire
def split_video_into_fragments(input_path, output_dir, duration_per_clip=60):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Créer le sous-répertoire s'il n'existe pas

    video = VideoFileClip(input_path)
    fragments = []
    duration = video.duration
    for start_time in range(0, int(duration), duration_per_clip):
        end_time = min(start_time + duration_per_clip, duration)
        fragment = video.subclip(start_time, end_time)
        fragment_path = os.path.join(output_dir, f"fragment_{start_time // 60}.mp4")
        fragment.write_videofile(fragment_path, codec="libx264")
        fragments.append(fragment_path)
    return fragments

# Fonction principale
def start_process():
    youtube_url = youtube_url_var.get()
    google_email = username_var.get()
    google_password = password_var.get()

    # Télécharger la vidéo YouTube
    log_message("Téléchargement de la vidéo YouTube en cours...")
    video_path = download_youtube_video(youtube_url, output_path="video.mp4")
    
    if video_path:
        # Créer le sous-répertoire pour les fragments
        output_dir = "fragments"
        log_message(f"Découpage de la vidéo et enregistrement dans le sous-répertoire '{output_dir}'...")
        fragments = split_video_into_fragments(video_path, output_dir)

        # Lancer Selenium pour TikTok
        driver = webdriver.Chrome()  # Assurez-vous que ChromeDriver est installé et dans votre PATH
        log_message("Connexion à TikTok via Google...")
        login_to_tiktok_with_google(driver, google_email, google_password)

        # Publier les 5 premiers fragments immédiatement
        log_message("Publication des 5 premiers fragments...")
        for i in range(5):
            if i < len(fragments):
                upload_video_to_tiktok(driver, fragments[i], f"Fragment {i + 1} of {len(fragments)}")
                time.sleep(5)

        # Programmer les fragments restants (5 par jour)
        log_message("Programmation des fragments restants...")
        current_fragment = 5
        current_date = datetime.datetime.now()

        while current_fragment < len(fragments):
            current_date += datetime.timedelta(days=1)  # Incrémenter la date d'un jour

            for i in range(5):
                if current_fragment < len(fragments):
                    publish_time = current_date.replace(hour=9, minute=0)  # Planifier à 9h00 chaque jour
                    upload_video_to_tiktok(driver, fragments[current_fragment], f"Fragment {current_fragment + 1} of {len(fragments)}", schedule=True, publish_time=publish_time)
                    current_fragment += 1
                    time.sleep(5)

        driver.quit()
        log_message("Processus terminé.")

# Fonction pour afficher les messages dans la zone de log
def log_message(message):
    log_box.insert(END, message + "\n")
    log_box.see(END)

# Interface utilisateur Tkinter
root = Tk()
root.title("YouTube to TikTok Automator")

# Variables Tkinter
youtube_url_var = StringVar()
username_var = StringVar()
password_var = StringVar()

# Champs d'entrée dans l'interface
Label(root, text="URL de la vidéo YouTube:").grid(row=0, column=0, padx=10, pady=5)
Entry(root, textvariable=youtube_url_var, width=40).grid(row=0, column=1, padx=10, pady=5)

Label(root, text="Email Google:").grid(row=1, column=0, padx=10, pady=5)
Entry(root, textvariable=username_var, width=40).grid(row=1, column=1, padx=10, pady=5)

Label(root, text="Mot de passe Google:").grid(row=2, column=0, padx=10, pady=5)
Entry(root, textvariable=password_var, show="*", width=40).grid(row=2, column=1, padx=10, pady=5)

Button(root, text="Lancer le processus", command=start_process).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Zone de log pour les messages
log_box = Text(root, width=50, height=10)
log_box.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

root.mainloop()
