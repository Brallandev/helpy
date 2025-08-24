from src.model.prompts import META_AGENT_PROMPT, CONSOLIDATOR_PROMPT
from langchain.schema import HumanMessage
import json
from src.utils.str_parsing import parse_str

class MetaAgent:
    def __init__(self, user_info: str, doc: str, config: dict, llm):
        self.user_info = user_info
        self.doc = doc
        self.llm = llm
        self.prompt = META_AGENT_PROMPT.format(
            user_info=self.user_info,
            doc=self.doc,
            min_agent=config['min_agents'],
            max_agent=config['max_agents'],
            language=config['language'],
            num_questions=config['num_questions'],
            scores = config['decision_scores']
        )

    def run(self):
        response = self.llm.invoke([HumanMessage(content=self.prompt)])
        if not isinstance(response, dict):
            cleaned = parse_str(response.content)
            d = json.loads(cleaned)
        else:
            d = response
        response_dict = d

        self.questions_agent = response_dict.get("questioner-prompt", [])
        self.critical_agents = response_dict.get("critical-agents", [])

class SimpleAgent:
    def __init__(self, prompt: str, llm):
        self.prompt = prompt
        self.llm = llm

    def run(self):
        response = self.llm.invoke([HumanMessage(content=self.prompt)])
        if not isinstance(response, dict):
            cleaned = parse_str(response.content)
            d = json.loads(cleaned)
        else:
            d = response
        self.response = d

class AgentsGroup:
    def __init__(self, agents: list, llm_init, llm_params: dict):
        self.agents_data = agents
        self.llm_init = llm_init
        self.llm_params = llm_params
        self.responses = []

    def run(self, questions):
        s = f'\nAnd these were the questions asked to the user with the answers:\n\n {questions} \n\nPlease remeber that the only output must be the JSON'
        for agent in self.agents_data:
            agent_instance = SimpleAgent(agent['prompt']+s, self.llm_init(**self.llm_params))
            agent_instance.run()
            if not isinstance(agent_instance.response, dict):
                cleaned = parse_str(agent_instance.response.content)
                d = json.loads(cleaned)
            else:
                d = agent_instance.response
            self.responses.append({
                "name": agent['name'],
                "response": d
            })

class ConsolidatorAgent:
    def __init__(self, responses: list, llm):
        self.responses = responses
        self.llm = llm
        self.response = None

    def run(self, doc: str):
        response = self.llm.invoke([HumanMessage(content=CONSOLIDATOR_PROMPT.format(agent_outputs=self.responses,
                                                                             doc=doc))])
        if not isinstance(response, dict):
            cleaned = parse_str(response.content)
            d = json.loads(cleaned)
        else:
            d = response
        self.response = d