# Author: Abhijeet Verma
# Email: parrotabhijeet@gmail.com
# College: School Of Information Technology, RGPV, Bhopal
# Course: Computer Science and Business System
# Degree: Bachelor Of Technology
# Dependencies: playwright
# Code tested on Chromium on Fedora Linux 43.

from playwright.sync_api import sync_playwright
import re, csv

root_url = "https://www3.shoalhaven.nsw.gov.au/masterviewUI/modules/ApplicationMaster/default.aspx"
data_export_file = "./scrapped_data.csv"
record_page_links = []
record_page_link_prefix = "https://www3.shoalhaven.nsw.gov.au/masterviewUI/modules/ApplicationMaster/"
final_data = [[
    "DA_Number", "Details URL", "Description",
    "Submission Date", "Decision", "Categories",
    "Property Address", "Applicant", "Progress",
    "Fees", "Documents", "Contact Council"]]
non_empty_fee_rows = 0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        print("Starting Scraping ...")
        page.goto(root_url)

        # clicking agree button
        agree_button_selector = "input[value='Agree']"

        with page.expect_navigation():
            page.click(agree_button_selector)

        # going to DA tracking

        DA_tracking_link = "a[href='Default.aspx']"

        with page.expect_navigation():
            page.click(DA_tracking_link)

        # filling and submitting search information

        advance_search_tab = "li.rtsLI:nth-child(2)"
        start_date_input = "#ctl00_cphContent_ctl00_ctl03_dateInput_text"
        end_date_input = "#ctl00_cphContent_ctl00_ctl05_dateInput_text"
        search_button = "#ctl00_cphContent_ctl00_btnSearch"

        page.click(advance_search_tab)
        page.type(start_date_input, "01/09/2025")
        page.type(end_date_input, "30/09/2025")

        with page.expect_navigation():
            page.click(search_button)

        # collecting submit buttons' links (record_page_links)
        print('Scraping pages ...')
        count = 1

        while(True):

            print('Scraping page {} ..'.format(count))

            record_links_selector = "#ctl00_cphContent_ctl01_ctl00_RadGrid1_ctl00 > tbody > tr > td > a"

            for locator in page.locator(record_links_selector).all():
                href = locator.get_attribute('href')
                record_page_links.append(href)

            next_page_button_selector = ".rgPageNext"
            next_page_button = tuple(page.locator(next_page_button_selector).all())[0]

            #if(count == 2): break # Use while developing, to reduce records

            if(next_page_button.get_attribute('onclick').startswith('return')): break

            page.click(next_page_button_selector)
            count += 1

        # scrapping each record from its page
        print("Scraping Records ...")
        count = 1
        total = len(record_page_links)
        for page_link in record_page_links:
            print("Scraping record {}/{} ..".format(count, total))
            page.goto('{}{}'.format(record_page_link_prefix,page_link))
            record = []

            # DA_Number
            record.append(page.locator("#ctl00_cphContent_ctl00_lblApplicationHeader").text_content())
            
            # Detail URL
            record.append('{}{}'.format(record_page_link_prefix,page_link))

            # Description and Submission Date
            
            c = page.locator("#lblDetails").text_content().strip()
            pattern = r"Description:(.*?)Submitted:([\d/]*)"
            match = re.search(pattern, c)

            date, description = '', ''
            if match:
                description = match.group(1).strip()
                date = match.group(2).strip()

            if match:
                record.append(description)
                record.append(date)
            else:
                record.append(c)

            # Decision
            record.append(page.locator("#lblDecision").text_content().strip())

            # Categories
            record.append(page.locator("#lblCat").text_content().strip())

            # Property_Address
            record.append(page.locator("#lblProp").text_content().strip())

            # Applicant
            record.append(page.locator("#lblPeople").text_content().strip())

            # Progress
            locator = page.locator("tr.shTableAlt:nth-child(2) > td:nth-child(2)")
            if(locator.count() == 0):
                record.append("No progress.")
            else:
                # in progress, appending progress message
                record.append(locator.text_content().strip())

            # Fees
            scrapped_string = page.locator("#lblFees").text_content().strip()
            if(scrapped_string.startswith('No fees')):
                record.append("Not Required")
            else:
                record.append(
                    re.search(
                        r"\$([\d,]+(?:\.\d{1,2})?)",
                        page.locator("#lblFees > table > tbody > tr:nth-last-child(1) > td").text_content().strip()
                        ).group(1).strip()
                    )
                non_empty_fee_rows += 1

            # Documents
            # in case there are multiple documents
            documents = ''
            for document in page.locator("#lblDocs > b").all():
                documents = documents + document.text_content().strip() + '; '
            record.append(documents)
            

            # Contact_Council
            scrapped_string = page.locator("#lbl91").text_content().strip()
            if(scrapped_string.startswith("Application Is Not on exhibition")):
                record.append("Not required")
            else:
                record.append(scrapped_string)
            
            final_data.append(record)

            #if count == 20: break   # use while developing to reduce records
            count += 1


    except Exception as e:
        print("!!! An exception occured. !!! \n{}".format(e))
    finally:
        browser.close()
        print("Browser closed.")
        print("Scrapping Done.")

# writing collected data to csv file
print("Writing data to csv file ...")
with open(data_export_file, 'w') as f:
    writer = csv.writer(f)
    writer.writerows(final_data)

print("Rows with fees/Total rows = {}/{}.".format(non_empty_fee_rows, len(final_data)-1))
print("Exit.")

# Note: Due to limited hackathon time, I wasn't able to use
#       asynchronous programmming. So scrapping time is blocking and thus high.
#       I understand that if we can implement async pattern, time will reduce significantly
#       due to parallel GET requests.