from robocorp.tasks import task
from robocorp import browser
import logging


from RPA.HTTP import HTTP
from RPA.Tables import Tables 
from RPA.PDF import PDF 
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    orders robots from robotsparebin industries inc.
    saves the order html receipt as a pdf file
    saves the screenshot of the ordered robot
    embeds the screenshot of the robot to the pdf receipt
    creates ZIP archive of the receipts and the images
    """
    # browser.configure(
    #     slowmo=100,
    # )
    open_robot_order_website()
    archive_receipts()
    

def get_orders():
    http = HTTP()
    worksheet = http.download(url="https://robotsparebinindustries.com/orders.csv",overwrite=True)
    return worksheet

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

    orders= get_orders()
    library = Tables()
    tables = library.read_table_from_csv(path="orders.csv",header=True)

    for order in tables:
        fill_form(order)

def fill_form(data):
    page=browser.page()

    page.click("button:text('OK')")

    page.select_option("#head",str(data['Head']))
    body = str(data['Body'])
    page.click(f'input[type="radio"][value="{body}"]')
    page.fill(".form-control",str(data['Legs']))
    page.fill("#address",data['Address'])
    page.click("button:text('Preview')")
    page.click("button:text('Order')") 
    
    logging.basicConfig(level=logging.ERROR)
    orderAnother=False
    # try:
    #     # Wait for the error message to appear (with a timeout)
    #     page.wait_for_selector('div[role="alert"]', timeout=3000)
    #     page.click("button:text('Order')")
    #     logging.error("alert found")
    # except Exception as e:
    #     logging.error("no alert found")


    while not orderAnother:
        try:
            page.wait_for_selector("button:text('Order another robot')", timeout=3000)
            orderAnother=True
            file_path = store_receipt_as_pdf(str(data['Order number']))
            img_path = screenshot_robot(str(data['Order number']))
            embed_screenshot_to_receipt(img_path,file_path)
            page.click("button:text('Order another robot')") 
        except Exception as e:
            orderAnother=False
            page.click("button:text('Order')")

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    file_path="outputII/"+order_number+".pdf"
    pdf.html_to_pdf(receipt_html,file_path)
    return file_path

def screenshot_robot(order_number):
    page = browser.page()
    img_path = "outputII/"+order_number+".png"
    page.screenshot(path=img_path)
    return img_path


def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    list_of_files = [
        pdf_file,
        screenshot,
    ]
    pdf.add_files_to_pdf(
        files=list_of_files,
        target_document=pdf_file,
    )

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./outputII', 'receipts.zip')