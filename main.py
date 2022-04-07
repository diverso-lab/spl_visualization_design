import jinja2

from famapy.core.models import Configuration
from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature
from famapy.metamodels.fm_metamodel.transformations.uvl_reader import UVLReader
from famapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader

from scripts.variation_point import VariationPoint


EXAMPLE_CONFIG = {'SPLC2022', 'Color', 'Blue', 'Mark', 'Diamond'}
CONFIG_FM1 = {'Visualization', 'MessageToDisplay', 'EntireSeriesOfValues', 'Graph'}
CONFIG_FM2 = {'Graph', 'Information', 'MissingValues', 'DataRelationship', 'TimeSeries', 'change', 'ValueEncodingObject', 'Points', 'DotPlot'}




def get_variant(feature: Feature, configuration: Configuration) -> Feature:
    return next((f for f in configuration.elements if configuration.elements[f] and f.get_parent() == feature), None)


# def get_variation_points(fm: FeatureModel, configuration: Configuration) -> list[VariationPoint]:
#     return [
#         VariationPoint(fm.get_feature_by_name('Color'), 'color', get_variant(fm.get_feature_by_name('Color'), configuration)),
#         VariationPoint(fm.get_feature_by_name('Mark'), 'mark', get_variant(fm.get_feature_by_name('Mark'), configuration)),
#     ]

def get_variation_points(fm: FeatureModel, configuration: Configuration) -> list[VariationPoint]:
    return [
        VariationPoint(fm.get_feature_by_name('Blue'), 'color', 'blue'),
        VariationPoint(fm.get_feature_by_name('Diamond'), 'mark', 'diamond'),
    ]


def main():
    # Load feature model
    #feature_model = UVLReader('fm.uvl').transform()  # Fail the UVL Reader (because of constraints and parents of features)
    feature_model = FeatureIDEReader('fm.xml').transform()
    configuration = Configuration({f: (True if f.name in EXAMPLE_CONFIG else False) for f in feature_model.get_features()})
    print('FM loaded.')
    print(feature_model)
    print(f'Features: {[str(f) for f in feature_model.get_features()]}')
    for f in feature_model.get_features():
        print(f'{str(f)} -> {str(f.get_parent())}')
    print(f'Configuration: {[str(f) for f in configuration.elements if configuration.elements[f]]}')

    vps = get_variation_points(feature_model, configuration)
    print(vps)

    maps = {vp.handle: vp.value for vp in vps if vp.feature in configuration.elements and configuration.elements[vp.feature]}
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    environment = jinja2.Environment(loader=template_loader)
    template = environment.get_template('template.csv')
    content = template.render(maps)

    with open('example.csv', 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == '__main__':
    main()