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
        self.product_name_label.setText('Product 1 name:')
        self.product_name_field = QtGui.QLineEdit(self)

        self.product_2_name_label = QtGui.QLabel(self)
        self.product_2_name_label.setText('Product 2 name:')
        self.product_2_name_field = QtGui.QLineEdit(self)

        self.product_3_name_label = QtGui.QLabel(self)
        self.product_3_name_label.setText('Product 3 name:')
        self.product_3_name_field = QtGui.QLineEdit(self)


        self.product_color_label = QtGui.QLabel(self)
        self.product_color_label.setText('Product 1 color:')
        self.product_color_field = QtGui.QLineEdit(self)

        self.product_2_color_label = QtGui.QLabel(self)
        self.product_2_color_label.setText('Product 2 color:')
        self.product_2_color_field = QtGui.QLineEdit(self)

        self.product_3_color_label = QtGui.QLabel(self)
        self.product_3_color_label.setText('Product 3 color:')
        self.product_3_color_field = QtGui.QLineEdit(self)


        self.product_size_label = QtGui.QLabel(self)
        self.product_size_label.setText('Product 1 size:')
        self.product_size_field = QtGui.QLineEdit(self)

        self.product_2_size_label = QtGui.QLabel(self)
        self.product_2_size_label.setText('Product 2 size:')
        self.product_2_size_field = QtGui.QLineEdit(self)

        self.product_3_size_label = QtGui.QLabel(self)
        self.product_3_size_label.setText('Product 3 size:')
        self.product_3_size_field = QtGui.QLineEdit(self)


        self.product_quantity_label = QtGui.QLabel(self)
        self.product_quantity_label.setText('Product 1 quantity:')
        self.product_quantity_field = QtGui.QLineEdit(self)

        self.product_2_quantity_label = QtGui.QLabel(self)
        self.product_2_quantity_label.setText('Product 2 quantity:')
        self.product_2_quantity_field = QtGui.QLineEdit(self)

        self.product_3_quantity_label = QtGui.QLabel(self)
        self.product_3_quantity_label.setText('Product 3 quantity:')
        self.product_3_quantity_field = QtGui.QLineEdit(self)


        self.submit_button = QtGui.QPushButton("Submit")
        self.exit_button = QtGui.QPushButton("Exit")

        grid = QtGui.QGridLayout()
        grid.setSpacing(20)

        grid.addWidget(self.product_name_label, 1, 0)
        grid.addWidget(self.product_name_field, 2, 0)
        grid.addWidget(self.product_2_name_label, 1, 1)
        grid.addWidget(self.product_2_name_field, 2, 1)
        grid.addWidget(self.product_3_name_label, 1, 2)
        grid.addWidget(self.product_3_name_field, 2, 2)

        grid.addWidget(self.product_color_label, 3, 0)
        grid.addWidget(self.product_color_field, 4, 0)
        grid.addWidget(self.product_2_color_label, 3, 1)
        grid.addWidget(self.product_2_color_field, 4, 1)
        grid.addWidget(self.product_3_color_label, 3, 2)
        grid.addWidget(self.product_3_color_field, 4, 2)

        grid.addWidget(self.product_size_label, 5, 0)
        grid.addWidget(self.product_size_field, 6, 0)
        grid.addWidget(self.product_2_size_label, 5, 1)
        grid.addWidget(self.product_2_size_field, 6, 1)
        grid.addWidget(self.product_3_size_label, 5, 2)
        grid.addWidget(self.product_3_size_field, 6, 2)

        grid.addWidget(self.product_quantity_label, 7, 0)
        grid.addWidget(self.product_quantity_field, 8, 0)
        grid.addWidget(self.product_2_quantity_label, 7, 1)
        grid.addWidget(self.product_2_quantity_field, 8, 1)
        grid.addWidget(self.product_3_quantity_label, 7, 2)
        grid.addWidget(self.product_3_quantity_field, 8, 2)

        grid.addWidget(self.submit_button, 9, 0)
        grid.addWidget(self.exit_button, 9, 2)

        self.field_elements = {
            self.product_name_field:{
                'color': self.product_color_field,
                'size': self.product_size_field,
                'quantity': self.product_quantity_field
            },
            self.product_2_name_field: {
                'color': self.product_2_color_field,
                'size': self.product_2_size_field,
                'quantity': self.product_2_quantity_field
            },
            self.product_3_name_field: {
                'color': self.product_3_color_field,
                'size': self.product_3_size_field,
                'quantity': self.product_3_quantity_field
            }
        }

        # slots
        self.submit_button.clicked.connect(lambda: self.set_all())
        self.exit_button.clicked.connect(lambda: self.exit())

        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Supreme')
        self.show()

    def set_all(self):
        # TODO Set class attributes for this product search and clear fields for next item
        # TODO Allow for concurrent searches and display background tasks
        for product_field in self.field_elements:
            if product_field.text() == '':
                print('Name not given for this product - skipping')
                continue
            self.product_name = product_field.text()
            self.product_color = self.field_elements[product_field]['color'].text()
            self.product_size = self.field_elements[product_field]['size'].text()
            self.product_quantity = int(self.field_elements[product_field]['quantity'].text())
            product_thread = threading.Thread(target=SupremeProduct, args=(self.product_name, self.product_color, self.product_size, self.product_quantity,))
            print(f'[[ Thread ]] {str(self.product_name)} :: {str(self.product_size)} :: {str(self.product_color)} :: {str(self.product_quantity)} :: Thread initialized!')
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
