import tkinter as tk
from tkinter import ttk
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageTk
import base64


def colouring_rgb(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def encode_base64(data):
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def decode_base64(data):
    return base64.b64decode(data.encode("utf-8")).decode("utf-8")


def AppStart():
    AppStart.root = tk.Tk()
    AppStart.root.iconbitmap("hamter\\hamterico.ico")
    AppStart.root.geometry("1366x768")
    AppStart.root.title("hamter.")

    colourhex = colouring_rgb(238, 232, 170)
    AppStart.mainframe = tk.Frame(AppStart.root, background=colourhex)
    AppStart.mainframe.pack(fill="both", expand=True)

    AppStart.label = ttk.Label(
        AppStart.mainframe,
        text="Welcome to Hamter.",
        background=colourhex,
        font=("Adobe Caslon Pro Bold", 30),
    )
    AppStart.label.grid(row=0, column=0, sticky="NW", padx=10, pady=10)

    AppStart.text = ttk.Label(
        AppStart.mainframe,
        text="Enter your Instagram username, email, or phone:",
        background=colourhex,
        font=("Chaparral Pro", 20),
    )
    AppStart.text.grid(row=1, column=0, pady=(0, 10), padx=10, sticky="W")

    AppStart.set_text_field = ttk.Entry(AppStart.mainframe)
    AppStart.set_text_field.grid(row=2, column=0, pady=(10, 20), padx=10, sticky="NWES")

    AppStart.text2 = ttk.Label(
        AppStart.mainframe,
        text="Enter your Instagram password:",
        background=colourhex,
        font=("Chaparral Pro", 20),
    )
    AppStart.text2.grid(row=3, column=0, pady=(30, 10), padx=10, sticky="W")

    AppStart.set_text_field2 = ttk.Entry(AppStart.mainframe, show="*")
    AppStart.set_text_field2.grid(
        row=4, column=0, pady=(10, 20), padx=10, sticky="NWES"
    )

    AppStart.text3 = ttk.Label(
        AppStart.mainframe,
        text="Enter the user you want to hampt :3",
        background=colourhex,
        font=("Chaparral Pro", 20),
    )
    AppStart.text3.grid(row=5, column=0, pady=(30, 10), padx=10, sticky="W")

    AppStart.set_text_field3 = ttk.Entry(AppStart.mainframe)
    AppStart.set_text_field3.grid(
        row=6, column=0, pady=(10, 20), padx=10, sticky="NWES"
    )

    style = ttk.Style()
    style.configure(
        "TButton",
        font=("Bell Gothic Std Black", 20),
        padding=(10, 5),
        foreground=colouring_rgb(230, 63, 255),
    )

    AppStart.start_button = ttk.Button(
        AppStart.mainframe, text="Start Hamting.", style="TButton", command=startcommand
    )
    AppStart.start_button.grid(row=7, column=0, pady=(30, 20), padx=10, sticky="W")

    AppStart.show_help_button = ttk.Button(
        AppStart.mainframe, text="Help", style="TButton", command=show_help
    )
    AppStart.show_help_button.grid(row=7, column=0, pady=(30, 20), padx=250, sticky="W")

    AppStart.root.mainloop()


def get_credentials():
    entered_username = AppStart.set_text_field.get()
    entered_password = AppStart.set_text_field2.get()

    saved_username = None
    saved_password = None

    if os.path.exists("hamter\\credentials.txt"):
        with open("hamter\\credentials.txt", "r") as file:
            lines = file.readlines()
            if len(lines) >= 2:
                encoded_username = lines[0].strip()
                encoded_password = lines[1].strip()
                saved_username = decode_base64(encoded_username)
                saved_password = decode_base64(encoded_password)

    if not entered_username:
        entered_username = saved_username
    if not entered_password:
        entered_password = saved_password

    if (
        (entered_username != saved_username or entered_password != saved_password)
        and entered_username
        and entered_password
    ):
        encoded_username = encode_base64(entered_username)
        encoded_password = encode_base64(entered_password)
        with open("hamter\\credentials.txt", "w") as file:
            file.write(f"{encoded_username}\n{encoded_password}")

    return entered_username, entered_password


def startcommand():
    username, password = get_credentials()
    target_user = AppStart.set_text_field3.get()

    AppStart.start_button.config(state=tk.DISABLED)

    follower_scraper(username, password, target_user)
    follower_comparison()
    show_results()


def follower_scraper(username, password, target_user):
    path = "hamter\\chromedriver.exe"
    service = Service(path)
    driver = webdriver.Chrome(service=service)
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")

    width = 1400
    height = 820
    x = AppStart.root.winfo_x()
    y = AppStart.root.winfo_y()
    driver.set_window_size(width, height)
    driver.set_window_position(x, y)

    driver.get("https://www.instagram.com/accounts/login/")

    time.sleep(10)

    cookies_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[2]",
            )
        )
    )
    driver.execute_script("arguments[0].click();", cookies_button)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")

    username_field.send_keys(username)
    password_field.send_keys(password)

    login_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="loginForm"]/div/div[3]/button')
        )
    )
    driver.execute_script("arguments[0].click();", login_button)

    time.sleep(10)
    driver.get(f"https://www.instagram.com/{target_user}/followers/")
    time.sleep(3.5)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers')]"))
    ).click()

    time.sleep(5)

    previous_usernames = set()
    unchanged_count = 0
    max_unchanged = 3

    while True:
        try:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;",
                driver.find_element(
                    By.XPATH,
                    "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]",
                ),
            )
        except Exception:
            pass

        usernames = driver.find_elements(
            By.XPATH, "//span[starts-with(@class, '_ap3a')]"
        )
        current_usernames = set(
            [username.text.strip().lower() for username in usernames]
        )

        if current_usernames == previous_usernames:
            unchanged_count += 1
            if unchanged_count >= max_unchanged:
                X_button = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button",
                        )
                    )
                )
                X_button.click()
                break
        else:
            unchanged_count = 0

        previous_usernames = current_usernames

        with open("hamter\\usernames_followers.txt", "w", encoding="utf-8") as file:
            for username in current_usernames:
                file.write(username + "\n")

        time.sleep(1.5)

    time.sleep(5)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers')]"))
    ).click()

    existing_usernames = set()
    if os.path.exists("hamter\\usernames_followers.txt"):
        with open("hamter\\usernames_followers.txt", "r", encoding="utf-8") as file:
            existing_usernames.update(line.strip().lower() for line in file)

    previous_usernames = set()
    unchanged_count = 0
    max_unchanged = 10

    while True:
        try:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;",
                driver.find_element(
                    By.XPATH,
                    "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]",
                ),
            )
        except Exception:
            pass

        usernames = driver.find_elements(
            By.XPATH, "//span[starts-with(@class, '_ap3a')]"
        )
        current_usernames = set(
            [username.text.strip().lower() for username in usernames]
        )

        if current_usernames == previous_usernames:
            unchanged_count += 1
            if unchanged_count >= max_unchanged:
                X_button = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button",
                        )
                    )
                )
                X_button.click()
                break
        else:
            unchanged_count = 0

        previous_usernames = current_usernames

        new_usernames = current_usernames - existing_usernames
        if new_usernames:
            with open("hamter\\usernames_followers.txt", "a", encoding="utf-8") as file:
                for username in new_usernames:
                    file.write(username + "\n")
            existing_usernames.update(new_usernames)

        time.sleep(1.5)

    time.sleep(1)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers')]"))
    ).click()

    existing_usernames = set()
    if os.path.exists("hamter\\usernames_followers.txt"):
        with open("hamter\\usernames_followers.txt", "r", encoding="utf-8") as file:
            existing_usernames.update(line.strip().lower() for line in file)

    previous_usernames = set()
    unchanged_count = 0
    max_unchanged = 10

    while True:
        try:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;",
                driver.find_element(
                    By.XPATH,
                    "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]",
                ),
            )
        except Exception:
            pass

        usernames = driver.find_elements(
            By.XPATH, "//span[starts-with(@class, '_ap3a')]"
        )
        current_usernames = set(
            [username.text.strip().lower() for username in usernames]
        )

        if current_usernames == previous_usernames:
            unchanged_count += 1
            if unchanged_count >= max_unchanged:
                X_button = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button",
                        )
                    )
                )
                X_button.click()
                break
        else:
            unchanged_count = 0

        previous_usernames = current_usernames

        new_usernames = current_usernames - existing_usernames
        if new_usernames:
            with open("hamter\\usernames_followers.txt", "a", encoding="utf-8") as file:
                for username in new_usernames:
                    file.write(username + "\n")
            existing_usernames.update(new_usernames)

        time.sleep(1.5)

    time.sleep(1)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers')]"))
    ).click()

    existing_usernames = set()
    if os.path.exists("hamter\\usernames_followers.txt"):
        with open("hamter\\usernames_followers.txt", "r", encoding="utf-8") as file:
            existing_usernames.update(line.strip().lower() for line in file)

    previous_usernames = set()
    unchanged_count = 0
    max_unchanged = 15

    while True:
        try:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;",
                driver.find_element(
                    By.XPATH,
                    "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]",
                ),
            )
        except Exception:
            pass

        usernames = driver.find_elements(
            By.XPATH, "//span[starts-with(@class, '_ap3a')]"
        )
        current_usernames = set(
            [username.text.strip().lower() for username in usernames]
        )

        if current_usernames == previous_usernames:
            unchanged_count += 1
            if unchanged_count >= max_unchanged:
                X_button = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button",
                        )
                    )
                )
                X_button.click()
                break
        else:
            unchanged_count = 0

        previous_usernames = current_usernames

        new_usernames = current_usernames - existing_usernames
        if new_usernames:
            with open("hamter\\usernames_followers.txt", "a", encoding="utf-8") as file:
                for username in new_usernames:
                    file.write(username + "\n")
            existing_usernames.update(new_usernames)

        time.sleep(1.5)

    time.sleep(5)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/following')]"))
    ).click()

    time.sleep(5)
    previous_usernames = set()
    unchanged_count = 0
    max_unchanged = 3

    while True:
        try:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;",
                driver.find_element(
                    By.XPATH,
                    "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[4]",
                ),
            )
        except Exception:
            pass

        usernames = driver.find_elements(
            By.XPATH, "//span[starts-with(@class, '_ap3a')]"
        )
        current_usernames = set(
            [username.text.strip().lower() for username in usernames]
        )

        if current_usernames == previous_usernames:
            unchanged_count += 1
            if unchanged_count >= max_unchanged:
                X_button = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button",
                        )
                    )
                )
                X_button.click()
                break
        else:
            unchanged_count = 0

        previous_usernames = current_usernames

        with open("hamter\\usernames_following.txt", "w", encoding="utf-8") as file:
            for username in current_usernames:
                file.write(username + "\n")

        time.sleep(1.5)

    time.sleep(5)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/following')]"))
    ).click()
    existing_usernames = set()
    if os.path.exists("hamter\\usernames_following.txt"):
        with open("hamter\\usernames_following.txt", "r", encoding="utf-8") as file:
            existing_usernames.update(line.strip().lower() for line in file)

    previous_usernames = set()
    unchanged_count = 0
    max_unchanged = 10

    while True:
        try:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;",
                driver.find_element(
                    By.XPATH,
                    "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[4]",
                ),
            )
        except Exception:
            pass

        usernames = driver.find_elements(
            By.XPATH, "//span[starts-with(@class, '_ap3a')]"
        )
        current_usernames = set(
            [username.text.strip().lower() for username in usernames]
        )

        if current_usernames == previous_usernames:
            unchanged_count += 1
            if unchanged_count >= max_unchanged:
                X_button = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button",
                        )
                    )
                )
                X_button.click()
                break
        else:
            unchanged_count = 0

        previous_usernames = current_usernames

        new_usernames = current_usernames - existing_usernames
        if new_usernames:
            with open("hamter\\usernames_following.txt", "a", encoding="utf-8") as file:
                for username in new_usernames:
                    file.write(username + "\n")
            existing_usernames.update(new_usernames)

        time.sleep(1.5)
    time.sleep(5)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/following')]"))
    ).click()
    existing_usernames = set()
    if os.path.exists("hamter\\usernames_following.txt"):
        with open("hamter\\usernames_following.txt", "r", encoding="utf-8") as file:
            existing_usernames.update(line.strip().lower() for line in file)

    previous_usernames = set()
    unchanged_count = 0
    max_unchanged = 10

    while True:
        try:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;",
                driver.find_element(
                    By.XPATH,
                    "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[4]",
                ),
            )
        except Exception:
            pass

        usernames = driver.find_elements(
            By.XPATH, "//span[starts-with(@class, '_ap3a')]"
        )
        current_usernames = set(
            [username.text.strip().lower() for username in usernames]
        )

        if current_usernames == previous_usernames:
            unchanged_count += 1
            if unchanged_count >= max_unchanged:
                X_button = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button",
                        )
                    )
                )
                X_button.click()
                break
        else:
            unchanged_count = 0

        previous_usernames = current_usernames

        new_usernames = current_usernames - existing_usernames
        if new_usernames:
            with open("hamter\\usernames_following.txt", "a", encoding="utf-8") as file:
                for username in new_usernames:
                    file.write(username + "\n")
            existing_usernames.update(new_usernames)

        time.sleep(1.5)


def follower_comparison():
    with open("hamter\\usernames_followers.txt", "r", encoding="utf-8") as f1:
        followers = set(f1.read().splitlines())

    with open("hamter\\usernames_following.txt", "r", encoding="utf-8") as f2:
        following = set(f2.read().splitlines())

    with open("hamter\\fans.txt", "w", encoding="utf-8") as f3:
        for name in followers - following:
            f3.write(name + "\n")

    with open("hamter\\not_mutuals.txt", "w", encoding="utf-8") as f4:
        for name in following - followers:
            f4.write(name + "\n")


def show_results():

    for widget in AppStart.mainframe.winfo_children():
        widget.destroy()

    fans = []
    not_mutuals = []

    if os.path.exists("hamter\\fans.txt"):
        with open("hamter\\fans.txt", "r", encoding="utf-8") as f:
            fans = f.read().splitlines()

    if os.path.exists("hamter\\not_mutuals.txt"):
        with open("hamter\\not_mutuals.txt", "r", encoding="utf-8") as f:
            not_mutuals = f.read().splitlines()

    fans_label = ttk.Label(
        AppStart.mainframe,
        text="Fans",
        background=colouring_rgb(238, 232, 170),
        font=("Chaparral Pro", 20),
    )
    fans_label.grid(row=0, column=2, padx=80, pady=10, sticky="W")

    not_mutuals_label = ttk.Label(
        AppStart.mainframe,
        text="Not Mutuals ",
        background=colouring_rgb(238, 232, 170),
        font=("Chaparral Pro", 20),
    )
    not_mutuals_label.grid(row=0, column=0, padx=10, pady=10, sticky="W")

    fans_listbox = tk.Listbox(
        AppStart.mainframe, height=25, width=30, font=("Arial", 14)
    )
    not_mutuals_listbox = tk.Listbox(
        AppStart.mainframe, height=25, width=30, font=("Arial", 14)
    )

    fans_listbox.grid(row=1, column=2, padx=80, pady=10)
    not_mutuals_listbox.grid(row=1, column=0, padx=10, pady=10)

    for fan in fans:
        fans_listbox.insert(tk.END, fan)

    for not_mutual in not_mutuals:
        not_mutuals_listbox.insert(tk.END, not_mutual)

    if os.path.exists("hamter\\hamtergif.gif"):

        gif_label = ttk.Label(
            AppStart.mainframe, background=colouring_rgb(238, 232, 170)
        )
        gif_label.grid(row=1, column=3, padx=10, pady=10, rowspan=10)

        gif_image = Image.open("hamter\\hamtergif.gif")

        frames = []
        try:
            for i in range(gif_image.n_frames):
                gif_image.seek(i)
                frame = gif_image.convert("RGBA")
                frames.append(ImageTk.PhotoImage(frame))
        except Exception as e:
            pass
            return

        def update_gif(frame_idx=0):
            frame = frames[frame_idx]
            gif_label.config(image=frame)

            AppStart.root.after(100, update_gif, (frame_idx + 1) % len(frames))

        update_gif()


def show_help():

    for widget in AppStart.mainframe.winfo_children():
        widget.destroy()

    instructions_label = ttk.Label(
        AppStart.mainframe,
        text="Instructions",
        background=colouring_rgb(238, 232, 170),
        font=("Chaparral Pro", 40),
        foreground=colouring_rgb(230, 63, 255),
    )
    instructions_label.grid(row=0, column=0, padx=80, pady=10, sticky="W")
    intructions_text = (
        "• If you leave the username and password fields empty,\n  the program will use the default username and password\n  you typed the last time you used the app."
        "\n\n• Do NOT use the app excesively often. Instagram can detect\n  suspicious activity and ban you if you use the app too much.\n  (once a day should be alright)"
        "\n\n• Do NOT touch the google driver bot until it is done with its job.\n  It will show you the results shortly after."
        "\n\n• The app is still unstable and in construction. It might crash, be slow,\n  or fail to collect all the followers. Please try again and be patient :3"
        "\n\n\nThis app was made by Pantelis Zarakis as a fun and educational project.\nThank you for using it! Have fun hampting ;)"
        "\n• Instagram : _zarakis_\n• Github : PantelisZara\n• Email : zarakisp@gmail.com"
    )
    help_label = ttk.Label(
        AppStart.mainframe,
        text=intructions_text,
        background=colouring_rgb(238, 232, 170),
        font=("Arial Bold", 20),
    )
    help_label.grid(row=1, column=0, padx=80, pady=10, sticky="W")

    back_button = ttk.Button(AppStart.mainframe, text="Back", command=back)
    back_button.grid(row=0, column=2, pady=(20, 10), padx=80, sticky="W")


def back():
    AppStart.root.destroy()
    AppStart()


if __name__ == "__main__":
    AppStart()
