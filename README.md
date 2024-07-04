# Inventory Management System

This project is a web-based Inventory Management System built using Flask, SQLite, and Pandas. It allows users to upload product data, manage borrowing and returning of items, and send email reminders for outstanding borrowed items.

## Incoming updates

- Scanning part for a delivery order

## Features

- **Borrow and Return Items**: Record borrowing and returning of items.
- **Outstanding Borrowers**: View outstanding borrowers and send email reminders.
- **Search Functionality**: Search for products by part number or description.


## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/inventory-management-system.git
    cd inventory-management-system
    ```

2. Install the required Python packages:
    ```bash
    pip install flask pandas schedule
    ```

3. Set up the SQLite database:
    ```bash
    sqlite3 products.db < schema.sql
    ```

## Endpoints

- **/return_item**: Update the return date of a borrowed item.
- **/borrow_list**: View the list of borrowed items.
- **/get_outstanding_borrowers2**: Send email reminders to outstanding borrowers to all the users that has borrowed an item - Manual trigger
- **/get_outstanding_borrowers**: Send email reminders to outstanding borrowers every 3 days
- **/returns**: View the list of return authorizations.
- **/borrow**: Borrow an item.

## Email Reminders

The application can send email reminders to users with outstanding borrowed items. Ensure you configure the SMTP settings in the `send_email` function with your email credentials.


## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.

---

For detailed setup instructions and customization, refer to the source code and comments within the scripts.
