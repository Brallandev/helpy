from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from typing import List
from src.model.schemas import MetaAgentOutputSchema, QuestionerSchema, AgentResponseSchema, ConsolidatorOutputSchema, CriticalAgentSchema
from src.model.prompts import META_AGENT_PROMPT, CONSOLIDATOR_PROMPT


meta_parser = PydanticOutputParser(pydantic_object=MetaAgentOutputSchema)
consolidator_parser = PydanticOutputParser(pydantic_object=ConsolidatorOutputSchema)
agent_parser = PydanticOutputParser(pydantic_object=AgentResponseSchema)
questioner_parser = PydanticOutputParser(pydantic_object=QuestionerSchema)

meta_prompt_template = PromptTemplate(
    template=META_AGENT_PROMPT + "\n\n{format_instructions}",
    input_variables=["user_info", "doc", "min_agent", "max_agent", "language", "num_questions", "scores"],
    partial_variables={"format_instructions": meta_parser.get_format_instructions()}
)

consolidator_prompt_template = PromptTemplate(
    template=CONSOLIDATOR_PROMPT + "\n\n{format_instructions}",
    input_variables=["agent_outputs", "doc"],
    partial_variables={"format_instructions": consolidator_parser.get_format_instructions()}
)


class MetaAgent:
    def __init__(self, user_info: str, doc: str, config: dict, llm):
        self.user_info = user_info
        self.doc = doc
        self.llm = llm
        self.config = config
        self.output: MetaAgentOutputSchema = None

        # New attributes
        self.questions_agent: str = ""
        self.critical_agents: List[CriticalAgentSchema] = []

    def run(self) -> MetaAgentOutputSchema:
        prompt_text = meta_prompt_template.format(
            user_info=self.user_info,
            doc=self.doc,
            min_agent=self.config['min_agents'],
            max_agent=self.config['max_agents'],
            language=self.config['language'],
            num_questions=self.config['num_questions'],
            scores=self.config['decision_scores']
        )
        response = self.llm.invoke([HumanMessage(content=prompt_text)])
        self.output = meta_parser.parse(response.content)

        self.questions_agent = self.output.questioner_prompt
        self.critical_agents = self.output.critical_agents

        return self.output

class QuestionerAgent:
    def __init__(self, prompt: str, llm):
        self.llm = llm
        self.prompt = prompt
        self.output: QuestionerSchema | None = None

    def run(self) -> QuestionerSchema:
        response = self.llm.invoke([HumanMessage(content=self.prompt)])
        self.response = questioner_parser.parse(response.content)

class SimpleAgent:
    def __init__(self, name: str, prompt: str, llm):
        self.name = name
        self.prompt = prompt
        self.llm = llm
        self.response: AgentResponseSchema = None

    def run(self, questions: str) -> AgentResponseSchema:
        full_prompt = self.prompt + f"\n\nAnd these were the questions asked to the user with the answers:\n{questions}\nPlease return strictly JSON with comments, score, and suggestions."
        raw_response = self.llm.invoke([HumanMessage(content=full_prompt)])
        self.response = agent_parser.parse(raw_response.content)
        return self.response


class AgentsGroup:
    def __init__(self, agents_data: List[dict], llm_init, llm_params: dict):
        self.agents_data = agents_data
        self.llm_init = llm_init
        self.llm_params = llm_params
        self.responses: List[dict] = []

    def run(self, questions: str):
        self.responses = []
        for agent_info in self.agents_data:
            agent_instance = SimpleAgent(agent_info.name,
                                         agent_info.prompt,
                                         self.llm_init(**self.llm_params))
            agent_response = agent_instance.run(questions)
            self.responses.append({
                "name": agent_info.name,
                "response": agent_response.dict()
            })
        return self.responses


class ConsolidatorAgent:
    def __init__(self, responses: List[dict], llm):
        self.responses = responses
        self.llm = llm
        self.output: ConsolidatorOutputSchema = None

    def run(self, doc: str) -> ConsolidatorOutputSchema:
        prompt_text = consolidator_prompt_template.format(agent_outputs=self.responses, doc=doc)
        raw_response = self.llm.invoke([HumanMessage(content=prompt_text)])
        self.response = consolidator_parser.parse(raw_response.content)