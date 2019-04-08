# coding=utf-8

"""les actions"""
import os
import glob
import shutil
from os.path import join, basename, exists, dirname
from qgis.core import QgsProject, QgsVectorLayer, QgsVectorFileWriter
from UnderMap.library_extras import xlsxwriter
from UnderMap.report.digitalize_report import export_report_file
from UnderMap.utilities.utilities import (
    PROJECT_GROUP,
    PDF_SUB_DIR,
    OPERATOR_SUB_DIR,
    create_dir,
    copy_file,
    get_project_path,
    groups_to_array,
    get_elements_name
    )
from UnderMap.gis.tools import (
    save_as_shp,
    add_layer_in_group,
    create_group,
    create_layer,
    categorized_layer,
    get_group,
    export_layer_as,
    merge_features_connected
    )


def initialise_pdf(from_operators):
    """ Initialiser PDF

    :param from_operators: Chemin des données brutes
    :return:
    """
    create_group()
    for i_op, item in enumerate(get_elements_name(from_operators, True, None)):
        operator_dir = join(from_operators, item)
        create_operator(item, operator_dir, i_op)


def create_operator(name, pdf, index):
    """ Creation d'un opeérateur

    :param name: Le nom de l'opérateur
    :type name: str

    :param pdf: Le(s) fichier(s) pdf associé(s) à un opérateur
    :type pdf: str

    :param index: la position de la couche dans qgis groupe
    """
    root = join(get_project_path(), PROJECT_GROUP[2])
    operator_dir = join(root, name)
    qgis_groups = get_group()
    tif_group = qgis_groups.findGroup(PROJECT_GROUP[3])
    if tif_group is not None:
        if qgis_groups.findGroup(name) is None:
            tif_group.addGroup(name)
    if not exists(root):
        os.makedirs(root)

    operators_content = get_elements_name(root, True, None)
    if not exists(join(root, name)):
        for item_operator_sub_dir in OPERATOR_SUB_DIR:
            os.makedirs(join(operator_dir, item_operator_sub_dir))
            if item_operator_sub_dir == 'SHP':
                layer = create_layer(join(operator_dir, item_operator_sub_dir), name)
                if index is not None:
                    add_layer_in_group(layer, qgis_groups.findGroup(PROJECT_GROUP[2]), index, 'line_style.qml')
                else:
                    add_layer_in_group(layer, qgis_groups.findGroup(PROJECT_GROUP[2]),
                                       len(operators_content), 'line_style.qml')
            elif item_operator_sub_dir == 'PDF':
                for item_sous_pdf in PDF_SUB_DIR:
                    sub_pdf = join(operator_dir, item_operator_sub_dir, item_sous_pdf)
                    os.makedirs(sub_pdf)
                copy_file(pdf, join(operator_dir, item_operator_sub_dir), ".pdf")
    else:
        pass


def initialise_fdp(dxf_file):
    """ Initialisation d'un fond de plan

    :param dxf_file: Le fichier dxf
    :type dxf_file: str
    """
    create_dir(get_project_path(), 'FDP/SHP')
    copy_file(dxf_file[0], join(get_project_path(), 'FDP'), None)
    if get_group().findGroup(PROJECT_GROUP[1]) is None :
        get_group().addGroup(PROJECT_GROUP[1])
    shp_path = join(get_project_path(),'FDP/SHP',basename(dxf_file[0].replace('dxf', 'shp')))
    dxf_info = "|layername=entities|geometrytype=LineString"
    layer_name = basename(dxf_file[0]).split('.')[0]
    dxf_vl = QgsVectorLayer(dxf_file[0]+dxf_info, layer_name, "ogr")
    if save_as_shp(dxf_vl, shp_path, dxf_vl.crs()):
        layer = QgsVectorLayer(shp_path,  layer_name)
        layer.setCrs(QgsProject.instance().crs())
        add_layer_in_group(layer, get_group().findGroup(PROJECT_GROUP[1]), 0, None)
        categorized_layer(layer, 'Layer')


def initialise_emprise(kml_file):
    """ Initialisation d'une emprise

    :param kml_file: Le fichier kml
    :type kml_file: str
    """
    qgis_groups = get_group()
    create_dir(get_project_path(), 'FDP/SHP')
    copy_file(kml_file[0], join(get_project_path(), 'FDP'), None)
    if qgis_groups.findGroup(PROJECT_GROUP[1]) is None:
        qgis_groups.addGroup(PROJECT_GROUP[1])
    shp_path = join(get_project_path(), 'FDP/SHP', basename(kml_file[0].replace('kml', 'shp')))
    layer_name = basename(kml_file[0]).split('.')[0]
    dxf_vl = QgsVectorLayer(kml_file[0], layer_name, "ogr")
    if save_as_shp(dxf_vl, shp_path, QgsProject.instance().crs()):
        layer = QgsVectorLayer(shp_path,  layer_name)
        add_layer_in_group(layer, qgis_groups.findGroup(PROJECT_GROUP[1]), 1, 'emprise_style.qml')


def export_xlsx_report(path):
    """Générer le fichier de rapport xlsx

    :param path: chemin du projet
    :return: l'état de géneration
    :rtype: Boolean
    """
    name_file = QgsProject.instance().baseName()
    file = join(path, name_file+'.xlsx')
    workbook = xlsxwriter.Workbook(file)

    try:
        export_report_file(workbook, path)
        return True
    except PermissionError:
        return False

def export_as_geojson(path):

    rsx_path = join(path, 'RSX')

    for root, dirs, files in os.walk(rsx_path):
        for file in files:
            if  root[-3:] == 'SHP' and file.endswith(".shp"):
                to_dir = join(root[0:-3], 'GEOJSON')
                create_dir(to_dir, None)
                layer = root + os.sep +file
                export_layer_as(layer, None, "GeoJSON", to_dir)
    return True

def merge_features_connected_layers(project_path):

    operators_path = join(project_path, 'RSX')
    operators_content = get_elements_name(operators_path, True, None)

    for i_op, item in enumerate(operators_content):
        # load vectors
        shp_path = join(operators_path, item, 'SHP')
        for shp_file in glob.glob(join(shp_path, '*.shp')):
            layer_name = basename(shp_file).replace(".shp", "")
            layer = QgsVectorLayer(shp_file, layer_name, "ogr")
            if layer.geometryType() == 1:
                merge_features_connected(layer, shp_file)


def get_layers_merged():

    layers = []
    project_path = get_project_path()
    operators_path = join(project_path, 'RSX')
    operators_content = get_elements_name(operators_path, True, None)
    for i_op, item in enumerate(operators_content):
        shp_path = join(operators_path, item, 'SHP_')
        for shp_file in glob.glob(join(shp_path, '*.shp')):
            layer_name = basename(shp_file).replace(".shp", "")
            layer = QgsVectorLayer(shp_file, layer_name, "ogr")
            layer.setCrs(QgsProject.instance().crs())
            layers.append(layer)
    return layers


def erase_two_layers(project_path):

    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup('RSX')
    operators_path = join(project_path, 'RSX')
    operators_content = get_elements_name(operators_path, True, None)

    layers = get_layers_merged()
    for i_op, item in enumerate(operators_content):
        # load vectors
        shp_path = join(operators_path, item, 'SHP')
        for shp_file in glob.glob(join(shp_path, '*.shp')):
            layer_name = basename(shp_file).replace(".shp", "")
            if '_' not in layer_name:
                print(layers[i_op], layers[i_op].name())
                if group is not None:
                    for child in group.children():
                        QgsProject.instance().removeMapLayer(child.layerId())
                root.removeChildNode(group)
                QgsVectorFileWriter.deleteShapeFile(shp_file)
                export_layer_as(layers[i_op], layer_name, "ESRI Shapefile", dirname(shp_file))
        shp_merged_path = join(operators_path, item, 'SHP_')
        print(shp_merged_path)
        QgsVectorFileWriter.deleteShapeFile(shp_file.replace('SHP','SHP_'))
        shutil.rmtree(shp_merged_path, ignore_errors=True)
