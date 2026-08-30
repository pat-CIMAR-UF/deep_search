import yaml
from pathlib import Path

def load_yaml(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

project_root_path = Path(__file__).parents[1]
yaml_file_path = project_root_path / "prompt" / "prompts.yaml"

prompt_yaml_content = load_yaml(yaml_file_path)

main_agent_content = prompt_yaml_content['main_agent']
sub_agents_content = prompt_yaml_content['sub_agents']

print(f"------Main Agent Content------\n{main_agent_content}")
print(f"\n")
for agent_name, agent_content in sub_agents_content.items():
    print(f"------Sub Agent Content: {agent_name}------\n{agent_content}")
    print(f"\n")    