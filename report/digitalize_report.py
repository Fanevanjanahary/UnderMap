# coding=utf-8

from os import listdir, rename, rmdir
from os.path import join, exists
from qgis.core import QgsVectorLayer, QgsProject
from UnderMap.gis.tools import length_feature
from UnderMap.definition.fields import rsx_color
from UnderMap.utilities.utilities import (
    get_project_path,
    get_folders_name,
    count_pdf_file,
    count_csv_line,
    residual_list,
    LOGO_PATH,
    WORKSHEETS,
    OPERATOR_SUB_DIR,
    RSX_SUB_GROUP,
    PDF_SUB_DIR
)

ECART = ['Moyen', 'Max']

def cell_color(rsx, workbook):
    cell_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        }
    )
    cell_format.set_fg_color(rsx_color[rsx])
    return cell_format



def create_head_content(worksheet, title, header_format, cell):
    logo = LOGO_PATH
    cell_to_nbr = ord(cell)
    cell_incr = 0
    item_head = 1
    head = ['Lineaire réseau (m)', 'En service', 'Abandonné', 'Total', 'Remarques']

    worksheet.set_column('A:A', 25)
    worksheet.insert_image('A1', logo)
    worksheet.set_column('{}:{}'.format(chr(cell_to_nbr + 12), chr(cell_to_nbr + 12)), 40)
    worksheet.merge_range('{}6:{}6'.format(cell, chr(cell_to_nbr + 11)), head[0], header_format)
    worksheet.merge_range('{}6:{}8'.format(chr(cell_to_nbr + 12), chr(cell_to_nbr + 12)), head[4], header_format)
    worksheet.merge_range('B2:{}2'.format(chr(cell_to_nbr + 11)), 'UnderMap', header_format)


    while item_head < 4 and cell_incr < 9:
        cell_head = cell_to_nbr + cell_incr
        worksheet.merge_range('{}7:{}7'.format(chr(cell_head), chr(cell_head+3)), head[item_head], header_format)
        cell_incr += 4
        item_head += 1
        for i, item in enumerate(['A', 'B', 'C', 'Total']):
            if item == 'Total':
                worksheet.write(7, cell_head + i - 65, item, header_format)
            else:
                 worksheet.write(7, cell_head + i - 65, 'Classe {}'.format(item), header_format)
    if cell == 'E':
        worksheet.set_column('B:B', 20)
        worksheet.merge_range('A6:A8', 'exploitant', header_format)
        worksheet.merge_range('B6:B8', 'Etat', header_format)
        worksheet.merge_range('C6:C8', 'Pages Traitées', header_format)
        worksheet.merge_range('D6:D8', 'Type de réseau', header_format)
        worksheet.merge_range('B3:{}3'.format(chr(cell_to_nbr + 11)), title, header_format)

    if cell == 'F':
        worksheet.merge_range('A6:A8', 'Etat', header_format)
        worksheet.merge_range('B6:D6', 'Pages', header_format)
        worksheet.merge_range('B7:B8', 'Traitées', header_format)
        worksheet.merge_range('C7:C8', 'Ingorées', header_format)
        worksheet.merge_range('D7:D8', 'Total', header_format)
        worksheet.merge_range('E6:E8', 'Type de réseau', header_format)
        worksheet.merge_range('B3:{}3'.format(chr(cell_to_nbr + 11)), title, header_format)

    if cell == 'B':
        worksheet.merge_range('A6:A8', 'Réseau', header_format)
        worksheet.merge_range('B3:{}3'.format(chr(cell_to_nbr + 11)), title, header_format)


def create_content(worksheet, worksheet_title, cell_header, workbook, row, column, data, layer):
    """ Création de contenue type de réseau

    :param worksheet: La feuille de travail
    :type worksheet: Worksheet

    :param worksheet_title: Titre de la feuille
    :type worksheet_title: str

    :param cell_header: Style entête de la feuille
    :type cell_header: Format

    :param workbook: Le fichier xlsx
    :type workbook: Workbook

    :param data: Les données à insérer
    :type data: List

     :param column: Colonne où ça va inserser
    :type column: str

    :param row: Ligne où ça va inserser
    :type row: int

    :param layer: une couche
    :type layer: QgsVectorLayer
    """

    create_head_content(worksheet, worksheet_title, cell_header, column)
    cell_letter_to_nbr = ord(column)
    cell_cord = cell_letter_to_nbr - 65
    last_row = row

    for i, item_value in enumerate(data):

        col_liner = 0
        sum_by_class = 0
        worksheet.write(row + i, cell_cord - 1, item_value, cell_color(item_value, workbook))
        worksheet.write(row + i, cell_cord + 12, '', cell_color(item_value, workbook))
        for j, item_class in enumerate(['A', 'B', 'C']):

            if layer is None:
                worksheet.write_formula(row + i, cell_cord + j,
                                 '=SUMIF({}!D9:D9999, $A%d, {}!{}9:{}9999)'
                                        .format(WORKSHEETS[0], WORKSHEETS[0], chr(ord('E') + j),
                                        chr(ord('E') + j)) % (row + i+ 1),
                                        cell_color(item_value, workbook))
                worksheet.write_formula(row + i, cell_cord + 4 + j,
                                 '=SUMIF({}!D9:D9999, $A%d, {}!{}9:{}9999)'
                                        .format(WORKSHEETS[0], WORKSHEETS[0], chr(ord('I') + j),
                                        chr(ord('I') + j)) % (row + i+ 1),
                                        cell_color(item_value, workbook))
            else:
                worksheet.write(row + i, cell_cord + j, length_feature(layer, item_value, item_class,0),
                                cell_color(item_value, workbook))
                worksheet.write(row + i, cell_cord + 4 + j, length_feature(layer, item_value, item_class,1),
                                cell_color(item_value, workbook))

        while sum_by_class<3 and col_liner < 9:
            cell_length_class = cell_letter_to_nbr + col_liner
            cell_by_class = cell_letter_to_nbr + sum_by_class
            cell_sum_by_func = cell_cord + col_liner + 3
            cell_sum_by_class = cell_cord + sum_by_class + 8
            worksheet.write_formula(row + i, cell_sum_by_func,
                            '=SUM(${}%d:${}%d)'.format(chr(cell_length_class), chr(cell_length_class + 2)) %
                                    (row + i + 1, row + i + 1),
                                    cell_color(item_value, workbook))
            worksheet.write_formula(row + i, cell_sum_by_class,
                            '=${}%d+${}%d'.format(chr(cell_by_class), chr(cell_by_class + 4)) %
                                    (row + i + 1, row + i + 1),
                                    cell_color(item_value, workbook))
            col_liner += 4
            sum_by_class += 1
        last_row  += 1
    return last_row


def get_position_operators(operators_path, operators_content):

    positions = [0]
    value = 0
    for i, item in enumerate(operators_content):
        layer_path = join(operators_path, item, OPERATOR_SUB_DIR[1], item)
        layer = QgsVectorLayer(layer_path+".shp")
        field = layer.dataProvider().fieldNameIndex('Reseau')
        values = sorted(layer.uniqueValues(field))
        if len(values) > 0 :
            value += len(values)-1
            positions.append(value)
        else:
            value += len(values)
            positions.append(value)
    return positions


def georeference_report(path, operator_name, row, worksheet, header_format):

    worksheet.merge_range('A{}:A{}'.format(row, row + 1), 'Page', header_format)
    worksheet.merge_range('B{}:B{}'.format(row, row + 1), 'Nombre de points', header_format)
    worksheet.merge_range('C{}:D{}'.format(row, row + 1), 'Methodede calage', header_format)
    worksheet.merge_range('E{}:F{}'.format(row, row), 'Ecart (m)', header_format)
    worksheet.merge_range('G{}:H{}'.format(row, row), 'Ecart (pix)', header_format)
    worksheet.merge_range('I{}:K{}'.format(row, row + 1), 'Remarques', header_format)
    worksheet.merge_range('M{}:O{}'.format(row, row + 1), 'Alertes', header_format)
    ecart_cell = 0
    while ecart_cell < 3:
        for i, item in enumerate(ECART):
            worksheet.write(row  , 4 + i + ecart_cell, item, header_format)
        ecart_cell += 2

    operator_path = join(path, RSX_SUB_GROUP[0], operator_name)
    tif_path = join(operator_path, RSX_SUB_GROUP[1])
    points = []
    for item in listdir(tif_path):
        points.append(item)

    pdf_root = join(operator_path, OPERATOR_SUB_DIR[0])
    pdf_path_to_treat = join(pdf_root, PDF_SUB_DIR[0])
    try:
        list_pdf = (pdf_file for pdf_file in listdir(pdf_path_to_treat) if pdf_file.endswith(".pdf"))
    except FileNotFoundError:
        rename(join(pdf_root, 'A-TRAITER'), pdf_path_to_treat)
        list_pdf = (pdf_file for pdf_file in listdir(pdf_path_to_treat) if pdf_file.endswith(".pdf"))
        if exists(join(pdf_root, 'IGNORE')):
            rename(join(pdf_root, 'IGNORE'), join(pdf_root, PDF_SUB_DIR[1]))
        if exists(join(pdf_root, 'UTILE')):
            rmdir(join(pdf_root, 'UTILE'))

    for i_pdf_to_treat, item_pdf_to_treat in enumerate(list_pdf):
        gcp_file_name = item_pdf_to_treat.replace('.pdf', '_modified.tif.points')
        if gcp_file_name in points:
            worksheet.write(row + 1 + i_pdf_to_treat, 0, item_pdf_to_treat)
            gcp_file = join(tif_path, gcp_file_name)
            list_of_residual = residual_list(gcp_file)
            if len(list_of_residual) > 0 :
                worksheet.write(row + 1 + i_pdf_to_treat, 1, count_csv_line(gcp_file) - 1)
                worksheet.write(row + 1 + i_pdf_to_treat, 4, round(
                    sum(list_of_residual)/len(list_of_residual), 2))
                worksheet.write(row + 1 + i_pdf_to_treat, 5, round(max(list_of_residual), 2))
            else:
                return

        else:
           return


def export_report_file(workbook, path):

    operators_path = join(path, RSX_SUB_GROUP[0])
    operators_content = get_folders_name(operators_path)

    cell_header = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#bebebe'})
    cell_rsx_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
    })
    cell_header.set_text_wrap()
    cell_rsx_format.set_text_wrap()


    position = get_position_operators(operators_path, operators_content)

    for i_worksheet, item_worksheet in  enumerate(WORKSHEETS):

        worksheet = workbook.add_worksheet(item_worksheet)
        for i, item in enumerate(operators_content):
            layer_path = join(operators_path, item, OPERATOR_SUB_DIR[1], item)
            layer = QgsVectorLayer(layer_path+".shp")
            field = layer.dataProvider().fieldNameIndex('Reseau')
            values = sorted(layer.uniqueValues(field))

            if i_worksheet == 0:
                create_content(worksheet, 'Synthèse par exploitant',
                                          cell_header, workbook, 8 + i + position[i], 'E', values, layer)
                if len(values) > 1:
                    worksheet.merge_range('A{}:A{}'.format(8 + i + position[i] + 1,
                                                           8 + i + position[i] + len(values)), item,
                                                           cell_rsx_format)
                    worksheet.merge_range('B{}:B{}'.format(8 + i + position[i] + 1,
                                                       8 + i + position[i] + len(values)), '',
                                                           cell_rsx_format)
                    worksheet.merge_range('C{}:C{}'.format(8 + i + position[i] + 1,
                                                       8 + i + position[i] + len(values)), count_pdf_file(item)[0],
                                                        cell_rsx_format)
                else:
                    worksheet.write(8 + i + position[i], 0, item, cell_rsx_format)
                    worksheet.write(8 + i + position[i], 1, '', cell_rsx_format)
                    worksheet.write(8 + i + position[i], 2, count_pdf_file(item)[0], cell_rsx_format)

            if i_worksheet == 1:
                try:
                    worksheet_rsx = workbook.add_worksheet(item)
                except:
                     worksheet_rsx = workbook.add_worksheet(item[0:30])
                last_row = create_content(worksheet_rsx, item, cell_header, workbook, 8, 'F', values, layer)
                for i_count_file, item_count_file in enumerate(count_pdf_file(item)[:2]):
                    worksheet_rsx.write(8, i_count_file + 1, item_count_file)
                worksheet_rsx.write_formula(8, 3,
                            '=${}%d+${}%d'.format('B', 'C')%(8 + 1, 8 + 1)
                )
                georeference_report(path, item, last_row + 2, worksheet_rsx, cell_header)

        if i_worksheet ==  1:
            create_content(worksheet, 'Synthèse par réseau', cell_header, workbook, 8, 'B', sorted(rsx_color), None)

    workbook.close()
