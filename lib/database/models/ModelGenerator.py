import os.path
from typing import List, Callable, Dict, Tuple

from peewee import Model


# TODO: Move to utils


class ModelGeneratorProps:
    """
    Properties file to initialize the ModelGenerator class.
    Separating to make it easier to run

    model: Model The Peewee model class to be updated
    file_path: str The file path the model class is in
    folder_level: int (Optional) How many levels deep is the file from the main lib folder, default = 3
    """
    model: Model
    model_file_path: str
    model_folder_level: int = 3


class ModelGenerator(object):
    """
    ModelGenerator is a tool used to generate a Peewee database model that has been changed to my liking.
    It takes a class that is a child of the Peewee Model class, and adds in extra functions I use while
    utilizing Peewee.

    In other words, it will take a pre-defined Peewee Model and modify the file itself (or optionally
    to a different file) to add in some more functionality. I use this on all models I create via Peewee.

    Things added include a Keys class to easily get text references of all keys, a batch upsert method,
    and to string methods for all models.

    Example use case:

    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.abspath(os.path.join(dir_path, './ModelClass.py'))

    props = ModelGeneratorProps()
    props.model = ModelClass
    props.model_file_path = file_path

    gen = ModelGenerator(props)
    gen.updateModelFile()

    """
    tab: Callable[[int], str] = lambda x=1: '    ' * x

    model: Model
    model_file_path: str
    folder_level: int

    model_keys: List[str]
    model_class_name: str

    imports: Tuple[str, str]
    keys_class: str
    output_functions: Dict[str, str]

    # noinspection PyProtectedMember
    def __init__(self, props: ModelGeneratorProps):
        """
        Initializes the generator class. Takes in the model and adds it to the class's global variables.

        prec: The parameter model extends Peewee's Model class
        postc: Initializes a ModelGenerator class

        :param props: The property file containing the model, model file path, and (optional) model folder level
            to instantiate the generator class
        """
        self.model = props.model
        self.model_file_path = props.model_file_path
        self.folder_level = props.model_folder_level

        self.model_class_name = self.model._meta.name.title()
        self.model_keys = self.model._meta.sorted_field_names

        self.keys_class = self.create_keys_class()
        self.output_functions = self.create_output_functions()

    def create_keys_class(self) -> str:
        """
        Generate the Key class for the model to be output into the model file

        prec: The class model has been initialized
        postc: Returns the key class for the model

        :return: str The key class as a string
        """
        key_class_name = self.model_class_name + 'Keys'

        # Create array to hold new lines for Key class
        keys_class_lines: List[str] = [
            '',
            'class {}:'.format(key_class_name)
        ]

        format_key_class_line: Callable[[str], str] = lambda key: '{}{}: str = \'{}\''.format(ModelGenerator.tab(), key,
                                                                                              key) + (
                                                                      '\n' if key == 'created_at' else '')

        keys_class_lines += [format_key_class_line(key) for key in self.model_keys]
        keys_class_lines += ['', '', 'Keys = {}'.format(key_class_name), '', '']

        return '\n'.join(keys_class_lines)

    # noinspection PyProtectedMember
    def create_output_functions(self) -> Dict[str, str]:
        """
        Returns a dictionary containing all the new functions (as strings) to be added to the model file.
        As of now, the new functions are: initialize and values

        prec: The class model has been initialized
        postc: Returns a dictionary of functions to be added to the model file

        :return: Dict[str, str] A dictionary of functions
        """
        model_class_name = self.model_class_name
        model_keys = self.model_keys
        tab = ModelGenerator.tab

        functions: Dict[str, str] = {
            'initialize': '',
            'values': '',
        }

        # Create and init array to hold lines for the initialize function
        initialize_lines: List[str] = [
            '',
            tab() + '@staticmethod',
            tab() + 'def initialize(params: dict) -> \'{}\':'.format(model_class_name),
            tab(2) + 'model = {}()'.format(model_class_name),
            ''
        ]
        format_init_line: Callable[[str], str] = lambda key: '{}if Keys.{} in params:\n{}model.{} = params[Keys.{}]\n' \
            .format(tab(2), key, tab(3), key, key)

        initialize_lines += [format_init_line(key) for key in model_keys]
        initialize_lines.append(tab(2) + 'return model')

        functions['initialize'] = '\n'.join(initialize_lines)

        # Create and init line array for values function
        values_lines: List[str] = [
            '',
            tab() + 'def values(self):'
        ]

        value_keys = ', '.join(['self.' + x for x in model_keys])
        values_lines.append('{}return [{}]'.format(tab(2), value_keys))

        functions['values'] = '\n'.join(values_lines)

        return functions

    # noinspection PyProtectedMember
    def updateModelFile(self, output_path=None):
        """
        Updates the given model file with extra functions I personally add to each Peewee model
        I create. 
        
        The model file must match the model given at initialization, or the update will fail.
        
        Output_path can optionally be used to designate the file be output in a separate file,
        but is rarely used.
        
        prec: model_file_path matches the file path of the given model from initialization
        postc: Updates (or outputs) the model file with extra functions

        prec: All additions to file have been initialized
        postc: Writes updates to file
        
        :param output_path: Optional - Use to output the model file updates to a separate file
        """
        # Grab model and tab - just making things easier
        tab = ModelGenerator.tab
        model_file_path = self.model_file_path

        # Check if file exists
        if not os.path.isfile(model_file_path):
            raise FileNotFoundError('The path {} did not exist.'.format(model_file_path))

        # Check if output path exist
        if output_path is not None:
            output_path_check = output_path[:output_path.rfind('/')]

            if not os.path.exists(output_path_check):
                raise FileNotFoundError('Output path {} does not exist.'.format(output_path_check))

        # Output all updates to file
        print('Opening file to update...', end='')
        with open(model_file_path, 'r+') as file:
            print('Success')
            print('Parsing updates...', end='')

            class_file: str = file.read()
            lines: List[str] = class_file.split('\n')

            class_idx: int = 0
            for idx in range(len(lines)):
                line = lines[idx]
                if 'class' in line:
                    class_idx = idx
                    lines[idx] += '\n{}global Keys\n'.format(tab())
                    break

            end_idx = len(lines) - 1
            if lines[-1].strip() != '':
                end_idx += 1

            lines = lines[:class_idx - 1] + [self.keys_class] + lines[class_idx:end_idx]

            for func in self.output_functions:
                lines += [self.output_functions[func]]

            class_file = '\n'.join(lines) + '\n'
            print('Success')

            print('Outputting updates to file...', end='')
            file.seek(0)
            file.write(class_file)
            file.truncate()
            print('Success')

# import sys
#
# dir_path = os.path.dirname(os.path.realpath(__file__))
# dir_path = os.path.abspath(os.path.join(dir_path, '../../..'))
#
# sys.path.append(dir_path)
#
# from lib.database.models.Taxes import Taxes
#
# dir_path = os.path.dirname(os.path.realpath(__file__))
# file_path = os.path.abspath(os.path.join(dir_path, './Taxes.py'))
#
# model_props = ModelGeneratorProps()
# model_props.model = Taxes
# model_props.model_file_path = file_path
#
# gen = ModelGenerator(model_props)
# gen.updateModelFile()
