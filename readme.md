This is a small web scraping project for a hackathon
organised on 15 Nov 2025.

The details required for understanding the project's working
are described below -
- `scrap_script.py` is used to scrap the data.
- Scrapped data is processed and stored in `scrapped_data.csv` file.
- `webdisplay` is a flask project used to showcase the data
   in form of a website.
- To launch `webdisplay` in debug mode, source `launch_webdisplay.sh`
  on terminal from the root directory.
- Dependencies -
    - `playwright` for `scrap_script.py`.
    - `flask` for `webdisplay`.
- After installing `playwright` run -
    `python3 -m playwright install` to install
    playwright specific utilities.