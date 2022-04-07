import os
import argparse

from xml.etree import ElementTree

from famapy.core.models import Configuration

from famapy.metamodels.fm_metamodel.models import FeatureModel
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEReader


# CONSTANTS
FM1 = 'feature_models/step1.xml'
FM2 = 'feature_models/step2.xml'
FM3 = 'feature_models/step3.xml'
FM4 = 'feature_models/step4.xml'


def get_files(dir: str) -> tuple[list[str], list[str]]:
    """Return the list of configurations files (.xml) and 
    the list of attributes files (.csv) in the provided directory.
    """
    configurations_files = []
    attributes_files = []
    for subdir, _, files in os.walk(dir):
        for file in files:
            filepath = os.path.join(subdir, file)
            _, file_extension = os.path.splitext(filepath)
            if file_extension.endswith('xml'):
                configurations_files.append(filepath)
            elif file_extension.endswith('csv'):
                attributes_files.append(filepath)
    return (configurations_files, attributes_files)


def parse_configuration(filepath: str) -> Configuration:
    """Parse a .xml configuration file generated with FeatureIDE."""
    tree = ElementTree.parse(filepath)
    root = tree.getroot()

    features = {}
    for child in root:
        feature_name = child.attrib['name']
        if 'automatic' in child.attrib:
            feature_selected = child.attrib['automatic'] == 'selected'
        elif 'manual' in child.attrib:
            feature_selected = child.attrib['manual'] == 'selected'
        else:
            feature_selected = False
        features[feature_name] = feature_selected
    return Configuration(elements=features)


def parse_attributes(filepath: str) -> dict[str, str]:
    """Parse a .csv file with the attributes configured."""

def load_feature_models() -> list[FeatureModel]:
    """Load the feature models of the visualization design process."""
    fm1 = FeatureIDEReader(FM1).transform()
    fm2 = FeatureIDEReader(FM2).transform()
    fm3 = FeatureIDEReader(FM3).transform()
    fm4 = FeatureIDEReader(FM4).transform()
    return [fm1, fm2, fm3, fm4]


def main():
    configuration = parse_configuration('feature_models/configurations/scenario1/config_fm1.xml')
    print(configuration)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Visualization')
    parser.add_argument('-f', dest='folder', type=str, required=True, 
                        help='Directory with the configurations and attributes files.')
    args = parser.parse_args()

    # Identify configurations and attributes files
    configurations_files, attributes_files = get_files(args.folder)

    # Parse configurations and attributes
    configurations = [parse_configuration(file) for file in configurations_files]
    attributes = [parse_attributes(file) for file in attributes_files]

    # Load the feature models
    fms = load_feature_models()

    # Load the mapping model


    print(configurations_files)
    print(attributes_files)
    