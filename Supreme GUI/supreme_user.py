#!/usr/bin/python3
# Zachary Weeden 2018

import sys
from PyQt4 import QtGui
from supreme_app import SupremeWidget


class UIUserInfoWindow(QtGui.QWidget):
    def __init__(self):
        """
        Constructor for GUI widget
        """
        super(UIUserInfoWindow, self).__init__()

        self.user_config_info = None

        # Layout stuff
        self.customer_name_label = QtGui.QLabel()
        self.customer_name_label.setText('First and Last name:')
        self.customer_name_field = QtGui.QLineEdit()

        self.customer_email_label = QtGui.QLabel()
        self.customer_email_label.setText('Email:')
        self.customer_email_field = QtGui.QLineEdit()

        self.customer_phone_label = QtGui.QLabel()
        self.customer_phone_label.setText('Phone eg. (585-867-5309):')
        self.customer_phone_field = QtGui.QLineEdit()

        self.customer_address_label = QtGui.QLabel()
        self.customer_address_label.setText('Street Address:')
        self.customer_address_field = QtGui.QLineEdit()

        self.customer_zip_code_label = QtGui.QLabel()
        self.customer_zip_code_label.setText('Zip Code:')
        self.customer_zip_code_field = QtGui.QLineEdit()

        self.customer_city_label = QtGui.QLabel()
        self.customer_city_label.setText('City:')
        self.customer_city_field = QtGui.QLineEdit()

        self.customer_state_label = QtGui.QLabel()
        self.customer_state_label.setText('State eg. (NY):')
        self.customer_state_field = QtGui.QLineEdit()

        self.customer_country_label = QtGui.QLabel()
        self.customer_country_label.setText('Country eg. (USA):')
        self.customer_country_field = QtGui.QLineEdit()

        self.customer_card_type_label = QtGui.QLabel()
        self.customer_card_type_label.setText('Card type eg. (visa, mastercard):')
        self.customer_card_type_field = QtGui.QLineEdit()

        self.customer_card_number_label = QtGui.QLabel()
        self.customer_card_number_label.setText('Card number eg. (9999 9999 9999 9999):')
        self.customer_card_number_field = QtGui.QLineEdit()

        self.customer_card_exp_month_label = QtGui.QLabel()
        self.customer_card_exp_month_label.setText('Card expiration month eg. (02):')
        self.customer_card_exp_month_field = QtGui.QLineEdit()

        self.customer_card_exp_year_label = QtGui.QLabel()
        self.customer_card_exp_year_label.setText('Card expiration year eg. (2020):')
        self.customer_card_exp_year_field = QtGui.QLineEdit()

        self.customer_cvv_label = QtGui.QLabel()
        self.customer_cvv_label.setText('3 Digit CVV:')
        self.customer_cvv_field = QtGui.QLineEdit()

        self.submit_button = QtGui.QPushButton("Save user info")
        self.exit_button = QtGui.QPushButton("Exit")

        grid = QtGui.QGridLayout()
        grid.setSpacing(20)

        grid.addWidget(self.customer_name_label, 1, 0)
        grid.addWidget(self.customer_name_field, 2, 0)

        grid.addWidget(self.customer_email_label, 3, 0)
        grid.addWidget(self.customer_email_field, 4, 0)

        grid.addWidget(self.customer_phone_label, 5, 0)
        grid.addWidget(self.customer_phone_field, 6, 0)

        grid.addWidget(self.customer_address_label, 7, 0)
        grid.addWidget(self.customer_address_field, 8, 0)

        grid.addWidget(self.customer_city_label, 9, 0)
        grid.addWidget(self.customer_city_field, 10, 0)

        grid.addWidget(self.customer_zip_code_label, 9, 1)
        grid.addWidget(self.customer_zip_code_field, 10, 1)

        grid.addWidget(self.customer_state_label, 9, 2)
        grid.addWidget(self.customer_state_field, 10, 2)

        grid.addWidget(self.customer_country_label, 11, 0)
        grid.addWidget(self.customer_country_field, 12, 0)

        grid.addWidget(self.customer_card_type_label, 1, 4)
        grid.addWidget(self.customer_card_type_field, 2, 4)

        grid.addWidget(self.customer_card_number_label, 3, 4)
        grid.addWidget(self.customer_card_number_field, 4, 4)

        grid.addWidget(self.customer_card_exp_month_label, 5, 4)
        grid.addWidget(self.customer_card_exp_month_field, 6, 4)

        grid.addWidget(self.customer_card_exp_year_label, 5, 5)
        grid.addWidget(self.customer_card_exp_year_field, 6, 5)

        grid.addWidget(self.customer_cvv_label, 5, 7)
        grid.addWidget(self.customer_cvv_field, 6, 7)

        grid.addWidget(self.submit_button, 20, 0)
        grid.addWidget(self.exit_button, 20, 2)

        self.submit_button.clicked.connect(self.open_window)
        self.exit_button.clicked.connect(lambda: self.exit())

        self.setLayout(grid)

        self.setWindowTitle('Supreme')
        self.show()

    def set_user_dict(self):
        self.user_config_info = {
            'firstAndLast': self.customer_name_field.text(),
            'email': self.customer_email_field.text(),
            'phone': self.customer_phone_field.text(),
            'address': self.customer_address_field.text(),
            'zip': self.customer_zip_code_field.text(),
            'city': self.customer_city_field.text(),
            'state': self.customer_state_field.text(),
            'country': self.customer_country_field.text(),
            'cardType': self.customer_card_type_field.text(),
            'cardNumber': self.customer_card_number_field.text(),
            'cardMonth': self.customer_card_exp_month_field.text(),
            'cardYear': self.customer_card_exp_year_field.text(),
            'cardCVV': self.customer_cvv_field.text()
        }

    def exit(self):
        print('State: Exitting')
        sys.exit()

    def open_window(self):
        self.set_user_dict()
        self.window = QtGui.QMainWindow()
        self.ui = SupremeWidget(self.user_config_info)
        UIUserInfoWindow.hide(self)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    UserInfoWindow = QtGui.QMainWindow()
    ui = UIUserInfoWindow()
    sys.exit(app.exec_())
