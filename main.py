import os
import argparse
import csv
from typing import Any

import jinja2

from xml.etree import ElementTree

from famapy.core.models import Configuration

from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEReader, UVLReader

from variation_point import VariationPoint, Variant

# CONSTANTS
FM1 = 'feature_models/FeatureIDE/step1.xml'

FM2_graph = 'feature_models/FeatureIDE/step2_graph.xml'
FM3_graph = 'feature_models/FeatureIDE/step3_graph.xml'
FM4_graph = 'feature_models/FeatureIDE/step4_graph.xml'

FM2_table = 'feature_models/FeatureIDE/step2_table.xml'
FM3_table = 'feature_models/FeatureIDE/step3_table.xml'
FM4_table = 'feature_models/FeatureIDE/step4_table.xml'


def get_files(dir: str) -> tuple[list[str], list[str]]:
    """Return the list of configurations files (.xml) and 
    the list of attributes files (.csv) in the provided directory.
    """
    configurations_files = []
    attributes_files = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            filepath = os.path.join(root, file)
            _, file_extension = os.path.splitext(filepath)
            if file_extension.endswith('xml'):
                configurations_files.append(filepath)
            elif file_extension.endswith('csv'):
                attributes_files.append(filepath)
    configurations_files.sort()
    attributes_files.sort()
    return (configurations_files, attributes_files)


def load_feature_models_graph() -> list[FeatureModel]:
    """Load the feature models of the visualization design process."""
    fm1 = FeatureIDEReader(FM1).transform()
    fm2 = FeatureIDEReader(FM2_graph).transform()
    fm3 = FeatureIDEReader(FM3_graph).transform()
    fm4 = FeatureIDEReader(FM4_graph).transform()
    return [fm1, fm2, fm3, fm4]


def load_feature_models_table() -> list[FeatureModel]:
    fm1 = FeatureIDEReader(FM1).transform()
    fm2 = FeatureIDEReader(FM2_table).transform()
    fm3 = FeatureIDEReader(FM3_table).transform()
    #fm4 = FeatureIDEReader(FM4_table).transform()
    return [fm1, fm2, fm3]


def get_feature_from_fms(feature_name: str, fms: list[FeatureModel]) -> Feature:
    """Return the feature object from all the feature models of the VIS process."""
    for fm in fms:
        feature = fm.get_feature_by_name(feature_name)
        if feature is not None:
            return feature
    raise Exception(f'The feature {feature_name} does not exist in any feature model.')


def parse_configuration(filepath: str, fms: list[FeatureModel]) -> Configuration:
    """Parse a .xml configuration file generated with FeatureIDE."""
    tree = ElementTree.parse(filepath)
    root = tree.getroot()

    features = {}
    for child in root:
        if child.attrib:
            feature_name = child.attrib['name']
            if 'automatic' in child.attrib:
                feature_selected = child.attrib['automatic'] == 'selected'
            elif 'manual' in child.attrib:
                feature_selected = child.attrib['manual'] == 'selected'
            else:
                feature_selected = False
            feature_object = get_feature_from_fms(feature_name, fms)
            features[feature_object] = feature_selected
    return Configuration(elements=features)


def parse_attributes(filepath: str) -> dict[str, str]:
    """Parse a .csv file with the attributes configured."""
    attributes = {}  # dictionary of attribute_identifier -> value
    with open(filepath, mode='r') as file:
        csv_reader = csv.DictReader(file, skipinitialspace=True)
        for row in csv_reader:
            attribute = row['Attribute']
            value = row['Value']
            attributes[attribute] = value
    return attributes


def load_mapping_model(filepath: str, fms: list[FeatureModel]) -> dict[str, VariationPoint]:
    """Load the mapping model with the variation points and variants information."""
    variation_points = {}  # dictionary of feature -> variation points
    with open(filepath, mode='r') as file:
        csv_reader = csv.DictReader(file, skipinitialspace=True)
        for row in csv_reader:
            vp_feature = row['VariationPointFeature']
            vp_handler = row['Handler']
            variant_feature = row['VariantIdentifier']
            variant_value = row['VariantValue']
            if '.' in variant_feature:  # it is an attribute
                key = variant_feature
                variation_points[variant_feature] = VariationPoint(feature=get_feature_from_fms(vp_feature, fms),
                                                                   handler=vp_handler)
            elif not vp_feature in variation_points:
                key = vp_feature
                variation_points[vp_feature] = VariationPoint(feature=get_feature_from_fms(vp_feature, fms),
                                                              handler=vp_handler)
            else:
                key = vp_feature
            if variant_value == '-':
                variant_value = None
            variant = Variant(identifier=variant_feature, value=variant_value)
            variation_points[key].variants.append(variant)
    return variation_points


def is_selected_in_a_configuration(feature: Feature, configurations: list[Configuration]) -> bool:
    return any(feature in config.elements and config.elements[feature] for config in configurations)


def get_attribute_value(identifier: str, attributes: list[dict[str, str]]) -> str:
    for attributes_dict in attributes:
        if identifier in attributes_dict:
            return attributes_dict[identifier]
    return None


def get_variant_value(fms: list[FeatureModel], variation_point: VariationPoint, configurations: list[Configuration],
                      attributes: list[dict[str, str]]) -> str:
    """Return the value of the variant according to the provided configurations/attributes."""
    for variant in variation_point.variants:
        identifier = variant.identifier
        if '.' in identifier:
            feature = identifier[:identifier.index('.')]
            value = get_attribute_value(identifier, attributes)
        else:
            feature = identifier
            value = variant.value
        if is_selected_in_a_configuration(get_feature_from_fms(feature, fms), configurations):
            return value
    return None


def get_variant_value_in_configuration(fms: list[FeatureModel], variation_point: VariationPoint,
                                       configuration: Configuration, attributes: dict[str, str]) -> str:
    """Return the value of the variant according to a specific configuration/attributes."""
    for variant in variation_point.variants:
        identifier = variant.identifier
        if '.' in identifier:
            feature = identifier[:identifier.index('.')]
            value = attributes.get(identifier)
        else:
            feature = identifier
            value = variant.value
        feature = get_feature_from_fms(feature, fms)
        if feature in configuration.elements and configuration.elements[feature]:
            return value
    return None


def build_template_maps(fms: list[FeatureModel], mapping_model: dict[str, VariationPoint],
                        configurations: list[Configuration], attributes: list[dict[str, str]]) -> dict[str, Any]:
    # set_of_attributes = {a[a.index('.')+1:] for a_dict in attributes for a in a_dict.keys()}
    maps = {}
    multi_features_maps = []

    # Simple features
    for vp in mapping_model.values():
        if not '.' in vp.handler:  # it is a simple feature (not a multi-feature)
            if is_selected_in_a_configuration(vp.feature, configurations):
                if not vp.variants:
                    maps[vp.handler] = True
                elif vp.variants[0].identifier == '-':
                    maps[vp.handler] = True
                else:
                    maps[vp.handler] = get_variant_value(fms, vp, configurations, attributes)

    # Multi-features:
    i = 0
    for config in configurations:
        feature = get_feature_from_fms('DataSet', fms)
        if feature in config.elements and config.elements[
            feature]:  # it is a instance configuration of the multi-feature
            config_attributes = attributes[i]
            try:
                while not any('DataSet' in a for a in attributes[i].keys()):
                    i += 1
                    config_attributes = attributes[i]
            except:
                raise Exception('There is needed one configuration file for the attributes for at least one DataSet.')
            dataset_map = {}
            for vp in mapping_model.values():
                if '.' in vp.handler:  # it is a multi-feature
                    handler_identifier_in_template = vp.handler[vp.handler.index('.') + 1:]
                    if vp.feature in config.elements and config.elements[feature]:
                        if not vp.variants:
                            dataset_map[handler_identifier_in_template] = True
                        else:
                            dataset_map[handler_identifier_in_template] = get_variant_value_in_configuration(fms, vp,
                                                                                                             config,
                                                                                                             config_attributes)
            multi_features_maps.append(dataset_map)
            i += 1
    maps['plots'] = multi_features_maps
    return maps


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate Visualization')

    parser.add_argument('-f', dest='folder', type=str, required=True,
                        help='Directory with the configurations and attributes files.')

    parser.add_argument('-t', dest='type', type=str, required=False,
                        help='Directory with the configurations and attributes files.')

    args = parser.parse_args()

    # Identify configurations and attributes files
    configurations_files, attributes_files = get_files(args.folder)

    print('CONFIGURATION FILES:')
    for i, config_file in enumerate(configurations_files):
        print(f'|-{i}: {config_file}')

    print('ATTRIBUTES FILES:')
    for i, attribute_file in enumerate(attributes_files):
        print(f'|-{i}: {attribute_file}')

    type = args.type

    if type == "graph":

        # Load the feature models
        fms = load_feature_models_graph()

        # Parse configurations and attributes
        configurations = [parse_configuration(file, fms) for file in configurations_files]
        attributes = [parse_attributes(file) for file in attributes_files]

        # Load the mapping model
        mapping_model = load_mapping_model('mapping_models/pgfplots_map.csv', fms)
        print(f'MAPPING MODEL:')
        for i, vp in enumerate(mapping_model.values()):
            print(f'|-vp{i}: {vp}')

        maps = build_template_maps(fms, mapping_model, configurations, attributes)
        print(f'TEMPLATE CONFIGURATION:')
        for h, v in maps.items():
            if isinstance(v, list):
                for i, multi_map in enumerate(v):
                    print(f'|-plot{i}: {multi_map}')
            else:
                print(f'|-{h}: {v}')

        template_loader = jinja2.FileSystemLoader(searchpath="./")
        environment = jinja2.Environment(loader=template_loader)
        template = environment.get_template('templates/template.tex')
        content = template.render(maps)

        with open('visualization.tex', 'w', encoding='utf-8') as file:
            file.write(content)

    if type == "table":

        # Load the feature models
        fms = load_feature_models_table()


    # print(f'MAPPING MODEL: {mapping_model}')
    # print(f'CONFIGURATIONS: {configurations}')
    # print(f'ATTRIBUTES: {attributes}')
