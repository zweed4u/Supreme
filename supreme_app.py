#!/usr/bin/python3
# Zachary Weeden 2018

import sys
import threading
from PyQt4 import QtGui
from supreme_3 import SupremeProduct


class MyWidget(QtGui.QWidget):
    def __init__(self):
        """
        Constructor for GUI widget
        """
        super(MyWidget, self).__init__()

        # layout stuff
        # TODO also include config information here - billing, etc.
        self.product_name_label = QtGui.QLabel(self)
        self.product_name_label.setText('Product name:')
        self.product_name_field = QtGui.QLineEdit(self)

        self.product_color_label = QtGui.QLabel(self)
        self.product_color_label.setText('Product color:')
        self.product_color_field = QtGui.QLineEdit(self)

        self.product_size_label = QtGui.QLabel(self)
        self.product_size_label.setText('Product size:')
        self.product_size_field = QtGui.QLineEdit(self)

        self.product_quantity_label = QtGui.QLabel(self)
        self.product_quantity_label.setText('Product quantity:')
        self.product_quantity_field = QtGui.QLineEdit(self)

        self.submit_button = QtGui.QPushButton("Submit")
        self.exit_button = QtGui.QPushButton("Exit")

        vLayout = QtGui.QVBoxLayout()
        vLayout.addWidget(self.product_name_label)
        vLayout.addWidget(self.product_name_field)
        vLayout.addWidget(self.product_color_label)
        vLayout.addWidget(self.product_color_field)
        vLayout.addWidget(self.product_size_label)
        vLayout.addWidget(self.product_size_field)
        vLayout.addWidget(self.product_quantity_label)
        vLayout.addWidget(self.product_quantity_field)
        vLayout.addWidget(self.submit_button)
        vLayout.addWidget(self.exit_button)
        self.setLayout(vLayout)

        # slots
        self.submit_button.clicked.connect(lambda: self.set_all())
        self.exit_button.clicked.connect(lambda: self.exit())
        self.show()

    def set_all(self):
        # TODO Set class attributes for this product search and clear fields for next item
        # TODO Allow for concurrent searches and display background tasks
        self.product_name = self.product_name_field.text()
        self.product_color = self.product_color_field.text()
        self.product_size = self.product_size_field.text()
        self.product_quantity = int(self.product_quantity_field.text())
        product_thread = threading.Thread(target=SupremeProduct, args=(self.product_name, self.product_color, self.product_size, self.product_quantity,))
        print(f'[[ Thread ]]{str(self.product_name)} :: {str(self.product_size)} :: {str(self.product_color)} :: {str(self.product_quantity)} :: Thread initialized!')
        product_thread.start()

    def exit(self):
        """
        Exit logic used when exit button pressed on gui
        :return:
        """
        print('State: Exitting')
        sys.exit()


def main():
    """
    Main of lab 3 desktop gui
    :return:
    """
    app = QtGui.QApplication(sys.argv)
    myWidget = MyWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
