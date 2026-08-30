import yaml
from pathlib import Path

def load_yaml(file_path: str | Path) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

project_root_path = Path(__file__).parents[1]
yaml_file_path = project_root_path / "prompt" / "prompts.yaml"

prompt_yaml_content = load_yaml(yaml_file_path)

main_agent_content = prompt_yaml_content.get('main_agent', {})
sub_agents_content = prompt_yaml_content.get('sub_agents', {})

if __name__ == "__main__":
    print(f"------Main Agent------\nName: {main_agent_content.get('name', 'N/A')}\nDescription: {main_agent_content.get('description', 'N/A')}System Prompt: {main_agent_content.get('system_prompt', 'N/A')}\n")
    for agent_name, agent_content in sub_agents_content.items():
        print(f"------Sub Agent: {agent_name}------\nName: {agent_content.get('name', 'N/A')}\nDescription: {agent_content.get('description', 'N/A')}System Prompt: {agent_content.get('system_prompt', 'N/A')}\n")
    