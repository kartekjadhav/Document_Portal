import yaml

def load_config(config_file_path="config/config.yaml"):
    with open(config_file_path, "r") as f:
        return yaml.safe_load(f)

if __name__=="__main__":
    print(load_config())
