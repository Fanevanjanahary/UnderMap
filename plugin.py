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

import os, logging
from os.path import dirname, join, exists

from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolButton, QMenu, QFileDialog, QMessageBox
from qgis.core import QgsSettings, QgsProject

# Initialize Qt resources from file resources.py
# from .resources import *
# Import the code for the dialog
from .ui.undermap_dialog import UnderMapDialog
from .ui.add_operator_dialog import AjouterOperateurDialog
from .ui.manage_pdf_dialog import DialogAddPDF, DialogSplitPDF
from .ui.import_points_dialog import DialogImportPoint
from .utilities.utilities import get_project_path
from UnderMap.process import (
    initialise_pdf,
    initialise_fdp,
    initialise_emprise,
    export_xlsx_report,
    export_as_geojson
    )
from UnderMap.gis.tools import (
    get_layers_in_group,
    manage_buffer,
    transparency_raster
    )


LOGGER = logging.getLogger('UnderMap')


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
        self.addpdf = DialogAddPDF()
        self.splitpdf = DialogSplitPDF()
        self.importpoints = DialogImportPoint()

        # Initialise buttton
        self.init_button = QToolButton()
        self.init_button.setMenu(QMenu())
        self.init_button.setPopupMode(QToolButton.MenuButtonPopup)

        # toolBar
        self.toolbar = self.iface.addToolBar('UnderMap')
        self.toolbar.setObjectName('UnderMap')

        # actions
        self.initialisePDFAction = None
        self.reportAction = None
        self.addOperatorAction = None
        self.initialiseFDPAction = None
        self.initialiseEmpriseAction = None
        self.addPDFAction = None
        self.splitPDFAction = None
        self.importPointsAction = None
        self.manageBufferAction = None
        self.saveAsGeoJsonAction = None
        self.controlAction = None

        QgsSettings().setValue("qgis/digitizing/reuseLastValues", True)
        # For enable/disable the addpdf editor icon
        self.iface.currentLayerChanged.connect(self.layer_changed)

    @staticmethod
    def tr(message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('UnderMap', message)

    # noinspection PyPep8Naming
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # the actions
        self.initialisePDFAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'initialpdf.png')),
            'Initialiser PDF',
            self.iface.mainWindow())

        self.addOperatorAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'ajouterOperateur.png')),
            'Ajouter un exploitant',
            self.iface.mainWindow())

        self.reportAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'icon.png')),
            'Générer le rapport',
            self.iface.mainWindow())

        self.initialiseFDPAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'icon.png')),
            'Initialiser un FDP',
            self.iface.mainWindow())

        self.initialiseEmpriseAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'icon.png')),
            'Initialiser une emprise',
            self.iface.mainWindow())

        self.addPDFAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'add_pdf.png')),
            'Ajouter pdf',
            self.iface.mainWindow())

        self.splitPDFAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'add_pdf.png')),
            'Découper un PDF',
            self.iface.mainWindow())

        self.importPointsAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'icon.png')),
            'Importer les points de calage',
            self.iface.mainWindow())

        self.manageBufferAction = QAction(
            QIcon(join(dirname(__file__), 'resources', '')),
            'Génerer les buffers',
            self.iface.mainWindow())

        self.saveAsGeoJsonAction = QAction(
            QIcon(join(dirname(__file__), 'resources', '')),
            'Exporter les GeoJSON',
            self.iface.mainWindow())

        self.controlAction = QAction(
            QIcon(join(dirname(__file__), 'resources', 'icon.png')),
            'Controller',
            self.iface.mainWindow())

        # actions dialogs
        self.initialisePDFAction.triggered.connect(self.initialise_PDF)
        self.addOperatorAction.triggered.connect(self.add_operator)
        self.initialiseFDPAction.triggered.connect(self.initialise_FDP)
        self.initialiseEmpriseAction.triggered.connect(self.initialise_emprise)
        self.reportAction.triggered.connect(self.export_report)
        self.addPDFAction.triggered.connect(self.add_pdf)
        self.splitPDFAction.triggered.connect(self.split_pdf)
        self.importPointsAction.triggered.connect(self.import_points)
        self.manageBufferAction.triggered.connect(self.manage_buffer)
        self.saveAsGeoJsonAction.triggered.connect(self.save_geojson)
        self.controlAction.triggered.connect(self.control)


        # add actions on menu
        self.init_button.menu().addAction(self.initialisePDFAction)
        self.init_button.menu().addAction(self.addOperatorAction)
        self.init_button.setDefaultAction(self.initialisePDFAction)
        # add separator
        #self.initialiseFDPAction.insertSeparator(self.initialisePDFAction)
        self.init_button.menu().addAction(self.initialiseFDPAction)
        self.init_button.menu().addAction(self.initialiseEmpriseAction)
        self.init_button.menu().addAction(self.splitPDFAction)
        self.init_button.menu().addAction(self.manageBufferAction)
        self.init_button.menu().addAction(self.saveAsGeoJsonAction)

        # add actions and menu in toolbar
        self.toolbar.addWidget(self.init_button)
        self.toolbar.addAction(self.reportAction)
        self.toolbar.addAction(self.addPDFAction)
        self.toolbar.addAction(self.importPointsAction)
        self.toolbar.addAction(self.controlAction)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.mainWindow().removeToolBar(self.toolbar)
        self.iface.currentLayerChanged.disconnect(self.layer_changed)

    def layer_changed(self, layer):

        try:
            layers = get_layers_in_group("RSX")
        except AttributeError:
            return
        if not hasattr(layer, 'name'):
            enable_addpdf = False

        elif layer.name() not in layers:
            enable_addpdf = False

        elif not hasattr(layer, 'providerType'):
            enable_addpdf = False
        elif layer.providerType() == 'wms':
            enable_addpdf = False
        elif not layer.geometryType() == 1:
            enable_addpdf = False
        else:
            enable_addpdf = True
        self.addPDFAction.setEnabled(enable_addpdf)

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

    def add_operator(self):
        self.addop.exec_()


    def add_pdf(self):
        self.addpdf.exec_()


    def split_pdf(self):
        self.splitpdf.exec_()


    def import_points(self):
        self.importpoints.exec_()

    def manage_buffer(self):
        project_path = get_project_path()
        manage_buffer(project_path)
        self.iface.messageBar().pushInfo('Undermap', "La génération des buffers a bien reussi."
                                                            )
    def control(self):
        opacity = 0.5
        transparency_raster(opacity)

    def initialise_PDF(self):
        project_path = get_project_path()
        if project_path == './':
            QMessageBox.warning(None,"Avertisment","Veulliez ouvrir un projet qgis")
            return
        else:
            dir_selected = QFileDialog.getExistingDirectory(None, "Sélectionner un dossier", project_path,  QFileDialog.ShowDirsOnly)
            if dir_selected == '':
                self.iface.messageBar().pushWarning('Undermap', "Aucun dossier séléctionné")
                return
            else:
                initialise_pdf(dir_selected)

    def initialise_FDP(self):
        project_path = get_project_path()
        if project_path == './':
            QMessageBox.warning(None, "Avertisment", "Veulliez ouvrir un projet qgis")
            return
        else:
            fileSelected = QFileDialog.getOpenFileName(None, "Sélectionnez un fichier", project_path, "*.dxf")
            if fileSelected == ('', ''):
                self.iface.messageBar().pushWarning('Undermap', "Aucun fichier dxf séléctionné")
                return
            else:
                initialise_fdp(fileSelected)

    def initialise_emprise(self):
        project_path = get_project_path()
        if project_path == './':
            QMessageBox.warning(None, "Avertissement", "Veuillez ouvrir un projet QGIS et l’enregistrer")
            return
        else:
            fileSelected = QFileDialog.getOpenFileName(None, "Sélectionnez un fichier", project_path, "*.kml")
            if fileSelected == ('', ''):
                self.iface.messageBar().pushWarning('Undermap', "Aucun fichier kml séléctionné")
                return
            else:
                initialise_emprise(fileSelected)


    def export_report(self):
        project_path = get_project_path()
        if project_path == './':
            QMessageBox.warning(None, "Avertisment", "Veuillez ouvrir un projet qgis")
            return
        else:
            if export_xlsx_report(project_path):
                self.iface.messageBar().pushInfo('Undermap', "La génération du rapport a bien reussi."
                                                            )
                os.startfile(join(project_path, QgsProject.instance().baseName()+'.xlsx'))
            else:
                QMessageBox.warning(None, 'Undermap', "QGIS ne peut pas écrire "
                                                         "le rapport car le fichier"
                                                             " {} est ouvert "
                                                         "dans une autre application"
                                                        .format(join(project_path, QgsProject.instance()
                                                        .baseName()+'.xlsx')))

    def save_geojson(self):
        project_path = get_project_path()
        if project_path == './':
            QMessageBox.warning(None, "Avertisment", "Veuillez ouvrir un projet qgis")
            return
        else:
            if export_as_geojson(project_path):
                 self.iface.messageBar().pushInfo('Undermap', "Les fichiers GeoJSON sont bien enregistrés dans {}".
                                                  format(join(project_path, "GEOJSON"))
                                                            )
