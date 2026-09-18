# hamter.

Hamter is a small Instagram follower comparison tool created as a fun and educational programming project.

The project originally started as a Windows desktop application using Python, Tkinter, Selenium and ChromeDriver. The original version attempted to automate Instagram login, navigation and follower/following scraping through a graphical interface.

The project was later migrated to **Arch Linux** and redesigned around a simpler command-line workflow. The current version leaves Instagram login and navigation to the user and focuses on collecting the Followers and Following lists and comparing them.

---

# Legacy Windows Version

The original Hamter application was developed for Windows.

It used:

- Python
- Tkinter
- Selenium
- ChromeDriver
- automated Instagram login
- automated navigation
- automatic follower/following scraping
- a graphical interface for displaying results

The original implementation is now considered **legacy/outdated** and is no longer maintained. Instagram changes its website structure frequently, so the original automated approach may no longer work reliably.

The original files remain in this repository for historical reference.

## Original Application



<img width="1209" height="1300" alt="Original Hamter Windows application" src="https://github.com/user-attachments/assets/66231442-f1f7-4aef-acf6-bd982dbecb54" />

---

# Arch Linux Version

The current version was rebuilt for **Arch Linux** with a much simpler workflow.

Instead of asking the program to automatically log into Instagram and navigate through the website, the user controls the browser manually while Selenium handles the repetitive task of collecting the usernames from the Followers and Following lists.

The current implementation is located in:

```text
arch-linux/
├── instagram_scraper.py
├── requirements.txt
├── setup.sh
└── run.sh
