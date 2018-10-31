# coding=utf-8

"""Définition des attributs"""


from PyQt5.QtCore import QVariant


operator_def = {
    'name': 'Operateur',
    'type': QVariant.String,
    'length': 50,
    'precision': 0
}
class_def = {
    'name': 'Classe',
    'type': QVariant.String,
    'length': 1,
    'precision': 0,
}

diameter_def = {
    'name': 'Diametre',
    'type': QVariant.Double,
    'length': 10,
    'precision': 3,
}

rsx_def = {
    'name': 'Reseau',
    'type': QVariant.String,
    'length': 10,
    'precision': 0,
}

abandoned_def = {
    'name': 'Abandon',
    'type': QVariant.Double,
    'length': 1,
    'precision': 0,
}
