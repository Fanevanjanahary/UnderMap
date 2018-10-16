# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UnderMap
                                 A QGIS plugin
 Plugin de Futurmap pour le traitement des réseaux enterrés
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-10-15
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Futurmap
        email                : fanevanjanahary@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from os.path import dirname, join, exists, isfile

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QToolButton, QMenu

# Initialize Qt resources from file resources.py
# from .resources import *
# Import the code for the dialog
from .ui.undermap_dialog import UnderMapDialog
from .ui.ajouter_operateur_dialog import AjouterOperateurDialog


class UnderMap:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = join(
            self.plugin_dir,
            'i18n',
            'UnderMap_{}.qm'.format(locale))

        if exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = UnderMapDialog()
        self.addop = AjouterOperateurDialog()
        self.initialisePDF = InitialisePDF()

        # Initialise buttton
        self.init_button = QToolButton()
        self.init_button.setMenu(QMenu())
        self.init_button.setPopupMode(QToolButton.MenuButtonPopup)

        # toolBar
        self.toolbar = self.iface.addToolBar('UnderMap')
        self.toolbar.setObjectName('UnderMap')

        # actions
        self.actions = None
        self.initialisePDFAction = None
        self.operateursAction = None
        self.vectorisationAction = None
        self.modificationAction = None
        self.rapportAction = None
        self.ajouterOperateurAction = None
        self.initialiseFDPAction = None
        self.initialiseemprise = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('UnderMap', message)



    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # the actions
        self.initialisePDFAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'initialpdf.png')),
            'Initialises PDF',
            self.iface.mainWindow())

        self.ajouterOperateurAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'ajouterOperateur.png')),
            'Ajouter un opérateur',
            self.iface.mainWindow())

        self.operateursAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'icon.png')),
            'Opérateurs',
            self.iface.mainWindow())
        self.vectorisationAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'vectorisation.png')),
            'Vectorisation',
            self.iface.mainWindow())

        # actions dialogs
        self.initialisePDFAction.triggered.connect(self.run)
        self.ajouterOperateurAction.triggered.connect(self.addOperateur)

        # add actions on menu
        self.init_button.menu().addAction(self.initialisePDFAction)
        self.init_button.menu().addAction(self.ajouterOperateurAction)
        self.init_button.setDefaultAction(self.initialisePDFAction)


        # add actions and menu in toolbar
        self.toolbar.addWidget(self.init_button)
        self.toolbar.addAction(self.operateursAction)
        self.toolbar.addAction(self.initialisePDFAction)
        self.toolbar.addAction(self.vectorisationAction)




    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removeToolBarIcon(self.init_button)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def addOperateur(self):
        self.addop.show()
        result = self.addop.exec_()

    def initialisePDF(self):


