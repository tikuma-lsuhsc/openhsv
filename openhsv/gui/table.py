from PyQt5.QtWidgets import QWidget, QTableWidget, QGridLayout, \
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, \
    QPushButton

import pandas as pd

class Table(QWidget):
    def __init__(self, d, headers=['parameter', 'mean', 'std'], title="Table"):
        super().__init__()

        self.d = d
        self.headers = headers
        self.setWindowTitle(title)

        # Add table
        self.l = QGridLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(headers)

        # Adjust table to window size
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Stretch)
        self.l.addWidget(self.table)

        # Add export option
        p = QPushButton("Export table to csv")
        p.clicked.connect(self.exportToCSV)
        self.l.addWidget(p)

        self.initTable()

    def initTable(self):
        for k, v in self.d.items():
            # Add a new row at the end of the table
            i = self.table.rowCount()
            self.table.setRowCount(i+1)

            # Write the dictionary key in first column
            self.table.setItem(i, 0, QTableWidgetItem(k))

            # if only one number is provided
            if type(v) is float or type(v) is int:
                self.table.setItem(i, 1, QTableWidgetItem(str(v)))

            # if multiple values are provided
            elif type(v) is tuple:
                for j, v_ in enumerate(v):
                    self.table.setItem(i, 1+j, QTableWidgetItem(str(v_)))

            else:
                self.table.setItem(i, 1, QTableWidgetItem(str(v)))

    def exportToCSV(self):
        # Specify default CSV export option
        fd = QFileDialog()
        fd.setDefaultSuffix("csv")
        
        saveTo = fd.getSaveFileName(filter="*.csv")[0]

        # No file is selected, abort export routine
        if not saveTo:
            return

        # Retrieve information from table
        items = []

        for i in range(self.table.rowCount()):
            row = {}

            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                
                if item != None:
                    row[self.headers[j]] = item.text()

            items.append(row)

        # Create pandas DataFrame and export to CSV
        df = pd.DataFrame(items)
        df.to_csv(saveTo, index=False)

        QMessageBox.information(
            self,
            "Data exported",
            f"Table was successfully exported to \n{saveTo}."
        )


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    
    # Use some random numbers for illustration
    params = {
        'Fundamental frequency': (100, 10),
        'Mean shimmer': 3.123,
        'Mean jitter': 0.245,
        'Other': (13.32, 0.111)
    }

    T = Table(params)
    T.show()

    app.exec_()