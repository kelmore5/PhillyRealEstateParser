class SearchForm:
    """
    XPath and HTML id references for the address lookup form on Philadelphia's real estate site
    """
    search_box_id: str = "ctl00_BodyContentPlaceHolder_SearchByAddressControl_txtLookup"
    submit_button_id: str = "ctl00_BodyContentPlaceHolder_SearchByAddressControl_btnLookup"

    error_box_id: str = 'ctl00_BodyContentPlaceHolder_lblMessage'


class TaxInformation:
    """
    XPath and HTML id references for the tax information being parsed from Philadelphia's real estate site
    """
    customer_table_id: str = 'ctl00_BodyContentPlaceHolder_GetTaxInfoControl_frm'

    brt_id: str = 'ctl00_BodyContentPlaceHolder_GetTaxInfoControl_frm_lblPropertyTaxAccountNo'
    address_id: str = 'ctl00_BodyContentPlaceHolder_GetTaxInfoControl_frm_lblPropertyAddress'
    postal_code_id: str = 'ctl00_BodyContentPlaceHolder_GetTaxInfoControl_frm_Label1'
    owner_id: str = 'ctl00_BodyContentPlaceHolder_GetTaxInfoControl_frm_lblOwnerName'
    payments_id: str = 'ctl00_BodyContentPlaceHolder_GetTaxInfoControl_frm_lblPaymentPostDate'

    tax_summary_table_id: str = 'ctl00_BodyContentPlaceHolder_GetTaxInfoControl_grdPaymentsHistory'
    tax_table_header_class: str = 'grdHeader'


class PhillyHTMLElements(object):
    """
    This class hosts all the HTML elements that will be searched for within Masonic's web site
    via XPath
    """
    base_url: str = 'http://www.phila.gov/revenue/realestatetax/'

    search_form: SearchForm = SearchForm()
    tax_info: TaxInformation = TaxInformation()
