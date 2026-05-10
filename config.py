import yaml


def load_config(path):
    
    try:
        
        with open(path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
            return (data)
    except FileNotFoundError:
        print(f'File not found: {path}')
    except yaml.YAMLError as e:
        print(f'Error yaml parsing: {e}')