import datetime
import os.path
import sys
import tkinter as tk
from tkinter import filedialog
from typing import List, Dict, Callable, TypeVar, Union

# noinspection PyUnresolvedReferences
from PhillyHTMLElements import PhillyHTMLElements
# noinspection PyUnresolvedReferences
from SeleniumBrowser.lib.SeleniumBrowser import SeleniumBrowser
# noinspection PyUnresolvedReferences
from SeleniumBrowser.lib.XPathLookupProps import XPathLookupProps
# noinspection PyUnresolvedReferences
from database.models.BaseModel import BaseModel
# noinspection PyUnresolvedReferences
from database.models.Errors import Errors, ErrorsKeys
# noinspection PyUnresolvedReferences
from database.models.Properties import Properties
# noinspection PyUnresolvedReferences
from database.models.Taxes import Taxes
from peewee import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
# noinspection PyUnresolvedReferences,PyPep8Naming
from utils.lib.Excel import Excel as Excel

dir_path: str = ''
try:
    dir_path = os.path.dirname(os.path.realpath(__file__))
except NameError:
    dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.append(dir_path)

from lib.PhillyHTMLElements import PhillyHTMLElements
from lib.SeleniumBrowser.lib.SeleniumBrowser import SeleniumBrowser
from lib.SeleniumBrowser.lib.XPathLookupProps import XPathLookupProps
from lib.database.models.BaseModel import BaseModel
from lib.database.models.Properties import Properties
from lib.database.models.Taxes import Taxes
from lib.database.models.Errors import Errors
from lib.utils.lib.Excel import Excel

BaseModelT = TypeVar('T', bound=BaseModel)

root = tk.Tk()
root.withdraw()


class ParsedAddressPageResp:
    property_model: Properties
    tax_models: List[Taxes]


class PhillyParser(object):
    db: SqliteDatabase
    browser: SeleniumBrowser
    search_elements: PhillyHTMLElements

    output_headers: List[str]
    error_headers: List[str]
    output_file: Excel
    error_file: Excel

    # TODO: Check for chromedriver existence, exit if not
    def __init__(self, path_to_chromedriver: str = dir_path + "/chromedriver"):
        """
        Initialize Selenium headless browser class, SQLite database, XPath search patterns for traversing
        Masonic, and create database tables

        :param path_to_chromedriver: The path to chromedriver which is used by Selenium for browsing via Chrome
        """
        self.browser = SeleniumBrowser(path_to_chromedriver)
        self.db = Properties.db
        self.db.connect()

        self.output_headers = []
        self.error_headers = []

        self.output_file = Excel('./estates.xlsx')
        self.error_file = Excel('./errors.xlsx')

        self.search_elements = PhillyHTMLElements()
        self.db.create_tables([Properties, Taxes, Errors])

    @staticmethod
    def get_chromedriver_path():
        plat = sys.platform
        if plat == 'linux':
            return '/chromedriver/linux'
        elif plat == 'darwin':
            return '/chromedriver/osx'
        else:
            return '/chromedriver/windows'

    def parse_philly(self):
        print('\n\nStarting script\n\n')
        print('Select the CSV file for parsing*:')
        print('*Note: Address queries must be listed in the first column (A) in the selected spreadsheet file\n\n')

        csv_file: str = filedialog.askopenfilename()
        # csv_file: str = PhillyParser.get_csv_file_path('../input/TESTInput.csv')

        output_path: str = csv_file[:csv_file.rfind('/')]

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.output_file.file_name = '{}/estates_{}.xlsx'.format(output_path, timestamp)
        self.error_file.file_name = '{}/errors_{}.xlsx'.format(output_path, timestamp)

        print('Will download addresses from \n{}\n\n'.format(csv_file))

        print('Loading search page...', end='')
        # TODO: Fix
        address_list = [x for x in PhillyParser.get_address_list(csv_file) if 'address' not in x.lower() and x != '']
        if not self.browse_to_homepage(done_message='Success\n'):
            raise SystemExit('Something went wrong when loading the search page, exiting script')

        # address_list = ['1021 S 60th ']

        # Clear errors table - don't want lingering errors to be output
        Errors.delete().where(Errors.id >= 0).execute()

        print('Beginning download of address information...\n')
        self.parse_address_list(address_list)
        print('All address information has been downloaded and output to Excel.\n')

        print('Checking for errors...')
        if len(self.error_headers) > 0:
            print('There were some problems when downloading the addresses.\n')
            print('Please check errors.xlsx to see which addresses need to be re-run through the script. You can take '
                  'a look at the reason each download failed or you can run errors.xlsx itself through the script '
                  'and attempt to re-download the addresses automatically.\n')
        else:
            print('No errors were found when downloading addresses! Everything was successful\n')

        print('\nScript finished, exiting\n\n')

        self.browser.quit()

    @staticmethod
    def get_csv_file_path(relative_path: str) -> str:
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.abspath(os.path.join(current_dir_path, relative_path))

    @staticmethod
    def get_address_list(csv_file_path: str):
        rows = Excel.convert_csv_file_to_rows(csv_file_path)
        return [x[0] for x in rows if len(x) > 0]

    def parse_address_list(self, addresses: List[str]):
        error_addresses: List[str] = []
        output_addresses: List[str] = []
        total_output: int = 0
        total_errors: int = 0
        for idx in range(len(addresses)):
            address = addresses[idx]
            print('Downloading information for {}...'.format(address))
            info = self.get_address_info(address)

            if info is None:
                print('Something went wrong, skipping address ' + address + '\n')
                error_addresses.append(address)
            else:
                print('\nAll information for {} parsed, uploading to database'.format(address))
                self.upload_tax_info_to_db([info])
                output_addresses.append(address)
                print('Success - Moving on to next address\n\n')

            upload_count = len(output_addresses)
            if upload_count >= 5 or idx + 1 == len(addresses):
                self.browser.restart_browser()
                self.browse_to_homepage()

                if len(output_addresses) > 0:
                    print('Outputting data to Excel file')
                    output = PhillyParser.convert_database_for_output(output_addresses)
                    self.update_output_headers(output[0])

                    if total_output > 0:
                        output = output[3:]

                    self.output_file.save_rows(output, total_output)

                    if total_output == 0:
                        total_output += 3

                    total_output += len(output_addresses)
                    output_addresses.clear()
                    print('Done. {} addresses have been output so far\n\n'.format(total_output - 3))

                if len(error_addresses) > 0:
                    print('Some errors were found when downloading the last batch of addresses. Outputting to Excel')
                    self.output_any_errors(error_addresses, total_errors)
                    total_errors += len(error_addresses) + 2 if total_errors == 0 else 0
                    error_addresses.clear()
                    print('Done. {} total errors have been found so far\n\n'.format(total_errors - 2))

    @staticmethod
    def upload_to_errors(address: str, code: str, message: str = ''):
        error = Errors()
        error.search_by_address = address
        error.error_code = code
        error.message = message

        Errors.insert(error.to_dict()).on_conflict_replace().execute()

    def browse_to_homepage(self, done_message: str = None):
        load_check: XPathLookupProps = XPathLookupProps(By.ID, self.search_elements.search_form.search_box_id,
                                                        done_message=done_message)
        return self.browser.browse_to_url(self.search_elements.base_url, load_check)

    def update_output_headers(self, rows: List[str]):
        if len(self.output_headers) == 0:
            self.output_headers = rows[0]
            return

        sheet = self.output_file.workbook.active

        check_headers = rows[0]
        for idx in range(len(check_headers)):
            current = self.output_headers[idx]
            check = check_headers[idx]

            if current != check:
                self.output_headers.insert(idx, check)
                sheet.insert_cols(idx, 1)
                sheet.cell(1, idx + 1, check)

    # noinspection PyProtectedMember
    def get_address_info(self, address: str) -> Union[ParsedAddressPageResp, None]:
        browser: webdriver.Chrome = self.browser.get_browser()

        elements = self.search_elements
        search_form = elements.search_form
        tax_info = elements.tax_info

        property_model: Properties = Properties()
        tax_models: List[Taxes] = []

        load_check: XPathLookupProps = XPathLookupProps(By.ID, search_form.search_box_id, done_message=None)
        if not self.browser.check_presence_of_element(load_check):
            print('Something went wrong when loading the page, attempting reload')

            load_check.done_message = 'Reload successful\nContinuing'

            if not self.browser.browse_to_url(elements.base_url, load_check):
                PhillyParser.upload_to_errors(address, 'Load Page', 'Could not load Philly\'s search page')
                return print('Page could not be reloaded, moving on to next address')

        search_box: WebElement = browser.find_element_by_id(search_form.search_box_id)
        submit: WebElement = browser.find_element_by_id(search_form.submit_button_id)

        browser.execute_script("arguments[0].setAttribute('value', '{}')".format(address), search_box)
        submit.click()

        # Check page for no address found
        error_check: XPathLookupProps = XPathLookupProps(By.ID, search_form.error_box_id, done_message=None)
        if self.browser.check_presence_of_element(error_check):
            error_box: WebElement = browser.find_element_by_id(search_form.error_box_id)
            if error_box.get_attribute('innerHTML') != '':
                PhillyParser.upload_to_errors(address, 'Address Not Found',
                                              'The search form could not find the given address. Check the address manually')
                return print(
                    'Could not download information for {}; the address was not found through Philly\'s search form. Continuing'.format(
                        address))

        load_check = XPathLookupProps(By.ID, tax_info.brt_id, done_message='Address found and page loaded successfully')
        if not self.browser.check_presence_of_element(load_check):
            # TODO: Error table
            PhillyParser.upload_to_errors(address, 'Load Page', 'Could not load Philly\'s search page')
            return print('Could not download information for {}, continuing'.format(address))

        print('Parsing out property information...', end='')

        contact_table: WebElement = browser.find_element_by_id(tax_info.customer_table_id)

        brt = contact_table.find_element_by_id(tax_info.brt_id).get_attribute('innerHTML')
        property_address = contact_table.find_element_by_id(tax_info.address_id).get_attribute('innerHTML')
        postal = contact_table.find_element_by_id(tax_info.postal_code_id).get_attribute('innerHTML')
        owner = contact_table.find_element_by_id(tax_info.owner_id).get_attribute('innerHTML')
        payments = contact_table.find_element_by_id(tax_info.payments_id).get_attribute('innerHTML')

        print('Done\nParsing out tax information...', end='')

        tax_table: WebElement = browser.find_element_by_id(tax_info.tax_summary_table_id)
        tax_table_header: WebElement = tax_table.find_element_by_class_name(tax_info.tax_table_header_class)

        tax_header_elements: List[WebElement] = tax_table_header.find_elements_by_xpath('.//th')
        tax_header_cols: List[str] = [
            x.get_attribute('innerHTML').lower().replace(' ', '_').replace('#', '_number') for x in tax_header_elements
        ]

        # Skip header row
        tax_table_rows: List[WebElement] = tax_table.find_elements_by_xpath('.//tr')[1:]

        formatted_tax_rows: List[Dict[str, Union[str, None]]] = []
        for row in tax_table_rows:
            tax_cols: List[WebElement] = row.find_elements_by_xpath('.//td')

            formatted_tax_dict: Dict[str, str] = dict()
            for idx in range(len(tax_cols)):
                header: str = tax_header_cols[idx]
                col: str = tax_cols[idx].get_attribute('innerHTML').replace('&nbsp;', '')

                formatted_tax_dict[header] = col

            formatted_tax_rows.append(formatted_tax_dict)

        print(
            'Done\nAll information for {} has been gathered\n\nOutputting to database models for safekeeping...'.format(
                property_address), end='')

        property_model.search_by_address = address
        property_model.brt_number = brt
        property_model.property_address = property_address
        property_model.postal_code = postal
        property_model.owner_name = owner
        property_model.includes_payments_through = payments

        for tax_info in formatted_tax_rows:

            if 'year' in tax_info:
                datum: str = tax_info.pop('year')
                tax_info['tax_category'] = datum

            keys: List[str] = list(tax_info.keys())
            tax_db_keys: List[str] = Taxes._meta.sorted_field_names

            for key in keys:
                if key not in tax_db_keys:
                    tax_info.pop(key)
                elif tax_info[key] == '':
                    tax_info[key] = None

            tax_models.append(Taxes().initialize(tax_info))

        output = ParsedAddressPageResp()
        output.property_model = property_model
        output.tax_models = tax_models

        print('Done')

        return output

    @staticmethod
    def upload_tax_info_to_db(address: List[ParsedAddressPageResp]):
        properties = Properties()
        taxes = Taxes()

        property_models: List[Properties] = [x.property_model for x in address]
        tax_models_list: List[List[Taxes]] = [x.tax_models for x in address]

        properties.upload_many(property_models)

        for idx in range(len(tax_models_list)):
            property_model = property_models[idx]
            tax = tax_models_list[idx]

            prop_db = Properties.select().where(Properties.brt_number == property_model.brt_number).limit(1)[0]

            for model in tax:
                model.property_internal_id = prop_db.id

            taxes.upload_many(tax)

    # TODO: Move to utils class - Maybe?
    # noinspection PyProtectedMember
    @staticmethod
    def convert_database_for_output(address_list: List[str]) -> List[List[str]]:
        properties: List[Properties] = Properties.select().where(Properties.search_by_address.in_(address_list))

        output: List[List[str]] = []
        headers: List[str] = []
        convert_header: Callable[[str], str] = lambda x: x.replace('_', ' ').replace('number', '#').title().replace(
            'By', 'by').replace('Brt', 'BRT')

        tax_category_models = Taxes.select(Taxes.tax_category).distinct(True)
        tax_categories: List[str] = [x.tax_category for x in tax_category_models]
        tax_categories = list(filter(lambda x: not x.isdigit() or (x.isdigit() and int(x) >= 2000), tax_categories))

        tax_categories.sort()
        tax_categories = list(reversed(tax_categories))

        property_headers = list(Properties._meta.sorted_field_names)
        tax_keys = list(Taxes._meta.sorted_field_names)
        remove_keys = ['id', 'created_at', 'property_internal_id', 'tax_category']
        for key in remove_keys:
            tax_keys.remove(key) if key in tax_keys else 0
            property_headers.remove(key) if key in property_headers else 0

        tax_key_replacements = [convert_header(x) for x in tax_keys]
        property_header_replacements = [convert_header(x) for x in property_headers]

        headers += property_header_replacements

        for category in tax_categories:
            for key in tax_key_replacements:
                headers.append(category + '_' + key)

        output += [headers, [], ['File created: ' + str(datetime.datetime.now())], []]

        for property_model in properties:
            property_dict = property_model.to_dict()

            taxes: List[Taxes] = Taxes.select().where(Taxes.property_internal_id == property_model.id)
            grouped_taxes: Dict[str, Taxes] = {tax.tax_category: tax for tax in taxes}

            new_row: List[str] = []

            for key in property_headers:
                if key in property_dict and property_dict[key] is not None:
                    new_row.append(str(property_dict[key]))
                else:
                    new_row.append('')

            for category in tax_categories:
                if category in grouped_taxes:
                    tax = grouped_taxes[category].to_dict()
                    for key in tax_keys:
                        if key in tax and tax[key] is not None:
                            new_row.append(str(tax[key]))
                        else:
                            new_row.append('')
                else:
                    # Add blank rows
                    new_row += [''] * len(tax_key_replacements)

            output.append(new_row)

        return output

    @staticmethod
    def sort_tax_categories(a: str, b: str):
        if a == b:
            return 0
        elif a.isdigit() and b.isdigit():
            return int(b) - int(a)
        elif not a.isdigit() and not b.isdigit():
            return a > b
        elif not b.isdigit() and a.isdigit():
            return 1
        elif not a.isdigit() and b.isdigit():
            return -1
        else:
            return 1

    @staticmethod
    def output_to_excel(output: List[List[str]], file_name='output.xlsx', output_path: str = None):
        # TODO: Format excel spreadsheet output
        if output_path is None:
            output_path = os.path.dirname(os.path.realpath(__file__))
            output_path = os.path.abspath(os.path.join(output_path, '../output/' + file_name))
        else:
            output_path = os.path.abspath(os.path.join(output_path, './' + file_name))

        Excel.create_master_sheet(output_path, output)

    # TODO: Move row_start to Excel class
    def output_any_errors(self, addresses: List[str], row_start: int = 0):
        excel_output: List[List[str]] = []

        headers: List[str] = Errors._meta.sorted_field_names
        error_models: List[Errors] = Errors.select().where(Errors.search_by_address.in_(addresses))
        errors: List[dict] = [x.to_dict() for x in error_models]

        if len(errors) > 0:
            if len(self.error_headers) == 0:
                headers.remove('id')
                headers.remove('created_at')
                headers.append('created_at')

                replacement_headers = [x.replace('_', ' ').title().replace('By', 'by') for x in headers]
                self.error_headers = replacement_headers
                excel_output += [replacement_headers, []]

            for error in errors:
                new_row: List[str] = []
                for header in headers:
                    if header in error:
                        new_row.append(str(error[header]))
                    else:
                        new_row.append('')
                excel_output.append(new_row)

            self.error_file.save_rows(excel_output, row_start)


parser = PhillyParser(dir_path + PhillyParser.get_chromedriver_path())
parser.parse_philly()
