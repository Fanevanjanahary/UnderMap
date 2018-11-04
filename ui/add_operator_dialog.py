# -*- coding: utf-8 -*-
"""Ajouter opérateur dialog."""

from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QDialogButtonBox
from qgis.gui import QgsFileWidget
from qgis.core import QgsMessageLog, Qgis
from UnderMap.utilities.resources import get_ui_class
from UnderMap.process import create_operator

FORM_CLASS = get_ui_class('add_operator_dialog_base.ui')


class AjouterOperateurDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None, iface=None):
        """Constructor."""
        super(AjouterOperateurDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        QDialog.__init__(self, parent)
        self.parent = parent
        self.iface = iface
        self.setupUi(self)
        self.select_pdf_action.setDialogTitle("Selectionner les pdf")
        self.select_pdf_action.setFilter("*.pdf")
        self.select_pdf_action.setStorageMode(storageMode=QgsFileWidget.GetMultipleFiles)

        self.operator_name.textChanged.connect(self.check_form_validation)
        self.select_pdf_action.fileChanged.connect(self.check_form_validation)

        # buttonOperator.accepted.connect(QMessageBox.warning(None,"Avertisment","Veulliez ouvrir un projet qgis"))

        # Set up things for ok button
        self.save_button = self.button_add_operator.button(QDialogButtonBox.Save)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.accept)

        # Set up things for cancel button
        self.cancel_button = self.button_add_operator.button(QDialogButtonBox.Cancel)
        self.cancel_button.clicked.connect(self.reject)

    def check_form_validation(self):
        """Slot pour chaque modifs du formulaire."""
        name_operator = self.operator_name.value()
        file_operator = self.select_pdf_action.filePath()
        if name_operator != '' and file_operator != '':
            self.save_button.setEnabled(True)
        else:
            self.save_button.setEnabled(False)

    def accept(self):
        """Method invoked when OK button is clicked."""
        name_operator = self.operator_name.value().upper()
        paths = self.select_pdf_action.filePath()
        file_operator = QgsFileWidget.splitFilePaths(paths)
        QgsMessageLog.logMessage("Ajouter un opérateur: {} avec PDF: {}".format(name_operator, ','.join(file_operator)), 'UnderMap', Qgis.Info)
        # create_operator(name_operator, file_operator)
        # QMessageBox.warning(None,"Avertisment", file_operator)
        # self.iface.messageBar().pushInfo(u'My Plugin says', self.operator_name.value())
        self.close()
